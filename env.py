import os
from dotenv import load_dotenv

load_dotenv(".env")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
