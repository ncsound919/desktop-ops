"""Cost guard: daily LLM/API spend tracking with hard budget cap."""

import json
from datetime import date
from pathlib import Path

COST_LOG = Path("state/costs.jsonl")
import os

BUDGET = float(os.environ.get("DESKTOP_OPS_DAILY_BUDGET", "5.0"))  # USD per day


def record(provider, amount_usd, note=""):
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    import datetime

    entry = {
        "date": date.today().isoformat(),
        "provider": provider,
        "amount": amount_usd,
        "note": note,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with COST_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def today_spend():
    if not COST_LOG.exists():
        return 0.0
    total = 0.0
    today = date.today().isoformat()
    for line in COST_LOG.read_text().splitlines():
        try:
            e = json.loads(line)
            if e.get("date") == today:
                total += e.get("amount", 0.0)
        except Exception:
            pass
    return total


def check_budget(budget=None):
    budget = budget if budget is not None else BUDGET
    spent = today_spend()
    if spent >= budget:
        return {"status": "exceeded", "spent": spent, "budget": budget}
    return {"status": "ok", "spent": spent, "budget": budget, "remaining": budget - spent}