import fitz

from scan_classes import *

from jpg2pdf import jpg2fitz


FILE_NAME = "menu-3"
FILE_TYPE = "jpg"

# load the OCR data
menu = Menu.from_dict(json.load(open(f"./data/{FILE_NAME}.json")))

# load the PDF
if FILE_TYPE == "pdf":
    doc = fitz.Document(f"./data/{FILE_NAME}.pdf")
elif FILE_TYPE == "jpg":
    doc = jpg2fitz(f"./data/{FILE_NAME}.jpg")


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
