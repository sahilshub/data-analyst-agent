"""The web API. Run locally with: uv run uvicorn app.main:app --reload"""

from fastapi import FastAPI

from app import __version__

app = FastAPI(title="Data Analyst Agent", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check: used by Docker, the deploy script and uptime alarms."""
    return {"status": "ok", "version": __version__}
