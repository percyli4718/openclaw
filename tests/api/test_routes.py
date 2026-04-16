"""
API 路由集成测试
"""

import pytest
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


class TestContentGenAPI:
    """内容生成 API 测试"""

    def test_content_gen_api(self, client):
        """测试内容生成 API 端点"""
        response = client.get("/api/v1/skills/content-gen")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestCustomerAPI:
    """客户分析 API 测试"""

    def test_customer_api(self, client):
        """测试客户分析 API 端点"""
        response = client.get("/api/v1/skills/customer")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestFollowupAPI:
    """跟进管理 API 测试"""

    def test_followup_api(self, client):
        """测试跟进管理 API 端点"""
        response = client.get("/api/v1/skills/followup")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAPIResponseFormat:
    """API 响应格式测试"""

    def test_response_format(self, client):
        """测试 API 响应格式一致性"""
        endpoints = [
            "/",
            "/api/v1/skills/content-gen",
            "/api/v1/skills/customer",
            "/api/v1/skills/followup"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
