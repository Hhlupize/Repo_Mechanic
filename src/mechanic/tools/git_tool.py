from __future__ import annotations

from pathlib import Path

from .shell import run as shell_run


def init_and_commit(msg: str, cwd: str | Path = ".") -> dict[str, object]:
    outputs: list[str] = []
    errors: list[str] = []
    code = 0

    res_init = shell_run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd)
    if int(res_init.get("code", 1)) != 0:
        res = shell_run(["git", "init"], cwd=cwd)
        code = max(code, int(res.get("code", -1)))
        outputs.append(str(res.get("out", "")))
        errors.append(str(res.get("err", "")))

    res_add = shell_run(["git", "add", "-A"], cwd=cwd)
    code = max(code, int(res_add.get("code", -1)))
    outputs.append(str(res_add.get("out", "")))
    errors.append(str(res_add.get("err", "")))

    res_commit = shell_run(["git", "commit", "-m", msg], cwd=cwd)
    code = max(code, int(res_commit.get("code", -1)))
    outputs.append(str(res_commit.get("out", "")))
    errors.append(str(res_commit.get("err", "")))
    return {"code": code, "out": "\n".join(outputs).strip(), "err": "\n".join(errors).strip()}
