# Recording a Demo (Asciinema or GIF)

This project previously linked to a placeholder Asciinema URL. Use one of the options below to create a short recording and then update `README.md` with your link.

## Option A — Asciinema (Linux/macOS/WSL)

1) Install
- macOS (Homebrew): `brew install asciinema`
- Ubuntu/Debian: `sudo apt-get install -y asciinema`
- Anywhere (pipx): `pipx install asciinema`

2) Record the demo
- Non-interactive, using the provided script:
  - `asciinema rec -c "bash scripts/demo.sh"`
- Interactive session (type commands manually):
  - `asciinema rec`
  - Run: `uv sync && uv pip install -e .`
  - Run: `uv run repo-mechanic run fixtures/broken-calculator --fix-tests --dry-run`
  - Finish (Ctrl+D), accept upload → copy the URL

3) Update README
- Replace the “Recording (Coming Soon)” note with your Asciinema link.

## Option B — VHS (GIF), cross‑platform

1) Install VHS (https://github.com/charmbracelet/vhs)
- macOS: `brew install vhs`
- Windows: `scoop install vhs` (via Scoop) or download from releases
- Linux: download from releases

2) Create a tape (examples)
- See `vhs` docs; a simple tape can open a shell, run `bash scripts/demo.sh`, and export `docs/demo.gif`.

3) Commit the GIF and update README
- Save under `docs/demo.gif` and link it from README.

Tips
- Keep the demo short (30–60s). Show: lint + tests, wizard or run on the fixture, receipts HTML path.
- Run in a clean terminal for readability.
