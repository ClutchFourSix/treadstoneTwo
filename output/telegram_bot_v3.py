import os
import requests


class TelegramBotV3:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send(self, text: str):
        if not text or text.strip() == "":
            raise ValueError("Telegram message text is empty")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        print("Telegram HTTP status:", response.status_code)
        print("Telegram response:", data)
        if response.status_code != 200:
            raise RuntimeError(f"Telegram HTTP error: {response.status_code} | {data}")
        if not data.get("ok", False):
            raise RuntimeError(f"Telegram API rejected message: {data}")
        return data
