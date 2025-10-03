from pathlib import Path
from mechanic.receipts import ReceiptRun


def test_receipts_run_creates_files(tmp_path: Path, monkeypatch):
    # Write receipts under a temp cwd
    monkeypatch.chdir(tmp_path)
    run = ReceiptRun.start_run(meta={"test": True})
    run.log_event({"type": "event", "ok": True})
    run.write_summary(title="Test Run", lines=["OK"])

    assert run.steps_path.exists()
    assert run.summary_path.exists()
    data = run.steps_path.read_text(encoding="utf-8").strip().splitlines()
    assert any("\"type\": \"meta\"" in line for line in data)
    assert any("\"type\": \"event\"" in line for line in data)

