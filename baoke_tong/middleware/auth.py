"""
认证鉴权中间件

实现 JWT Token 验证
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from jose import JWTError, jwt
from typing import Optional
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT 认证中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
        # JWT 配置 - 生产环境应从环境变量读取
        self.jwt_secret = settings.JWT_SECRET_KEY or "dev-secret-key-change-in-production"
        self.jwt_algorithm = "HS256"
        # 跳过认证的路径
        # MVP 版本：跳过所有 API 路径的认证，方便开发和测试
        # 生产环境应只跳过健康检查和认证接口
        self.skip_auth_paths = {
            "/",
            "/health",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
        # MVP 模式：是否跳过所有 API 认证
        self.mvp_mode = True

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要跳过认证
        if self._should_skip_auth(request):
            return await call_next(request)

        # 验证 JWT Token
        try:
            credentials = await self._get_credentials(request)
            if credentials is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未提供认证凭证",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 解析和验证 Token
            payload = self._verify_token(credentials.credentials)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token 无效或已过期",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 将用户信息存入 request state
            request.state.user_id = payload.get("sub")
            request.state.tenant_id = payload.get("tenant_id")
            request.state.username = payload.get("username")

        except HTTPException as e:
            logger.warning(f"认证失败：{e.detail}")
            raise e
        except Exception as e:
            logger.error(f"认证处理异常：{e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证服务异常"
            )

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """检查是否需要跳过认证"""
        path = request.url.path
        # MVP 模式：跳过所有 API 路径的认证
        if self.mvp_mode and path.startswith("/api/"):
            return True
        return path in self.skip_auth_paths or path.startswith("/api/auth/")

    async def _get_credentials(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        """获取认证凭证"""
        return await self.security(request)

    def _verify_token(self, token: str) -> Optional[dict]:
        """验证 JWT Token"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token 验证失败：{e}")
            return None
        except Exception as e:
            logger.error(f"Token 解析异常：{e}", exc_info=True)
            return None

    @staticmethod
    def create_token(
        user_id: str,
        username: str,
        tenant_id: str,
        expires_in: int = 3600
    ) -> str:
        """创建 JWT Token"""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "username": username,
            "tenant_id": tenant_id,
            "exp": now + timedelta(seconds=expires_in),
            "iat": now,
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY or "dev-secret-key-change-in-production",
            algorithm="HS256"
        )
