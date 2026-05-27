SHELL := /usr/bin/env bash
COMPOSE := docker compose -f docker/docker-compose.yml
PY := .venv/bin/python
CELERY := .venv/bin/celery
PYTEST := .venv/bin/pytest

.PHONY: certs up down worker send test smoke clean

certs:
	./docker/gen-certs.sh

up: certs
	$(COMPOSE) up -d
	@echo "Waiting for broker to become healthy..."
	@for i in $$(seq 1 30); do \
	  status=$$(docker inspect -f '{{.State.Health.Status}}' celery-rmq-tls 2>/dev/null || echo "starting"); \
	  if [ "$$status" = "healthy" ]; then echo "Broker healthy."; exit 0; fi; \
	  sleep 2; \
	done; \
	echo "Broker did not become healthy in 60s." >&2; exit 1

down:
	$(COMPOSE) down -v

worker:
	$(CELERY) -A celery_app.app worker -Q notification -l INFO

send:
	$(PY) client.py --count 3

test:
	$(PYTEST) -v

smoke:
	./scripts/smoke.sh

clean:
	rm -rf result/notification/*.json
