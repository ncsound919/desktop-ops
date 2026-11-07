"""Backup/restore of desktop-ops state as a single bundle."""

import shutil
import zipfile
from pathlib import Path

BUNDLE = Path("state/backup.zip")


def backup():
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
        for d in ("state", "config"):
            p = Path(d)
            if not p.exists():
                continue
            for f in p.rglob("*"):
                if f.is_file():
                    z.write(f, f.as_posix())
    return str(BUNDLE)


def restore(path=None):
    path = Path(path) if path else BUNDLE
    if not path.exists():
        return {"status": "error", "reason": "bundle not found"}
    with zipfile.ZipFile(path) as z:
        z.extractall(".")
    return {"status": "ok", "bundle": str(path)}