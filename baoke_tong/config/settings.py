"""
配置管理

保客通配置模块
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "保客通 (BaokeTong)"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql://baoke:password@localhost:5432/baoke_tong"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"

    # AI 模型配置
    AI_PROVIDER: str = "anthropic"  # anthropic (云端) 或 ollama (本地)
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # 多租户配置
    TENANT_ID: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
