from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Sandbox:
    root: Path

    @classmethod
    def from_path(cls, path: str | Path) -> Sandbox:
        return cls(root=Path(path).resolve())

    def within(self, rel: str | Path) -> Path:
        p = (self.root / rel).resolve()
        if not str(p).startswith(str(self.root)):
            raise PermissionError("Path escapes sandbox root")
        return p
