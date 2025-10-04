from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from markdown_it import MarkdownIt


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            pass
    return events


def build_html(run_dir: Path) -> Path:
    run_dir = Path(run_dir)
    md_path = run_dir / "summary.md"
    steps_path = run_dir / "steps.jsonl"
    html_path = run_dir / "summary.html"

    md = MarkdownIt()
    summary_md = md_path.read_text(encoding="utf-8") if md_path.exists() else "# Summary\n"
    summary_html = md.render(summary_md)
    events = _read_jsonl(steps_path)

    tool_rows: List[str] = []
    diff_blocks: List[str] = []

    for ev in events:
        et = ev.get("type")
        if et in {"lint", "pytest"}:
            name = et
            code = ev.get("code") or ev.get("results")
            args = ev.get("args") or ev.get("actions") or []
            tool_rows.append(
                f"<tr><td>{name}</td><td><code>{args}</code></td><td>{code}</td></tr>"
            )
        if et == "patch":
            diff = ev.get("diff")
            if diff:
                diff_html = (
                    "<details><summary>View diff</summary>"
                    f"<pre style='background:#111;color:#eee;padding:8px;overflow:auto'>{_escape(diff)}</pre>"
                    "</details>"
                )
                diff_blocks.append(diff_html)

    # Optional coverage percent
    cov_html = ""
    cov = _coverage_percent(run_dir)
    if cov is not None:
        cov_html = f"<p><strong>Coverage:</strong> {cov:.2f}%</p>"

    table_html = (
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<thead><tr><th>Tool</th><th>Args/Actions</th><th>Exit/Result</th></tr></thead>"
        f"<tbody>{''.join(tool_rows) if tool_rows else '<tr><td colspan=3>(no tools logged)</td></tr>'}</tbody>"
        "</table>"
    )

    body = (
        "<html><head><meta charset='utf-8'><title>Repo Mechanic Receipts</title>"
        "<style>body{font-family:Arial,Helvetica,sans-serif;margin:24px} code,pre{font-family:Consolas,monospace}</style>"
        "</head><body>"
        "<h1>Repo Mechanic Receipt</h1>"
        f"<section>{summary_html}{cov_html}</section>"
        "<h2>Tool Calls</h2>"
        f"{table_html}"
        "<h2>Patches</h2>"
        f"{''.join(diff_blocks) if diff_blocks else '<p>(no patch diffs)</p>'}"
        "</body></html>"
    )

    html_path.write_text(body, encoding="utf-8")
    return html_path


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _coverage_percent(run_dir: Path) -> float | None:
    # Prefer coverage.xml in run_dir; fallback to repo root
    for p in (run_dir / "coverage.xml", Path("coverage.xml")):
        if p.exists():
            try:
                txt = p.read_text(encoding="utf-8")
                import re

                m = re.search(r"line-rate=\"([0-9.]+)\"", txt)
                if m:
                    return float(m.group(1)) * 100.0
            except Exception:
                return None
    return None

