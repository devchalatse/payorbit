# PayOrbit

PayOrbit is a business-payments and invoice-reconciliation platform. The initial product goal is to help SMEs and their suppliers move away from manual proof-of-payment handling and spreadsheet-based reconciliation.

## Current backend foundation

- FastAPI application with versioned API routes under `/api/v1`.
- Business and customer creation and listing.
- Invoice creation, itemized totals, retrieval, listing, and draft-to-issued transition.
- PostgreSQL 16 with SQLAlchemy 2 and Alembic migrations.
- Docker image and Docker Compose local environment.
- Ruff formatting/linting and pytest coverage checks.
- GitHub Actions CI and scheduled dependency auditing.

Payment initiation, Stitch integration, provider webhook verification, invoice settlement/reconciliation, authentication, and production deployment are not implemented yet.

## Requirements

- Python 3.12+
- Docker Engine and Docker Compose (for containerized development)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
```

Set `DATABASE_URL` in your shell or `.env` to a reachable PostgreSQL database, then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs and http://localhost:8000/health.

## Run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Compose starts PostgreSQL, waits for its health check, applies Alembic migrations, and starts the API. The API is available at http://localhost:8000. PostgreSQL data is persisted in a named Docker volume. The supplied credentials are for local development only.

## API overview

- `POST /api/v1/businesses` and `GET /api/v1/businesses`
- `POST /api/v1/customers` and `GET /api/v1/customers?business_id={uuid}`
- `POST /api/v1/invoices`
- `GET /api/v1/invoices?business_id={uuid}`
- `GET /api/v1/invoices/{invoice_id}`
- `POST /api/v1/invoices/{invoice_id}/issue`

Invoice amounts are stored as integer minor units (for example, cents), not floating-point currency values. Invoices are created as drafts and must be explicitly issued. Customer/business ownership is checked when creating an invoice.

## Quality checks

Run these from this directory:

```bash
ruff format --check .
ruff check .
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
pip-audit --skip-editable
docker build -t payorbit:local .
```

## Product direction

The MVP will remain a modular FastAPI application rather than starting with microservices. The first payment-provider integration is planned to be Stitch, subject to confirming current merchant onboarding, API capabilities, fees, and settlement behaviour.

Provider credentials must remain server-side. Payment status must be based on authenticated provider events or verified provider status—not merely on a successful payment-initiation response.
