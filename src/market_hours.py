from datetime import datetime

def is_market_open():
    now = datetime.utcnow()
    # simple FX logic: closed weekends
    if now.weekday() >= 5:
        return False
    return True
