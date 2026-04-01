from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config.symbols import SYMBOLS
from config.strategy import JSON_SIGNAL_LIMIT
from data.polygon_client import PolygonClient
from output.telegram_bot_v3 import TelegramBotV3
from src.crt_futures_strategy import run_crt_strategy
from src.market_hours import is_market_open
from src.signal_ledger import append

STATE_PATH = Path("state/crt_state.json")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


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
        f"Time: {signal.timestamp.isoformat()}\n"
        f"Reason: {signal.reason}"
    )


def run() -> None:
    if not is_market_open():
        print("Market closed. No CRT scan.")
        return

    client = PolygonClient()
    bot = TelegramBotV3()
    state = load_state()

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

        signal_id = f"{symbol}_{signal.timestamp.isoformat()}_{signal.direction}"
        if state.get(symbol) == signal_id:
            print(f"{symbol} DUPLICATE_SIGNAL_SKIPPED")
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
        append(record, JSON_SIGNAL_LIMIT)
        bot.send(format_alert(symbol, signal))
        state[symbol] = signal_id
        print(f"{symbol} SIGNAL_SENT")

    save_state(state)


if __name__ == "__main__":
    run()
