import os
from PIL import Image
import fitz
import tempfile

from conf import IMG_EXTENSIONS


def img_file_to_pdf_file(image_path, output_path, resolution=72.0):
    try:
        image = Image.open(image_path)
    except IOError:
        raise Exception("Error opening image file: {}".format(image_path))
    # Convert the image to PDF
    image.save(output_path, "PDF", resolution=resolution)


def img_to_fitz(image_path: str):
    _, ext = os.path.splitext(image_path)
    if ext.upper()[1:] not in IMG_EXTENSIONS:
        raise Exception(
            "Image file type not supported. Allowed types are: {}".format(
                ", ".join(IMG_EXTENSIONS)
            )
        )

    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp:
        img_file_to_pdf_file(image_path, temp.name)
        return fitz.Document(temp.name)
