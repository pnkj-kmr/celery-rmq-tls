import json
from pathlib import Path

from celery_app.app import app
from celery_app.tasks import send_notification


def test_send_notification_writes_file_with_payload(tmp_path, monkeypatch):
    monkeypatch.setenv("RESULT_DIR", str(tmp_path))
    app.conf.task_always_eager = True
    try:
        result = send_notification.apply(args=[{"index": 7, "message": "hi"}])
    finally:
        app.conf.task_always_eager = False

    file_path = Path(result.get())
    assert file_path.exists()
    assert file_path.parent == tmp_path / "notification"
    data = json.loads(file_path.read_text())
    assert data["payload"] == {"index": 7, "message": "hi"}
    assert "task_id" in data
    assert "received_at" in data


def test_send_notification_filename_uses_task_id(tmp_path, monkeypatch):
    monkeypatch.setenv("RESULT_DIR", str(tmp_path))
    app.conf.task_always_eager = True
    try:
        result = send_notification.apply(args=[{"msg": "x"}])
    finally:
        app.conf.task_always_eager = False

    file_path = Path(result.get())
    assert file_path.name.startswith("message_")
    assert file_path.name.endswith(".json")
