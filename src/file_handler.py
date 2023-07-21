import glob
import os
import fitz
from fitz import Document
import json
from conf import IMG_EXTENSIONS, OPEN_AI_API_KEY

from models import *
from img2pdf import img_to_fitz
from logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = "output_ai" if OPEN_AI_API_KEY else "output"


def get_source_file(json_path):
    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(json_path))[0]

    # Get the directory name
    dir_name = os.path.dirname(json_path)

    # Glob for files with the same basename
    matching_files = glob.glob(os.path.join(dir_name, base_filename + ".*"))

    # Initialize the JSON and SOURCE files to None
    source_file = None

    # Go through each file and assign it to the appropriate variable based on its extension
    for file in matching_files:
        file_upper = file.upper()
        for ext in IMG_EXTENSIONS:
            if file_upper.endswith("." + ext):
                source_file = file
                break

    return source_file


def load_ocr_data(json_file) -> Menu:
    with open(json_file, "r") as f:
        return Menu.from_json(json.load(f))


def load_source_image(source_file: str) -> Document:
    # load the PDF or JPEG
    file_type: str = os.path.splitext(source_file)[-1].upper()

    if file_type == ".PDF":
        return fitz.Document(source_file)
    else:
        return img_to_fitz(source_file)


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
    filename: str,
    lines_to_pages: dict[int, int],
    menu: Menu,
    json_file: str,
):
    source_file = get_source_file(json_file)
    if not source_file:
        logger.warning("No source file found, skipping PDF output")
        return
    doc = load_source_image(source_file)
    if doc:
        for line in lines:
            page = doc[lines_to_pages[id(line)] - 1]
            line.bounding_box.draw(page, menu.pages[lines_to_pages[id(line)] - 1].unit)
            doc.save(os.path.join(OUTPUT_DIR, filename + ".pdf"))


def save(
    menu: Menu,
    path: str,
    possible_category_lines: List[Line],
    lines_to_pages: dict[int, int],
):
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    filename_without_extension = os.path.splitext(os.path.basename(path))[0]

    save_csv(possible_category_lines, filename_without_extension)

    save_pdf(
        possible_category_lines,
        filename_without_extension,
        lines_to_pages,
        menu,
        path,
    )
