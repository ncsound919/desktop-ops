"""MCP client to OpenHub (HTTP). Approval-gated: desktop asks, OpenHub decides."""

import os

import httpx

OPENHUB_URL = os.environ.get("DESKTOP_OPS_OPENHUB_URL", "").rstrip("/")
TOKEN = os.environ.get("DESKTOP_OPS_OPENHUB_TOKEN", "")


def available():
    return bool(OPENHUB_URL)


def list_tools():
    if not OPENHUB_URL:
        return {"status": "refused", "reason": "OPENHUB_URL not set"}
    try:
        r = httpx.get(f"{OPENHUB_URL}/mcp/tools", headers=_headers(), timeout=10.0)
        return r.json() if r.status_code == 200 else {"status": "error", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def call_tool(name, params=None):
    if not OPENHUB_URL:
        return {"status": "refused", "reason": "OPENHUB_URL not set"}
    try:
        r = httpx.post(
            f"{OPENHUB_URL}/mcp/call",
            json={"name": name, "params": params or {}},
            headers=_headers(),
            timeout=30.0,
        )
        return r.json() if r.status_code == 200 else {"status": "error", "code": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def _headers():
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h