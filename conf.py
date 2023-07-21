import os
from dotenv import load_dotenv

load_dotenv(".env")

# The confidence threshold required for a line to be considered a category, defaults to 0.75
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", 0.75))

# Logger leve, defaults to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Key for connecting to OpenAI's API for the AI based filter
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

# Model used for the AI based filter
MODEL_ID = "gpt-3.5-turbo"

# Maximum number of tokens per message. limit is 4096 tokens, but we will use 3500 to be safe
TOKEN_LIMIT = 3500

# Different possible scales for PDFs and images
PDF_SCALES = {"inch": 72, "mm": 2.83465, "pixel": 1}


# Image extensions that can be processed
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

# Extensions that can be processed
SOURCE_EXTENSIONS = IMG_EXTENSIONS + ["PDF"]
