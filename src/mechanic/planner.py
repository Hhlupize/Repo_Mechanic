from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlanStep:
    description: str


def simple_plan(fix_tests: bool, lint: bool) -> list[PlanStep]:
    steps: list[PlanStep] = []
    if lint:
        steps.append(PlanStep("Run ruff and black --check"))
    if fix_tests:
        steps.extend(
            [
                PlanStep("Run pytest -q and collect failures"),
                PlanStep("Propose minimal patch for first failure"),
                PlanStep("Re-run tests; iterate until green or step limit"),
            ]
        )
    return steps
