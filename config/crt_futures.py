from __future__ import annotations

# Session windows in UTC. Adjust later for DST-sensitive exchange/session handling.
ASIA_START_HOUR_UTC = 0
ASIA_END_HOUR_UTC = 6
LONDON_START_HOUR_UTC = 7
LONDON_END_HOUR_UTC = 10
NEW_YORK_START_HOUR_UTC = 13
NEW_YORK_END_HOUR_UTC = 17

# Execution timeframe assumptions
EXECUTION_TIMEFRAME_MINUTES = 15
MIN_RANGE_TICKS = 1
MIN_RR = 1.5
TARGET_R_MULTIPLE = 2.0
MAX_TRADES_PER_SESSION = 2

FUTURES_SYMBOLS = [
    "ES",
    "NQ",
    "CL",
    "GC",
]
