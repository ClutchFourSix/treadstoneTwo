from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd

from config.crt_futures import (
    ASIA_START_HOUR_UTC,
    ASIA_END_HOUR_UTC,
    LONDON_START_HOUR_UTC,
    LONDON_END_HOUR_UTC,
    NEW_YORK_START_HOUR_UTC,
    NEW_YORK_END_HOUR_UTC,
)


@dataclass
class Signal:
    symbol: str
    direction: str
    entry: float
    stop: float
    target: float
    timestamp: datetime
    reason: str


def get_session(df: pd.DataFrame, start_hour: int, end_hour: int) -> pd.DataFrame:
    return df[(df.index.hour >= start_hour) & (df.index.hour < end_hour)]


def build_range(df: pd.DataFrame) -> Optional[tuple]:
    if df.empty:
        return None
    high = df["high"].max()
    low = df["low"].min()
    return high, low


def detect_crt(df: pd.DataFrame, symbol: str) -> Optional[Signal]:
    df = df.copy()

    # Define sessions
    asia = get_session(df, ASIA_START_HOUR_UTC, ASIA_END_HOUR_UTC)
    london = get_session(df, LONDON_START_HOUR_UTC, LONDON_END_HOUR_UTC)
    ny = get_session(df, NEW_YORK_START_HOUR_UTC, NEW_YORK_END_HOUR_UTC)

    asia_range = build_range(asia)
    if asia_range is None:
        return None

    range_high, range_low = asia_range

    # Work on London + NY only
    active = pd.concat([london, ny]).sort_index()

    for i in range(2, len(active)):
        prev = active.iloc[i - 2]
        sweep = active.iloc[i - 1]
        confirm = active.iloc[i]

        # Bullish CRT
        if sweep.low < range_low and sweep.close > range_low:
            if confirm.close > sweep.high:
                entry = confirm.close
                stop = sweep.low
                target = range_high
                return Signal(symbol, "LONG", entry, stop, target, confirm.name, "CRT bullish")

        # Bearish CRT
        if sweep.high > range_high and sweep.close < range_high:
            if confirm.close < sweep.low:
                entry = confirm.close
                stop = sweep.high
                target = range_low
                return Signal(symbol, "SHORT", entry, stop, target, confirm.name, "CRT bearish")

    return None


def run_crt_strategy(df: pd.DataFrame, symbol: str) -> Optional[Signal]:
    return detect_crt(df, symbol)
