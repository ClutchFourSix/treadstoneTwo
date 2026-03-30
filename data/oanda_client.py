from __future__ import annotations

import requests
import pandas as pd

from config.settings import Settings


class OandaClient:
    def __init__(self) -> None:
        self.api_key = Settings.OANDA_API_KEY
        self.env = (Settings.OANDA_ENV or "practice").lower()
        self.base_url = "https://api-fxtrade.oanda.com" if self.env == "live" else "https://api-fxpractice.oanda.com"

    def get_candles(self, instrument: str, granularity: str = "M15", count: int = 200) -> pd.DataFrame:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        params = {
            "granularity": granularity,
            "count": count,
            "price": "M",
        }
        url = f"{self.base_url}/v3/instruments/{instrument}/candles"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        candles = payload.get("candles", [])

        rows = []
        for candle in candles:
            if not candle.get("complete", False):
                continue
            mid = candle.get("mid", {})
            rows.append({
                "time": candle.get("time"),
                "open": float(mid.get("o", 0.0)),
                "high": float(mid.get("h", 0.0)),
                "low": float(mid.get("l", 0.0)),
                "close": float(mid.get("c", 0.0)),
                "volume": int(candle.get("volume", 0)),
            })
        return pd.DataFrame(rows)
