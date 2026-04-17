"""
认证中间件测试
"""

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient
from starlette.responses import JSONResponse, Response
from baoke_tong.middleware.auth import AuthMiddleware
from datetime import datetime, timedelta, timezone
from jose import jwt


class TestTokenCreation:
    """JWT Token 创建和验证测试"""

    def test_create_token(self):
        token = AuthMiddleware.create_token(
            user_id="user_001",
            username="testuser",
            tenant_id="tenant_001",
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_expected_claims(self):
        secret = "dev-secret-key-change-in-production"
        token = AuthMiddleware.create_token(
            user_id="user_001",
            username="testuser",
            tenant_id="tenant_001",
        )
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        assert payload["sub"] == "user_001"
        assert payload["username"] == "testuser"
        assert payload["tenant_id"] == "tenant_001"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_expiry(self):
        token = AuthMiddleware.create_token(
            user_id="user_001",
            username="testuser",
            tenant_id="tenant_001",
            expires_in=3600,
        )
        secret = "dev-secret-key-change-in-production"
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        assert (exp - iat).total_seconds() == 3600

    def test_custom_expiry(self):
        token = AuthMiddleware.create_token(
            user_id="user_001",
            username="testuser",
            tenant_id="tenant_001",
            expires_in=7200,
        )
        secret = "dev-secret-key-change-in-production"
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        assert (exp - iat).total_seconds() == 7200


class TestMvpMode:
    """MVP 模式：/api/ 路径跳过认证"""

    def test_api_paths_skipped(self):
        """MVP 模式下 /api/ 路径跳过认证"""
        app = make_test_app(mvp_mode=True)
        with TestClient(app) as client:
            response = client.get("/api/test")
            assert response.status_code == 200
            assert response.json()["user_id"] is None

    def test_skip_path_works(self):
        """skip 路径在 MVP 模式正常工作（使用已知的 skip path）"""
        app = make_test_app(mvp_mode=True)
        with TestClient(app) as client:
            response = client.get("/docs")
            assert response.status_code == 200


class TestNonMvpMode:
    """非 MVP 模式测试（直接调用 dispatch 验证逻辑）"""

    def test_missing_token_raises_401(self):
        """没有 token 应该返回 401"""
        middleware, _, _ = make_middleware_and_state(mvp_mode=False)
        req = FakeRequest("/api/test", headers={})
        with pytest.raises(Exception) as exc_info:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                middleware.dispatch(req, fake_call_next)
            )
        assert exc_info.value.status_code == 401
        assert "未提供" in str(exc_info.value.detail)

    def test_invalid_token_raises_401(self):
        """无效 token 应该返回 401"""
        middleware, _, _ = make_middleware_and_state(mvp_mode=False)
        req = FakeRequest("/api/test", headers={"Authorization": "Bearer bad"})
        with pytest.raises(Exception) as exc_info:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                middleware.dispatch(req, fake_call_next)
            )
        assert exc_info.value.status_code == 401
        assert "无效" in str(exc_info.value.detail)

    def test_valid_token_sets_user(self):
        """有效 token 应该设置 user_id"""
        middleware, _, _ = make_middleware_and_state(mvp_mode=False)
        token = AuthMiddleware.create_token(
            user_id="user_001",
            username="testuser",
            tenant_id="tenant_001",
        )
        req = FakeRequest("/api/test", headers={"Authorization": f"Bearer {token}"})
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(req, fake_call_next)
        )
        assert req.state.user_id == "user_001"
        assert req.state.username == "testuser"

    def test_skip_path_bypasses(self):
        """docs 路径跳过认证"""
        middleware, _, _ = make_middleware_and_state(mvp_mode=False)
        req = FakeRequest("/docs", headers={})
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(req, fake_call_next)
        )
        assert result is not None

    def test_api_auth_paths_bypass(self):
        """/api/auth/ 路径跳过认证"""
        middleware, _, _ = make_middleware_and_state(mvp_mode=False)
        req = FakeRequest("/api/auth/login", headers={})
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            middleware.dispatch(req, fake_call_next)
        )
        assert result is not None


class TestShouldSkipAuth:
    """跳过认证路径判断逻辑"""

    def test_skip_auth_paths(self):
        middleware = AuthMiddleware(FakeApp())
        for path in ["/", "/health", "/api/health", "/docs", "/openapi.json", "/redoc"]:
            req = FakeRequest(path)
            assert middleware._should_skip_auth(req) is True, f"路径 {path} 应该被跳过"

    def test_api_paths_skipped_in_mvp(self):
        middleware = AuthMiddleware(FakeApp())
        middleware.mvp_mode = True
        req = FakeRequest("/api/anything")
        assert middleware._should_skip_auth(req) is True

    def test_api_paths_not_skipped_without_mvp(self):
        middleware = AuthMiddleware(FakeApp())
        middleware.mvp_mode = False
        req = FakeRequest("/api/something")
        assert middleware._should_skip_auth(req) is False

    def test_auth_paths_not_skipped(self):
        middleware = AuthMiddleware(FakeApp())
        req = FakeRequest("/api/test")
        middleware.mvp_mode = False
        assert middleware._should_skip_auth(req) is False


# ---- Helpers ----

def make_test_app(mvp_mode: bool = True):
    """创建测试应用"""
    from fastapi import Request as FastAPIRequest
    _app = FastAPI()

    if not mvp_mode:
        class StrictAuthMiddleware(AuthMiddleware):
            def __init__(self, app):
                super().__init__(app)
                self.mvp_mode = False
        _app.add_middleware(StrictAuthMiddleware)
    else:
        _app.add_middleware(AuthMiddleware)

    @_app.get("/api/test")
    async def test_endpoint(req: FastAPIRequest):
        return {
            "user_id": getattr(req.state, "user_id", None),
            "username": getattr(req.state, "username", None),
        }

    @_app.get("/skip")
    async def skip_endpoint():
        return {"status": "skipped"}

    return _app


def make_middleware_and_state(mvp_mode: bool = True):
    """创建中间件实例用于直接测试 dispatch"""
    middleware = AuthMiddleware(FakeApp())
    if not mvp_mode:
        middleware.mvp_mode = False
    return middleware, {}, {}


async def fake_call_next(request):
    return JSONResponse({"status": "ok"})


class FakeApp:
    async def __call__(self, scope, receive, send):
        pass


class FakeRequest:
    def __init__(self, path: str, headers: dict = None):
        self.url = type("FakeURL", (), {"path": path})()
        self.headers = headers or {}
        self.client = None
        self.state = type("FakeState", (), {})()
