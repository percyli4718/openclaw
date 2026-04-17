"""
Redis 缓存工具

提供简单的 cache_get / cache_set / cache_invalidate 接口，
使用 JSON 序列化。所有操作均为异步，Redis 不可用时自动降级。
"""

import json
import logging
from typing import Any, Optional

from .redis_client import get_redis

logger = logging.getLogger(__name__)


async def cache_get(key: str) -> Optional[Any]:
    """从 Redis 获取缓存值，JSON 反序列化。Redis 不可用时返回 None。"""
    try:
        redis = get_redis()
        raw = await redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        logger.debug(f"cache_get 失败（Redis 不可用）: {key}")
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """将值写入 Redis 缓存，JSON 序列化，带 TTL。Redis 不可用时静默跳过。"""
    try:
        redis = get_redis()
        await redis.setex(key, ttl, json.dumps(value))
    except Exception:
        logger.debug(f"cache_set 失败（Redis 不可用）: {key}")


async def cache_invalidate(key: str) -> None:
    """从 Redis 删除缓存。Redis 不可用时静默跳过。"""
    try:
        redis = get_redis()
        await redis.delete(key)
    except Exception:
        logger.debug(f"cache_invalidate 失败（Redis 不可用）: {key}")
