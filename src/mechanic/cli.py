from __future__ import annotations

import datetime as _dt
from pathlib import Path

import typer

from .patches import apply_patch
from .planner import simple_plan, suggest_minimal_fixes
from .receipts import ReceiptRun
from .tools import black_tool, pytest_tool, ruff_tool
from .tools.shell import run as shell_run
from .ui.receipts_html import build_html
from .ui.wizard import run_wizard

app = typer.Typer(
    add_completion=False,
    help=(
        "Repo Mechanic — local agentic code fixer.\n\n"
        "Examples:\n"
        "  repo-mechanic run . --lint --dry-run\n"
        "  repo-mechanic run fixtures/broken-calculator --fix-tests --max-steps 5 --dry-run\n"
    ),
)


@app.callback()
def cli() -> None:
    """Repo Mechanic CLI."""
    return


def run_core(
    path: str = typer.Argument(".", help="Target repository path to operate on"),
    fix_tests: bool = typer.Option(
        False, "--fix-tests", help="Attempt to plan/patch for failing tests"
    ),
    lint: bool = typer.Option(False, "--lint", help="Run ruff/black checks"),
    dry_run: bool = typer.Option(True, "--dry-run/--write", help="Plan only vs apply changes"),
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

    # Lint stage
    if lint:
        rr = ruff_tool.run(target)
        br = black_tool.run(target, check=True)
        run.log_event(
            {
                "type": "lint",
                "results": {"ruff": rr.get("code"), "black": br.get("code")},
                "ruff": rr,
                "black": br,
            }
        )

    # Test + plan stage
    before = pytest_tool.run(target)
    run.log_event(
        {
            "type": "pytest",
            "phase": "before",
            "code": before.get("code"),
            "failures": before.get("failures", []),
            "out": before.get("out"),
            "err": before.get("err"),
        }
    )

    applied: list[str] = []
    snapshot_sha: str | None = None
    if fix_tests:
        diffs = suggest_minimal_fixes(target, failures=before.get("failures", []) or [])
        if not dry_run:
            shell_run(["git", "add", "-A"], cwd=Path.cwd())
            c = shell_run(
                ["git", "commit", "-m", "chore(mechanic): pre-patch snapshot"], cwd=Path.cwd()
            )
            if int(c.get("code", 1)) == 0:
                h = shell_run(["git", "rev-parse", "HEAD"], cwd=Path.cwd())
                if int(h.get("code", 1)) == 0:
                    snapshot_sha = h.get("out", "").strip()
        for i, diff in enumerate(diffs[:max_steps]):
            res = apply_patch(diff, root=Path.cwd(), dry_run=dry_run)
            run.log_event(
                {
                    "type": "patch",
                    "index": i,
                    "ok": res.ok,
                    "files": res.files,
                    "lines": res.changed_lines,
                    "dry_run": dry_run,
                    "reasons": res.reasons,
                    "diff": diff,
                }
            )
            if res.ok:
                applied.extend(res.files)

    after = pytest_tool.run(target)
    run.log_event(
        {
            "type": "pytest",
            "phase": "after",
            "code": after.get("code"),
            "failures": after.get("failures", []),
            "out": after.get("out"),
            "err": after.get("err"),
        }
    )

    # Auto-revert on regression in write mode
    if not dry_run and snapshot_sha is not None:
        before_n = len(before.get("failures", []) or [])
        after_n = len(after.get("failures", []) or [])
        if after_n > before_n:
            r = shell_run(["git", "reset", "--hard", f"{snapshot_sha}~0"], cwd=Path.cwd())
            run.log_event(
                {
                    "type": "revert",
                    "snapshot": snapshot_sha,
                    "ok": int(r.get("code", 1)) == 0,
                    "exit": r.get("code"),
                    "err": r.get("err"),
                }
            )

    # Build HTML receipts and finish
    html = build_html(run.run_dir)
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
    typer.echo(f"HTML: {html}")
    typer.echo(f"Receipts written to: {run.run_dir}")


@app.command(help="Run planner/patcher on a target repo")
def run(
    path: str = typer.Argument(".", help="Target repository path to operate on"),
    fix_tests: bool = typer.Option(False, "--fix-tests"),
    lint: bool = typer.Option(False, "--lint"),
    dry_run: bool = typer.Option(True, "--dry-run/--write"),
    max_steps: int = typer.Option(10, "--max-steps"),
) -> None:
    run_core(path=path, fix_tests=fix_tests, lint=lint, dry_run=dry_run, max_steps=max_steps)


@app.command(help="Interactive wizard to select path and options")
def wizard() -> None:
    run_wizard()


@app.command(help="Open the latest receipts HTML")
def receipts(
    open_latest: bool = typer.Option(True, "--open-latest", help="Open newest run HTML")
) -> None:
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


if __name__ == "__main__":  # pragma: no cover
    app()
