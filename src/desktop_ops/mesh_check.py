"""Mesh wiring checker: scans a tree for apps still pointing at old endpoints."""

import re
from pathlib import Path

OLD_PATTERNS = [
    r"http://192\.168\.\d+\.\d+",
    r"http://10\.0\.2\.2",
    r"localhost:8000",
    r"localhost:8080",
]


def scan(tree):
    root = Path(tree)
    hits = []
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        if any(part in {".git", "node_modules", "build", "dist", ".expo", ".next", ".gradle"} for part in f.parts):
            continue
        if f.stat().st_size > 500_000:
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        for pat in OLD_PATTERNS:
            for m in re.finditer(pat, text):
                hits.append({"file": str(f), "pattern": pat, "match": m.group(0)})
    return hits