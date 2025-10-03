from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


@dataclass
class ReceiptRun:
    run_dir: Path
    steps_path: Path
    summary_path: Path
    last_error: str | None = field(default=None, init=False)

    @classmethod
    def start_run(cls, meta: dict[str, Any] | None = None) -> ReceiptRun:
        root = Path("receipts")
        root.mkdir(parents=True, exist_ok=True)
        run_dir = root / _now_stamp()
        run_dir.mkdir(parents=True, exist_ok=True)
        steps_path = run_dir / "steps.jsonl"
        summary_path = run_dir / "summary.md"
        run = cls(run_dir=run_dir, steps_path=steps_path, summary_path=summary_path)
        if meta:
            run.log_event({"type": "meta", **meta})
        return run

    def log_event(self, event: dict[str, Any]) -> bool:
        try:
            line = json.dumps(event, ensure_ascii=False)
            with self.steps_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def write_summary(self, title: str, lines: Iterable[str]) -> bool:
        try:
            with self.summary_path.open("w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                for ln in lines:
                    f.write(f"- {ln}\n")
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
