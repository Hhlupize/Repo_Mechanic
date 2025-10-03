from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .shell import run as shell_run


def ensure_env(path: str | Path = ".", requirements: Optional[str] = None) -> Dict[str, object]:
    code = 0
    out_parts: List[str] = []
    err_parts: List[str] = []

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
