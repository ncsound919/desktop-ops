"""Sherlock adapter (sherlock-project/sherlock). OSINT social media account hunter."""

import shutil
import subprocess


def probe():
    return shutil.which("sherlock") is not None


def capabilities():
    return ["osint.search_username", "osint.export"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "sherlock not installed (pip install sherlock-project)"}
    if action != "osint.search_username":
        return {"status": "refused", "reason": f"unknown action {action}"}
    username = params.get("username", "")
    if not username:
        return {"status": "refused", "reason": "username required"}
    out = params.get("out", "sherlock_results.txt")
    try:
        r = subprocess.run(
            ["sherlock", username, "--output", out],
            capture_output=True, text=True, timeout=300,
        )
        return {"status": "ok" if r.returncode == 0 else "failed", "out": out, "stdout": r.stdout[-1000:]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}