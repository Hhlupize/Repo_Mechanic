from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .guards import affected_paths, count_changed_lines, validate_patch
from .tools.shell import run as shell_run
from typing import Dict, List, Tuple


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
        if int(res.get("code", 1)) == 0:
            return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])
        # Fallback: apply simple +/- single-line replacements directly
        replacements = _extract_replacements(unified_diff)
        reasons = [str(res.get("err", "git apply failed"))]
        for fpath, old, new in replacements:
            p = root_path / fpath
            if not p.exists():
                reasons.append(f"missing file: {fpath}")
                continue
            text = p.read_text(encoding="utf-8")
            if old in text:
                text2 = text.replace(old, new)
                p.write_text(text2, encoding="utf-8")
            elif old.replace("\n", "\r\n") in text:
                text2 = text.replace(old.replace("\n", "\r\n"), new.replace("\n", "\r\n"))
                p.write_text(text2, encoding="utf-8")
            else:
                reasons.append(f"pattern not found in {fpath}")
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=reasons)
    finally:
        try:
            tmp_patch.unlink()
        except Exception:
            pass


def _extract_replacements(unified_diff: str) -> List[Tuple[str, str, str]]:
    replacements: List[Tuple[str, str, str]] = []
    current_file: str | None = None
    old_line: str | None = None
    new_line: str | None = None
    for line in unified_diff.splitlines():
        if line.startswith("+++ "):
            b = line.split(maxsplit=1)[1]
            if b.startswith("b/"):
                b = b[2:]
            current_file = b
            old_line = None
            new_line = None
            continue
        if line.startswith("@@"):
            old_line = None
            new_line = None
            continue
        if line.startswith("-") and not line.startswith("--- "):
            old_line = line[1:]
        elif line.startswith("+") and not line.startswith("+++ "):
            new_line = line[1:]
        if current_file and old_line is not None and new_line is not None:
            replacements.append((current_file, old_line, new_line))
            old_line = None
            new_line = None
    return replacements
