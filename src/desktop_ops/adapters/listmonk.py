"""Listmonk newsletter adapter (self-hosted). HTTP client to Listmonk API."""

import os

import httpx

URL = os.environ.get("LISTMONK_URL", "").rstrip("/")
USER = os.environ.get("LISTMONK_USER", "")
PASS = os.environ.get("LISTMONK_PASS", "")


def probe():
    if not URL:
        return False
    try:
        r = httpx.get(f"{URL}/api/health", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False


def capabilities():
    return ["newsletter.subscribers", "newsletter.campaign", "newsletter.send"]


def run(action, params):
    if not URL:
        return {"status": "refused", "reason": "LISTMONK_URL not set"}
    auth = (USER, PASS) if USER else None
    if action == "newsletter.subscribers":
        try:
            r = httpx.get(f"{URL}/api/subscribers", auth=auth, timeout=10.0)
            return {"status": "ok", "data": r.json()} if r.status_code == 200 else {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action == "newsletter.campaign":
        try:
            r = httpx.post(f"{URL}/api/campaigns", json=params, auth=auth, timeout=10.0)
            return {"status": "ok", "data": r.json()} if r.status_code in (200, 201) else {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    return {"status": "refused", "reason": f"unknown action {action}"}