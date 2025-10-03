from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .guards import affected_paths, count_changed_lines, validate_patch
from .tools.shell import run as shell_run


@dataclass
class PatchResult:
    ok: bool
    changed_lines: int
    files: List[str]
    reasons: List[str]


def apply_patch(unified_diff: str, root: Path | str = ".", dry_run: bool = True) -> PatchResult:
    ok, reasons = validate_patch(unified_diff)
    files = sorted(affected_paths(unified_diff))
    changed = count_changed_lines(unified_diff)
    if not ok:
        return PatchResult(ok=False, changed_lines=changed, files=files, reasons=reasons)

    if dry_run:
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])

    tmp_patch = Path(root) / ".mechanic.patch"
    tmp_patch.write_text(unified_diff, encoding="utf-8")
    try:
        res = shell_run(["git", "apply", str(tmp_patch)], cwd=root)
        if int(res.get("code", 1)) != 0:
            return PatchResult(
                ok=False,
                changed_lines=changed,
                files=files,
                reasons=[str(res.get("err", "git apply failed"))],
            )
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])
    finally:
        try:
            tmp_patch.unlink()  # type: ignore[call-arg]
        except Exception:
            pass
