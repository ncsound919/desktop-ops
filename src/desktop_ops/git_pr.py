"""GitHub PR creation via API (human-approved). Requires GITHUB_TOKEN env."""

import os

import httpx

TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
API = "https://api.github.com"


def available():
    return bool(TOKEN)


def create_pr(owner, repo, title, body, head, base="main"):
    if not TOKEN:
        return {"status": "refused", "reason": "GITHUB_TOKEN not set"}
    try:
        r = httpx.post(
            f"{API}/repos/{owner}/{repo}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
            headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
            timeout=30.0,
        )
        if r.status_code in (200, 201):
            data = r.json()
            return {"status": "ok", "number": data.get("number"), "url": data.get("html_url")}
        return {"status": "error", "code": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"status": "error", "reason": str(e)}