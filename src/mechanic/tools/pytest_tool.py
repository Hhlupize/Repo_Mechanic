from __future__ import annotations

import re
from pathlib import Path

from .shell import run as shell_run

_LOC_RE = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?:\s+in\s+.*)?")


def run(path: str | Path, extra_args: list[str] | None = None) -> dict[str, object]:
    args = ["pytest", "-q"] + (extra_args or [])
    res = shell_run(args, cwd=path)
    text = f"{res.get('out','')}{res.get('err','')}"
    failures: list[dict[str, object]] = []
    last_loc = None
    for line in text.splitlines():
        m = _LOC_RE.match(line.strip())
        if m:
            last_loc = {"file": m.group("file"), "line": int(m.group("line"))}
            continue
        if last_loc and line.strip():
            failures.append({**last_loc, "msg": line.strip()})
            last_loc = None
    return {"code": int(res.get("code", -1)), "failures": failures}
