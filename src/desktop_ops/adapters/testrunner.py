"""Test runner adapter (pytest / playwright / jest / vitest). Shells out to available runner."""

import shutil
import subprocess


RUNNERS = {
    "pytest": ["pytest", "-q"],
    "playwright": ["npx", "playwright", "test"],
    "jest": ["npx", "jest"],
    "vitest": ["npx", "vitest", "run"],
}


def probe():
    return any(shutil.which(r) for r in ("pytest", "npx"))


def capabilities():
    return ["test.run"]


def run(action, params):
    if action != "test.run":
        return {"status": "refused", "reason": f"unknown action {action}"}
    runner = params.get("runner", "pytest")
    path = params.get("path", ".")
    cmd = RUNNERS.get(runner)
    if not cmd:
        return {"status": "refused", "reason": f"unknown runner {runner}"}
    if shutil.which(cmd[0]) is None and cmd[0] != "npx":
        return {"status": "refused", "reason": f"{cmd[0]} not installed"}
    try:
        r = subprocess.run(cmd + [path], capture_output=True, text=True, timeout=600, cwd=path)
        return {"status": "ok" if r.returncode == 0 else "failed", "returncode": r.returncode,
                "stdout": r.stdout[-2000:], "stderr": r.stderr[-1000:]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}