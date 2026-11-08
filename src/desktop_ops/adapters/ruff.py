"""Ruff adapter (astral-sh/ruff). Fast Python linter and formatter."""

import shutil
import subprocess
import json


def probe():
    return shutil.which("ruff") is not None


def capabilities():
    return ["lint.check", "lint.fix", "format.check", "format.fix"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "ruff not installed (pip install ruff)"}
    path = params.get("path", ".")
    if action == "lint.check":
        try:
            r = subprocess.run(["ruff", "check", path, "--output-format", "json"], capture_output=True, text=True, timeout=120)
            try:
                data = json.loads(r.stdout) if r.stdout.strip() else []
            except Exception:
                data = []
            return {"status": "ok" if r.returncode == 0 else "issues", "count": len(data), "issues": data[:50]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action == "lint.fix":
        try:
            r = subprocess.run(["ruff", "check", "--fix", path], capture_output=True, text=True, timeout=120)
            return {"status": "ok" if r.returncode == 0 else "partial", "stdout": r.stdout[-1000:]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action == "format.check":
        try:
            r = subprocess.run(["ruff", "format", "--check", path], capture_output=True, text=True, timeout=120)
            return {"status": "ok" if r.returncode == 0 else "needs_format", "stdout": r.stdout[-500:]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    if action == "format.fix":
        try:
            r = subprocess.run(["ruff", "format", path], capture_output=True, text=True, timeout=120)
            return {"status": "ok" if r.returncode == 0 else "failed", "stdout": r.stdout[-500:]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    return {"status": "refused", "reason": f"unknown action {action}"}