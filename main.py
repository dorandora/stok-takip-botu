import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango

# CONFIG VE AYARLAR
# Not: GitHub'a config.json dosyasını da yüklemeyi unutma!
with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]

# TELEGRAM BİLGİLERİN (Tırnak içlerini doldurmayı unutma!)
BOT_API = "8270767436:AAHZBtsYQQTtsahDYM70H4QFlzykqxBXAUI"
CHAT_ID = "7743083402"


def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        print("Telegram bilgileri eksik.")
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
        print("Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"Mesaj gönderilemedi: {e}")

# TARAYICI AYARLARI (Linux sunucu için optimize edildi)
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("Bot başlatıldı, stoklar kontrol ediliyor...")

try:
    for item in urls_to_check:
        try:
            url = item.get("url")
            store = item.get("store")
            driver.get(url)
            time.sleep(5) # Sayfanın yüklenmesi için bekleme
            
            size_in_stock = None
            
            if store == "zara":
                size_in_stock = check_stock_zara(driver, sizes_to_check)
            elif store == "bershka":
                size_in_stock = check_stock_bershka(driver, sizes_to_check)
            elif store == "mango":
                size_in_stock = check_stock_mango(driver, sizes_to_check)
            
            if size_in_stock:
                msg = f"🚨 STOK ALARMI! 🚨\n\nMağaza: {store.upper()}\nBeden: {size_in_stock}\nLink: {url}"
                print(msg)
                send_telegram_message(msg)
            else:
                print(f"{store} - Stok yok.")
                
        except Exception as inner_e:
            print(f"Hata ({url}): {inner_e}")

except Exception as e:
    print(f"Genel hata: {e}")

finally:
    driver.quit()
    print("Kontrol bitti, tarayıcı kapatıldı.")