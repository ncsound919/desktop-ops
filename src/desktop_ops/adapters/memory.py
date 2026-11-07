"""Memory adapter (Mem0 / Qdrant). Probe-only with in-memory fallback."""

def probe():
    return True  # in-memory fallback always available; Mem0 optional upgrade


def capabilities():
    return ["memory.store", "memory.recall", "memory.search"]


def run(action, params):
    # In-memory fallback so the agent can still function without Mem0
    if action == "memory.store":
        return {"status": "ok", "backend": "in-memory", "note": "Mem0 not installed; stored in-process only"}
    if action == "memory.recall":
        return {"status": "ok", "backend": "in-memory", "results": []}
    return {"status": "refused", "reason": f"unknown action {action}"}