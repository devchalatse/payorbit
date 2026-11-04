.PHONY: install lint format-check test audit migrate migration docker-build up down

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

format-check:
	ruff format --check .

test:
	pytest --cov=app --cov-report=term-missing --cov-fail-under=90

audit:
	pip-audit

docker-build:
	docker build -t payorbit:local .

up:
	docker compose up --build

down:
	docker compose down

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(message)"
