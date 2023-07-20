from typing import List

from scan_classes import Line, Menu
from .filter_classes import *
from .base import LineFilter
from .gpt_filter import MakeAIDoTheFiltering


def get_possible_categories(
    menu: Menu,
    lines_to_pages: dict[int, int],
    conf_threshold=0.75,  # randomly chosen valueba
) -> List[Line]:
    """
    Filters lines from the provided menu and returns lines with a high category confidence.

    Args:
        menu (Menu): The menu from which to filter lines.
        lines_to_pages (dict[int, int]): A mapping from line numbers to page numbers.
        conf_threshold (float, optional): The minimum category confidence required for a line to be returned. Default is 0.75.

    Returns:
        List[Line]: A list of lines with category confidence above the provided threshold.
    """

    # The lower the number, the the higher the confidence reduction if the filter applies
    line_filter = LineFilter(
        FilterPriceLines(0.5, currency_signs=["€", "$", "£", "Kč", "kr", "Kc", ",-"]),
        FilterLongLines(0.1, dropoff_start=5),
        FilterContainsNumbers(0.85),
        FilterNottartWithCapital(0.95),
        FilterByOCRConfidence(0.8),
        FilterDuplicateText(0.5),
        FilterByEnding(
            0.75, unlikely_endings=[".", ",", ";", "!", "?", ")", "]", "}", "-"]
        ),
        FilterFontSize(0.75, percentile=0.75),
        FilterSameRowAsSomethingelse(0.85, lines_to_pages),
        MakeAIDoTheFiltering(1, conf_threshold),
    )
    return line_filter.get_possible_categories(menu, conf_threshold)
