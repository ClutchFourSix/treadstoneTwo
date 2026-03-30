from datetime import datetime

from config.symbols import SYMBOLS
from config.strategy import JSON_SIGNAL_LIMIT
from data.polygon_client import PolygonClient
from src.market_hours import is_market_open
from src.strategy_engine import detect_signal
from src.signal_ledger import append
from output.telegram_bot import TelegramBot


def run():
    if not is_market_open():
        return

    client = PolygonClient()
    bot = TelegramBot()

    for symbol in SYMBOLS:
        df = client.get_candles(symbol)

        if df is None or df.empty:
            continue

        signal = detect_signal(df)

        if signal:
            record = {
                "symbol": symbol,
                "time": datetime.utcnow().isoformat(),
                **signal,
            }

            append(record, JSON_SIGNAL_LIMIT)

            msg = (
                f"{symbol} {signal['direction']}\n"
                f"Entry: {signal['entry']}\n"
                f"SL: {signal['sl']}\n"
                f"TP: {signal['tp']}"
            )

            bot.send(msg)


if __name__ == "__main__":
    run()
