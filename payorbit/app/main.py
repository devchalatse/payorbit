"""PayOrbit API application entry point."""

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="PayOrbit API",
    description="Business payments and invoice reconciliation platform.",
    version="0.2.0",
)


app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the API process health status."""
    return {"status": "ok"}
