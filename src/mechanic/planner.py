from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
import difflib


@dataclass
class PlanStep:
    description: str


def simple_plan(fix_tests: bool, lint: bool) -> List[PlanStep]:
    steps: List[PlanStep] = []
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


@dataclass
class Failure:
    file: str
    line: int
    msg: str


def _read_text(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _write_text(path: Path, lines: Iterable[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_replacement_diff(file_path: Path, before: str, after: str) -> Optional[str]:
    text = file_path.read_text(encoding="utf-8")
    if before not in text:
        return None
    new_text = text.replace(before, after)
    a = text.splitlines()
    b = new_text.splitlines()
    try:
        rel = file_path.resolve().relative_to(Path.cwd().resolve())
    except Exception:
        rel = file_path
    rel_posix = rel.as_posix()
    diff = difflib.unified_diff(
        a,
        b,
        fromfile=f"a/{rel_posix}",
        tofile=f"b/{rel_posix}",
        lineterm="",
    )
    return "\n".join(diff)


def suggest_minimal_fixes(target: Path) -> List[str]:
    # MVP: Recognize the broken-calculator fixture and propose two minimal replacements
    calc = target / "calc" / "__init__.py"
    diffs: List[str] = []
    if calc.exists():
        d1 = build_replacement_diff(
            calc,
            before="def sub(a, b):\n    return a + b",
            after="def sub(a, b):\n    return a - b",
        )
        if d1:
            diffs.append(d1)
        d2 = build_replacement_diff(
            calc,
            before="def div(a, b):\n    return a * b",
            after="def div(a, b):\n    return a / b",
        )
        if d2:
            diffs.append(d2)
    return diffs
