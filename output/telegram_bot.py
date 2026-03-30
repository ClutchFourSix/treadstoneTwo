import requests
from config.settings import Settings

class TelegramBot:
    def send(self, text):
        url = f"https://api.telegram.org/bot{Settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": Settings.TELEGRAM_CHAT_ID,
            "text": text
        })
