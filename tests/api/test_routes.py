"""
API 路由集成测试

测试真实的 API 端点（非 stub）。
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from baoke_tong.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestHealthCheck:
    """健康检查测试"""

    def test_root_health(self, client):
        """测试根路径健康检查"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_endpoint(self, client):
        """测试 /health 端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_api_health(self, client):
        """测试 /api/health 端点"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestContentGenAPI:
    """内容生成 API 测试"""

    @pytest.mark.asyncio
    async def test_content_generate(self, client):
        """测试内容生成端点"""
        mock_result = {
            "status": "success",
            "data": {
                "copies": [
                    {"id": "copy_001", "content": "测试文案", "hashtags": ["保险"], "score": 0.85},
                ],
            },
            "duration_ms": 100,
        }

        with patch("baoke_tong.api.routes._content_generator") as mock_gen:
            mock_gen.generate_wechat_copywriting = AsyncMock(return_value=mock_result)

            response = client.post("/api/content/generate", json={
                "product_name": "健康保",
                "product_type": "重疾险",
                "target_audience": "25-40 岁白领",
                "tone": "专业",
                "count": 1,
            })

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "copies" in data["data"]

    def test_content_generate_validation(self, client):
        """测试请求体验证"""
        # 缺少必填字段
        response = client.post("/api/content/generate", json={})
        assert response.status_code == 422

        # count 超出范围
        response = client.post("/api/content/generate", json={
            "product_name": "健康保",
            "product_type": "重疾险",
            "count": 10,
        })
        assert response.status_code == 422

    def test_content_generate_invalid_enum(self, client):
        """测试无效枚举值"""
        response = client.post("/api/content/generate", json={
            "product_name": "健康保",
            "product_type": "无效类型",
        })
        assert response.status_code == 422


class TestCustomerAPI:
    """客户分析 API 测试"""

    @pytest.mark.asyncio
    async def test_customer_analyze(self, client):
        """测试客户画像分析"""
        mock_result = {
            "status": "success",
            "data": {
                "customer_id": "cust_001",
                "tags": ["中年", "高收入"],
                "risk_profile": "稳健型",
                "insurance_awareness": "高",
            },
            "duration_ms": 100,
        }

        with patch("baoke_tong.api.routes._customer_analyst") as mock_analyst:
            mock_analyst.analyze_customer_profile = AsyncMock(return_value=mock_result)

            response = client.post("/api/customer/analyze", json={
                "customer_id": "cust_001",
                "basic_info": {
                    "age": 35,
                    "occupation": "软件工程师",
                },
            })

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["customer_id"] == "cust_001"

    def test_customer_analyze_validation(self, client):
        """测试请求体验证"""
        response = client.post("/api/customer/analyze", json={})
        assert response.status_code == 422


class TestFollowupAPI:
    """跟进管理 API 测试"""

    @pytest.mark.asyncio
    async def test_followup_create(self, client):
        """测试创建跟进计划"""
        mock_result = {
            "status": "success",
            "data": {
                "plan_id": "plan_cust_001",
                "tasks": [
                    {"id": "task_001", "due_date": "2026-04-23", "type": "关怀消息", "content": "跟进"},
                ],
            },
            "duration_ms": 100,
        }

        with patch("baoke_tong.api.routes._followup_manager") as mock_mgr:
            mock_mgr.create_followup_plan = AsyncMock(return_value=mock_result)

            response = client.post("/api/followup/create", json={
                "customer_id": "cust_001",
                "plan_duration": 30,
                "frequency": "weekly",
            })

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "tasks" in data["data"]

    def test_followup_create_validation(self, client):
        """测试请求体验证"""
        # plan_duration 超出范围
        response = client.post("/api/followup/create", json={
            "customer_id": "cust_001",
            "plan_duration": 99999,
        })
        assert response.status_code == 422

        # 无效频率
        response = client.post("/api/followup/create", json={
            "customer_id": "cust_001",
            "frequency": "invalid",
        })
        assert response.status_code == 422


class TestAPIResponseFormat:
    """API 响应格式一致性测试"""

    def test_all_endpoints_return_json(self, client):
        """测试所有端点返回 JSON"""
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/api/health"),
        ]
        for method, path in endpoints:
            if method == "GET":
                response = client.get(path)
            assert response.headers["content-type"].startswith("application/json")

    def test_404_returns_json(self, client):
        """测试 404 返回 JSON 格式"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

    def test_405_returns_json(self, client):
        """测试 405 返回 JSON 格式"""
        response = client.post("/")
        assert response.status_code == 405
        assert "application/json" in response.headers["content-type"]
