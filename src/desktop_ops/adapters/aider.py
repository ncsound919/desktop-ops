"""Aider adapter (headless coding agent)."""

import shutil
import subprocess


def probe():
    return shutil.which("aider") is not None


def capabilities():
    return ["code.edit", "code.refactor", "code.test"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "aider not installed"}
    if action not in capabilities():
        return {"status": "refused", "reason": f"unknown action {action}"}
    # Placeholder: real implementation shells out to aider in headless mode.
    return {"status": "not_implemented", "action": action, "params": params}