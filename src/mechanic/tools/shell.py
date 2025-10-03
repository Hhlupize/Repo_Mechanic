from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def run(cmd: List[str], cwd: Optional[str | Path] = None, timeout: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> Dict[str, object]:
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

