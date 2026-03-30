from datetime import datetime

from config.symbols import SYMBOLS
from config.strategy import GRANULARITY, CANDLE_COUNT, JSON_SIGNAL_LIMIT
from data.oanda_client import OandaClient
from src.market_hours import is_market_open
from src.strategy_engine import detect_signal
from src.signal_ledger import append
from output.telegram_bot import TelegramBot


def run():
    if not is_market_open():
        return

    client = OandaClient()
    bot = TelegramBot()

    for symbol in SYMBOLS:
        df = client.get_candles(symbol, GRANULARITY, CANDLE_COUNT)
        signal = detect_signal(df)

        if signal:
            record = {
                "symbol": symbol,
                "time": datetime.utcnow().isoformat(),
                **signal,
            }
            append(record, JSON_SIGNAL_LIMIT)

            msg = f"{symbol} {signal['direction']}\nEntry: {signal['entry']}\nSL: {signal['sl']}\nTP: {signal['tp']}"
            bot.send(msg)


if __name__ == "__main__":
    run()
