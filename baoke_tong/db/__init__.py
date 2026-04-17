"""
保客通数据库连接管理

PostgreSQL + Redis + Qdrant 连接池初始化与生命周期管理。
"""

__all__ = [
    "engine",
    "get_db_session",
    "init_postgres",
    "close_postgres",
    "get_redis",
    "init_redis",
    "close_redis",
    "get_qdrant_client",
    "init_qdrant",
    "close_qdrant",
]


def __getattr__(name: str):
    """延迟导入 — 避免 qdrant_client 等依赖在 import 时报错"""
    if name in ("init_postgres", "close_postgres", "get_db_session", "engine"):
        from .postgres import init_postgres, close_postgres, get_db_session, engine
        return {"init_postgres": init_postgres, "close_postgres": close_postgres,
                "get_db_session": get_db_session, "engine": engine}[name]
    if name in ("init_redis", "close_redis", "get_redis"):
        from .redis_client import init_redis, close_redis, get_redis
        return {"init_redis": init_redis, "close_redis": close_redis,
                "get_redis": get_redis}[name]
    if name in ("init_qdrant", "close_qdrant", "get_qdrant_client"):
        from .qdrant import init_qdrant, close_qdrant, get_qdrant_client
        return {"init_qdrant": init_qdrant, "close_qdrant": close_qdrant,
                "get_qdrant_client": get_qdrant_client}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
