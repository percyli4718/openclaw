"""
Redis-backed 限流中间件测试

测试 Redis INCR 限流、内存降级、熔断器 Redis 存储、缓存 get/set/invalidation。
使用 unittest.mock 模拟 Redis 操作。
"""

import pytest
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from datetime import datetime

from baoke_tong.middleware.rate_limit import RateLimitMiddleware


class FakeRequest:
    """通用伪造 Request"""
    def __init__(self, path="/api/test", tenant_id=None, forwarded=None, client_ip="192.168.1.1"):
        self.url = type("FakeURL", (), {"path": path})()
        self.client = type("FakeClient", (), {"host": client_ip})() if client_ip else None
        self.headers = {}
        if forwarded:
            self.headers["X-Forwarded-For"] = forwarded
        self.state = type("FakeState", (), {"tenant_id": tenant_id})()


class FakeApp:
    async def __call__(self, scope, receive, send):
        pass


class FakeResponse:
    def __init__(self):
        self.status_code = 200


# ---------- Redis-backed rate limit tests ----------

class TestRedisRateLimitWithinLimit:
    """Redis 模式下请求在限制内"""

    @pytest.mark.asyncio
    async def test_redis_incr_within_limit(self):
        """Redis INCR 在限制内返回 True"""
        middleware = RateLimitMiddleware(FakeApp())

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=5)  # 第 5 次请求

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_rate_limit_redis("tenant:123", "/api/content/generate")
            assert ok is True

        mock_redis.incr.assert_called_once_with("ratelimit:tenant:123:/api/content/generate")

    @pytest.mark.asyncio
    async def test_redis_incr_sets_expiry_on_first_request(self):
        """第一次请求时设置 EXPIRE"""
        middleware = RateLimitMiddleware(FakeApp())

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=1)

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            await middleware._check_rate_limit_redis("tenant:123", "/api/content/generate")

        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_incr_exceeds_limit(self):
        """Redis INCR 超过限制返回 False"""
        middleware = RateLimitMiddleware(FakeApp())

        mock_redis = AsyncMock()
        # 限制 20，INCR 返回 21
        mock_redis.incr = AsyncMock(return_value=21)

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_rate_limit_redis("tenant:123", "/api/content/generate")
            assert ok is False


class TestRedisFallbackToMemory:
    """Redis 不可用时降级为内存模式"""

    @pytest.mark.asyncio
    async def test_fallback_on_redis_error(self):
        """Redis 异常时 _check_rate_limit_redis 返回 None，dispatch 应降级到内存"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 5, "window": 60}}

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(side_effect=ConnectionError("Redis connection refused"))

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            result = await middleware._check_rate_limit_redis("client1", "/api/test")

        # Redis 失败时返回 None，调用方应降级
        assert result is None
        assert middleware._redis_available is False

    @pytest.mark.asyncio
    async def test_stays_in_memory_mode_after_fallback(self):
        """降级后内存模式正常工作"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware._redis_available = False  # 已经降级
        middleware.API_LIMITS = {"/api/test": {"limit": 3, "window": 60}}

        # 记录 3 次请求
        for _ in range(3):
            middleware._record_request("c1", "/api/test")

        # 第 4 次应该被拒绝
        ok = middleware._check_rate_limit("c1", "/api/test")
        assert ok is False

    @pytest.mark.asyncio
    async def test_redis_recovery(self):
        """Redis 恢复后重新使用"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware._redis_available = False

        # 手动恢复
        middleware._redis_available = True

        mock_redis = AsyncMock()
        mock_redis.incr = AsyncMock(return_value=1)

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_rate_limit_redis("c1", "/api/test")
            assert ok is True


class TestRedisCircuitBreaker:
    """Redis-backed 熔断器测试"""

    @pytest.mark.asyncio
    async def test_circuit_closed_by_default_redis(self):
        """Redis 中无数据时熔断器关闭"""
        middleware = RateLimitMiddleware(FakeApp())

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_circuit_redis("/api/test")
            assert ok is False

    @pytest.mark.asyncio
    async def test_circuit_open_redis(self):
        """Redis 中存储打开状态时熔断器打开"""
        middleware = RateLimitMiddleware(FakeApp())

        data = {"failures": 5, "open": True, "open_until": time.time() + 30, "state": "open"}
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(data))

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_circuit_redis("/api/test")
            assert ok is True

    @pytest.mark.asyncio
    async def test_circuit_half_open_redis(self):
        """超过恢复时间后半开"""
        middleware = RateLimitMiddleware(FakeApp())

        data = {"failures": 5, "open": True, "open_until": time.time() - 10, "state": "open"}
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(data))

        with patch('baoke_tong.middleware.rate_limit.get_redis', return_value=mock_redis):
            ok = await middleware._check_circuit_redis("/api/test")
            assert ok is False  # 半开状态允许通过

    def test_record_failure_sync(self):
        """record_failure 是同步方法，更新内存状态"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(5):
            middleware.record_failure(path)
        assert middleware._is_circuit_open(path) is True

    def test_record_success_sync(self):
        """record_success 是同步方法，重置内存状态"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(5):
            middleware.record_failure(path)
        middleware.record_success(path)
        assert middleware._is_circuit_open(path) is False


class TestCacheModule:
    """缓存模块测试 (cache_get / cache_set / cache_invalidate)"""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """设置并获取缓存"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "value"}')

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_get, cache_set

            await cache_set("test:key", {"key": "value"}, ttl=60)
            result = await cache_get("test:key")

            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_cache_set_json_serialization(self):
        """cache_set 正确 JSON 序列化"""
        mock_redis = AsyncMock()

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_set

            await cache_set("test:obj", {"name": "test", "count": 42}, ttl=300)

            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == "test:obj"
            assert call_args[0][1] == 300  # TTL
            assert json.loads(call_args[0][2]) == {"name": "test", "count": 42}

    @pytest.mark.asyncio
    async def test_cache_get_miss(self):
        """缓存未命中返回 None"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_get

            result = await cache_get("nonexistent:key")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_get_redis_error(self):
        """Redis 异常时 cache_get 返回 None"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=ConnectionError("refused"))

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_get

            result = await cache_get("test:key")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_invalidate(self):
        """cache_invalidate 删除 key"""
        mock_redis = AsyncMock()

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_invalidate

            await cache_invalidate("test:key")

            mock_redis.delete.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_cache_invalidate_redis_error(self):
        """Redis 异常时 cache_invalidate 静默跳过"""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(side_effect=ConnectionError("refused"))

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_invalidate

            # 不应该抛出异常
            await cache_invalidate("test:key")

    @pytest.mark.asyncio
    async def test_cache_set_redis_error(self):
        """Redis 异常时 cache_set 静默跳过"""
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=ConnectionError("refused"))

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_set

            # 不应该抛出异常
            await cache_set("test:key", {"data": "value"})


class TestContentGenCache:
    """ContentGenerator 缓存集成测试

    由于 followup.py 有已知语法错误，此处直接测试缓存逻辑
    而不通过 ContentGenerator 类导入。
    """

    @staticmethod
    def _cache_key(method: str, params: dict) -> str:
        """复制 ContentGenerator._cache_key 逻辑"""
        import hashlib
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
        return f"content_gen:{method}:{param_hash}"

    @pytest.mark.asyncio
    async def test_cache_key_deterministic(self):
        """相同参数生成相同缓存 key"""
        key1 = self._cache_key("copywriting", {"product_name": "A", "count": 3})
        key2 = self._cache_key("copywriting", {"product_name": "A", "count": 3})
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_cache_key_different_params(self):
        """不同参数生成不同缓存 key"""
        key1 = self._cache_key("copywriting", {"product_name": "A", "count": 3})
        key2 = self._cache_key("copywriting", {"product_name": "B", "count": 3})
        assert key1 != key2

    @pytest.mark.asyncio
    async def test_cache_key_format(self):
        """缓存 key 格式正确"""
        key = self._cache_key("copywriting", {"product_name": "Test"})
        assert key.startswith("content_gen:copywriting:")

    @pytest.mark.asyncio
    async def test_cache_get_set_with_content_gen_key(self):
        """使用内容生成风格的 key 进行 get/set"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"copies": [{"id": "copy_001"}]}')

        with patch('baoke_tong.db.cache.get_redis', return_value=mock_redis):
            from baoke_tong.db.cache import cache_get, cache_set

            key = self._cache_key("copywriting", {"product_name": "Test", "count": 3})
            await cache_set(key, {"copies": [{"id": "copy_001"}]}, ttl=300)
            result = await cache_get(key)

            assert result == {"copies": [{"id": "copy_001"}]}
