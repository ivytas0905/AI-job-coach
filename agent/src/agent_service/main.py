# agent/src/agent_service/main.py

import os
import sys
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===== 1. 路径补丁 (保持原样，防止找不到模块) =====
CURRENT_FILE = os.path.abspath(__file__)
AGENT_SERVICE_DIR = os.path.dirname(CURRENT_FILE)
SRC_DIR = os.path.dirname(AGENT_SERVICE_DIR)
REPO_ROOT = os.path.dirname(SRC_DIR)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ===== 2. 统一导入 =====
from .config import get_settings
from .wiring import get_database_manager, get_memory_cache # 提前引入，避免函数内导入

# 一次性导入所有路由模块
from .api.routes import (
    parse, 
    jd, 
    master, 
    tailor, 
    jd_analysis, 
    resume_optimization,
    chat_assistant
)

# 加载环境变量
load_dotenv()

# 初始化配置
settings = get_settings()

app = FastAPI(
    title="Resume Agent Service",
    description="AI-powered resume parsing and optimization",
    version="2.0.0",
    debug=settings.debug,
)

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 3. 注册路由 (统一加上 /api/v1 前缀) =====

# 3.1 注册旧功能路由 (使用 try-except 防御)
try:
    from .api.routes import build
    # 修正：加上 /api/v1 前缀，防止前端 404
    app.include_router(build.router, prefix="/api/v1")
    print("✅ Build routes registered")
except ImportError as e:
    print(f"⚠️ Could not import build routes: {e}")

try:
    from .api.routes import optimize
    # 修正：加上 /api/v1 前缀
    app.include_router(optimize.router, prefix="/api/v1")
    print("✅ Optimize routes registered")
except ImportError as e:
    print(f"⚠️ Could not import optimize routes: {e}")

try:
    from .api.routes import export
    # 修正：加上 /api/v1 前缀
    app.include_router(export.router, prefix="/api/v1")
    print("✅ Export routes registered")
except ImportError as e:
    print(f"⚠️ Could not import export routes: {e}")

# 3.2 注册现有标准路由
app.include_router(parse.router, prefix="/api/v1")
app.include_router(jd.router, prefix="/api/v1")
app.include_router(master.router, prefix="/api/v1")
app.include_router(tailor.router, prefix="/api/v1")

# 3.3 注册增强功能路由 (New Features)
app.include_router(jd_analysis.router, prefix="/api/v1")
app.include_router(resume_optimization.router, prefix="/api/v1")
app.include_router(chat_assistant.router, prefix="/api/v1")


# ===== 4. 生命周期管理 =====
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    print("🚀 Starting Resume Agent Service...")

    # Initialize database
    db_manager = get_database_manager()
    await db_manager.create_tables()
    print("✅ Database initialized")

    # Start cache cleanup
    cache = get_memory_cache()
    await cache.start()
    print("✅ Cache service started")
    print("✅ All services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("🛑 Shutting down Resume Agent Service...")

    # Stop cache
    cache = get_memory_cache()
    await cache.stop()

    # Close database connections
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