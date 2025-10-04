from __future__ import annotations

import subprocess
from pathlib import Path


def run(
    cmd: list[str],
    cwd: str | Path | None = None,
    timeout: int | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            shell=False,
            check=False,
        )
        return {"code": proc.returncode, "out": proc.stdout, "err": proc.stderr}
    except Exception as e:
        return {"code": -1, "out": "", "err": str(e)}
