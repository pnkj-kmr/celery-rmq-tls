"""Load environment-driven connection settings for the Celery app."""
import os
import ssl
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def build_broker_url() -> str:
    host = _env("RABBITMQ_HOST", "localhost")
    port = _env("RABBITMQ_PORT", "5671")
    user = _env("RABBITMQ_USER", "celery")
    password = _env("RABBITMQ_PASS", "celerypass")
    vhost = _env("RABBITMQ_VHOST", "/")
    # The root vhost "/" must appear as a literal "/" in the URL path (giving "//").
    # Any other vhost with internal slashes must have those slashes percent-encoded.
    if vhost == "/":
        vhost_encoded = "/"
    else:
        vhost_encoded = quote(vhost, safe="")
    user_encoded = quote(user, safe="")
    password_encoded = quote(password, safe="")
    return f"amqps://{user_encoded}:{password_encoded}@{host}:{port}/{vhost_encoded}"


def build_broker_use_ssl() -> dict:
    ca_cert = _env("RABBITMQ_CA_CERT", "docker/certs/ca.crt")
    return {
        "ca_certs": ca_cert,
        "cert_reqs": ssl.CERT_REQUIRED,
    }


def result_dir() -> str:
    return _env("RESULT_DIR", "result")
