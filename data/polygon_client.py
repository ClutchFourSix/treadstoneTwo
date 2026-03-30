from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from config.settings import Settings


class PolygonClient:
    def __init__(self) -> None:
        self.api_key = Settings.POLYGON_API_KEY
        self.base_url = "https://api.polygon.io"

    def get_candles(self, symbol: str = "EURUSD", timespan: str = "minute", multiplier: int = 15, limit: int = 200) -> pd.DataFrame:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=5)
        ticker = f"C:{symbol}"
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start.date()}/{end.date()}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": limit,
            "apiKey": self.api_key,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        rows = []
        for candle in payload.get("results", []):
            rows.append({
                "time": datetime.fromtimestamp(candle["t"] / 1000, tz=timezone.utc).isoformat(),
                "open": float(candle["o"]),
                "high": float(candle["h"]),
                "low": float(candle["l"]),
                "close": float(candle["c"]),
                "volume": float(candle.get("v", 0.0)),
            })
        return pd.DataFrame(rows)
