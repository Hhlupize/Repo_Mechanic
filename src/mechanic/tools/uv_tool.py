from __future__ import annotations

from pathlib import Path

from .shell import run as shell_run


def ensure_env(path: str | Path = ".", requirements: str | None = None) -> dict[str, object]:
    code = 0
    out_parts: list[str] = []
    err_parts: list[str] = []

    res1 = shell_run(["uv", "venv"], cwd=path)
    code = max(code, int(res1.get("code", -1)))
    out_parts.append(str(res1.get("out", "")))
    err_parts.append(str(res1.get("err", "")))

    if requirements:
        res2 = shell_run(["uv", "pip", "install", "-r", requirements], cwd=path)
        code = max(code, int(res2.get("code", -1)))
        out_parts.append(str(res2.get("out", "")))
        err_parts.append(str(res2.get("err", "")))

    return {"code": code, "out": "\n".join(out_parts).strip(), "err": "\n".join(err_parts).strip()}
