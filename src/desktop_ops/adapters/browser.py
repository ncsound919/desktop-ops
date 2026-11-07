"""Browser adapter (Playwright). Probe-only until playwright is installed."""

import shutil


def probe():
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def capabilities():
    return ["browser.navigate", "browser.scrape", "browser.fill_form"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "playwright not installed"}
    return {"status": "not_implemented", "action": action, "params": params}