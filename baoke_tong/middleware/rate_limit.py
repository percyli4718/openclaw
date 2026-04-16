"""
限流中间件

实现 API 限流和熔断机制，遵循 Design Spec Section 10.2 SLA 定义
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import time

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
        # 内存存储限流计数 (生产环境应使用 Redis)
        self._request_counts: Dict[str, Dict] = {}
        # 熔断器状态
        self._circuit_breakers: Dict[str, Dict] = {}

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要跳过限流
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        try:
            # 获取客户端标识
            client_id = self._get_client_id(request)
            path = request.url.path

            # 检查熔断器状态
            if self._is_circuit_open(path):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="服务暂时不可用，请稍后重试"
                )

            # 检查限流
            if not self._check_rate_limit(client_id, path):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(self._get_limit(path)),
                        "X-RateLimit-Remaining": "0"
                    }
                )

            # 记录请求
            self._record_request(client_id, path)

        except HTTPException as e:
            logger.warning(f"限流检查：{e.detail}")
            raise e
        except Exception as e:
            logger.error(f"限流处理异常：{e}", exc_info=True)
            # 限流服务异常时不阻断请求

        return await call_next(request)

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
        """检查是否超过限流"""
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
        """记录请求"""
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
        """检查熔断器是否打开"""
        if path not in self._circuit_breakers:
            return False

        breaker = self._circuit_breakers[path]
        if not breaker.get("open", False):
            return False

        # 检查是否超过熔断恢复时间
        if datetime.now() > breaker.get("open_until", datetime.now()):
            # 熔断器半开，允许一次探测请求
            breaker["open"] = False
            breaker["state"] = "half-open"
            return False

        return True

    def record_failure(self, path: str):
        """记录失败，用于熔断器逻辑"""
        if path not in self._circuit_breakers:
            self._circuit_breakers[path] = {
                "failures": 0,
                "open": False,
                "state": "closed"
            }

        breaker = self._circuit_breakers[path]
        breaker["failures"] += 1

        # 5 次失败后打开熔断器
        if breaker["failures"] >= 5:
            breaker["open"] = True
            breaker["open_until"] = datetime.now() + timedelta(seconds=30)
            breaker["state"] = "open"
            logger.warning(f"熔断器打开：{path}")

    def record_success(self, path: str):
        """记录成功，重置熔断器"""
        if path in self._circuit_breakers:
            self._circuit_breakers[path]["failures"] = 0
            self._circuit_breakers[path]["open"] = False
            self._circuit_breakers[path]["state"] = "closed"
