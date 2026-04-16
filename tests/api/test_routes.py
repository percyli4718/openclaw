"""
API 路由测试
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# 导入 app - 需要根据实际路径调整
import sys
sys.path.insert(0, '/data/tmp/baoke-tong/.worktrees/feature-mvp')

from baoke_tong.main import app

client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""

    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "baoke" in data["service"].lower() or "保客通" in data["service"]

    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestContentGeneration:
    """内容生成 API 测试"""

    def test_generate_wechat_copywriting_success(self):
        """测试朋友圈文案生成 - 成功场景"""
        payload = {
            "product_name": "健康保",
            "product_type": "重疾险",
            "tone": "专业",
            "count": 3
        }
        response = client.post("/api/content/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "copies" in data["data"]
        assert len(data["data"]["copies"]) == 3

    def test_generate_wechat_copywriting_invalid_product_type(self):
        """测试朋友圈文案生成 - 无效产品类型"""
        payload = {
            "product_name": "健康保",
            "product_type": "无效类型",
            "tone": "专业",
            "count": 3
        }
        response = client.post("/api/content/generate", json=payload)
        assert response.status_code == 200  # 技能层处理返回 error status
        data = response.json()
        assert data["status"] == "error"
        assert "error_code" in data

    def test_generate_wechat_copywriting_empty_product_name(self):
        """测试朋友圈文案生成 - 空产品名称"""
        payload = {
            "product_name": "",
            "product_type": "重疾险",
            "tone": "专业",
            "count": 3
        }
        response = client.post("/api/content/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"

    def test_generate_video_script(self):
        """测试短视频脚本生成"""
        payload = {
            "topic": "如何选择合适的重疾险",
            "duration": 30,
            "style": "科普"
        }
        response = client.post("/api/content/video-script", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "script" in data["data"]

    def test_generate_poster(self):
        """测试海报文案生成"""
        payload = {
            "product_name": "意外保",
            "selling_point": "全年保障，每天仅需 1 元",
            "cta": "立即咨询"
        }
        response = client.post("/api/content/poster", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "poster" in data["data"]


class TestCustomerAnalysis:
    """客户分析 API 测试"""

    def test_analyze_customer_profile_success(self):
        """测试客户画像分析 - 成功场景"""
        payload = {
            "customer_id": "cust_001",
            "basic_info": {
                "age": 35,
                "occupation": "软件工程师",
                "annual_income": 500000,
                "marital_status": "已婚",
                "children": 1
            }
        }
        response = client.post("/api/customer/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tags" in data["data"]

    def test_analyze_customer_profile_empty_customer_id(self):
        """测试客户画像分析 - 空客户 ID"""
        payload = {
            "customer_id": "",
            "basic_info": {"age": 35}
        }
        response = client.post("/api/customer/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"

    def test_analyze_customer_profile_invalid_age(self):
        """测试客户画像分析 - 无效年龄"""
        payload = {
            "customer_id": "cust_001",
            "basic_info": {
                "age": -1,  # 无效年龄
                "occupation": "工程师"
            }
        }
        response = client.post("/api/customer/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"

    def test_segment_customers(self):
        """测试客户分层"""
        payload = {
            "customer_ids": ["cust_001", "cust_002", "cust_003", "cust_004"]
        }
        response = client.post("/api/customer/segment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "segments" in data["data"]

    def test_predict_insurance_needs(self):
        """测试需求预测"""
        payload = {
            "customer_id": "cust_001",
            "profile": {
                "age": 35,
                "tags": ["中年", "高收入", "家庭支柱"],
                "insurance_awareness": "高"
            }
        }
        response = client.post("/api/customer/needs", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "needs" in data["data"]

    def test_search_similar_customers(self):
        """测试相似客户检索"""
        payload = {
            "customer_id": "cust_001",
            "limit": 5
        }
        response = client.post("/api/customer/search-similar", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestFollowupManagement:
    """跟进管理 API 测试"""

    def test_create_followup_plan(self):
        """测试创建跟进计划"""
        payload = {
            "customer_id": "cust_001",
            "plan_duration": 30,
            "frequency": "weekly"
        }
        response = client.post("/api/followup/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "plan_id" in data["data"]
        assert "tasks" in data["data"]

    def test_create_followup_plan_invalid_frequency(self):
        """测试创建跟进计划 - 无效频率"""
        payload = {
            "customer_id": "cust_001",
            "plan_duration": 30,
            "frequency": "invalid"  # 无效频率
        }
        response = client.post("/api/followup/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"  # 应该降级为默认频率

    def test_schedule_automated_message(self):
        """测试定时消息推送"""
        future_time = datetime.now() + timedelta(hours=1)
        payload = {
            "customer_id": "cust_001",
            "message_content": "您好，这是一条测试消息",
            "send_time": future_time.isoformat()
        }
        response = client.post("/api/followup/schedule", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "schedule_id" in data["data"]

    def test_schedule_automated_message_past_time(self):
        """测试定时消息推送 - 过去时间"""
        past_time = datetime.now() - timedelta(hours=1)
        payload = {
            "customer_id": "cust_001",
            "message_content": "您好，这是一条测试消息",
            "send_time": past_time.isoformat()
        }
        response = client.post("/api/followup/schedule", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"

    def test_log_followup_record(self):
        """测试跟进记录"""
        payload = {
            "customer_id": "cust_001",
            "followup_type": "关怀消息",
            "content": "客户表示对产品感兴趣",
            "feedback": "希望了解更多详情"
        }
        response = client.post("/api/followup/log", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "record_id" in data["data"]

    def test_log_followup_record_empty_content(self):
        """测试跟进记录 - 空内容"""
        payload = {
            "customer_id": "cust_001",
            "followup_type": "关怀消息",
            "content": ""  # 空内容
        }
        response = client.post("/api/followup/log", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"


class TestAuthentication:
    """认证接口测试"""

    def test_login_success(self):
        """测试登录 - 成功"""
        response = client.post("/api/auth/login", params={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_empty_username(self):
        """测试登录 - 空用户名"""
        response = client.post("/api/auth/login", params={
            "username": "",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"

    def test_login_empty_password(self):
        """测试登录 - 空密码"""
        response = client.post("/api/auth/login", params={
            "username": "testuser",
            "password": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"


class TestMiddleware:
    """中间件测试"""

    def test_cors_headers(self):
        """测试 CORS 头"""
        # CORS 中间件会在响应中添加 CORS 头
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        # 检查 CORS 头是否存在
        assert "access-control-allow-origin" in response.headers

    def test_rate_limit_headers(self):
        """测试限流头"""
        # 多次请求测试限流
        for i in range(5):
            response = client.get("/api/health")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
