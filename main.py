import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango, check_stock_pullandbear

# CONFIG YÜKLEME
with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]

# TELEGRAM AYARLARI
BOT_API = "8270767436:AAHZBtsYQQTtsahDYM70H4QFlzykqxBXAUI"
CHAT_ID = "7743083402"

def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram hatası: {e}")

# TARAYICI AYARLARI (GÜNCELLENDİ)
chrome_options = Options()
chrome_options.add_argument("--headless=new") # Yeni headless modu
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# Bot olduğunu gizleyen kritik ayarlar:
chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
# Daha güncel bir User-Agent:
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Driver kurulumu
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Selenium'un bot olarak algılanmasını önlemek için JS enjeksiyonu
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

print("Bot başlatıldı (v2.0), kontroller başlıyor...")

try:
    for item in urls_to_check:
        try:
            url = item.get("url")
            store = item.get("store")
            print(f"Kontrol ediliyor: {store} - {url}")
            
            driver.get(url)
            time.sleep(7) # Yükleme süresini biraz artırdık
            
            size_in_stock = None
            
            if store == "zara":
                size_in_stock = check_stock_zara(driver, sizes_to_check)
            elif store == "bershka":
                size_in_stock = check_stock_bershka(driver, sizes_to_check)
            elif store == "mango":
                size_in_stock = check_stock_mango(driver, sizes_to_check)
            # YENİ EKLENEN KISIM:
            elif store == "pullandbear":
                size_in_stock = check_stock_pullandbear(driver, sizes_to_check)
            
            if size_in_stock:
                msg = f"🚨 STOK BULUNDU! 🚨\n\nMağaza: {store.upper()}\nBeden: {size_in_stock}\nLink: {url}"
                print(msg)
                send_telegram_message(msg)
            else:
                print(f"❌ {store} - Stok yok.")
                
        except Exception as inner_e:
            print(f"Link Hatası ({store}): {inner_e}")

except Exception as e:
    print(f"Genel hata: {e}")

finally:
    driver.quit()
    print("İşlem tamamlandı.")
