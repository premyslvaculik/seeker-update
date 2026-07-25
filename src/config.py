import os
import sys
from pathlib import Path

# Base Paths (SRC directory)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "update_seeker.db"

# Endoflife.date API configuration
ENDOFLIFE_API_BASE = "https://endoflife.date/api"
ENDOFLIFE_PRODUCTS = [
    {"brand": "Google", "product": "pixel", "name": "Google Pixel"},
    {"brand": "Samsung", "product": "samsung-galaxy", "name": "Samsung Galaxy"},
    {"brand": "Apple", "product": "iphone", "name": "Apple iPhone"},
    {"brand": "Xiaomi", "product": "xiaomi", "name": "Xiaomi"},
    {"brand": "Fairphone", "product": "fairphone", "name": "Fairphone"},
    {"brand": "OnePlus", "product": "oneplus", "name": "OnePlus"}
]

# Custom Connectors URLs
MOTOROLA_SECURITY_URL = "https://motorola-global-portal.custhelp.com/"
HONOR_SECURITY_URL = "https://www.hihonor.com/global/support/bulletin/"

# User Agent for HTTP requests
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
