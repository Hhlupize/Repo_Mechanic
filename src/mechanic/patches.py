from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .guards import affected_paths, count_changed_lines, validate_patch
from .tools.shell import run as shell_run
from typing import List, Tuple, Optional


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
        # Snapshot pre-contents
        before_contents = {}
        for f in files:
            p = root_path / f
            before_contents[f] = p.read_text(encoding="utf-8") if p.exists() else None

        res = shell_run(["git", "apply", "--ignore-space-change", "--whitespace=nowarn", str(tmp_patch)], cwd=root_path)
        if int(res.get("code", 1)) == 0:
            # Verify changes actually occurred
            changed_any = False
            for f in files:
                p = root_path / f
                after = p.read_text(encoding="utf-8") if p.exists() else None
                if after is not None and after != before_contents.get(f):
                    changed_any = True
                    break
            if changed_any:
                return PatchResult(ok=True, changed_lines=changed, files=files, reasons=[])
        # Fallback: apply simple +/- single-line replacements directly
        replacements = _extract_replacements(unified_diff)
        reasons = [str(res.get("err", "git apply failed"))]
        for fpath, ctx, old, new in replacements:
            p = root_path / fpath
            if not p.exists():
                reasons.append(f"missing file: {fpath}")
                continue
            text = p.read_text(encoding="utf-8")
            replaced = False
            if ctx:
                # Try context-bound replacement first
                pattern_unix = f"{ctx}\n{old}"
                replacement_unix = f"{ctx}\n{new}"
                if pattern_unix in text:
                    text = text.replace(pattern_unix, replacement_unix, 1)
                    replaced = True
                else:
                    pattern_crlf = pattern_unix.replace("\n", "\r\n")
                    replacement_crlf = replacement_unix.replace("\n", "\r\n")
                    if pattern_crlf in text:
                        text = text.replace(pattern_crlf, replacement_crlf, 1)
                        replaced = True
            if not replaced:
                # Fallback to single-line replace, once
                if old in text:
                    text = text.replace(old, new, 1)
                    replaced = True
                else:
                    old_crlf = old.replace("\n", "\r\n")
                    new_crlf = new.replace("\n", "\r\n")
                    if old_crlf in text:
                        text = text.replace(old_crlf, new_crlf, 1)
                        replaced = True
            if replaced:
                p.write_text(text, encoding="utf-8")
            else:
                reasons.append(f"pattern not found in {fpath}")
        return PatchResult(ok=True, changed_lines=changed, files=files, reasons=reasons)
    finally:
        try:
            tmp_patch.unlink()
        except Exception:
            pass


def _extract_replacements(unified_diff: str) -> List[Tuple[str, Optional[str], str, str]]:
    """Extract simple single-line replacements with optional preceding context line.

    Returns tuples of (file_path, context_line, old_line, new_line).
    context_line is typically a function signature like 'def sub(a, b):'.
    """
    replacements: List[Tuple[str, Optional[str], str, str]] = []
    current_file: str | None = None
    old_line: str | None = None
    new_line: str | None = None
    last_context: Optional[str] = None
    for line in unified_diff.splitlines():
        if line.startswith("+++ "):
            b = line.split(maxsplit=1)[1]
            if b.startswith("b/"):
                b = b[2:]
            current_file = b
            old_line = None
            new_line = None
            last_context = None
            continue
        if line.startswith("@@"):
            old_line = None
            new_line = None
            last_context = None
            continue
        if line.startswith("-") and not line.startswith("--- "):
            old_line = line[1:]
        elif line.startswith("+") and not line.startswith("+++ "):
            new_line = line[1:]
        elif not line.startswith(("diff ", "index ", "--- ", "+++ ", "@@", "+", "-")):
            # context line
            last_context = line
        if current_file and old_line is not None and new_line is not None:
            replacements.append((current_file, last_context, old_line, new_line))
            old_line = None
            new_line = None
    return replacements
