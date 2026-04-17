"""
PostgreSQL 连接管理

使用 SQLAlchemy async engine + asyncpg 驱动。
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from ..config import settings

engine = None
_session_factory: async_sessionmaker | None = None
Base = declarative_base()


async def init_postgres():
    """初始化 PostgreSQL 连接池"""
    global engine, _session_factory
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        echo=settings.DEBUG,
    )
    _session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def close_postgres():
    """关闭 PostgreSQL 连接池"""
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库 session（FastAPI 依赖注入用）"""
    if not _session_factory:
        raise RuntimeError("PostgreSQL 未初始化，请先调用 init_postgres()")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
