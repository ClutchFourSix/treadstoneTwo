from datetime import datetime, timezone

from output.telegram_bot import TelegramBot
from src.heartbeat import heartbeat


def main():
    bot = TelegramBot()
    hb = heartbeat()
    now = datetime.now(timezone.utc).isoformat()
    message = (
        "TREADSTONE TWO HEARTBEAT\n"
        f"Status: {hb['status']}\n"
        f"UTC Time: {now}\n"
        "Schedule: 08:00 UTC / manual on demand"
    )
    bot.send(message)


if __name__ == "__main__":
    main()
