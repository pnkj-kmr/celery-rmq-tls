"""Celery tasks for the notification queue."""
import json
from datetime import datetime, timezone
from pathlib import Path

from celery_app import config
from celery_app.app import app


@app.task(
    bind=True,
    name="celery_app.send_notification",
    max_retries=3,
    default_retry_delay=2,
)
def send_notification(self, payload: dict) -> str:
    """Write proof-of-execution file containing the payload."""
    try:
        out_dir = Path(config.result_dir()) / "notification"
        out_dir.mkdir(parents=True, exist_ok=True)

        file_path = out_dir / f"message_{self.request.id}.json"
        record = {
            "task_id": self.request.id,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        file_path.write_text(json.dumps(record, indent=2))
        return str(file_path)
    except OSError as exc:
        raise self.retry(exc=exc)
