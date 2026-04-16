"""
配置管理

保客通配置模块：
- 环境变量配置
- 多租户配置
- AI 模型配置 (云端/本地)
"""

from .settings import settings, get_cors_origins

__all__ = ["settings", "get_cors_origins"]
