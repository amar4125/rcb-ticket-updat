import requests
import time
import hashlib
import os
from datetime import datetime

# 🔐 Environment variables (SET IN RAILWAY)
URL = "https://shop.royalchallengers.com"
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 120  # seconds


def send_telegram(msg):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
            return

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=10
        )

        print("📩 Telegram status:", response.status_code)

    except Exception as e:
        print("❌ Telegram Error:", e)


def get_page_hash():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(URL, headers=headers, timeout=15)

        print("🌐 Website status:", response.status_code)

        if response.status_code != 200:
            return None

        content = response.text.encode("utf-8")
        return hashlib.md5(content).hexdigest()

    except Exception as e:
        print("❌ Website Error:", e)
        return None


def main():
    print("🚀 Script starting...")

    send_telegram("🚀 Bot started successfully")

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕒 Start time: {start_time}")

    last_hash = None

    # Try initial fetch with retry
    for _ in range(3):
        last_hash = get_page_hash()
        if last_hash:
            break
        print("⚠️ Retrying initial fetch...")
        time.sleep(5)

    if not last_hash:
        print("⚠️ Failed to initialize baseline hash")

    print("👀 Monitoring started...")

    while True:
        try:
            time.sleep(CHECK_INTERVAL)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n⏱ Checking at {current_time}")

            new_hash = get_page_hash()

            if new_hash is None:
                print("⚠️ Skipping this cycle due to error")
                continue

            if last_hash is None:
                last_hash = new_hash
                print("🔄 Initialized baseline hash")
                continue

            if new_hash != last_hash:
                print("🚨 WEBSITE CHANGED!")
                send_telegram(f"🚨 Website changed at {current_time}\n{URL}")
                last_hash = new_hash
            else:
                print("✅ No change detected")

        except Exception as e:
            print("❌ Loop error:", e)
            time.sleep(30)  # prevent crash loop


if __name__ == "__main__":
    main()