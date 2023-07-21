import os
from dotenv import load_dotenv

load_dotenv(".env")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

MODEL_ID = "gpt-3.5-turbo"

# limit is 4096 tokens, but we will use 3500 to be safe
TOKEN_LIMIT = 3500

PDF_SCALES = {"inch": 72, "mm": 2.83465, "pixel": 1}

CONF_THRESHOLD = 0.76

IMG_EXTENSIONS = [
    "JPEG",
    "JPG",
    "PNG",
    "BMP",
    "GIF",
    "TIFF",
    "WebP",
    "PPM",
    "PBM",
    "PSD",
]

SOURCE_EXTENSIONS = IMG_EXTENSIONS + ["PDF"]
