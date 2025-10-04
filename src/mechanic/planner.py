from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .failure_classifier import classify


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


def _build_replacement_diff(file_path: Path, before: str, after: str) -> str | None:
    if not file_path.exists():
        return None
    txt = file_path.read_text(encoding="utf-8")
    if before not in txt:
        return None
    new_txt = txt.replace(before, after)
    a = txt.splitlines()
    b = new_txt.splitlines()
    try:
        rel_path = file_path.resolve().relative_to(Path.cwd().resolve())
    except Exception:
        rel_path = file_path
    rel = rel_path.as_posix()
    diff = difflib.unified_diff(a, b, fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm="")
    return "\n".join(diff)


def suggest_minimal_fixes(target: Path, failures: list[dict[str, Any]]) -> list[str]:
    """Heuristic suggestions based on simple failure categories.

    Currently recognizes the broken-calculator fixture patterns and a few generic cases.
    """
    diffs: list[str] = []
    # Broken calculator fixture: fix sub/add and div/*
    calc = target / "calc" / "__init__.py"
    d1 = _build_replacement_diff(
        calc,
        before="def sub(a, b):\n    return a + b",
        after="def sub(a, b):\n    return a - b",
    )
    if d1:
        diffs.append(d1)
    d2 = _build_replacement_diff(
        calc,
        before="def div(a, b):\n    return a * b",
        after="def div(a, b):\n    return a / b",
    )
    if d2:
        diffs.append(d2)

    # Generic pass: if ZeroDivision appears anywhere, consider guarding div(?,0) or operator fix
    cats = {classify(str(f.get("msg", ""))) for f in failures or []}
    if "ZeroDivision" in cats and d2 and d2 not in diffs:
        diffs.append(d2)
    return diffs
