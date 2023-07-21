import os
import sys
from conf import CONF_THRESHOLD
from file_handler import load_ocr_data, save

from scan_classes import *
from filters import calculate_confindences
from logger import get_logger


logger = get_logger(__name__)


def process_ocr(path):
    logger.info(f"Processing file {path}")
    menu = load_ocr_data(path)

    # Get all lines linked to page numbers
    lines_to_pages = {
        id(line): page.page_num for page in menu.pages for line in page.lines
    }

    calculate_confindences(menu, lines_to_pages, CONF_THRESHOLD)

    possible_category_lines = [
        line
        for page in menu.pages
        for line in page.lines
        if line.analysis.category_confidence > CONF_THRESHOLD
    ]

    logger.info(f"Found {len(possible_category_lines)} possible categories")

    save(menu, path, possible_category_lines, lines_to_pages)


def main() -> None:
    # Retrieve the first argument
    path = sys.argv[1]

    if os.path.isfile(path):
        if not path.endswith(".json"):
            raise ValueError(
                "Please provide a JSON file containing OCR data or a directory containing such files"
            )
        process_ocr(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if not file.endswith(".json"):
                continue
            process_ocr(os.path.join(path, file))


if __name__ == "__main__":
    main()
