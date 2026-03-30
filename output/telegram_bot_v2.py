import os
import requests


class TelegramBotV2:
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

        response = requests.post(url, json=payload)

        print("Telegram response:", response.text)

        response.raise_for_status()
