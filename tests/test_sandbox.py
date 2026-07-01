"""Sandbox executor: compute, error capture, timeout enforcement, artifacts."""
from app.config import settings
from app.sandbox import executor


def test_compute_returns_stdout():
    r = executor.run("print(6 * 7)")
    assert r.ok
    assert r.stdout.strip() == "42"


def test_error_is_captured_not_raised():
    r = executor.run("raise ValueError('boom')")
    assert not r.ok
    assert "ValueError" in r.stderr


def test_timeout_is_enforced(monkeypatch):
    monkeypatch.setattr(settings, "sandbox_timeout_seconds", 2)
    r = executor.run("while True:\n    pass")
    assert not r.ok


def test_artifact_is_captured():
    # Write a file named output.png; the executor should lift it out.
    r = executor.run("open('output.png', 'wb').write(b'\\x89PNG\\r\\n')")
    assert r.ok
    assert r.artifact_path and r.artifact_path.endswith(".png")
