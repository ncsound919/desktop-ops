"""Agent-browser adapter (vercel-labs/agent-browser). Browser automation CLI for AI agents."""

import shutil
import subprocess
import json


def probe():
    return shutil.which("agent-browser") is not None


def capabilities():
    return ["browser.navigate", "browser.scrape", "browser.screenshot", "browser.fill"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "agent-browser not installed (cargo install agent-browser)"}
    if action not in capabilities():
        return {"status": "refused", "reason": f"unknown action {action}"}
    url = params.get("url", "")
    try:
        if action == "browser.navigate":
            r = subprocess.run(["agent-browser", "navigate", url], capture_output=True, text=True, timeout=60)
            return {"status": "ok" if r.returncode == 0 else "failed", "stdout": r.stdout[-2000:], "stderr": r.stderr[-500:]}
        if action == "browser.scrape":
            r = subprocess.run(["agent-browser", "scrape", url], capture_output=True, text=True, timeout=60)
            return {"status": "ok" if r.returncode == 0 else "failed", "content": r.stdout[:5000]}
        if action == "browser.screenshot":
            out = params.get("out", "screenshot.png")
            r = subprocess.run(["agent-browser", "screenshot", url, "-o", out], capture_output=True, text=True, timeout=60)
            return {"status": "ok" if r.returncode == 0 else "failed", "out": out}
        if action == "browser.fill":
            selector = params.get("selector", "")
            value = params.get("value", "")
            r = subprocess.run(["agent-browser", "fill", selector, value], capture_output=True, text=True, timeout=60)
            return {"status": "ok" if r.returncode == 0 else "failed", "stdout": r.stdout[-500:]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}
    return {"status": "refused", "reason": f"unhandled action {action}"}