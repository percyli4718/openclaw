"""
限流中间件

实现 API 限流和熔断机制，遵循 Design Spec Section 10.2 SLA 定义。
使用 Redis 作为主存储，Redis 不可用时自动降级为内存存储。

内部辅助方法保持同步（向后兼容），dispatch 中使用 async Redis 路径。
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import time
import json

from ..db.redis_client import get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API 限流中间件"""

    # 跳过限流的路径
    SKIP_RATE_LIMIT_PATHS = {
        "/",
        "/api/health",
        "/docs",
        "/openapi.json",
    }

    # 默认限流配置 (requests per window)
    DEFAULT_LIMIT = 100  # 默认每窗口 100 次请求
    DEFAULT_WINDOW_SECONDS = 60  # 默认 1 分钟窗口

    # API 特定限流配置 (遵循 Design Spec Section 10.2)
    API_LIMITS = {
        # 内容生成 API - AI 调用成本高，限流较严格
        "/api/content/generate": {"limit": 20, "window": 60},  # 20 次/分钟
        "/api/content/video-script": {"limit": 10, "window": 60},  # 10 次/分钟
        "/api/content/poster": {"limit": 20, "window": 60},  # 20 次/分钟

        # 客户分析 API
        "/api/customer/analyze": {"limit": 30, "window": 60},  # 30 次/分钟
        "/api/customer/segment": {"limit": 20, "window": 60},  # 20 次/分钟
        "/api/customer/needs": {"limit": 30, "window": 60},  # 30 次/分钟
        "/api/customer/search-similar": {"limit": 30, "window": 60},  # 30 次/分钟

        # 跟进管理 API
        "/api/followup/create": {"limit": 30, "window": 60},  # 30 次/分钟
        "/api/followup/schedule": {"limit": 60, "window": 60},  # 60 次/分钟
        "/api/followup/log": {"limit": 100, "window": 60},  # 100 次/分钟
    }

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # 内存存储限流计数 (Redis 不可用时的降级方案)
        self._request_counts: Dict[str, Dict] = {}
        # 熔断器状态 (内存侧，Redis 不可用时使用)
        self._circuit_breakers: Dict[str, Dict] = {}
        # Redis 健康标记
        self._redis_available = True

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要跳过限流
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        try:
            # 获取客户端标识
            client_id = self._get_client_id(request)
            path = request.url.path

            # Redis 优先：检查熔断器
            circuit_open = await self._check_circuit_redis(path)
            if circuit_open is None:
                # Redis 不可用，降级内存
                circuit_open = self._is_circuit_open(path)
            if circuit_open:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="服务暂时不可用，请稍后重试"
                )

            # Redis 优先：检查限流
            allowed = await self._check_rate_limit_redis(client_id, path)
            if allowed is None:
                # Redis 不可用，降级内存
                allowed = self._check_rate_limit(client_id, path)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(self._get_limit(path)),
                        "X-RateLimit-Remaining": "0"
                    }
                )

            # Redis 优先：记录请求
            recorded = await self._record_request_redis(client_id, path)
            if recorded is None:
                # Redis 不可用，降级内存
                self._record_request(client_id, path)

        except HTTPException as e:
            logger.warning(f"限流检查：{e.detail}")
            raise e
        except Exception as e:
            logger.error(f"限流处理异常：{e}", exc_info=True)
            # 限流服务异常时不阻断请求

        return await call_next(request)

    # ---- Redis 路径（async） ----

    async def _check_rate_limit_redis(self, client_id: str, path: str) -> Optional[bool]:
        """
        使用 Redis INCR 做限流检查。
        返回 None 表示 Redis 不可用，调用方应降级为内存模式。
        """
        try:
            redis = get_redis()
            key = f"ratelimit:{client_id}:{path}"
            window = self._get_window(path)
            limit = self._get_limit(path)

            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, window)

            self._redis_available = True
            return current <= limit
        except Exception as e:
            logger.debug(f"Redis 限流检查失败: {e}")
            self._redis_available = False
            return None

    async def _record_request_redis(self, client_id: str, path: str) -> Optional[bool]:
        """
        在 Redis 中记录请求（INCR 已在 check 中完成，此处仅用于一致性）。
        返回 None 表示 Redis 不可用。
        """
        # INCR 已在 _check_rate_limit_redis 中完成计数，无需重复操作
        return True

    async def _check_circuit_redis(self, path: str) -> Optional[bool]:
        """
        使用 Redis 检查熔断器状态。
        返回 None 表示 Redis 不可用，调用方应降级为内存模式。
        """
        try:
            redis = get_redis()
            key = f"circuitbreaker:{path}"

            state = await redis.get(key)
            if state is None:
                self._redis_available = True
                return False

            data = json.loads(state)
            if not data.get("open", False):
                self._redis_available = True
                return False

            # 检查是否超过恢复时间
            open_until = data.get("open_until", 0)
            if time.time() > open_until:
                # 半开状态
                data["open"] = False
                data["state"] = "half-open"
                await redis.setex(key, 120, json.dumps(data))
                self._redis_available = True
                return False

            self._redis_available = True
            return True
        except Exception as e:
            logger.debug(f"Redis 熔断检查失败: {e}")
            self._redis_available = False
            return None

    def record_failure(self, path: str):
        """记录失败，用于熔断器逻辑。同时更新 Redis 和内存。"""
        # 更新内存
        self._record_failure_memory(path)

        # 尝试更新 Redis（失败时静默跳过）
        try:
            redis = get_redis()
            key = f"circuitbreaker:{path}"
            data = {"failures": 0, "open": False, "state": "closed"}
            raw = redis.get(key)
            if raw:
                data = json.loads(raw)
            data["failures"] += 1
            if data["failures"] >= 5:
                data["open"] = True
                data["open_until"] = time.time() + 30
                data["state"] = "open"
                logger.warning(f"熔断器打开：{path}")
            redis.set(key, json.dumps(data), ex=120)
        except Exception:
            pass

    def record_success(self, path: str):
        """记录成功，重置熔断器。同时更新 Redis 和内存。"""
        # 更新内存
        self._record_success_memory(path)

        # 尝试更新 Redis（失败时静默跳过）
        try:
            redis = get_redis()
            key = f"circuitbreaker:{path}"
            data = {"failures": 0, "open": False, "state": "closed"}
            redis.set(key, json.dumps(data), ex=120)
        except Exception:
            pass

    # ---- 同步路径（向后兼容 + 降级） ----

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """检查是否需要跳过限流"""
        path = request.url.path
        return path in self.SKIP_RATE_LIMIT_PATHS

    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用 tenant_id
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            return f"tenant:{tenant_id}"

        # 降级使用 IP 地址
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _get_limit(self, path: str) -> int:
        """获取路径对应的限流值"""
        # 精确匹配
        if path in self.API_LIMITS:
            return self.API_LIMITS[path]["limit"]

        # 前缀匹配
        for api_path, config in self.API_LIMITS.items():
            if path.startswith(api_path):
                return config["limit"]

        return self.DEFAULT_LIMIT

    def _get_window(self, path: str) -> int:
        """获取路径对应的窗口大小 (秒)"""
        if path in self.API_LIMITS:
            return self.API_LIMITS[path]["window"]
        return self.DEFAULT_WINDOW_SECONDS

    def _check_rate_limit(self, client_id: str, path: str) -> bool:
        """
        内存降级方案的限流检查。
        同步方法，向后兼容。
        """
        now = datetime.now()
        key = f"{client_id}:{path}"
        window = self._get_window(path)
        limit = self._get_limit(path)

        # 清理过期数据
        self._cleanup_old_records(client_id, window)

        # 获取请求计数
        if key not in self._request_counts:
            self._request_counts[key] = {"timestamps": [], "count": 0}

        record = self._request_counts[key]
        window_start = now - timedelta(seconds=window)

        # 计算窗口内请求数
        current_count = sum(
            1 for ts in record["timestamps"]
            if ts > window_start
        )

        return current_count < limit

    def _record_request(self, client_id: str, path: str):
        """内存模式记录请求"""
        now = datetime.now()
        key = f"{client_id}:{path}"

        if key not in self._request_counts:
            self._request_counts[key] = {"timestamps": [], "count": 0}

        self._request_counts[key]["timestamps"].append(now)
        self._request_counts[key]["count"] += 1

    def _cleanup_old_records(self, client_id: str, window: int):
        """清理过期的请求记录"""
        cutoff = datetime.now() - timedelta(seconds=window)

        for key in list(self._request_counts.keys()):
            if key.startswith(client_id):
                record = self._request_counts[key]
                record["timestamps"] = [
                    ts for ts in record["timestamps"] if ts > cutoff
                ]

    def _is_circuit_open(self, path: str) -> bool:
        """
        内存降级方案检查熔断器。
        同步方法，向后兼容。
        """
        if path not in self._circuit_breakers:
            return False

        breaker = self._circuit_breakers[path]
        if not breaker.get("open", False):
            return False

        # 检查是否超过熔断恢复时间
        if datetime.now() > breaker.get("open_until", datetime.now()):
            breaker["open"] = False
            breaker["state"] = "half-open"
            return False

        return True

    def _record_failure_memory(self, path: str):
        """内存模式记录失败"""
        if path not in self._circuit_breakers:
            self._circuit_breakers[path] = {
                "failures": 0,
                "open": False,
                "state": "closed"
            }

        breaker = self._circuit_breakers[path]
        breaker["failures"] += 1

        if breaker["failures"] >= 5:
            breaker["open"] = True
            breaker["open_until"] = datetime.now() + timedelta(seconds=30)
            breaker["state"] = "open"
            logger.warning(f"熔断器打开：{path}")

    def _record_success_memory(self, path: str):
        """内存模式记录成功"""
        if path in self._circuit_breakers:
            self._circuit_breakers[path]["failures"] = 0
            self._circuit_breakers[path]["open"] = False
            self._circuit_breakers[path]["state"] = "closed"
