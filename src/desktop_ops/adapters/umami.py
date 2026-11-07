"""Umami analytics adapter (self-hosted, privacy-first)."""

import os

import httpx

URL = os.environ.get("UMAMI_URL", "").rstrip("/")
TOKEN = os.environ.get("UMAMI_TOKEN", "")


def probe():
    if not URL:
        return False
    try:
        r = httpx.get(f"{URL}/api/heartbeat", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False


def capabilities():
    return ["analytics.pageviews", "analytics.events"]


def run(action, params):
    if not URL:
        return {"status": "refused", "reason": "UMAMI_URL not set"}
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        r = httpx.get(f"{URL}/api/websites", headers=headers, timeout=10.0)
        return {"status": "ok", "data": r.json()} if r.status_code == 200 else {"status": "error", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "reason": str(e)}