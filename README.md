# celery-rmq-tls

Minimal Celery + RabbitMQ demo where all AMQP traffic runs over **TLS (AMQPS)**.

- Broker: Dockerized RabbitMQ 3.13, listening **only** on `5671` (AMQPS). Plaintext `5672` is disabled.
- TLS: self-signed CA + server cert generated locally; client verifies the server cert against the CA (`cert_reqs=CERT_REQUIRED`). Auth is username/password over the encrypted channel.
- Worker consumes from queue `notification`; each task writes `result/notification/message_<task_id>.json` so you can verify execution.

> The self-signed CA is for local dev only. Do not reuse these certs in production.

## Requirements

- Python 3.13
- Docker + Docker Compose v2
- `openssl`, `make`

## Quickstart

```bash
# 1. Python venv + deps
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Generate certs and bring up the broker
make up

# 3. In one terminal: start the worker
make worker

# 4. In another terminal: publish 3 tasks
make send

# 5. Verify
ls result/notification/
cat result/notification/message_*.json | head
```

To tear down:

```bash
make down
```

## One-shot end-to-end check

```bash
make smoke
```

Generates certs, starts the broker, runs a worker in the background, publishes 3 tasks, and asserts 3 files appear under `result/notification/`. Tears everything down on exit.

## Tests

```bash
make test
```

## Configuration

All connection settings come from env vars (see `.env.example`). Defaults match the Dockerized broker.

| Var | Default | Purpose |
|---|---|---|
| `RABBITMQ_HOST` | `localhost` | Broker host |
| `RABBITMQ_PORT` | `5671` | AMQPS port |
| `RABBITMQ_USER` | `celery` | Username |
| `RABBITMQ_PASS` | `celerypass` | Password |
| `RABBITMQ_VHOST` | `/` | Virtual host |
| `RABBITMQ_CA_CERT` | `docker/certs/ca.crt` | CA cert path for server verification |
| `RESULT_DIR` | `result` | Where the task writes its proof-of-execution file |

## How TLS is wired

- `docker/rabbitmq.conf` disables plaintext (`listeners.tcp = none`) and enables `listeners.ssl.default = 5671`, pointing at the mounted cert files.
- `celery_app/config.py` builds an `amqps://...` broker URL and sets `broker_use_ssl = {"ca_certs": ..., "cert_reqs": CERT_REQUIRED}`. A MITM presenting a different cert fails the handshake.
- The broker does **not** require client certs (`ssl_options.verify = verify_none`); authentication is via username/password over the encrypted channel.
