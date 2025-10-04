from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.status import Status

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
        args = [
            sys.executable,
            "-m",
            "mechanic.cli",
            "run",
            str(target),
        ]
        if fix_tests:
            args.append("--fix-tests")
        if lint:
            args.append("--lint")
        args.append("--dry-run" if dry_run else "--write")
        args += ["--max-steps", str(max_steps)]
        subprocess.run(args, check=False)

    console.print("[bold green]Done.[/bold green]")
