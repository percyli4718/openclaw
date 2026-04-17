"""
跟进管理技能测试
"""

import pytest
from datetime import datetime, timedelta
from baoke_tong.skills.followup import FollowupManager
from tests.mock_llm import MockLLMProvider


class TestFollowupManager:
    """跟进管理器测试"""

    def setup_method(self):
        """每个测试前的准备"""
        self.mock_llm = MockLLMProvider()
        self.manager = FollowupManager(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_create_followup_plan(self):
        """测试创建跟进计划"""
        self.mock_llm.set_responses([
            '{"tasks": [{"due_date": "2026-04-23", "type": "关怀消息", "content": "上周沟通的产品考虑得怎么样了？"}]}',
        ])
        result = await self.manager.create_followup_plan(
            customer_id="cust_001",
            plan_duration=30,
            frequency="weekly",
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "plan_id" in result["data"]
        assert "tasks" in result["data"]
        assert len(result["data"]["tasks"]) > 0

    @pytest.mark.asyncio
    async def test_create_daily_followup_plan(self):
        """测试创建每日跟进计划"""
        self.mock_llm.set_responses([
            '{"tasks": [{"due_date": "2026-04-17", "type": "关怀消息", "content": "您好！"}]}',
        ])
        result = await self.manager.create_followup_plan(
            customer_id="cust_002",
            plan_duration=7,
            frequency="daily",
        )

        assert result["status"] == "success"
        assert result["data"]["plan_id"] == "plan_cust_002"

    @pytest.mark.asyncio
    async def test_schedule_automated_message(self):
        """测试定时消息推送"""
        send_time = datetime.now() + timedelta(hours=1)
        result = await self.manager.schedule_automated_message(
            customer_id="cust_001",
            message_content="您好，上次聊的产品考虑得怎么样了？",
            send_time=send_time,
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "schedule_id" in result["data"]

    @pytest.mark.asyncio
    async def test_log_followup_record(self):
        """测试记录跟进内容"""
        result = await self.manager.log_followup_record(
            customer_id="cust_001",
            followup_type="call",
            content="与客户电话沟通，了解保险需求",
            feedback="客户对产品表示兴趣，需要进一步沟通",
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "record_id" in result["data"]

    @pytest.mark.asyncio
    async def test_log_followup_without_feedback(self):
        """测试记录跟进内容（无反馈）"""
        result = await self.manager.log_followup_record(
            customer_id="cust_002",
            followup_type="message",
            content="发送产品介绍资料",
        )

        assert result["status"] == "success"
        assert "record_id" in result["data"]


class TestFollowupManagerWithScheduler:
    """跟进管理器（带调度器）测试"""

    def setup_method(self):
        self.mock_llm = MockLLMProvider()
        self.manager = FollowupManager(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_create_plan_with_scheduler(self):
        """测试使用调度器创建计划"""
        self.mock_llm.set_responses([
            '{"tasks": [{"due_date": "2026-04-23", "type": "关怀消息", "content": "跟进"}]}',
        ])
        result = await self.manager.create_followup_plan(
            customer_id="cust_003",
            plan_duration=14,
            frequency="weekly",
        )

        assert result["status"] == "success"
        assert "plan_id" in result["data"]
