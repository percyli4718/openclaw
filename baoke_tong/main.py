"""
保客通 (BaokeTong) 主入口

基于 Hermes Agent 的 AI+ 保险获客系统
"""

from fastapi import FastAPI
from .config import settings
from .skills import ContentGenerator, CustomerAnalyst, FollowupManager

app = FastAPI(
    title="保客通 (BaokeTong)",
    description="AI+ 保险获客系统",
    version="0.1.0"
)

# 初始化技能
content_generator = ContentGenerator()
customer_analyst = CustomerAnalyst()
followup_manager = FollowupManager()


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Docker 健康检查端点"""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/api/v1/skills/content-gen")
async def content_generation_api():
    """内容生成 API 入口"""
    return {"message": "Content Generation API"}


@app.get("/api/v1/skills/customer")
async def customer_analysis_api():
    """客户分析 API 入口"""
    return {"message": "Customer Analysis API"}


@app.get("/api/v1/skills/followup")
async def followup_api():
    """跟进管理 API 入口"""
    return {"message": "Followup Management API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
