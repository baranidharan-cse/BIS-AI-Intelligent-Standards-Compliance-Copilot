"""
Health check router.

GET /api/health — returns DB connectivity status and current LLM provider.
This endpoint MUST remain dependency-free enough to be called by load
balancers and container health probes.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["health"])

settings = get_settings()


class HealthResponse(BaseModel):
    status: str                  # "ok" | "degraded"
    timestamp: str
    version: str
    llm_provider: str
    database: str                # "connected" | "error: <msg>"


@router.get("/health", response_model=HealthResponse, summary="Application health check")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Returns the current health of the application.

    - **status**: "ok" if all systems are operational, "degraded" if DB is unreachable.
    - **llm_provider**: the active LLM_PROVIDER setting.
    - **database**: "connected" if a test query succeeds.
    """
    db_status = "connected"
    overall_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        db_status = f"error: {exc}"
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.APP_VERSION,
        llm_provider=settings.LLM_PROVIDER,
        database=db_status,
    )
