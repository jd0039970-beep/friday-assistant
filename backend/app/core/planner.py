"""Long-task planner: break a goal into steps, track progress, resume."""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path

PLANS_DIR = Path.home() / ".friday" / "plans"
PLANS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Step:
    id: str
    description: str
    status: str = "pending"  # pending | running | done | failed | skipped
    result: str = ""


@dataclass
class Plan:
    id: str
    goal: str
    steps: list[Step] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    status: str = "active"  # active | completed | aborted

    def save(self):
        path = PLANS_DIR / f"{self.id}.json"
        data = {
            "id": self.id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "steps": [asdict(s) for s in self.steps],
        }
        path.write_text(json.dumps(data, indent=2))

    @staticmethod
    def load(plan_id: str) -> "Plan | None":
        path = PLANS_DIR / f"{plan_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        steps = [Step(**s) for s in data.get("steps", [])]
        return Plan(id=data["id"], goal=data["goal"], steps=steps,
                    created_at=data.get("created_at", 0), status=data.get("status", "active"))


def create_plan(goal: str, step_descriptions: list[str]) -> Plan:
    plan = Plan(
        id=uuid.uuid4().hex[:10],
        goal=goal,
        steps=[Step(id=str(i + 1), description=d) for i, d in enumerate(step_descriptions)],
    )
    plan.save()
    return plan


def list_plans() -> str:
    files = sorted(PLANS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return "No saved plans."
    lines = []
    for f in files[:15]:
        try:
            data = json.loads(f.read_text())
            lines.append(f"{data['id']} [{data.get('status')}] {data.get('goal','')[:60]}")
        except Exception:
            continue
    return "\n".join(lines)


def plan_status(plan_id: str) -> str:
    plan = Plan.load(plan_id)
    if not plan:
        return f"Plan not found: {plan_id}"
    lines = [f"Plan {plan.id}: {plan.goal}", f"Status: {plan.status}", ""]
    for s in plan.steps:
        lines.append(f"  [{s.status:8}] {s.id}. {s.description}")
        if s.result:
            lines.append(f"           → {s.result[:200]}")
    return "\n".join(lines)


def mark_step(plan_id: str, step_id: str, status: str, result: str = "") -> str:
    plan = Plan.load(plan_id)
    if not plan:
        return f"Plan not found: {plan_id}"
    for s in plan.steps:
        if s.id == step_id:
            s.status = status
            s.result = result
            break
    else:
        return f"Step {step_id} not found"
    if all(s.status in ("done", "skipped") for s in plan.steps):
        plan.status = "completed"
    plan.save()
    return plan_status(plan_id)
