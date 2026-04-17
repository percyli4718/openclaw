"""
配置管理

保客通配置模块
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator
from typing import Optional
import os
import secrets


class Settings(BaseSettings):
    """应用配置"""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    # 应用配置
    APP_NAME: str = "保客通 (BaokeTong)"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://baoke:password@localhost:5432/baoke_tong"
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
    SECRET_KEY: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ENCRYPTION_KEY: Optional[str] = None

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]

    @model_validator(mode="after")
    def validate_security_keys(self):
        """生产环境必须配置 SECRET_KEY 和 ENCRYPTION_KEY"""
        if self.APP_ENV != "development":
            if not self.SECRET_KEY:
                raise ValueError(
                    "生产环境必须设置 SECRET_KEY，"
                    "建议: openssl rand -hex 32"
                )
            if not self.ENCRYPTION_KEY:
                raise ValueError(
                    "生产环境必须设置 ENCRYPTION_KEY（32 字节）"
                )
        # 开发环境自动生成随机 SECRET_KEY
        if not self.SECRET_KEY:
            object.__setattr__(self, "SECRET_KEY", secrets.token_hex(32))
        if not self.ENCRYPTION_KEY:
            object.__setattr__(self, "ENCRYPTION_KEY", secrets.token_hex(16))
        return self


settings = Settings()
