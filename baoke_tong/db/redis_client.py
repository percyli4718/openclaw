"""
Redis 连接管理

使用 redis.asyncio 提供异步 Redis 操作。
"""

from redis.asyncio import Redis

from ..config import settings

_redis: Redis | None = None


async def init_redis():
    """初始化 Redis 连接"""
    global _redis
    _redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=20,
    )


async def close_redis():
    """关闭 Redis 连接"""
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis() -> Redis:
    """获取 Redis 客户端实例"""
    if not _redis:
        raise RuntimeError("Redis 未初始化，请先调用 init_redis()")
    return _redis
