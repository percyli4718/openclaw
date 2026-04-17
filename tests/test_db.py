"""
数据库连接管理测试

测试 db 模块结构和未初始化时的错误行为。
不依赖真实数据库连接。
"""

import pytest


class TestRedisClient:
    """Redis 连接测试"""

    def test_get_redis_not_initialized_raises(self):
        """Redis 未初始化时抛出 RuntimeError"""
        from baoke_tong.db.redis_client import get_redis
        with pytest.raises(RuntimeError, match="Redis 未初始化"):
            get_redis()


class TestQdrant:
    """Qdrant 连接测试"""

    def test_get_qdrant_not_initialized_raises(self):
        """Qdrant 未初始化时抛出 RuntimeError"""
        try:
            from baoke_tong.db.qdrant import get_qdrant_client
        except ModuleNotFoundError:
            pytest.skip("qdrant_client not installed")
        with pytest.raises(RuntimeError, match="Qdrant 未初始化"):
            get_qdrant_client()


class TestDbStructure:
    """db 模块结构测试"""

    def test_postgres_module_exists(self):
        """测试 postgres 模块可导入"""
        import importlib
        mod = importlib.import_module("baoke_tong.db.postgres")
        assert hasattr(mod, "init_postgres")
        assert hasattr(mod, "close_postgres")
        assert hasattr(mod, "get_db_session")

    def test_redis_module_exists(self):
        """测试 redis_client 模块可导入"""
        import importlib
        mod = importlib.import_module("baoke_tong.db.redis_client")
        assert hasattr(mod, "init_redis")
        assert hasattr(mod, "close_redis")
        assert hasattr(mod, "get_redis")

    def test_qdrant_module_exists(self):
        """测试 qdrant 模块可导入"""
        try:
            import importlib
            mod = importlib.import_module("baoke_tong.db.qdrant")
            assert hasattr(mod, "init_qdrant")
            assert hasattr(mod, "close_qdrant")
        except ModuleNotFoundError:
            pytest.skip("qdrant_client not installed")

    def test_db_init_lazy_import(self):
        """测试 __init__.py 使用延迟导入"""
        from baoke_tong import db
        # 只检查 __getattr__ 存在
        assert hasattr(db, "__getattr__")
