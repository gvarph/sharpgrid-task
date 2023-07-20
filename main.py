import glob
import os
import sys
import fitz
from fitz import Document

from scan_classes import *

from jpg2pdf import jpg2fitz

from filters import get_possible_categories

from logger import get_logger

logger = get_logger(__name__)


def main():
    # Retrieve the first argument
    menu_json_path = sys.argv[1]

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(menu_json_path))[0]

    # Get the directory name
    dir_name = os.path.dirname(menu_json_path)

    # Glob for files with the same basename
    matching_files = glob.glob(os.path.join(dir_name, base_filename + ".*"))

    # Initialize the JSON and SOURCE files to None
    JSON_FILE = None
    SOURCE_FILE = None

    # Go through each file and assign it to the appropriate variable based on its extension
    for file in matching_files:
        if file.endswith(".json"):
            JSON_FILE = file
        elif file.endswith(".jpg") or file.endswith(".pdf"):
            SOURCE_FILE = file

    if JSON_FILE is None or SOURCE_FILE is None:
        raise ValueError("Both JSON and SOURCE files are needed")

    # load the OCR data
    menu = Menu.from_json(json.load(open(JSON_FILE, "r")))

    # load the PDF or JPEG
    file_type = SOURCE_FILE.split(".")[-1]

    if file_type == "pdf":
        doc: Document = fitz.Document(SOURCE_FILE)
    elif file_type == "jpg":
        doc: Document = jpg2fitz(SOURCE_FILE)
    else:
        raise ValueError("Invalid file type")

    CONF_THRESHOLD = 0.76
    # Get all lines linked to page numbers
    lines_to_pages = {
        id(line): page.page_num for page in menu.pages for line in page.lines
    }

    lines = get_possible_categories(menu, lines_to_pages, CONF_THRESHOLD)
    # iterate over all lines and their pages
    counter = 0
    for line in lines:
        page = doc[lines_to_pages[id(line)] - 1]

        counter += 1

        line.bounding_box.draw(
            page,
            menu.pages[lines_to_pages[id(line)] - 1].unit,
        )

    possible_categories = {
        line.text
        for line in lines
        if line.analysis.category_confidence > CONF_THRESHOLD
    }

    logger.info(f"Found {counter} lines that could be categories")

    doc.save("output.pdf")


if __name__ == "__main__":
    main()
