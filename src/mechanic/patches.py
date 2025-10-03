from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .guards import affected_paths, count_changed_lines, validate_patch


@dataclass
class PatchResult:
    ok: bool
    changed_lines: int
    files: list[str]
    reasons: list[str]


def apply_patch(unified_diff: str, root: Path | str = ".", dry_run: bool = True) -> PatchResult:
    ok, reasons = validate_patch(unified_diff)
    files = sorted(affected_paths(unified_diff))
    changed = count_changed_lines(unified_diff)
    return PatchResult(ok=ok, changed_lines=changed, files=files, reasons=reasons)
