from collections import Counter
import re
from typing import List, Tuple, Dict

from scan_classes import Line
from .base import Filter


class FilterPriceLines(Filter):
    """Penalizes lines that look like prices."""

    currency_signs: List[str]

    def __init__(self, confidence_multiplier: float, currency_signs: List[str]):
        super().__init__(confidence_multiplier)
        self.currency_signs = [sign.lower() for sign in currency_signs]

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if any(
                currency_sign in line.text.lower()
                for currency_sign in self.currency_signs
            ):
                line.analysis.type = "price"
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterLongLines(Filter):
    """Filters long lines. Penalizes lines for every word after the dropoff_start."""

    def __init__(
        self,
        confidence_multiplier: float,
        dropoff_start: int,
    ):
        super().__init__(confidence_multiplier)
        self.dropoff_start = dropoff_start

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            length = len(line.words)
            if len(line.words) > self.dropoff_start:
                line.analysis.category_confidence *= 1 - (
                    (length - self.dropoff_start) * self.confidence_multiplier
                )


class FilterContainsNumbers(Filter):
    """Filters lines containing numbers."""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if any(char.isdigit() for char in line.text):
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterNottartWithCapital(Filter):
    """Penalizes lines that do not start with a capital letter."""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if not line.text[0].isupper():
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterByOCRConfidence(Filter):
    """Filters lines based on readability. This is decided by checking if the OCR confidence is low."""

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if any(word.confidence == "Low" for word in line.words):
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterDuplicateText(Filter):
    """Filters duplicate lines of text."""

    def __init__(self, confidence_multiplier: float, pattern: str = r"[^a-zA-Z0-9\s]"):
        super().__init__(confidence_multiplier)
        self.pattern = pattern

    def apply(self, lines: List[Line]) -> None:
        regex = re.compile(self.pattern)
        text_counter = Counter([regex.sub("", line.text) for line in lines])
        for line in lines:
            if text_counter[regex.sub("", line.text)] > 1:
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterByEnding(Filter):
    """Filters lines based on their ending."""

    def __init__(self, confidence_multiplier: float, unlikely_endings: List[str]):
        super().__init__(confidence_multiplier)
        self.unlikely_endings = unlikely_endings

    def apply(self, lines: List[Line]) -> None:
        for line in lines:
            if line.text[-1] in self.unlikely_endings:
                line.analysis.category_confidence *= self.confidence_multiplier


class FilterFontSize(Filter):
    """Filters based on font size. Penalizes lines with font size below the a certain percentile and rewards lines with font size above the percentile."""

    def __init__(self, confidence_multiplier: float, percentile=0.75):
        super().__init__(confidence_multiplier)
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
                line.analysis.category_confidence *= (
                    1 + self.confidence_multiplier * relative_distance
                )
            else:
                line.analysis.category_confidence *= (
                    1 - self.confidence_multiplier * relative_distance
                )


class FilterSameRowAsSomethingelse(Filter):
    """Filters lines that are in the same row as something else."""

    def __init__(
        self,
        confidence_multiplier: float,
        lines_to_pages: Dict[int, int],
    ):
        super().__init__(confidence_multiplier)
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
                    e[0].analysis.category_confidence *= self.confidence_multiplier
            if i != len(with_center_and_page) - 1:
                next_line = with_center_and_page[i + 1][0]
                if self._in_same_row(e[1], next_line):
                    e[0].analysis.category_confidence *= self.confidence_multiplier

    def apply(self, lines: List[Line]):
        with_center_and_page = self._calculate_center_y(lines)
        with_center_and_page.sort(key=lambda x: (x[2], x[1]))
        self._adjust_confidence(with_center_and_page)
