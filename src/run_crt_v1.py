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


def format_alert(symbol: str, signal) -> str:
    return (
        f"CRT V1 {symbol} {signal.direction}\n"
        f"Entry: {signal.entry}\n"
        f"Stop: {signal.stop}\n"
        f"Target: {signal.target}\n"
        f"Signal Time: {signal.timestamp.isoformat()}\n"
        f"Reason: {signal.reason}"
    )


def main() -> None:
    client = PolygonClient()
    bot = TelegramBotV3()

    for symbol in SYMBOLS:
        try:
            df = client.get_candles(symbol)
        except Exception as exc:
            print(f"{symbol} DATA_ERROR={exc}")
            continue

        if df is None or df.empty:
            print(f"{symbol} NO_DATA")
            continue

        prepared = prepare_dataframe(df)
        signal = run_crt_strategy(prepared, symbol)

        if signal is None:
            print(f"{symbol} NO_SIGNAL")
            continue

        record = {
            "symbol": symbol,
            "strategy": "crt_futures_v1",
            "time": datetime.now(timezone.utc).isoformat(),
            "signal_time": signal.timestamp.isoformat(),
            "direction": signal.direction,
            "entry": signal.entry,
            "sl": signal.stop,
            "tp": signal.target,
            "reason": signal.reason,
        }
        append(record, 100)
        bot.send(format_alert(symbol, signal))
        print(f"{symbol} SIGNAL_SENT")


if __name__ == "__main__":
    main()
