from PIL import Image
import fitz
import tempfile


def convert_jpg_to_pdf(image_path, output_path):
    image = Image.open(image_path)
    pdf_path = output_path

    # Convert the image to PDF
    image.save(pdf_path, "PDF", resolution=72.0)


def jpg2fitz(image_path: str):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp:
        convert_jpg_to_pdf(image_path, temp.name)
        return fitz.Document(temp.name)
