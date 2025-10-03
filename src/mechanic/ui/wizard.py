from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.status import Status

from mechanic.cli import cli as run_core  # reuse underlying logic via Typer callback


console = Console()


def run_wizard() -> None:
    console.rule("Repo Mechanic Wizard")
    target_default = "fixtures/broken-calculator"
    target_str = Prompt.ask("Target repo path", default=target_default)
    target = Path(target_str).resolve()
    fix_tests = Confirm.ask("Attempt to fix tests?", default=True)
    lint = Confirm.ask("Run lint (ruff/black)?", default=True)
    dry_run = Confirm.ask("Dry-run (no writes)?", default=True)
    max_steps = IntPrompt.ask("Max steps", default=6)

    with Status("Running Repo Mechanic...", console=console):
        # Call into the same CLI callback to ensure one code path
        try:
            run_core(
                path=str(target),
                fix_tests=fix_tests,
                lint=lint,
                dry_run=dry_run,
                max_steps=max_steps,
            )
        except typer.Exit:
            # bubbled exit from CLI; already printed message
            pass

    console.print("[bold green]Done.[/bold green]")

