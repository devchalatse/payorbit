# PayOrbit

PayOrbit is a business-payments and invoice-reconciliation platform. The initial product goal is to help SMEs and their suppliers move away from manual proof-of-payment handling and spreadsheet-based reconciliation.

## Current foundation

- FastAPI application with a health endpoint.
- PostgreSQL 16 development service.
- Docker image and Docker Compose setup.
- Ruff formatting and lint checks.
- Pytest smoke tests with a coverage gate.
- GitHub Actions CI and scheduled Python dependency auditing.

Payment initiation, Stitch integration, webhook verification, invoice reconciliation, and authentication are not implemented yet.

## Requirements

- Python 3.12+
- Docker Engine and Docker Compose (for containerized development)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs and http://localhost:8000/health.

## Run with Docker Compose

```bash
cp env.sample .env
docker compose up --build
```

The API is available at http://localhost:8000. PostgreSQL data is persisted in a named Docker volume. The supplied credentials are for local development only.

## Quality checks

```bash
ruff format --check .
ruff check .
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
pip-audit
docker build -t payorbit:local .
```

## Project direction

The MVP will remain a modular FastAPI application rather than starting with microservices. The first payment-provider integration is planned to be Stitch, subject to confirming its current merchant onboarding, API capabilities, fees, and settlement behaviour.

Provider credentials must remain server-side. Payment status must be based on authenticated provider events or verified provider status—not merely on a successful payment-initiation response.
