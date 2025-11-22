# agent/src/agent_service/main.py

import os
import sys

# ===== 1. 先处理路径，保证下面的 import 都能找到 =====
CURRENT_FILE = os.path.abspath(__file__)              # .../agent/src/agent_service/main.py
AGENT_SERVICE_DIR = os.path.dirname(CURRENT_FILE)      # .../agent/src/agent_service
SRC_DIR = os.path.dirname(AGENT_SERVICE_DIR)           # .../agent/src
REPO_ROOT = os.path.dirname(SRC_DIR)                   # .../agent

# 让 Python 能 import agent_service.xxx
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# 之前加的这行也可以留着，万一以后把 config 挪到上一级
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ===== 2. 再开始正常的 import =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent_service.config import get_settings   
from .config import get_settings
from .api.routes import parse, jd, master, tailor
# New enhanced routes
from .api.routes import jd_analysis, resume_optimization, chat_assistant
import uvicorn
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

settings = get_settings()

app = FastAPI(
<<<<<<< HEAD
    title="Resume Agent Service",
    description="AI-powered resume parsing and optimization",
    version="1.0.0",
    debug=settings.debug,
=======
    title = "Resume Agent Service",
    description = "AI-powered resume parsing and optimization",
    version = "2.0.0",
    debug = settings.debug,
>>>>>>> origin/feature/api-routes-and-frontend
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# ===== 3. 注册路由 =====
try:
    from agent_service.api.routes import build
    app.include_router(build.router)
    print("Build routes registered")
except ImportError as e:
    print(f"Could not import build routes: {e}")

try:
    from agent_service.api.routes import optimize
    app.include_router(optimize.router)
    print("Optimize routes registered.")
except ImportError as e:
    print(f"Could not import optimize routes: {e}")

try:
    from agent_service.api.routes import export
    app.include_router(export.router)
    print("Export routes registered")
except ImportError as e:
    print(f"Could not import export routes: {e}")
# Register routes
=======
# Register existing routes
>>>>>>> origin/feature/api-routes-and-frontend
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
