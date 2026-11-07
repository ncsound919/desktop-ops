"""Research adapter (SearXNG / Crawl4AI / duckduckgo). Probe-only."""

def probe():
    try:
        import crawl4ai  # noqa: F401
        return True
    except ImportError:
        try:
            import duckduckgo_search  # noqa: F401
            return True
        except ImportError:
            return False


def capabilities():
    return ["research.search", "research.crawl", "research.summarize"]


def run(action, params):
    if not probe():
        return {"status": "refused", "reason": "no research library installed (crawl4ai or duckduckgo-search)"}
    return {"status": "not_implemented", "action": action, "params": params}