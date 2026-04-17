"""
合规审核 API 测试
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from baoke_tong.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestComplianceAPI:
    """合规审核 API 测试"""

    @pytest.mark.asyncio
    async def test_review_content(self, client):
        """测试内容合规审核"""
        mock_result = {
            "status": "success",
            "data": {
                "review_id": "test-uuid",
                "final_status": "approved",
                "sensitive_word_result": {"is_sensitive": False, "sensitive_words_found": []},
                "ai_review_result": {"review_result": "approved", "risk_score": 0.1},
                "requires_manual_review": False,
            },
            "audit_log": {},
            "duration_ms": 10,
        }
        with patch("baoke_tong.api.routes._compliance_reviewer") as mock:
            mock.review_content = AsyncMock(return_value=mock_result)
            response = client.post("/api/compliance/review", json={
                "content": "这是一条测试内容",
                "content_type": "copywriting",
                "product_name": "测试产品",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "final_status" in data["data"]

    @pytest.mark.asyncio
    async def test_audit_logs(self, client):
        """测试审计日志查询"""
        mock_logs = [{"audit_log": {"action": "review_content", "user_id": "anonymous"}}]
        with patch("baoke_tong.api.routes._compliance_reviewer") as mock:
            mock.get_audit_logs = MagicMock(return_value=mock_logs)
            response = client.post("/api/compliance/audit-logs", json={
                "user_id": "anonymous",
                "limit": 10,
            })
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total"] == 1

    @pytest.mark.asyncio
    async def test_list_sensitive_words(self, client):
        """测试敏感词列表"""
        with patch("baoke_tong.api.routes._compliance_reviewer") as mock:
            mock.sensitive_words = ["最", "第一", "保本"]
            response = client.get("/api/compliance/sensitive-words")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total"] == 3
            assert "最" in data["data"]["words"]

    @pytest.mark.asyncio
    async def test_add_sensitive_word(self, client):
        """测试添加敏感词"""
        with patch("baoke_tong.api.routes._compliance_reviewer") as mock:
            mock.add_sensitive_word = MagicMock()
            response = client.post("/api/compliance/sensitive-words/add", json={
                "word": "测试敏感词"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["action"] == "added"
            assert data["data"]["word"] == "测试敏感词"

    @pytest.mark.asyncio
    async def test_remove_sensitive_word(self, client):
        """测试移除敏感词"""
        with patch("baoke_tong.api.routes._compliance_reviewer") as mock:
            mock.remove_sensitive_word = MagicMock()
            response = client.post("/api/compliance/sensitive-words/remove", json={
                "word": "测试词"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["action"] == "removed"
