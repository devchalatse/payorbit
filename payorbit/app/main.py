"""PayOrbit API application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="PayOrbit API",
    description="Business payments and invoice reconciliation platform.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the API process health status."""
    return {"status": "ok"}
