"""
租户上下文中间件

实现多租户隔离，通过中间件设置 tenant_id
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """租户上下文中间件"""

    # 跳过租户检查的路径
    SKIP_TENANT_PATHS = {
        "/",
        "/api/health",
        "/api/auth/login",
        "/api/auth/register",
        "/docs",
        "/openapi.json",
    }

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # MVP 模式：是否严格要求 tenant_id
        # MVP 阶段允许空 tenant_id，方便开发和测试
        self.mvp_mode = True

    async def dispatch(self, request: Request, call_next):
        # 检查是否需要跳过租户检查
        if self._should_skip_tenant_check(request):
            return await call_next(request)

        try:
            # 从多个来源获取 tenant_id
            tenant_id = self._extract_tenant_id(request)

            if tenant_id is None:
                # MVP 模式：生成一个默认 tenant_id
                if self.mvp_mode:
                    tenant_id = "default_tenant"
                else:
                    # 生产环境：如果没有 tenant_id，返回错误
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="缺少租户标识 (tenant_id)"
                    )

            # 将 tenant_id 存入 request state，供后续使用
            request.state.tenant_id = tenant_id

            # TODO: 生产环境需设置 PostgreSQL RLS 上下文
            # await self._set_postgres_tenant_context(tenant_id)

        except HTTPException as e:
            logger.warning(f"租户上下文设置失败：{e.detail}")
            raise e
        except Exception as e:
            logger.error(f"租户上下文处理异常：{e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="租户上下文服务异常"
            )

        return await call_next(request)

    def _should_skip_tenant_check(self, request: Request) -> bool:
        """检查是否需要跳过租户检查"""
        path = request.url.path
        return path in self.SKIP_TENANT_PATHS or path.startswith("/api/auth/")

    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """
        从多个来源提取 tenant_id

        优先级：
        1. X-Tenant-ID Header
        2. request.state (由认证中间件设置)
        3. JWT Token payload (由认证中间件解析)
        """
        # 从 Header 获取
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            logger.debug(f"从 Header 获取 tenant_id: {tenant_id}")
            return tenant_id

        # 从 request.state 获取（认证中间件已设置）
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            logger.debug(f"从 request.state 获取 tenant_id: {tenant_id}")
            return tenant_id

        return None

    async def _set_postgres_tenant_context(self, tenant_id: str):
        """
        设置 PostgreSQL RLS 上下文

        生产环境需实现：
        SET LOCAL app.current_tenant = 'tenant_id';
        """
        # TODO: 获取数据库连接并设置上下文
        # async with get_db_connection() as conn:
        #     await conn.execute(
        #         "SET LOCAL app.current_tenant = $1",
        #         tenant_id
        #     )
        pass
