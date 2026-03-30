import os

class Settings:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Polygon / Massive
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

    # (optional fallback, keep if needed)
    OANDA_API_KEY = os.getenv("OANDA_API_KEY")
    OANDA_ENV = os.getenv("OANDA_ENV", "practice")
