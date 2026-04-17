"""
数据库表创建工具

使用 SQLAlchemy metadata.create_all() 在启动时创建表。
Alembic 配置暂未引入，先用此方案实现快速建表。
"""

import logging
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def create_tables(engine: AsyncEngine) -> None:
    """
    创建所有 ORM 表（如果不存在）。

    包含：
    - 多租户综合模型（models/__init__.py 的 Base）
    - 技能层简化模型（models/orm.py 的 Base）

    失败时仅记录日志，不会中断应用启动。
    """
    try:
        # 导入所有模型的 Base
        from ..models import Base as MultiTenantBase
        from ..models.orm import Base as SkillBase

        async with engine.begin() as conn:
            # 创建多租户综合模型表
            await conn.run_sync(MultiTenantBase.metadata.create_all)
            logger.info("多租户模型表创建完成")

            # 创建技能层简化模型表
            await conn.run_sync(SkillBase.metadata.create_all)
            logger.info("技能层模型表创建完成")

    except Exception as e:
        logger.warning(f"创建数据库表失败（可稍后手动执行）：{e}")


async def drop_tables(engine: AsyncEngine) -> None:
    """
    删除所有 ORM 表（仅用于测试/开发环境）。
    """
    try:
        from ..models import Base as MultiTenantBase
        from ..models.orm import Base as SkillBase

        async with engine.begin() as conn:
            await conn.run_sync(SkillBase.metadata.drop_all)
            await conn.run_sync(MultiTenantBase.metadata.drop_all)
            logger.info("所有数据库表已删除")

    except Exception as e:
        logger.warning(f"删除数据库表失败：{e}")
