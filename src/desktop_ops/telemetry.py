"""Telemetry emitter: EcosystemEvent v1 facts.

Desktop emits facts (never commands). Default sink is a local JSONL file;
optionally POSTs to sieve-ingest if DESKTOP_OPS_TELEMETRY_URL is set.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

TELEMETRY_URL = os.environ.get("DESKTOP_OPS_TELEMETRY_URL", "").rstrip("/")
SINK = Path("state/telemetry.jsonl")


def emit(event_type, source="desktop-ops", subject=None, data=None, idempotency_key=None):
    evt = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "schema_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "subject": subject or {"kind": "app", "id": "desktop-ops"},
        "idempotency_key": idempotency_key or str(uuid.uuid4()),
        "data": data or {},
    }
    SINK.parent.mkdir(parents=True, exist_ok=True)
    with SINK.open("a") as f:
        f.write(json.dumps(evt) + "\n")

    if TELEMETRY_URL:
        try:
            import httpx

            httpx.post(TELEMETRY_URL, json=evt, timeout=10.0)
        except Exception:
            pass
    return evt["id"]