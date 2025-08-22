import os
from dotenv import load_dotenv

load_dotenv()

# === Google Sheets ===
SHEET_ID = os.getenv("SHEET_ID", "")
SHEET_NAME = os.getenv("SHEET_NAME", "torob links")
CREDS_FILE = os.getenv("CREDS_FILE", "service_account.json")

# === CSVs ===
INPUT_CSV = os.getenv("INPUT_CSV", "input_products.csv")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "output_products.csv")

# === Scraper / Chrome ===
PROFILE_PATH = os.getenv("PROFILE_PATH", "")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
AFTER_NAV_SLEEP = int(os.getenv("AFTER_NAV_SLEEP", "10"))
PRICE_SELECTOR = os.getenv("PRICE_SELECTOR", "a.price.seller-element")
