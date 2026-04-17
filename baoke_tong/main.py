"""
保客通 (BaokeTong) 主入口

基于 Hermes Agent 的 AI+ 保险获客系统
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import router
from .middleware import AuthMiddleware, TenantMiddleware, RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="保客通 (BaokeTong)",
    description="AI+ 保险获客系统",
    version="0.1.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 中间件栈（顺序重要：最外层最先执行）
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)

# 注册 API 路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Docker 健康检查端点"""
    return {"status": "ok", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
