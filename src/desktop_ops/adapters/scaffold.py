"""Scaffolding adapter (Cookiecutter-like, pure Python, no external deps)."""

import os
import shutil
from pathlib import Path

TEMPLATES = {
    "python-cli": {
        "files": {
            "pyproject.toml": "[project]\nname = \"{name}\"\nversion = \"0.1.0\"\n",
            "src/{name}/__init__.py": "",
            "src/{name}/cli.py": "def main():\n    print('hello from {name}')\n",
            "README.md": "# {name}\n",
            ".gitignore": "__pycache__/\n*.pyc\n",
        }
    },
    "astro-blog": {
        "files": {
            "package.json": '{{"name":"{name}","version":"0.1.0"}}',
            "src/pages/index.astro": "---\n---\n<h1>{name}</h1>\n",
            "README.md": "# {name}\n",
        }
    },
}


def probe():
    return True


def capabilities():
    return ["scaffold.create", "scaffold.list"]


def run(action, params):
    if action == "scaffold.list":
        return {"status": "ok", "templates": list(TEMPLATES.keys())}
    if action != "scaffold.create":
        return {"status": "refused", "reason": f"unknown action {action}"}
    name = params.get("name")
    template = params.get("template", "python-cli")
    dest = params.get("dest", ".")
    if not name:
        return {"status": "refused", "reason": "name required"}
    if template not in TEMPLATES:
        return {"status": "refused", "reason": f"unknown template {template}"}
    base = Path(dest) / name
    base.mkdir(parents=True, exist_ok=True)
    for rel, content in TEMPLATES[template]["files"].items():
        path = base / rel.format(name=name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.format(name=name))
    return {"status": "ok", "path": str(base), "template": template}