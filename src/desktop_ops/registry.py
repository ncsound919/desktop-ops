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
}


def get_adapter(name):
    if name not in ADAPTERS:
        return None
    mod = import_module(ADAPTERS[name])
    return mod


def list_adapters():
    return list(ADAPTERS.keys())