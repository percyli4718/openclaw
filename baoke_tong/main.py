"""
保客通 (BaokeTong) 主入口

基于 Hermes Agent 的 AI+ 保险获客系统
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 — 启动时初始化连接，关闭时释放"""
    # Startup
    logger.info("正在初始化数据库连接...")
    try:
        from .db import init_postgres, init_redis, init_qdrant
        await init_postgres()
        logger.info("PostgreSQL 连接池已创建")
    except Exception as e:
        logger.warning(f"PostgreSQL 连接失败（MVP 模式可忽略）：{e}")

    try:
        await init_redis()
        logger.info("Redis 连接已创建")
    except Exception as e:
        logger.warning(f"Redis 连接失败（MVP 模式可忽略）：{e}")

    try:
        await init_qdrant()
        logger.info("Qdrant 连接已创建")
    except Exception as e:
        logger.warning(f"Qdrant 连接失败（MVP 模式可忽略）：{e}")

    logger.info(f"保客通 v{settings.APP_VERSION} 启动完成")

    yield

    # Shutdown
    try:
        from .db import close_postgres, close_redis, close_qdrant
        await close_postgres()
        await close_redis()
        await close_qdrant()
    except Exception as e:
        logger.warning(f"关闭连接时出错：{e}")


app = FastAPI(
    title="保客通 (BaokeTong)",
    description="AI+ 保险获客系统",
    version="0.1.0",
    lifespan=lifespan,
)

logging.basicConfig(level=logging.INFO)

from .api import router
from .middleware import AuthMiddleware, TenantMiddleware, RateLimitMiddleware

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 中间件栈（顺序重要：后注册的最先执行）
# 执行顺序: RateLimit(最外层) → Tenant → Auth(最内层)
app.add_middleware(AuthMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(RateLimitMiddleware)

# 注册 API 路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Docker 健康检查端点 — 包含数据库连通性"""
    health = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "services": {},
    }

    # PostgreSQL 检查
    try:
        from .db import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        health["services"]["postgres"] = "connected"
    except Exception:
        health["services"]["postgres"] = "unavailable"

    # Redis 检查
    try:
        from .db import get_redis
        await get_redis().ping()
        health["services"]["redis"] = "connected"
    except Exception:
        health["services"]["redis"] = "unavailable"

    # Qdrant 检查
    try:
        from .db import get_qdrant_client
        await get_qdrant_client().get_collections()
        health["services"]["qdrant"] = "connected"
    except Exception:
        health["services"]["qdrant"] = "unavailable"

    # 只要有一个服务可用就认为是 ok（MVP 模式不强制全部可用）
    available = [v for v in health["services"].values() if v == "connected"]
    if not available:
        health["status"] = "degraded"

    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
