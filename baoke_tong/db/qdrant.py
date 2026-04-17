"""
Qdrant 向量数据库连接管理
"""

from qdrant_client import AsyncQdrantClient

from ..config import settings

_qdrant: AsyncQdrantClient | None = None


async def init_qdrant():
    """初始化 Qdrant 连接"""
    global _qdrant
    url = settings.QDRANT_URL
    _qdrant = AsyncQdrantClient(url=url)


async def close_qdrant():
    """关闭 Qdrant 连接"""
    global _qdrant
    if _qdrant:
        await _qdrant.close()
        _qdrant = None


def get_qdrant_client() -> AsyncQdrantClient:
    """获取 Qdrant 客户端实例"""
    if not _qdrant:
        raise RuntimeError("Qdrant 未初始化，请先调用 init_qdrant()")
    return _qdrant
