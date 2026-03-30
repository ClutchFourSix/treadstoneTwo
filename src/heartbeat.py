from datetime import datetime


def heartbeat():
    return {
        "status": "alive",
        "time": datetime.utcnow().isoformat()
    }
