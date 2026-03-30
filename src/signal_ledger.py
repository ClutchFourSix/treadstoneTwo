import json
from pathlib import Path

LEDGER_PATH = Path("state/signals.json")


def _ensure():
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        LEDGER_PATH.write_text("[]")


def load():
    _ensure()
    return json.loads(LEDGER_PATH.read_text())


def save(records):
    _ensure()
    LEDGER_PATH.write_text(json.dumps(records, indent=2))


def append(record, limit=100):
    data = load()
    data.append(record)
    data = data[-limit:]
    save(data)
