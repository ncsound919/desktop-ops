"""Simple agent loop: plan -> act -> observe -> reflect.

Uses the LLM router for planning/reflection and the adapter registry for actions.
Not LangGraph (optional upgrade). Refusal-aware: a refused action stops the loop.
"""

from desktop_ops import registry, telemetry
from desktop_ops.adapters import llm


def run_task(task, max_steps=5):
    """Run a task through the agent loop. Returns a list of step records."""
    steps = []
    context = f"Task: {task}\n"

    for i in range(max_steps):
        # PLAN
        plan_prompt = (
            f"{context}\nStep {i+1}: What is the single next action? "
            f"Reply with one line: ACTION <adapter.action> | PARAMS <json> or DONE."
        )
        plan, src = llm.chat(plan_prompt, system="You are a concise planning agent. Output one line only.")
        if plan is None:
            steps.append({"step": i + 1, "phase": "plan", "error": src})
            break
        steps.append({"step": i + 1, "phase": "plan", "output": plan, "source": src})

        if "DONE" in plan.upper():
            break

        # Parse action (best-effort, simple format)
        action = None
        params = {}
        if "ACTION" in plan.upper():
            try:
                # Extract adapter.action
                part = plan.split("ACTION", 1)[1].strip()
                action = part.split("|")[0].strip().split()[0]
            except Exception:
                action = None

        if not action:
            steps.append({"step": i + 1, "phase": "act", "note": "no parseable action; stopping"})
            break

        adapter_name, _, act = (action.split(".", 1) + [None])[:2] if "." in action else (action, None)
        # Normalize: expect "adapter.action"
        if "." not in action:
            steps.append({"step": i + 1, "phase": "act", "note": f"bad action format: {action}"})
            break
        adapter_name, act = action.split(".", 1)

        mod = registry.get_adapter(adapter_name)
        if mod is None:
            steps.append({"step": i + 1, "phase": "act", "refused": f"unknown adapter {adapter_name}"})
            break

        result = mod.run(act, params)
        steps.append({"step": i + 1, "phase": "act", "adapter": adapter_name, "action": act, "result": result})

        if isinstance(result, dict) and result.get("status") == "refused":
            # Refusal is a result, not an error — stop and report
            break

        context += f"\nStep {i+1} result: {result}\n"

    telemetry.emit("agent.task.completed", data={"task": task, "steps": len(steps)})
    return steps