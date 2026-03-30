import requests
from config.settings import Settings

class TelegramBotV2:
    def send(self, text):
        url = f"https://api.telegram.org/bot{Settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": Settings.TELEGRAM_CHAT_ID,
                "text": text,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok", False):
            raise RuntimeError(f"Telegram send failed: {payload}")
        return payload
