"""
租户上下文中间件测试
"""

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient
from starlette.responses import JSONResponse
from baoke_tong.middleware.tenant import TenantMiddleware


async def fake_call_next(request):
    return JSONResponse({"status": "ok"})


class TestSkipPaths:
    """跳过租户检查的路径测试（直接测试中间件逻辑）"""

    def test_skip_tenant_paths(self):
        middleware = TenantMiddleware(FakeApp())
        for path in ["/", "/api/health", "/docs", "/openapi.json"]:
            req = FakeRequest(path)
            assert middleware._should_skip_tenant_check(req) is True, f"路径 {path} 应该被跳过"

    def test_api_auth_paths_skipped(self):
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequest("/api/auth/login")
        assert middleware._should_skip_tenant_check(req) is True

    def test_api_paths_not_skipped(self):
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequest("/api/test")
        assert middleware._should_skip_tenant_check(req) is False


class TestMvpMode:
    """MVP 模式测试"""

    def test_api_path_gets_default_tenant(self):
        """MVP 模式下 API 路径获得默认 tenant_id"""
        _app = FastAPI()
        _app.add_middleware(TenantMiddleware)

        @_app.get("/api/test")
        async def test_endpoint(req: Request):
            return {"tenant_id": getattr(req.state, "tenant_id", None)}

        client = TestClient(_app)
        response = client.get("/api/test")
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "default_tenant"


class TestTenantExtraction:
    """租户 ID 提取测试"""

    def test_tenant_from_header(self):
        """从 X-Tenant-ID header 提取"""
        _app = FastAPI()
        _app.add_middleware(TenantMiddleware)

        @_app.get("/api/info")
        async def info_endpoint(req: Request):
            return {"tenant_id": getattr(req.state, "tenant_id", None)}

        client = TestClient(_app)
        response = client.get(
            "/api/info",
            headers={"X-Tenant-ID": "my_tenant_123"},
        )
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "my_tenant_123"

    def test_tenant_header_priority(self):
        """X-Tenant-ID header 优先"""
        _app = FastAPI()
        _app.add_middleware(TenantMiddleware)

        @_app.get("/api/info")
        async def info_endpoint(req: Request):
            return {"tenant_id": getattr(req.state, "tenant_id", None)}

        client = TestClient(_app)
        # 只提供 header，不设置 state
        response = client.get(
            "/api/info",
            headers={"X-Tenant-ID": "from_header"},
        )
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "from_header"

    def test_no_header_uses_default(self):
        """没有 header 时使用默认 tenant"""
        _app = FastAPI()
        _app.add_middleware(TenantMiddleware)

        @_app.get("/api/info")
        async def info_endpoint(req: Request):
            return {"tenant_id": getattr(req.state, "tenant_id", None)}

        client = TestClient(_app)
        response = client.get("/api/info")
        assert response.status_code == 200
        assert response.json()["tenant_id"] == "default_tenant"


class TestNonMvpMode:
    """非 MVP 模式测试"""

    def test_missing_tenant_raises_400(self):
        middleware = TenantMiddleware(FakeApp())
        middleware.mvp_mode = False
        req = FakeRequestWithHeaders("/api/test")
        import asyncio
        with pytest.raises(Exception) as exc_info:
            asyncio.get_event_loop().run_until_complete(
                middleware.dispatch(req, fake_call_next)
            )
        assert exc_info.value.status_code == 400
        assert "缺少" in str(exc_info.value.detail)

    def test_tenant_header_passes(self):
        """有 header 应该通过"""
        middleware = TenantMiddleware(FakeApp())
        middleware.mvp_mode = False
        req = FakeRequestWithHeaders("/api/test", headers={"X-Tenant-ID": "valid_tenant"})
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(req, fake_call_next)
        )
        assert result is not None
        assert req.state.tenant_id == "valid_tenant"


class TestTenantExtractionLogic:
    """测试 _extract_tenant_id 方法"""

    def test_from_header(self):
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequestWithHeaders("/api/test", headers={"X-Tenant-ID": "hdr_tenant"})
        result = middleware._extract_tenant_id(req)
        assert result == "hdr_tenant"

    def test_from_state(self):
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequestWithHeaders("/api/test", state_tenant="state_tenant")
        result = middleware._extract_tenant_id(req)
        assert result == "state_tenant"

    def test_header_priority_over_state(self):
        """Header 优先级高于 state"""
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequestWithHeaders(
            "/api/test",
            headers={"X-Tenant-ID": "hdr_tenant"},
            state_tenant="state_tenant",
        )
        result = middleware._extract_tenant_id(req)
        assert result == "hdr_tenant"

    def test_returns_none_if_not_found(self):
        middleware = TenantMiddleware(FakeApp())
        req = FakeRequestWithHeaders("/api/test")
        result = middleware._extract_tenant_id(req)
        assert result is None


class FakeApp:
    async def __call__(self, scope, receive, send):
        pass


class FakeRequest:
    def __init__(self, path: str):
        self.url = type("FakeURL", (), {"path": path})()


class FakeRequestWithHeaders:
    def __init__(self, path: str, headers: dict = None, state_tenant: str = None):
        self.url = type("FakeURL", (), {"path": path})()
        self.headers = headers or {}
        self.state = type("FakeState", (), {"tenant_id": state_tenant})()
