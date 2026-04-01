from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config.symbols import SYMBOLS
from data.polygon_client import PolygonClient
from output.telegram_bot_v3 import TelegramBotV3
from src.crt_futures_strategy import run_crt_strategy
from src.signal_ledger import append

RESULTS_PATH = Path("state/scan_v3_results.json")


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
    now = datetime.now(timezone.utc)
    print("=== SCAN V3 START ===", flush=True)
    print(f"NOW_UTC={now.isoformat()}", flush=True)
    print(f"SYMBOLS={','.join(SYMBOLS)}", flush=True)

    client = PolygonClient()
    bot = TelegramBotV3()
    results = {
        "run_time_utc": now.isoformat(),
        "symbols": [],
    }

    for symbol in SYMBOLS:
        row = {"symbol": symbol}
        print("-" * 60, flush=True)
        print(f"SYMBOL={symbol}", flush=True)
        try:
            print(f"{symbol} FETCHING_DATA", flush=True)
            df = client.get_candles(symbol)
        except Exception as exc:
            row["status"] = "DATA_ERROR"
            row["error"] = str(exc)
            results["symbols"].append(row)
            print(f"{symbol} DATA_ERROR={exc}", flush=True)
            continue

        if df is None:
            row["status"] = "DF_IS_NONE"
            results["symbols"].append(row)
            print(f"{symbol} DF_IS_NONE", flush=True)
            continue

        if df.empty:
            row["status"] = "NO_DATA"
            results["symbols"].append(row)
            print(f"{symbol} NO_DATA", flush=True)
            continue

        row["raw_candle_count"] = int(len(df))
        row["last_raw_candle_time"] = str(df.iloc[-1]["time"])
        row["last_raw_close"] = float(df.iloc[-1]["close"])
        print(f"{symbol} RAW_CANDLE_COUNT={len(df)}", flush=True)
        print(f"{symbol} LAST_RAW_CANDLE_TIME={df.iloc[-1]['time']}", flush=True)
        print(f"{symbol} LAST_RAW_CLOSE={df.iloc[-1]['close']}", flush=True)

        prepared = prepare_dataframe(df)
        row["prepared_candle_count"] = int(len(prepared))
        row["last_prepared_candle_time"] = prepared.index[-1].isoformat()
        row["last_prepared_close"] = float(prepared.iloc[-1]["close"])
        lag_seconds = int((now - prepared.index[-1]).total_seconds())
        row["data_lag_seconds"] = lag_seconds
        print(f"{symbol} PREPARED_CANDLE_COUNT={len(prepared)}", flush=True)
        print(f"{symbol} LAST_PREPARED_CANDLE_TIME={prepared.index[-1].isoformat()}", flush=True)
        print(f"{symbol} LAST_PREPARED_CLOSE={prepared.iloc[-1]['close']}", flush=True)
        print(f"{symbol} DATA_LAG_SECONDS={lag_seconds}", flush=True)

        event = run_crt_strategy(prepared, symbol)

        if event is None:
            row["status"] = "NO_SIGNAL"
            results["symbols"].append(row)
            print(f"{symbol} NO_SIGNAL", flush=True)
            continue

        row["status"] = "SIGNAL_FOUND"
        row["direction"] = event.direction
        row["entry"] = float(event.entry)
        row["stop"] = float(event.stop)
        row["target"] = float(event.target)
        row["signal_time"] = event.timestamp.isoformat()
        row["reason"] = event.reason
        results["symbols"].append(row)

        print(
            f"{symbol} SIGNAL_FOUND direction={event.direction} entry={event.entry} stop={event.stop} target={event.target}",
            flush=True,
        )

        record = {
            "symbol": symbol,
            "strategy": "crt_futures_v1",
            "time": now.isoformat(),
            "signal_time": event.timestamp.isoformat(),
            "direction": event.direction,
            "entry": event.entry,
            "sl": event.stop,
            "tp": event.target,
            "reason": event.reason,
        }
        append(record, 100)
        print(f"{symbol} RECORD_APPENDED", flush=True)

        try:
            bot.send(format_alert(symbol, event))
            print(f"{symbol} ALERT_SENT", flush=True)
        except Exception as exc:
            row["alert_error"] = str(exc)
            print(f"{symbol} ALERT_ERROR={exc}", flush=True)

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"RESULTS_WRITTEN={RESULTS_PATH}", flush=True)
    print("=== SCAN V3 END ===", flush=True)


if __name__ == "__main__":
    main()
