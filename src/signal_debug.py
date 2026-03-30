from __future__ import annotations

from datetime import datetime, timezone

from config.symbols import SYMBOLS
from data.polygon_client import PolygonClient
from src.strategy_engine import detect_signal


def main() -> None:
    client = PolygonClient()
    now = datetime.now(timezone.utc)
    print(f"NOW_UTC={now.isoformat()}")

    for symbol in SYMBOLS:
        print("-" * 60)
        print(f"SYMBOL={symbol}")
        try:
            df = client.get_candles(symbol)
        except Exception as exc:
            print(f"STATUS=ERROR")
            print(f"ERROR={exc}")
            continue

        if df is None or df.empty:
            print("STATUS=NO_DATA")
            continue

        last = df.iloc[-1]
        last_time = datetime.fromisoformat(str(last['time']))
        lag = now - last_time
        print("STATUS=OK")
        print(f"CANDLE_COUNT={len(df)}")
        print(f"LAST_CANDLE_TIME_UTC={last_time.isoformat()}")
        print(f"LAST_CLOSE={last['close']}")
        print(f"DATA_LAG_SECONDS={int(lag.total_seconds())}")
        print(f"DATA_LAG_MINUTES={lag.total_seconds()/60:.2f}")
        signal = detect_signal(df)
        print(f"STRATEGY_SIGNAL={signal}")


if __name__ == "__main__":
    main()
