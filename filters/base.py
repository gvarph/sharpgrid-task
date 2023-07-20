from abc import ABC, abstractmethod
from scan_classes import *

from logger import get_logger

logger = get_logger(__name__)


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
            logger.info(
                f"{filter.__class__.__name__} - remaining lines:{len(lines_above_confidence())}"
            )

        return lines_above_confidence()
