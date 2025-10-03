from __future__ import annotations

import datetime as _dt
from pathlib import Path

import typer

from .receipts import ReceiptRun
from .tools import ruff_tool, black_tool, pytest_tool
from .planner import simple_plan, suggest_minimal_fixes
from .patches import apply_patch
from .tools.shell import run as shell_run
from .ui.wizard import run_wizard
from .ui.receipts_html import build_html
from .ui.tui import run_tui


app = typer.Typer(
    add_completion=False,
    help=(
        "Repo Mechanic — local agentic code fixer.\n\n"
        "Examples:\n"
        "  repo-mechanic . --lint --dry-run\n"
        "  repo-mechanic fixtures/broken-calculator --fix-tests --max-steps 5 --dry-run\n"
    ),
)


@app.callback()
def cli(
    path: str = typer.Argument(".", help="Target repository path to operate on"),
    fix_tests: bool = typer.Option(
        False, "--fix-tests", help="Attempt to plan/patch for failing tests"
    ),
    lint: bool = typer.Option(False, "--lint", help="Run ruff/black checks"),
    dry_run: bool = typer.Option(
        True, "--dry-run/--write", help="Plan only vs apply changes"
    ),
    max_steps: int = typer.Option(10, "--max-steps", help="Maximum steps to attempt"),
) -> None:
    """Plan fixes for a small Python repo and write receipts."""
    target = Path(path).resolve()
    if not target.exists():
        typer.echo(f"Path does not exist: {target}")
        raise typer.Exit(code=2)

    run = ReceiptRun.start_run(
        meta={
            "command": "repo-mechanic",
            "timestamp": _dt.datetime.utcnow().isoformat() + "Z",
            "path": str(target),
            "fix_tests": fix_tests,
            "lint": lint,
            "dry_run": dry_run,
            "max_steps": max_steps,
        }
    )

    run.log_event({"type": "start", "cwd": str(target)})
    actions = []
    if lint:
        actions.append("lint")
    if fix_tests:
        actions.append("fix-tests")
    plan = [s.description for s in simple_plan(fix_tests=fix_tests, lint=lint)]
    run.log_event({"type": "plan", "actions": actions, "dry_run": dry_run, "steps": plan})
    if dry_run and plan:
        for step in plan:
            typer.echo(f"- {step}")

    lint_results = {}
    if lint:
        rr = ruff_tool.run(target)
        br = black_tool.run(target, check=True)
        lint_results = {"ruff": rr.get("code"), "black": br.get("code")}
        run.log_event({"type": "lint", "results": lint_results, "ruff": rr, "black": br})

    before = pytest_tool.run(target)
    run.log_event({"type": "pytest", "phase": "before", "code": before.get("code"), "failures": before.get("failures", []), "out": before.get("out"), "err": before.get("err")})

    applied: list[str] = []
    snapshot_sha: str | None = None
    if fix_tests:
        diffs = suggest_minimal_fixes(target)
        if not dry_run:
            shell_run(["git", "add", "-A"], cwd=Path.cwd())
            # best-effort snapshot before patch
            c = shell_run(["git", "commit", "-m", "chore(mechanic): pre-patch snapshot"], cwd=Path.cwd())
            if int(c.get("code", 1)) == 0:
                h = shell_run(["git", "rev-parse", "HEAD"], cwd=Path.cwd())
                if int(h.get("code", 1)) == 0:
                    snapshot_sha = h.get("out", "").strip()
        for i, diff in enumerate(diffs[:max_steps]):
            res = apply_patch(diff, root=Path.cwd(), dry_run=dry_run)
            run.log_event({
                "type": "patch",
                "index": i,
                "ok": res.ok,
                "files": res.files,
                "lines": res.changed_lines,
                "dry_run": dry_run,
                "reasons": res.reasons,
                "diff": diff,
            })
            if res.ok:
                applied.extend(res.files)

    after = pytest_tool.run(target)
    run.log_event({"type": "pytest", "phase": "after", "code": after.get("code"), "failures": after.get("failures", []), "out": after.get("out"), "err": after.get("err")})

    # Auto-revert on regression in write mode
    reverted = False
    if not dry_run and snapshot_sha is not None:
        before_n = len(before.get("failures", []) or [])
        after_n = len(after.get("failures", []) or [])
        if after_n > before_n:
            r = shell_run(["git", "reset", "--hard", f"{snapshot_sha}~0"], cwd=Path.cwd())
            reverted = int(r.get("code", 1)) == 0
            run.log_event({"type": "revert", "snapshot": snapshot_sha, "ok": reverted, "exit": r.get("code"), "err": r.get("err")})

    run.write_summary(
        title="Repo Mechanic Run",
        lines=[
            f"Target: {target}",
            f"Actions: {', '.join(actions) if actions else 'none'}",
            f"Mode: {'dry-run' if dry_run else 'write'}",
            f"Applied files: {', '.join(sorted(set(applied))) if applied else 'none'}",
            f"Failures before: {len(before.get('failures', []))}",
            f"Failures after: {len(after.get('failures', []))}",
        ],
    )
    # Build and announce HTML receipts
    html = build_html(run.run_dir)
    typer.echo(f"HTML: {html}")
    typer.echo(f"Receipts written to: {run.run_dir}")


@app.command(help="Interactive wizard to select path and options")
def wizard() -> None:
    run_wizard()


@app.command(help="Open the latest receipts HTML")
def receipts(open_latest: bool = typer.Option(True, "--open-latest", help="Open newest run HTML")) -> None:
    import webbrowser
    root = Path("receipts")
    if not root.exists():
        typer.echo("No receipts yet.")
        raise typer.Exit(code=0)
    runs = sorted([p for p in root.iterdir() if p.is_dir()])
    if not runs:
        typer.echo("No receipts yet.")
        raise typer.Exit(code=0)
    latest = runs[-1]
    html = build_html(latest)
    typer.echo(f"Latest: {html}")
    if open_latest:
        webbrowser.open(html.as_uri())


@app.command(help="Text UI to browse receipts")
def tui() -> None:
    run_tui()


if __name__ == "__main__":  # pragma: no cover
    app()
