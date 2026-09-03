"""
Progress router.

GET /api/progress/dashboard — aggregated study progress dashboard
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)) -> dict:
    """Return aggregated progress stats for the dashboard."""
    try:
        svc = ProgressService(db)
        return await svc.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)) -> dict:
    """Return detailed learner profile metrics and achievements."""
    try:
        svc = ProgressService(db)
        return await svc.get_profile_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

