from abc import ABC, abstractmethod
from collections import Counter
import re
from typing import Tuple
from scan_classes import *


class Filter(ABC):
    """Abstract base class for filters with an abstract method `apply()`."""

    def __init__(self, weight: float):
        """Initialize the Filter with a weight parameter."""
        self.weight = weight

    @abstractmethod
    def apply(self, lines: List[Line]):
        """Apply the filter on a given list of lines."""
        raise NotImplementedError


class LineFilter:
    """
    LineFilter is used to apply multiple filters on lines.

    Args:
        filters (Filter): Filters to be applied.
    """

    def __init__(self, *filters: Filter):
        self.filters = filters

    def get_possible_categories(self, menu: Menu, conf_threshold=0.76) -> List[Line]:
        """
        Filters the lines and returns those with category_confidence above the conf_threshold.

        Args:
            menu (Menu): The menu that contains the lines to be filtered.
            conf_threshold (float): The minimum category_confidence for a line to be considered.

        Returns:
            List[Line]: Lines with category_confidence greater than conf_threshold.
        """

        def lines_above_confidence() -> List[Line]:
            return [
                line
                for line in lines
                if line.analysis.category_confidence > conf_threshold
            ]

        # get all lines
        lines = [line for page in menu.pages for line in page.lines]

        for filter in self.filters:
            filter.apply(lines)
            print(
                f"{filter.__class__.__name__} - remaining lines:{len(lines_above_confidence())}"
            )

        return lines_above_confidence()


class FilterPriceLines(Filter):
    """Penalizes lines that look like prices."""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if ",-" in line.text and any(char.isdigit() for char in line.text):
                line.analysis.type = "price"
                line.analysis.category_confidence *= self.weight


class FilterLongLines(Filter):
    """Filters long lines. Penalizes lines for every word after the dropoff_start."""

    def __init__(
        self,
        weight: float,
        dropoff_start: int,
        reduction_per_word: float,
    ):
        super().__init__(weight)
        self.dropoff_start = dropoff_start
        self.reduction_per_word = reduction_per_word

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            length = len(line.words)
            if len(line.words) > self.dropoff_start:
                line.analysis.category_confidence *= 1 - (
                    self.reduction_per_word * (length - self.dropoff_start)
                )


class FilterContainsNumbers(Filter):
    """Filters lines containing numbers"""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if any(char.isdigit() for char in line.text):
                line.analysis.category_confidence *= self.weight


class FilterStartWithCapital(Filter):
    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if not line.text[0].isupper():
                line.analysis.category_confidence *= self.weight


class FilterByOCRConfidence(Filter):
    """Filters lines based on readability. This is decided by checking if the OCR confidence is low."""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if any(word.confidence == "Low" for word in line.words):
                line.analysis.category_confidence *= self.weight


class FilterDuplicateText(Filter):
    """Filters duplicate lines of text."""

    def __init__(self, weight: float, pattern: str = r"[^a-zA-Z0-9\s]"):
        super().__init__(weight)
        self.pattern = pattern

    def apply(self, lines: List[Line]) -> None:
        # compiles the pattern into a regex object
        regex = re.compile(self.pattern)
        text_counter = Counter([regex.sub("", line.text) for line in lines])
        for line in lines:
            if text_counter[regex.sub("", line.text)] > 1:
                line.analysis.category_confidence *= self.weight


class FilterByEnding(Filter):
    """Filters lines based on their ending."""

    def __init__(self, weight: float, unlikely_endings: List[str]):
        super().__init__(weight)
        self.unlikely_endings = unlikely_endings

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if line.text[-1] in self.unlikely_endings:
                line.analysis.category_confidence *= self.weight


class FilterFontSize(Filter):
    """Filters based on font size. Penalizes lines with font size below the a certain percentile and rewards lines with font size above the percentile."""

    def __init__(self, weight: float, percentile=0.75):
        super().__init__(weight)
        self.percentile = percentile

    def apply(self, lines: List[Line]) -> None:
        lines_with_font_size: List[Tuple[Line, float]] = []

        heights = []
        for line in lines:
            left_height = line.bounding_box.points[3].y - line.bounding_box.points[0].y
            right_height = line.bounding_box.points[2].y - line.bounding_box.points[1].y
            font_size = (left_height + right_height) / 2

            heights.append(font_size)
            lines_with_font_size.append((line, font_size))

        heights.sort()

        percentile_height = heights[int(len(heights) * self.percentile)]

        for line, font_size in lines_with_font_size:
            relative_distance = abs(percentile_height - font_size) / percentile_height

            if font_size > percentile_height:
                line.analysis.category_confidence *= 1 + self.weight * relative_distance
            else:
                line.analysis.category_confidence *= 1 - self.weight * relative_distance


class FilterSameRowAsSomethingelse(Filter):
    """Filters lines that are in the same row as something else."""

    def __init__(
        self,
        weight: float,
        lines_to_pages: dict[int, int],
    ):
        super().__init__(weight)
        self.lines_to_pages = lines_to_pages

    def _in_same_row(self, y: float, other_line: Line) -> bool:
        other_line_top: float = other_line.bounding_box.points[3].y
        other_line_bottom = other_line.bounding_box.points[0].y
        return other_line_top > y > other_line_bottom

    def _calculate_center_y(self, lines: List[Line]) -> List[Tuple[Line, float, int]]:
        with_center_and_page: List[Tuple[Line, float, int]] = []
        for line in lines:
            y = sum(point.y for point in line.bounding_box.points) / 4
            page_num = self.lines_to_pages[id(line)]
            with_center_and_page.append((line, y, page_num))
        return with_center_and_page

    def _adjust_confidence(self, with_center_and_page: List[Tuple[Line, float, int]]):
        for i, e in enumerate(with_center_and_page):
            if i != 0:
                prev_line: Line = with_center_and_page[i - 1][0]
                if self._in_same_row(e[1], prev_line):
                    e[0].analysis.category_confidence *= self.weight
            if i != len(with_center_and_page) - 1:
                next_line = with_center_and_page[i + 1][0]
                if self._in_same_row(e[1], next_line):
                    e[0].analysis.category_confidence *= self.weight

    def apply(self, lines: List[Line]):
        with_center_and_page = self._calculate_center_y(lines)
        with_center_and_page.sort(key=lambda x: (x[2], x[1]))
        self._adjust_confidence(with_center_and_page)


def get_possible_categories(
    menu: Menu,
    lines_to_pages: dict[int, int],
    conf_treshold=0.75,  # randomly chosen value
) -> List[Line]:
    line_filter = LineFilter(
        FilterPriceLines(0.5),
        FilterLongLines(0.1, dropoff_start=6, reduction_per_word=0.2),
        FilterContainsNumbers(0.5),
        FilterStartWithCapital(0.5),
        FilterByOCRConfidence(0.3),
        FilterDuplicateText(0.5),
        FilterByEnding(
            0.8, unlikely_endings=[".", ",", ";", "!", "?", ")", "]", "}", "-"]
        ),
        FilterFontSize(0.1, percentile=0.75),
        FilterSameRowAsSomethingelse(0.75, lines_to_pages),
    )
    return line_filter.get_possible_categories(menu, conf_treshold)
