import ssl
from celery_app import config


def test_build_broker_url_uses_amqps_and_env(monkeypatch):
    monkeypatch.setenv("RABBITMQ_HOST", "rmq.example.com")
    monkeypatch.setenv("RABBITMQ_PORT", "5671")
    monkeypatch.setenv("RABBITMQ_USER", "alice")
    monkeypatch.setenv("RABBITMQ_PASS", "s3cret")
    monkeypatch.setenv("RABBITMQ_VHOST", "/")

    url = config.build_broker_url()

    assert url == "amqps://alice:s3cret@rmq.example.com:5671//"


def test_build_broker_url_url_encodes_vhost(monkeypatch):
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5671")
    monkeypatch.setenv("RABBITMQ_USER", "u")
    monkeypatch.setenv("RABBITMQ_PASS", "p")
    monkeypatch.setenv("RABBITMQ_VHOST", "my/vhost")

    url = config.build_broker_url()

    assert url == "amqps://u:p@localhost:5671/my%2Fvhost"


def test_build_broker_use_ssl_requires_cert_and_ca(monkeypatch, tmp_path):
    ca = tmp_path / "ca.crt"
    ca.write_text("dummy")
    monkeypatch.setenv("RABBITMQ_CA_CERT", str(ca))

    ssl_opts = config.build_broker_use_ssl()

    assert ssl_opts["ca_certs"] == str(ca)
    assert ssl_opts["cert_reqs"] == ssl.CERT_REQUIRED


def test_result_dir_defaults_to_result(monkeypatch):
    monkeypatch.delenv("RESULT_DIR", raising=False)
    assert config.result_dir() == "result"


def test_result_dir_honors_env(monkeypatch):
    monkeypatch.setenv("RESULT_DIR", "/tmp/out")
    assert config.result_dir() == "/tmp/out"


def test_build_broker_url_url_encodes_user_and_password(monkeypatch):
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5671")
    monkeypatch.setenv("RABBITMQ_USER", "user@name")
    monkeypatch.setenv("RABBITMQ_PASS", "p@ss:w0rd")
    monkeypatch.setenv("RABBITMQ_VHOST", "/")

    url = config.build_broker_url()

    assert url == "amqps://user%40name:p%40ss%3Aw0rd@localhost:5671//"
