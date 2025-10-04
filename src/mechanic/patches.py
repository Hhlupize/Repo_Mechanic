from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .guards import affected_paths, count_changed_lines, validate_patch
from .tools.shell import run as shell_run


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
    if not ok:
        return PatchResult(ok=False, changed_lines=changed, files=files, reasons=reasons)

    if dry_run:
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])

    root_path = Path(root)
    tmp_patch = root_path / ".mechanic.patch"
    tmp_patch.write_text(unified_diff, encoding="utf-8")
    try:
        res = shell_run(["git", "apply", "--ignore-space-change", "--whitespace=nowarn", str(tmp_patch)], cwd=root_path)
        if int(res.get("code", 1)) != 0:
            return PatchResult(ok=False, changed_lines=changed, files=files, reasons=[str(res.get("err", "git apply failed"))])
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])
    finally:
        try:
            tmp_patch.unlink()
        except Exception:
            pass
