from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from config.symbols import SYMBOLS
from data.polygon_client import PolygonClient
from output.telegram_bot_v3 import TelegramBotV3
from src.crt_futures_strategy import run_crt_strategy
from src.signal_ledger import append


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["time"] = pd.to_datetime(out["time"], utc=True)
    out = out.set_index("time").sort_index()
    return out


def format_alert(symbol: str, event) -> str:
    return (
        f"CRT V1 {symbol} {event.direction}\n"
        f"Entry: {event.entry}\n"
        f"Stop: {event.stop}\n"
        f"Target: {event.target}\n"
        f"Signal Time: {event.timestamp.isoformat()}\n"
        f"Reason: {event.reason}"
    )


def main() -> None:
    print("=== SCAN V2 START ===")
    print(f"NOW_UTC={datetime.now(timezone.utc).isoformat()}")
    print(f"SYMBOLS={','.join(SYMBOLS)}")

    client = PolygonClient()
    bot = TelegramBotV3()

    for symbol in SYMBOLS:
        print("-" * 60)
        print(f"SYMBOL={symbol}")
        try:
            print(f"{symbol} FETCHING_DATA")
            df = client.get_candles(symbol)
        except Exception as exc:
            print(f"{symbol} DATA_ERROR={exc}")
            continue

        if df is None:
            print(f"{symbol} DF_IS_NONE")
            continue

        if df.empty:
            print(f"{symbol} NO_DATA")
            continue

        print(f"{symbol} RAW_CANDLE_COUNT={len(df)}")
        print(f"{symbol} LAST_RAW_CANDLE_TIME={df.iloc[-1]['time']}")
        print(f"{symbol} LAST_RAW_CLOSE={df.iloc[-1]['close']}")

        prepared = prepare_dataframe(df)
        print(f"{symbol} PREPARED_CANDLE_COUNT={len(prepared)}")
        print(f"{symbol} LAST_PREPARED_CANDLE_TIME={prepared.index[-1].isoformat()}")
        print(f"{symbol} LAST_PREPARED_CLOSE={prepared.iloc[-1]['close']}")

        event = run_crt_strategy(prepared, symbol)

        if event is None:
            print(f"{symbol} NO_SIGNAL")
            continue

        print(f"{symbol} EVENT_FOUND direction={event.direction} entry={event.entry} stop={event.stop} target={event.target}")
        record = {
            "symbol": symbol,
            "strategy": "crt_futures_v1",
            "time": datetime.now(timezone.utc).isoformat(),
            "signal_time": event.timestamp.isoformat(),
            "direction": event.direction,
            "entry": event.entry,
            "sl": event.stop,
            "tp": event.target,
            "reason": event.reason,
        }
        append(record, 100)
        print(f"{symbol} RECORD_APPENDED")
        bot.send(format_alert(symbol, event))
        print(f"{symbol} ALERT_SENT")

    print("=== SCAN V2 END ===")


if __name__ == "__main__":
    main()
