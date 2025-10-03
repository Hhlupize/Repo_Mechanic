from __future__ import annotations

from pathlib import Path

from .shell import run as shell_run


def run(path: str | Path = ".", fix: bool = False) -> dict[str, object]:
    args = ["ruff", "check", str(path)]
    if fix:
        args.append("--fix")
    res = shell_run(args, cwd=path)
    return {"code": res.get("code", -1), "out": res.get("out", ""), "err": res.get("err", "")}
