import glob
import os
import sys
import fitz
from fitz import Document

from scan_classes import *

from jpg2pdf import jpg2fitz


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
    menu = Menu.from_dict(json.load(open(JSON_FILE)))

    # load the PDF or JPEG
    file_type = SOURCE_FILE.split(".")[-1]

    if file_type == "pdf":
        doc: Document = fitz.Document(SOURCE_FILE)
    elif file_type == "jpg":
        doc: Document = jpg2fitz(SOURCE_FILE)
    else:
        raise ValueError("Invalid file type")

    for m_page in menu.pages:
        page = doc[m_page.page_num - 1]
        for line in m_page.lines:
            bbox = line.bounding_box
            points = bbox.to_fitz_points(page.rect.height, m_page.unit)
            points = [(x, page.mediabox.y1 - y) for x, y in points]
            annot = page.add_polygon_annot(points)
            annot.set_border(width=0.3, dashes=[2])
            annot.set_colors(stroke=(0, 0, 1))
            annot.update()

    # Save pdf
    doc.save("output.pdf")


if __name__ == "__main__":
    main()
