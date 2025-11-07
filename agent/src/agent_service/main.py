from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .api.routes import parse, jd, master, tailor
# New enhanced routes
from .api.routes import jd_analysis, resume_optimization, chat_assistant
import uvicorn

settings = get_settings()
app = FastAPI(
    title = "Resume Agent Service",
    description = "AI-powered resume parsing and optimization",
    version = "2.0.0",
    debug = settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register existing routes
app.include_router(parse.router, prefix="/api/v1")
app.include_router(jd.router, prefix="/api/v1")
app.include_router(master.router, prefix="/api/v1")
app.include_router(tailor.router, prefix="/api/v1")

# Register new enhanced routes
app.include_router(jd_analysis.router, prefix="/api/v1")
app.include_router(resume_optimization.router, prefix="/api/v1")
app.include_router(chat_assistant.router, prefix="/api/v1")


# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    print("🚀 Starting Resume Agent Service...")

    # Initialize database
    from .wiring import get_database_manager
    db_manager = get_database_manager()
    await db_manager.create_tables()
    print("✅ Database initialized")

    # Start cache cleanup
    from .wiring import get_memory_cache
    cache = get_memory_cache()
    await cache.start()
    print("✅ Cache service started")

    print("✅ All services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("🛑 Shutting down Resume Agent Service...")

    # Stop cache
    from .wiring import get_memory_cache
    cache = get_memory_cache()
    await cache.stop()

    # Close database connections
    from .wiring import get_database_manager
    db_manager = get_database_manager()
    await db_manager.close()

    print("✅ Cleanup complete")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Resume Agent",
        "environment": settings.environment,
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
