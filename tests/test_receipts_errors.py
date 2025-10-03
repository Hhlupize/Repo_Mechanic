from pathlib import Path

from mechanic.receipts import ReceiptRun


def test_log_event_handles_io_errors(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    run = ReceiptRun.start_run(meta={"case": "io-error"})

    orig_open = Path.open

    def fake_open(self, *args, **kwargs):
        if self == run.steps_path:
            raise OSError("simulated write error")
        return orig_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)
    ok = run.log_event({"type": "event"})
    assert ok is False
    assert run.last_error and "simulated write error" in run.last_error


def test_write_summary_handles_io_errors(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    run = ReceiptRun.start_run(meta={"case": "io-error"})

    orig_open = Path.open

    def fake_open(self, *args, **kwargs):
        if self == run.summary_path:
            raise OSError("simulated summary error")
        return orig_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)
    ok = run.write_summary("Title", ["line"])
    assert ok is False
    assert run.last_error and "simulated summary error" in run.last_error

