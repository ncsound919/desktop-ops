"""Astro blog / SEO adapter (content site generation)."""

import os
import shutil
import subprocess
from pathlib import Path

BLOG_DIR = os.environ.get("BLOG_DIR", "./blog")


def probe():
    return shutil.which("npm") is not None or shutil.which("npx") is not None


def capabilities():
    return ["blog.init", "blog.build", "blog.deploy"]


def run(action, params):
    if action == "blog.init":
        name = params.get("name", "blog")
        base = Path(BLOG_DIR) / name
        base.mkdir(parents=True, exist_ok=True)
        (base / "src" / "content").mkdir(parents=True, exist_ok=True)
        (base / "src" / "content" / "post.md").write_text(f"# {name}\n\nHello.\n")
        return {"status": "ok", "path": str(base)}
    if action == "blog.build":
        path = params.get("path", BLOG_DIR)
        try:
            r = subprocess.run(["npm", "run", "build"], cwd=path, capture_output=True, text=True, timeout=300)
            return {"status": "ok" if r.returncode == 0 else "failed", "returncode": r.returncode,
                    "stderr": r.stderr[-1000:]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    return {"status": "refused", "reason": f"unknown action {action}"}