# Torob Price Scraper → Google Sheets

Torob Scraper:
1) دریافت لیست نام/لینک از Google Sheet  
2) اسکرپ قیمت از صفحات Torob  
3) ساخت خروجی CSV  
4) آپلود همان خروجی در همان Google Sheet

---

## ویژگی‌ها

- استفاده از **undetected-chromedriver** برای کاهش بلاک شدن
- کش داخلی برای لینک‌های تکراری
- تنظیمات کاملاً **کانفیگ‌پذیر** از طریق `.env`
- ورودی/خروجی UTF-8-SIG سازگار با اکسل

---

## پیش‌نیازها

- Python 3.9+
- Google Chrome (یا Chromium)
- فعال‌سازی Google Sheets API و ساخت Service Account

---

## نصب

```bash
git clone https://github.com/<username>/torob-scraper.git
cd torob-scraper
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
# source .venv/bin/activate

pip install -r requirements.txt
