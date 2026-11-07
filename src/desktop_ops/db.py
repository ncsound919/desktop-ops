"""Local SQLite mirror of the receipt / run-record schema.

Mirrors openhub's append-only, hash-chained receipt model. Desktop writes here
and syncs to OpenHub; OpenHub remains the source of truth for approvals.
"""

import hashlib
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("state/ops.db")


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute(
        """CREATE TABLE IF NOT EXISTS receipt (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            data_json TEXT NOT NULL,
            prev_hash TEXT,
            hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    c.commit()
    return c


def write_receipt(label, data, prev_hash=None):
    c = _conn()
    payload = json.dumps({"label": label, "data": data, "prev": prev_hash}, sort_keys=True)
    h = hashlib.sha256(payload.encode()).hexdigest()
    import datetime

    ts = datetime.datetime.utcnow().isoformat() + "Z"
    rid = h[:16]
    c.execute(
        "INSERT INTO receipt (id, label, data_json, prev_hash, hash, created_at) VALUES (?,?,?,?,?,?)",
        (rid, label, json.dumps(data), prev_hash, h, ts),
    )
    c.commit()
    c.close()
    return rid, h