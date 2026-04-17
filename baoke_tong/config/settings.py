"""
配置管理

保客通配置模块
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    # 应用配置
    APP_NAME: str = "保客通 (BaokeTong)"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql://baoke:password@localhost:5432/baoke_tong"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"

    # AI 模型配置（LiteLLM 统一接口）
    # LITELLM_MODEL 格式: "provider/model_name"
    # 示例: "anthropic/claude-3-5-sonnet-20241022" 或 "ollama/qwen2.5:7b"
    LITELLM_MODEL: str = "anthropic/claude-sonnet-4-20250514"
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # 多租户配置
    TENANT_ID: Optional[str] = None

    # 安全配置
    SECRET_KEY: str = "baoke_tong_secret_key_change_in_production"
    JWT_SECRET_KEY: Optional[str] = None  # 默认使用 SECRET_KEY
    ENCRYPTION_KEY: str = "baoke_tong_encryption_key_32bytes!"


settings = Settings()
