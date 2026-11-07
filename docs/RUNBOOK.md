# Desktop-Ops Runbook

## Daily
- `ops doctor` — verify OSS tools.
- `ops harden cost-check` — ensure spend under budget.
- `ops harden mesh-check --tree <app>` — find apps still on old endpoints.

## Weekly
- `ops agent run "summarize week"` (requires LLM).
- `ops harden backup` — bundle state + config.

## Troubleshooting
- No LLM: set `DESKTOP_OPS_MESH_URL` (phone) or `DESKTOP_OPS_CLOUD_URL` + `DESKTOP_OPS_CLOUD_KEY`.
- Refusal is a result: an adapter returning `{"status":"refused"}` is expected behavior, not a bug.
- Cost exceeded: `ops harden cost-check` reports; non-essential lanes should be disabled.

## Kill switches
- Each playbook has `killSwitchEnv` (e.g. `FACELESS_YOUTUBE_ENABLED`). Set to `0` to disable.