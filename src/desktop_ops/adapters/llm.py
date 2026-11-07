"""LLM router: mesh client (phone :8788) with optional cloud fallback.

The desktop has no GPU, so it never hosts a model. It calls the phone mesh
when reachable, otherwise falls back to a cloud provider configured via env.
"""

import os
from typing import Optional

import httpx

def probe():
    # LLM is available if mesh or cloud is configured (env) OR httpx present
    return True  # httpx is a hard dependency; availability checked at call time


MESH_URL = os.environ.get("DESKTOP_OPS_MESH_URL", "").rstrip("/")
CLOUD_URL = os.environ.get("DESKTOP_OPS_CLOUD_URL", "").rstrip("/")
CLOUD_KEY = os.environ.get("DESKTOP_OPS_CLOUD_KEY", "")
APP_ID = "desktop-ops"


def capabilities():
    return ["llm.chat", "llm.plan", "llm.reflect"]


def available():
    return bool(MESH_URL or CLOUD_URL)


def chat(prompt, system=None, max_tokens=512):
    """Send a chat completion. Returns (text, source) or raises."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Try mesh first
    if MESH_URL:
        try:
            r = httpx.post(
                f"{MESH_URL}/v1/chat/completions",
                json={"model": "auto", "messages": messages, "max_tokens": max_tokens},
                headers={"x-llm-app": APP_ID},
                timeout=30.0,
            )
            if r.status_code == 200:
                data = r.json()
                text = data["choices"][0]["message"]["content"]
                return text, "mesh"
        except Exception:
            pass

    # Cloud fallback
    if CLOUD_URL:
        headers = {"Content-Type": "application/json"}
        if CLOUD_KEY:
            headers["Authorization"] = f"Bearer {CLOUD_KEY}"
        try:
            r = httpx.post(
                f"{CLOUD_URL}/v1/chat/completions",
                json={"model": "auto", "messages": messages, "max_tokens": max_tokens},
                headers=headers,
                timeout=60.0,
            )
            if r.status_code == 200:
                data = r.json()
                text = data["choices"][0]["message"]["content"]
                return text, "cloud"
            return None, f"cloud error {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return None, f"cloud exception: {e}"

    return None, "no LLM available (set DESKTOP_OPS_MESH_URL or DESKTOP_OPS_CLOUD_URL)"