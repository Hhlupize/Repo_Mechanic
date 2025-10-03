from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _load_run(dir_path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {"summary": "", "diffs": []}
    md = dir_path / "summary.md"
    jl = dir_path / "steps.jsonl"
    if md.exists():
        data["summary"] = md.read_text(encoding="utf-8")
    diffs: List[str] = []
    if jl.exists():
        for line in jl.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") == "patch" and ev.get("diff"):
                diffs.append(ev["diff"])
    data["diffs"] = diffs
    return data


def run_tui() -> None:
    try:
        from textual.app import App, ComposeResult
        from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
        from textual.containers import Horizontal
        from textual.reactive import reactive
    except Exception:
        print("Textual is not installed. Install with: pip install textual")
        return

    class ReceiptsApp(App):
        CSS = """
        Screen { layout: vertical; }
        #content { height: 1fr; }
        .pane { width: 1fr; height: 1fr; }
        """

        runs: reactive[List[Path]] = reactive([])
        current_index: reactive[int] = reactive(0)
        showing_diff: reactive[bool] = reactive(False)

        def compose(self) -> ComposeResult:  # type: ignore[override]
            yield Header(show_clock=True)
            with Horizontal(id="content"):
                self.list_view = ListView(classes="pane")
                self.right = Static("", classes="pane")
                yield self.list_view
                yield self.right
            yield Footer()

        def on_mount(self) -> None:  # type: ignore[override]
            root = Path("receipts")
            if root.exists():
                self.runs = sorted([p for p in root.iterdir() if p.is_dir()])
            else:
                self.runs = []
            if not self.runs:
                self.right.update("No receipts yet. Run the CLI first.")
                return
            for p in self.runs:
                self.list_view.append(ListItem(Label(p.name)))
            self.list_view.index = len(self.runs) - 1
            self.current_index = self.list_view.index
            self._render_current()

        def action_toggle_view(self) -> None:
            self.showing_diff = not self.showing_diff
            self._render_current()

        def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
            self.current_index = event.index
            self._render_current()

        def _render_current(self) -> None:
            if not self.runs:
                return
            run = self.runs[self.current_index]
            info = _load_run(run)
            if not self.showing_diff:
                summary = info.get("summary", "").strip()
                diffs = info.get("diffs", [])
                body = f"[b]Run:[/b] {run}\n\n" + summary + "\n\n[b]Diffs:[/b]\n" + ("\n".join(f"#{i+1} ({len(d)} lines)" for i, d in enumerate(diffs)) or "(none)")
                self.right.update(body)
            else:
                diffs = info.get("diffs", [])
                if not diffs:
                    self.right.update("(no diffs)")
                else:
                    # Show the last diff for simplicity
                    self.right.update(diffs[-1])

        BINDINGS = [
            ("enter", "toggle_view", "Toggle summary/diff"),
        ]

    ReceiptsApp().run()

