"""CLI: publish N send_notification tasks to the broker."""
import argparse

from celery_app.tasks import send_notification


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish notification tasks.")
    parser.add_argument("--count", type=int, default=1, help="How many tasks to send.")
    parser.add_argument("--message", type=str, default="hello", help="Message body.")
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be >= 1")

    for i in range(args.count):
        payload = {"index": i, "message": args.message}
        async_result = send_notification.delay(payload)
        print(f"queued task_id={async_result.id} payload={payload}")


if __name__ == "__main__":
    main()
