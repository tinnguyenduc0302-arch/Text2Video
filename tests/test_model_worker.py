import queue
import sys
from app.core import model

def test_windowed_child_has_writable_streams(monkeypatch):
    messages = queue.Queue()
    def fake_sync(*_):
        sys.stderr.write("progress\n")
        sys.stdout.write("status\n")
    monkeypatch.setattr(model, "_sync_impl", fake_sync)
    monkeypatch.setattr(sys, "stderr", None)
    monkeypatch.setattr(sys, "stdout", None)
    model._sync_child("face", "audio", "output", "gan", messages)
    assert messages.get_nowait() is None
