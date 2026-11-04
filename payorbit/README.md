# PayOrbit

PayOrbit is a business-payments and invoice-reconciliation platform. The initial product goal is to help SMEs and their suppliers move away from manual proof-of-payment handling and spreadsheet-based reconciliation.

## Current backend foundation

- FastAPI application with versioned API routes under `/api/v1`.
- Email/password registration and login, Argon2 password hashing, and short-lived signed JWT access tokens.
- Business ownership and membership records; business, customer and invoice endpoints enforce tenant membership.
- Invoice creation, itemized totals, retrieval, listing, and draft-to-issued transition.
- PostgreSQL 16 with SQLAlchemy 2 and Alembic migrations.
- Docker image and Docker Compose local environment.
- Ruff formatting/linting and pytest coverage checks.
- GitHub Actions CI and dependency auditing.

Payment initiation, Stitch integration, provider webhook verification, invoice settlement/reconciliation, invitations, password reset, MFA, refresh-token rotation, and production deployment are not implemented yet.

## Requirements

- Python 3.12+
- Docker Engine and Docker Compose (recommended for local development)

## Run with Docker Compose

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into `JWT_SECRET_KEY` in `.env`, and replace the local PostgreSQL password consistently in `POSTGRES_PASSWORD` and `DATABASE_URL`. Then run:

```bash
docker compose up --build
```

Compose starts PostgreSQL, waits for its health check, applies Alembic migrations, and starts the API. The API is available at http://localhost:8000. PostgreSQL data is persisted in a named Docker volume. All supplied credentials are development examples only.

## Run the API directly with Python

Create and activate a Python 3.12 virtual environment, then install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Set `DATABASE_URL` to a reachable PostgreSQL instance and `JWT_SECRET_KEY` to a unique random value of at least 32 characters. Then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs and http://localhost:8000/health.

## Authentication and API

Register the first business owner:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "business_name": "Example Wholesale",
    "business_email": "accounts@example.co.za",
    "full_name": "Example Owner",
    "email": "owner@example.co.za",
    "password": "replace-with-a-long-unique-password"
  }'
```

The response contains a short-lived bearer access token and the businesses the user belongs to. Send it on protected requests:

```bash
curl http://localhost:8000/api/v1/businesses \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

Authentication endpoints:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Business endpoints:
- `POST /api/v1/businesses`, `GET /api/v1/businesses`
- `GET /api/v1/businesses/{business_id}`

Customer endpoints:
- `POST /api/v1/customers`
- `GET /api/v1/customers?business_id={uuid}`
- `GET /api/v1/customers/{customer_id}`

Invoice endpoints:
- `POST /api/v1/invoices`
- `GET /api/v1/invoices?business_id={uuid}`
- `GET /api/v1/invoices/{invoice_id}`
- `POST /api/v1/invoices/{invoice_id}/issue`

All business/customer/invoice operations require a bearer token and verify the user's membership in the relevant business. A user cannot access another business's records by changing an ID in the request. Invoice amounts are stored as integer minor units (for example, cents), not floating-point currency values.

## Quality checks

Run these from the `payorbit` directory:

```bash
ruff format --check .
ruff check .
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
pip-audit --skip-editable
docker build -t payorbit:local .
```

## Security status

This is an MVP development foundation, not a production-ready financial service. Before production, add rate limiting and abuse controls for authentication, email verification, password reset, MFA appropriate to the risk, refresh-token rotation/revocation, audit logging, secrets management, TLS, backups, monitoring, and a security review. Do not use real customer or payment data until those controls and operational procedures are in place.

## Product direction

The MVP will remain a modular FastAPI application rather than starting with microservices. The first payment-provider integration is planned to be Stitch, subject to confirming current merchant onboarding, API capabilities, fees, and settlement behaviour.

Provider credentials must remain server-side. Payment status must be based on authenticated provider events or verified provider status—not merely on a successful payment-initiation response.
