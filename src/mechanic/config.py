from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


DEFAULT_ALLOWLIST_PREFIXES: tuple[str, ...] = ("src/", "tests/", "fixtures/")
DEFAULT_MAX_PATCH_LINES: int = 200


@dataclass(frozen=True)
class MechanicConfig:
    allowlist_prefixes: tuple[str, ...] = DEFAULT_ALLOWLIST_PREFIXES
    max_patch_lines: int = DEFAULT_MAX_PATCH_LINES
    fixtures_root: Optional[str] = None


def _load_from_toml(root: Path) -> Optional[MechanicConfig]:
    if tomllib is None:
        return None
    cfg_path = root / "repo-mechanic.toml"
    if not cfg_path.exists():
        return None
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    allow = data.get("allowlist", {}).get("prefixes") or list(DEFAULT_ALLOWLIST_PREFIXES)
    max_lines = data.get("guards", {}).get("max_patch_lines") or DEFAULT_MAX_PATCH_LINES
    fixtures_root = data.get("fixtures", {}).get("root")
    return MechanicConfig(allowlist_prefixes=tuple(allow), max_patch_lines=int(max_lines), fixtures_root=fixtures_root)


@lru_cache(maxsize=1)
def get_config() -> MechanicConfig:
    root = Path.cwd()
    cfg = _load_from_toml(root)
    return cfg or MechanicConfig()

