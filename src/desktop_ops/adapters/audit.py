"""Audit adapter (Semgrep + SARIF). Probe-only wrapper."""

import shutil
import subprocess
import json


def probe():
    return shutil.which("semgrep") is not None


def capabilities():
    return ["audit.scan", "audit.sarif"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "semgrep not installed"}
    if action not in ("audit.scan", "audit.sarif"):
        return {"status": "refused", "reason": f"unknown action {action}"}
    path = params.get("path", ".")
    try:
        r = subprocess.run(
            ["semgrep", "scan", "--json", path],
            capture_output=True, text=True, timeout=300,
        )
        try:
            data = json.loads(r.stdout)
        except Exception:
            data = {"raw": r.stdout[:2000]}
        return {"status": "ok", "findings": len(data.get("results", [])), "data": data}
    except Exception as e:
        return {"status": "error", "reason": str(e)}