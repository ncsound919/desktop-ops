# Desktop-Ops

Desktop execution plane for the overlay365 ecosystem. Compiles OSS tools; runs on an
old (no-GPU) desktop. Headless CLI.

## Quick start

```bash
python -m pip install -e .
ops doctor          # probe for OSS tools
ops adapters        # list adapters + probe status
ops status          # show state
```

## Commands

| Command | Description |
|---|---|
| `ops doctor` | Probe for required OSS tools |
| `ops adapters` | List registered adapters |
| `ops agent run <task>` | Run a task through the agent loop |
| `ops build scaffold --name X --template python-cli` | Scaffold a new tool |
| `ops build audit --path .` | Run Semgrep audit |
| `ops build test --runner pytest --path .` | Run tests |
| `ops content tts --text "..."` | Text-to-speech (Kokoro) |
| `ops content thumbnail --text "..."` | PIL thumbnail |
| `ops content ingest --path file.pdf` | Docling ingestion |
| `ops marketing blog-init --name myblog` | Init Astro blog |
| `ops git-bootstrap <tree>` | Initialize git in unversioned tree |
| `ops harden mesh-check --tree <path>` | Find apps on old endpoints |
| `ops harden cost-check` | Check daily budget |
| `ops harden backup` | Backup state + config |
| `ops playbooks list` | List playbooks |
| `ops licenses` | Dump third-party licenses |

## Architecture

- **Mesh client**: uses phone's LLM mesh (`:8788`) via `x-llm-app: desktop-ops`. No local model (no GPU).
- **Adapters**: each OSS tool is an adapter with `probe()`, `capabilities()`, `run()`.
- **Gated autonomy**: first N runs are drafts requiring approval.
- **Refusal is a result**: adapters return structured refusals, never best-effort.

## Tests

```bash
python -m pytest tests/ -q
```

## Environment

Copy `.env.example` to `.env` and configure. See `.env.example` for all variables.

## License

MIT (core). OSS adapters retain their own licenses (see `ops licenses`).