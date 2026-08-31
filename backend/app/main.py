"""
FastAPI application factory.

All routers are registered here. Feature routers (ingestion, quiz, etc.)
will be added in future sessions as stubs are replaced with real implementations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.api import health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup/shutdown side-effects."""
    # Startup: ensure all DB tables exist
    await init_db()
    yield
    # Shutdown: (nothing to clean up for SQLite; connection pool handles it)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Study Buddy API — AI-powered study assistant. "
            "Foundation layer: health check and DB connectivity only. "
            "Feature endpoints are added in subsequent sessions."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)

    # TODO (Session 2): add ingestion router
    # from app.api import ingestion
    # app.include_router(ingestion.router)

    # TODO (Session 3): add learning path router
    # TODO (Session 4): add quiz router
    # TODO (Session 5): add explain router
    # TODO (Session 6): add revision router
    # TODO (Session 7): add chatbot router

    return app


app = create_app()
