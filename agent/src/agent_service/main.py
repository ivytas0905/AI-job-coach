"""FastAPI application composition root."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import build, export, jd, master, optimize, parse, tailor
from .api.auth import get_current_user
from .config import get_settings
from .wiring import get_database_manager, get_memory_cache


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    database = get_database_manager()
    cache = get_memory_cache()
    if settings.database_auto_create:
        await database.create_tables()
    await cache.start()
    try:
        yield
    finally:
        await cache.stop()
        await database.close()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Resume Agent Service",
        description="AI-powered resume parsing and optimization",
        version="2.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for router in (build, export, optimize, parse, jd, master, tailor):
        application.include_router(
            router.router,
            prefix="/api/v1",
            dependencies=[Depends(get_current_user)],
        )

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": "Resume Agent",
            "environment": settings.environment,
        }

    return application


app = create_app()
