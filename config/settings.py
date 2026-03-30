import os

class Settings:
    OANDA_API_KEY = os.getenv("OANDA_API_KEY")
    OANDA_ENV = os.getenv("OANDA_ENV", "practice")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
