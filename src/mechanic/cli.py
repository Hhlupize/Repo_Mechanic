from __future__ import annotations

import datetime as _dt
from pathlib import Path

import typer

from .receipts import ReceiptRun

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
    run.log_event({"type": "plan", "actions": actions, "dry_run": dry_run})
    run.write_summary(
        title="Repo Mechanic Run",
        lines=[
            f"Target: {target}",
            f"Actions: {', '.join(actions) if actions else 'none'}",
            f"Mode: {'dry-run' if dry_run else 'write'}",
        ],
    )
    typer.echo(f"Receipts written to: {run.run_dir}")


if __name__ == "__main__":  # pragma: no cover
    app()
