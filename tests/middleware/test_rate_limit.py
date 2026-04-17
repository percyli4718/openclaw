"""
限流中间件测试
"""

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient
from baoke_tong.middleware.rate_limit import RateLimitMiddleware


class TestSkipPaths:
    """跳过限流的路径测试"""

    def test_skip_paths_logic(self):
        middleware = RateLimitMiddleware(FakeApp())
        for path in ["/", "/api/health", "/docs", "/openapi.json"]:
            req = FakeRequest(path)
            assert middleware._should_skip_rate_limit(req) is True, f"路径 {path} 应该被跳过"

    def test_api_paths_not_skipped(self):
        middleware = RateLimitMiddleware(FakeApp())
        req = FakeRequest("/api/test")
        assert middleware._should_skip_rate_limit(req) is False


class TestPerPathLimits:
    """不同路径不同限流配置"""

    def test_content_generate_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/content/generate") == 20

    def test_video_script_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/content/video-script") == 10

    def test_poster_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/content/poster") == 20

    def test_customer_analyze_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/customer/analyze") == 30

    def test_followup_schedule_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/followup/schedule") == 60

    def test_followup_log_limit(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/followup/log") == 100

    def test_default_limit_for_unknown(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_limit("/api/unknown") == 100

    def test_prefix_matching(self):
        """前缀匹配限流规则"""
        middleware = RateLimitMiddleware(FakeApp())
        limit = middleware._get_limit("/api/followup/log/extra")
        assert limit == 100


class TestWindowSize:
    """窗口大小测试"""

    def test_content_generate_window(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_window("/api/content/generate") == 60

    def test_default_window(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._get_window("/api/unknown") == 60


class TestRateLimiting:
    """限流功能测试"""

    def test_request_within_limit(self):
        """请求在限制范围内正常通过"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 5, "window": 60}}
        for _ in range(5):
            ok = middleware._check_rate_limit("c1", "/api/test")
            assert ok is True
            middleware._record_request("c1", "/api/test")

    def test_rate_limit_exceeded(self):
        """超限应该被拒绝"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 3, "window": 60}}
        # 前 3 次记录
        for _ in range(3):
            middleware._record_request("c1", "/api/test")
        # 第 4 次应该被拒绝
        assert middleware._check_rate_limit("c1", "/api/test") is False

    def test_rate_limit_per_client(self):
        """不同客户端独立限流"""
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 2, "window": 60}}
        middleware._record_request("client_a", "/api/test")
        middleware._record_request("client_a", "/api/test")
        # client_a 超限
        assert middleware._check_rate_limit("client_a", "/api/test") is False
        # client_b 仍然可以
        assert middleware._check_rate_limit("client_b", "/api/test") is True


class TestCircuitBreaker:
    """熔断器测试"""

    def test_circuit_closed_by_default(self):
        middleware = RateLimitMiddleware(FakeApp())
        assert middleware._is_circuit_open("/api/test") is False

    def test_open_circuit_after_5_failures(self):
        """5 次失败后熔断器打开"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(5):
            middleware.record_failure(path)
        assert middleware._is_circuit_open(path) is True

    def test_4_failures_not_open(self):
        """4 次失败不足以打开熔断器"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(4):
            middleware.record_failure(path)
        assert middleware._is_circuit_open(path) is False

    def test_record_success_resets_circuit(self):
        """记录成功重置熔断器"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(3):
            middleware.record_failure(path)
        middleware.record_success(path)
        for _ in range(2):
            middleware.record_failure(path)
        assert middleware._is_circuit_open(path) is False

    def test_circuit_breaker_state_values(self):
        """熔断器状态值验证"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        middleware.record_failure(path)
        assert middleware._circuit_breakers[path]["state"] == "closed"
        assert middleware._circuit_breakers[path]["failures"] == 1
        # 达到阈值
        for _ in range(4):
            middleware.record_failure(path)
        assert middleware._circuit_breakers[path]["state"] == "open"
        assert middleware._circuit_breakers[path]["open"] is True

    def test_circuit_breaker_open_until_set(self):
        """熔断器打开时设置恢复时间"""
        middleware = RateLimitMiddleware(FakeApp())
        path = "/api/test"
        for _ in range(5):
            middleware.record_failure(path)
        assert middleware._circuit_breakers[path]["open_until"] is not None


class TestClientId:
    """客户端标识提取测试"""

    def test_from_tenant_id(self):
        middleware = RateLimitMiddleware(FakeApp())
        req = FakeRequestWithState(tenant_id="t1")
        assert middleware._get_client_id(req) == "tenant:t1"

    def test_from_forwarded_for(self):
        middleware = RateLimitMiddleware(FakeApp())
        req = FakeRequestWithForwarded(forwarded="1.2.3.4, 5.6.7.8")
        assert middleware._get_client_id(req) == "ip:1.2.3.4"

    def test_from_client_ip(self):
        middleware = RateLimitMiddleware(FakeApp())
        req = FakeRequestWithClient(client_ip="192.168.1.1")
        assert middleware._get_client_id(req) == "ip:192.168.1.1"

    def test_from_unknown_client(self):
        middleware = RateLimitMiddleware(FakeApp())
        req = FakeRequestWithNoClient()
        assert middleware._get_client_id(req) == "ip:unknown"


class TestRequestRecording:
    """请求记录测试"""

    def test_record_and_count(self):
        middleware = RateLimitMiddleware(FakeApp())
        middleware._record_request("client1", "/api/test")
        middleware._record_request("client1", "/api/test")
        assert middleware._request_counts["client1:/api/test"]["count"] == 2

    def test_check_rate_limit_pass(self):
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 10, "window": 60}}
        for _ in range(9):
            middleware._record_request("client1", "/api/test")
        assert middleware._check_rate_limit("client1", "/api/test") is True

    def test_check_rate_limit_fail(self):
        middleware = RateLimitMiddleware(FakeApp())
        middleware.API_LIMITS = {"/api/test": {"limit": 3, "window": 60}}
        for _ in range(3):
            middleware._record_request("client1", "/api/test")
        assert middleware._check_rate_limit("client1", "/api/test") is False

    def test_cleanup_old_records(self):
        middleware = RateLimitMiddleware(FakeApp())
        middleware._request_counts["client1:/api/test"] = {"timestamps": [], "count": 5}
        middleware._cleanup_old_records("client1", 60)
        assert middleware._request_counts["client1:/api/test"]["timestamps"] == []


class FakeApp:
    async def __call__(self, scope, receive, send):
        pass


class FakeRequest:
    def __init__(self, path: str):
        self.url = type("FakeURL", (), {"path": path})()


class FakeRequestWithState:
    def __init__(self, tenant_id: str = None):
        self.url = type("FakeURL", (), {"path": "/api/test"})()
        self.client = None
        self.headers = {}
        self.state = type("FakeState", (), {"tenant_id": tenant_id})()


class FakeRequestWithForwarded:
    def __init__(self, forwarded: str):
        self.url = type("FakeURL", (), {"path": "/api/test"})()
        self.client = None
        self.headers = {"X-Forwarded-For": forwarded}
        self.state = type("FakeState", (), {"tenant_id": None})()


class FakeRequestWithClient:
    def __init__(self, client_ip: str):
        self.url = type("FakeURL", (), {"path": "/api/test"})()
        self.client = type("FakeClient", (), {"host": client_ip})()
        self.headers = {}
        self.state = type("FakeState", (), {"tenant_id": None})()


class FakeRequestWithNoClient:
    def __init__(self):
        self.url = type("FakeURL", (), {"path": "/api/test"})()
        self.client = None
        self.headers = {}
        self.state = type("FakeState", (), {"tenant_id": None})()
