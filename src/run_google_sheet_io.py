import csv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import SHEET_ID, SHEET_NAME, INPUT_CSV, OUTPUT_CSV, CREDS_FILE
from torob_scraper import process_csv

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def download_sheet_data():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    print("📥 دریافت داده از Google Sheet...")
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A1:Z",
    ).execute()
    values = result.get("values", [])

    if not values or len(values) < 2:
        raise Exception("❌ هیچ داده‌ای پیدا نشد.")

    header = values[0]
    data = values[1:]

    with open(INPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    print(f"✅ داده‌ها ذخیره شدند در {INPUT_CSV}")


def upload_output_to_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    print("📤 آپلود خروجی به شیت...")

    with open(OUTPUT_CSV, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    range_ = f"{SHEET_NAME}!A1"
    body = {"values": all_rows}

    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SHEET_ID,
            range=range_,
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )

    print(f"✅ {result.get('updatedCells')} سلول آپدیت شد.")


def main():
    download_sheet_data()
    process_csv(INPUT_CSV, OUTPUT_CSV)
    upload_output_to_sheet()


if __name__ == "__main__":
    main()
