"""Plugin registry: each OSS tool is an adapter module under adapters/.

An adapter exposes:
  - probe() -> bool
  - capabilities() -> list[str]
  - run(action, params) -> dict  (returns {"status": ..., "result": ...} or refusal)
"""

from importlib import import_module
from pathlib import Path


ADAPTERS = {
    "aider": "desktop_ops.adapters.aider",
    "llm": "desktop_ops.adapters.llm",
    "browser": "desktop_ops.adapters.browser",
    "research": "desktop_ops.adapters.research",
    "memory": "desktop_ops.adapters.memory",
    "scaffold": "desktop_ops.adapters.scaffold",
    "audit": "desktop_ops.adapters.audit",
    "testrunner": "desktop_ops.adapters.testrunner",
    "kokoro": "desktop_ops.adapters.kokoro",
    "ffmpeg": "desktop_ops.adapters.ffmpeg",
    "thumbnail": "desktop_ops.adapters.thumbnail",
    "docling": "desktop_ops.adapters.docling",
    "blog": "desktop_ops.adapters.blog",
    "listmonk": "desktop_ops.adapters.listmonk",
    "umami": "desktop_ops.adapters.umami",
    "agent_browser": "desktop_ops.adapters.agent_browser",
    "ruff": "desktop_ops.adapters.ruff",
    "sherlock": "desktop_ops.adapters.sherlock",
}


def get_adapter(name):
    if name not in ADAPTERS:
        return None
    mod = import_module(ADAPTERS[name])
    return mod


def list_adapters():
    return list(ADAPTERS.keys())