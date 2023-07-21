from abc import ABC, abstractmethod
from typing import Tuple
from models import *

from logger import get_logger

logger = get_logger(__name__)


class Filter(ABC):
    """
    Abstract base class for filters.
    Each filter must implement an `apply` method which modifies a provided list of lines.
    """

    def __init__(self, confidence_multiplier: float):
        """Initialize the Filter with a confidence_multiplier parameter."""
        self.confidence_multiplier = confidence_multiplier

    @abstractmethod
    def apply(self, lines: List[Line]):
        """Apply the filter on a given list of lines."""
        raise NotImplementedError


class LineFilter:
    """
    A filter that applies multiple sub-filters to a list of lines.

    Args:
        filters (Filter): The filters to be applied to the lines.
    """

    filters: Tuple[Filter]

    def __init__(self, *filters: Filter):
        self.filters = filters

    def get_possible_categories(self, menu: Menu, conf_threshold=0.76) -> List[Line]:
        """
        Filters the lines from the provided menu and returns lines with category confidence above the provided threshold.

        Args:
            menu (Menu): The menu from which to filter lines.
            conf_threshold (float, optional): The minimum category confidence required for a line to be returned. Default is 0.75.

        Returns:
            List[Line]: A list of lines with category confidence above the provided threshold.
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
            logger.debug(
                f"{filter.__class__.__name__} - remaining lines:{len(lines_above_confidence())}"
            )
            for line in lines:
                if 0 < line.analysis.category_confidence > 1:
                    logger.warning(
                        f"Line {line.text} has a category confidence of {line.analysis.category_confidence}"
                    )
                    line.analysis.category_confidence = 1

        return lines_above_confidence()
