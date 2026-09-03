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
from app.api import materials, learning_paths, quizzes, revision, chat, progress

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
            "Study Buddy API — AI-powered study assistant with LLM-driven "
            "ingestion, quizzes, learning paths, revision scheduling, and chat."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        redirect_slashes=False,
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
    app.include_router(materials.router)
    app.include_router(learning_paths.router)
    app.include_router(quizzes.router)
    app.include_router(revision.router)
    app.include_router(chat.router)
    app.include_router(progress.router)

    return app


app = create_app()
