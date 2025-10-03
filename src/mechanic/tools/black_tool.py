from __future__ import annotations

from pathlib import Path

from .shell import run as shell_run


def run(path: str | Path = ".", check: bool = True) -> dict[str, object]:
    args = ["black", str(path)]
    if check:
        args.append("--check")
    res = shell_run(args, cwd=path)
    return {"code": res.get("code", -1), "out": res.get("out", ""), "err": res.get("err", "")}
