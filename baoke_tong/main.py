"""
保客通 (BaokeTong) 主入口

基于 Hermes Agent 的 AI+ 保险获客系统
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings, get_cors_origins
from .api.routes import router
from .middleware.auth import AuthMiddleware
from .middleware.tenant import TenantMiddleware
from .middleware.rate_limit import RateLimitMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("保客通 (BaokeTong) 启动中...")
    logger.info(f"版本：{settings.APP_VERSION}")
    logger.info(f"调试模式：{settings.DEBUG}")

    yield

    # 关闭时执行
    logger.info("保客通 (BaokeTong) 关闭中...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI+ 保险获客系统 - 基于 Hermes Agent",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# ==================== 中间件注册 ====================

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流中间件
app.add_middleware(RateLimitMiddleware)

# 租户上下文中间件
app.add_middleware(TenantMiddleware)

# 认证鉴权中间件 (最后注册，最先执行)
app.add_middleware(AuthMiddleware)

# ==================== 路由注册 ====================

# 注册 API 路由
app.include_router(router)


# ==================== 健康检查 ====================


@app.get("/")
async def root():
    """根路径 - 服务信息"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


# ==================== 认证接口 ====================


@app.post("/api/auth/login")
async def login(username: str, password: str):
    """
    用户登录接口

    返回 JWT Token
    """
    from .middleware.auth import AuthMiddleware

    # TODO: 实现真实的用户认证逻辑
    # 这里是占位符实现
    if not username or not password:
        return {
            "status": "error",
            "error": "用户名或密码不能为空"
        }

    # 模拟认证成功
    user_id = f"user_{username}"
    tenant_id = settings.TENANT_ID or f"tenant_{username}"

    token = AuthMiddleware.create_token(
        user_id=user_id,
        username=username,
        tenant_id=tenant_id,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "status": "success",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }


# ==================== 应用入口 ====================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if settings.DEBUG else "warning"
    )
