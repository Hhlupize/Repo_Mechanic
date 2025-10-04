from __future__ import annotations

from .config import get_config


def is_path_allowed(path: str) -> bool:
    norm = path.replace("\\", "/").lstrip("./")
    cfg = get_config()
    return any(norm.startswith(prefix) for prefix in cfg.allowlist_prefixes)


def affected_paths(unified_diff: str) -> set[str]:
    paths: set[str] = set()
    for line in unified_diff.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                p = parts[1]
                if p.startswith("a/") or p.startswith("b/"):
                    p = p[2:]
                paths.add(p)
    return {p for p in paths if p not in {"/dev/null"}}


def count_changed_lines(unified_diff: str) -> int:
    count = 0
    for line in unified_diff.splitlines():
        if not line:
            continue
        if line.startswith(("diff ", "index ", "@@", "+++ ", "--- ")):
            continue
        if line.startswith("+") or line.startswith("-"):
            count += 1
    return count


def validate_patch(unified_diff: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    paths = affected_paths(unified_diff)
    if not paths:
        reasons.append("no affected paths detected")
    disallowed = [p for p in paths if not is_path_allowed(p)]
    if disallowed:
        reasons.append(f"paths not allowed: {', '.join(disallowed)}")
    changed = count_changed_lines(unified_diff)
    max_lines = get_config().max_patch_lines
    if changed > max_lines:
        reasons.append(f"changed lines {changed} exceeds max {max_lines}")
    return (len(reasons) == 0, reasons)
