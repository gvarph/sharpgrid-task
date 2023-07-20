import glob
import os
import sys
import fitz
from fitz import Document
import json
from env import OPEN_AI_API_KEY

from scan_classes import *
from img2pdf import img_to_fitz, ALLOWED_EXTENSIONS as IMG_EXTENSIONS
from filters import calculate_confindences
from logger import get_logger


logger = get_logger(__name__)

CONF_THRESHOLD = 0.76
OUTPUT_DIR = "output_gpt"


def get_file_paths(menu_json_path):
    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(menu_json_path))[0]

    # Get the directory name
    dir_name = os.path.dirname(menu_json_path)

    # Glob for files with the same basename
    matching_files = glob.glob(os.path.join(dir_name, base_filename + ".*"))

    # Initialize the JSON and SOURCE files to None
    json_file = None
    source_file = None

    # Go through each file and assign it to the appropriate variable based on its extension
    for file in matching_files:
        if file.endswith(".json"):
            json_file = file
        elif file.endswith((".jpg", ".pdf")):
            source_file = file

    if json_file is None or source_file is None:
        raise ValueError("Both JSON and SOURCE files are needed")

    return json_file, source_file


def load_ocr_data(json_file):
    with open(json_file, "r") as f:
        return Menu.from_json(json.load(f))


def load_doc(source_file) -> Document | None:
    # load the PDF or JPEG
    file_type = os.path.splitext(source_file)[-1].lower()

    if file_type == ".pdf":
        return fitz.Document(source_file)
    elif file_type in IMG_EXTENSIONS:
        return img_to_fitz(source_file)
    else:
        logger.info(f"Could not find source image/pdf, won't be creating a PDF")
        return None


def save_csv(lines: List[Line], filename: str):
    if OPEN_AI_API_KEY:
        logger.info(
            "The AI based filter was applied. This will result in the confindences being bogus because we only reduce the confidence if the for those with a high confidence to save on tokens."
        )

    with open(os.path.join(OUTPUT_DIR, filename + ".csv"), "w") as f:
        f.write("text,confidence\n")
        for line in lines:
            f.write(f"{line.text},{line.analysis.category_confidence}\n")


def save_pdf(
    lines: List[Line],
    source_file: str,
    filename: str,
    lines_to_pages: dict[int, int],
    menu: Menu,
):
    doc = load_doc(source_file)
    if doc:
        for line in lines:
            page = doc[lines_to_pages[id(line)] - 1]
            line.bounding_box.draw(page, menu.pages[lines_to_pages[id(line)] - 1].unit)
            doc.save(os.path.join(OUTPUT_DIR, filename + ".pdf"))


def process_file(path):
    logger.info(f"Processing file {path}")
    json_file, source_file = get_file_paths(path)
    menu = load_ocr_data(json_file)

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

    logger.info(f"Found {len(possible_category_lines)} possible categories:")

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    filename_without_extension = os.path.splitext(os.path.basename(source_file))[0]

    save_csv(possible_category_lines, filename_without_extension)
    save_pdf(
        possible_category_lines,
        source_file,
        filename_without_extension,
        lines_to_pages,
        menu,
    )


def main():
    # Retrieve the first argument
    path = sys.argv[1]

    if os.path.isfile(path):
        if not path.endswith(".json"):
            raise ValueError(
                "Please provide a JSON file containing OCR data or a directory containing such files"
            )
        process_file(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if not file.endswith(".json"):
                continue
            process_file(os.path.join(path, file))


if __name__ == "__main__":
    main()
