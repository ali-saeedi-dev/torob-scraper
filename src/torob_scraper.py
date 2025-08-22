import csv
import random
import time
from typing import List

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    PROFILE_PATH,
    HEADLESS,
    PAGE_LOAD_TIMEOUT,
    AFTER_NAV_SLEEP,
    PRICE_SELECTOR,
)


def _normalize_digits(s: str) -> str:
    """
    تبدیل ارقام فارسی/عربی به انگلیسی
    """
    persian = "۰۱۲۳۴۵۶۷۸۹"
    arabic = "٠١٢٣٤٥٦٧٨٩"
    eng = "0123456789"
    trans = {}
    for p, e in zip(persian, eng):
        trans[ord(p)] = e
    for a, e in zip(arabic, eng):
        trans[ord(a)] = e
    return s.translate(trans)


def _clean_price_text(price_text: str) -> str:
    t = _normalize_digits(price_text)

    for ch in ["تومان", "ریال", "٬", ",", "٫", " "]:
        t = t.replace(ch, "")
    return t.strip()


def extract_prices_from_torob(url: str) -> List[int]:
    """
    صفحه ترب را لود می‌کند و قیمت‌ها را برمی‌گرداند.
    """
    options = uc.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    if PROFILE_PATH:
        options.add_argument(f"--user-data-dir={PROFILE_PATH}")

    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    try:
        print(f"⏳ بارگذاری: {url}")
        driver.get(url)


        time.sleep(AFTER_NAV_SLEEP + random.uniform(0.3, 1.2))


        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, PRICE_SELECTOR))
            )
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        price_elements = soup.select(PRICE_SELECTOR)

        prices: List[int] = []
        for el in price_elements:
            try:
                txt = el.get_text(strip=True)
                cleaned = _clean_price_text(txt)
                if cleaned.isdigit():
                    prices.append(int(cleaned))
            except Exception as e:
                print("❌ خطا در تبدیل قیمت:", e)
                continue

        return prices
    finally:
        driver.quit()


def process_csv(input_csv: str, output_csv: str) -> None:
    """
    CSV ورودی را می‌خواند، قیمت‌ها را استخراج می‌کند و CSV خروجی را می‌سازد.
    قوانین:
      - اگر هیچ قیمتی نبود → "نامشخص"
      - اگر <5 فروشنده → قیمت آخرین فروشنده
      - اگر >=5 فروشنده → میانگین فروشنده‌های ۲ تا ۵
    """
    rows_out = []
    price_cache = {}

    with open(input_csv, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header_in = reader.fieldnames or []
        if not header_in:
            raise RuntimeError("هدرهای فایل ورودی پیدا نشد.")

        header_out = list(header_in)
        if "price" not in header_out:
            header_out.append("price")

        for row in reader:
            name = row.get("name", "").strip()
            link = row.get("link", "").strip()

            print(f"\n📦 در حال بررسی محصول: {name or '(بدون نام)'}")

            if not link:
                print("⚠️ لینک خالی است. پرش.")
                row["price"] = "نامشخص"
                rows_out.append(row)
                continue

            if link in price_cache:
                print(f"🔁 لینک تکراری → استفاده از کش قبلی برای {link}")
                prices = price_cache[link]
            else:
                prices = extract_prices_from_torob(link)
                price_cache[link] = prices

 
            if not prices:
                print("❌ قیمت یافت نشد")
                row["price"] = "نامشخص"
            elif len(prices) < 5:
                row["price"] = prices[-1]
                print(f"🟡 فروشنده کمتر از ۵ → قیمت آخرین فروشنده: {prices[-1]:,}")
            else:
                subset = prices[1:5]  
                avg = sum(subset) // len(subset)
                row["price"] = avg
                print(f"🟢 میانگین قیمت فروشنده‌های ۲ تا ۵: {avg:,}")

            rows_out.append(row)

    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows_out[0].keys())
        writer.writeheader()
        writer.writerows(rows_out)

    print("\n✅ فایل خروجی ذخیره شد:", output_csv)
