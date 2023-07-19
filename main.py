import fitz

from scan_classes import *


FILE_NAME = "menu-1"
FILE_TYPE = "pdf"

# load the OCR data
menu = Menu.from_dict(json.load(open(f"./data/{FILE_NAME}.json")))

# load the PDF
if FILE_TYPE == "pdf":
    doc = fitz.Document(f"./data/{FILE_NAME}.pdf")

else:
    raise ValueError("Invalid file type")


for m_page in menu.pages:
    # match the page number
    page = doc[m_page.page_num - 1]

    # draw the bounding boxes
    annot = page.add_rect_annot(([100, 150, 200, 250]))


# Save pdf
doc.save("output.pdf")
