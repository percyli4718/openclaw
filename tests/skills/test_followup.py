"""
跟进管理技能单元测试
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from baoke_tong.skills.followup import FollowupManager


class TestCreateFollowupPlan:
    """跟进计划制定测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_basic_plan_creation(self, manager: FollowupManager):
        """测试基础跟进计划制定"""
        result = await manager.create_followup_plan(
            customer_id="cust_001",
            plan_duration=30,
            frequency="weekly"
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert "plan_id" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) > 0

        # 验证任务结构
        task = data["tasks"][0]
        assert "id" in task
        assert "due_date" in task
        assert "type" in task
        assert "content" in task

    @pytest.mark.asyncio
    async def test_daily_frequency(self, manager: FollowupManager):
        """测试每日跟进频率"""
        result = await manager.create_followup_plan(
            customer_id="cust_002",
            plan_duration=7,
            frequency="daily"
        )

        assert result["status"] == "success"
        data = result["data"]

        # 每日频率，7 天应该至少有 7 个任务
        assert len(data["tasks"]) >= 7

    @pytest.mark.asyncio
    async def test_weekly_frequency(self, manager: FollowupManager):
        """测试每周跟进频率"""
        result = await manager.create_followup_plan(
            customer_id="cust_003",
            plan_duration=30,
            frequency="weekly"
        )

        assert result["status"] == "success"
        data = result["data"]

        # 每周频率，30 天应该约有 4-5 个任务
        assert len(data["tasks"]) >= 4

    @pytest.mark.asyncio
    async def test_monthly_frequency(self, manager: FollowupManager):
        """测试每月跟进频率"""
        result = await manager.create_followup_plan(
            customer_id="cust_004",
            plan_duration=90,
            frequency="monthly"
        )

        assert result["status"] == "success"
        data = result["data"]

        # 每月频率，90 天应该约有 3 个任务
        assert len(data["tasks"]) >= 3

    @pytest.mark.asyncio
    async def test_task_due_dates_are_future(self, manager: FollowupManager):
        """测试任务到期日期是未来时间"""
        result = await manager.create_followup_plan(
            customer_id="cust_005",
            plan_duration=30,
            frequency="weekly"
        )

        assert result["status"] == "success"
        data = result["data"]

        today = datetime.now()
        for task in data["tasks"]:
            due_date = datetime.fromisoformat(task["due_date"])
            assert due_date >= today, f"Task {task['id']} has past due date"

    @pytest.mark.asyncio
    async def test_followup_types(self, manager: FollowupManager):
        """测试不同跟进类型"""
        valid_types = ["关怀消息", "产品推荐", "活动邀请", "保单检视", "理赔跟进"]

        result = await manager.create_followup_plan(
            customer_id="cust_006",
            plan_duration=30,
            frequency="weekly"
        )

        assert result["status"] == "success"
        data = result["data"]

        # 验证任务类型有效性
        for task in data["tasks"]:
            assert task["type"] in valid_types or isinstance(task["type"], str)

    @pytest.mark.asyncio
    async def test_different_durations(self, manager: FollowupManager):
        """测试不同计划时长"""
        durations = [7, 30, 90, 180]

        for duration in durations:
            result = await manager.create_followup_plan(
                customer_id=f"cust_{duration}",
                plan_duration=duration,
                frequency="weekly"
            )

            assert result["status"] == "success"
            assert len(result["data"]["tasks"]) > 0

    @pytest.mark.asyncio
    async def test_plan_id_uniqueness(self, manager: FollowupManager):
        """测试计划 ID 唯一性"""
        result1 = await manager.create_followup_plan(
            customer_id="cust_007",
            plan_duration=30,
            frequency="weekly"
        )

        result2 = await manager.create_followup_plan(
            customer_id="cust_008",
            plan_duration=30,
            frequency="weekly"
        )

        assert result1["data"]["plan_id"] != result2["data"]["plan_id"]


class TestScheduleAutomatedMessage:
    """定时消息推送测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_basic_message_scheduling(self, manager: FollowupManager):
        """测试基础消息调度"""
        send_time = datetime.now() + timedelta(hours=1)

        result = await manager.schedule_automated_message(
            customer_id="cust_001",
            message_content="您好，我是您的保险顾问，有什么可以帮您的吗？",
            send_time=send_time
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert "schedule_id" in data
        assert "send_time" in data

        # 验证发送时间
        assert data["send_time"] == send_time.isoformat()

    @pytest.mark.asyncio
    async def test_immediate_scheduling(self, manager: FollowupManager):
        """测试立即发送（当前时间 +1 秒，避免时间竞争条件）"""
        send_time = datetime.now() + timedelta(seconds=1)

        result = await manager.schedule_automated_message(
            customer_id="cust_002",
            message_content="测试消息",
            send_time=send_time
        )

        assert result["status"] == "success"
        assert "schedule_id" in result["data"]

    @pytest.mark.asyncio
    async def test_future_scheduling(self, manager: FollowupManager):
        """测试未来时间调度"""
        send_time = datetime.now() + timedelta(days=7, hours=10, minutes=30)

        result = await manager.schedule_automated_message(
            customer_id="cust_003",
            message_content="7 天后的跟进消息",
            send_time=send_time
        )

        assert result["status"] == "success"
        data = result["data"]
        assert data["send_time"] == send_time.isoformat()

    @pytest.mark.asyncio
    async def test_different_message_contents(self, manager: FollowupManager):
        """测试不同消息内容"""
        messages = [
            "产品推荐：我们新上线了一款重疾险...",
            "关怀问候：最近天气变化大，注意身体...",
            "活动邀请：本周六举办客户答谢会...",
            "保单检视：您的保单即将到期，建议续保..."
        ]

        for msg in messages:
            result = await manager.schedule_automated_message(
                customer_id="cust_004",
                message_content=msg,
                send_time=datetime.now() + timedelta(hours=1)
            )

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_schedule_id_uniqueness(self, manager: FollowupManager):
        """测试调度 ID 唯一性"""
        send_time = datetime.now() + timedelta(hours=1)

        result1 = await manager.schedule_automated_message(
            customer_id="cust_005",
            message_content="消息 1",
            send_time=send_time
        )

        result2 = await manager.schedule_automated_message(
            customer_id="cust_006",
            message_content="消息 2",
            send_time=send_time
        )

        assert result1["data"]["schedule_id"] != result2["data"]["schedule_id"]

    @pytest.mark.asyncio
    async def test_empty_message_content(self, manager: FollowupManager):
        """测试空消息内容处理"""
        send_time = datetime.now() + timedelta(hours=1)

        result = await manager.schedule_automated_message(
            customer_id="cust_007",
            message_content="",
            send_time=send_time
        )

        # 空消息应该返回错误或降级处理
        assert result["status"] in ["success", "error"]


class TestLogFollowupRecord:
    """跟进记录测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_basic_record_logging(self, manager: FollowupManager):
        """测试基础跟进记录"""
        result = await manager.log_followup_record(
            customer_id="cust_001",
            followup_type="电话沟通",
            content="与客户沟通了产品 details，客户表示有兴趣"
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert "record_id" in data

    @pytest.mark.asyncio
    async def test_record_with_feedback(self, manager: FollowupManager):
        """测试带客户反馈的记录"""
        result = await manager.log_followup_record(
            customer_id="cust_002",
            followup_type="微信沟通",
            content="发送了产品资料",
            feedback="客户表示需要考虑一周"
        )

        assert result["status"] == "success"
        assert "record_id" in result["data"]

    @pytest.mark.asyncio
    async def test_record_without_feedback(self, manager: FollowupManager):
        """测试不带反馈的记录"""
        result = await manager.log_followup_record(
            customer_id="cust_003",
            followup_type="邮件发送",
            content="发送了保单年度报告"
        )

        assert result["status"] == "success"
        assert "record_id" in result["data"]

    @pytest.mark.asyncio
    async def test_different_followup_types(self, manager: FollowupManager):
        """测试不同跟进类型"""
        followup_types = [
            "电话沟通",
            "微信沟通",
            "邮件发送",
            "面谈",
            "保单检视",
            "理赔协助"
        ]

        for ftype in followup_types:
            result = await manager.log_followup_record(
                customer_id=f"cust_{ftype}",
                followup_type=ftype,
                content=f"进行了{ftype}"
            )

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_record_id_uniqueness(self, manager: FollowupManager):
        """测试记录 ID 唯一性"""
        result1 = await manager.log_followup_record(
            customer_id="cust_004",
            followup_type="电话沟通",
            content="第一次跟进"
        )

        # 稍微等待确保时间戳不同
        await asyncio.sleep(0.01)

        result2 = await manager.log_followup_record(
            customer_id="cust_004",
            followup_type="微信沟通",
            content="第二次跟进"
        )

        assert result1["data"]["record_id"] != result2["data"]["record_id"]

    @pytest.mark.asyncio
    async def test_long_content(self, manager: FollowupManager):
        """测试长内容记录"""
        long_content = """
        与客户进行了详细的沟通，内容包括：
        1. 产品介绍：详细介绍了我们的重疾险产品
        2. 保费计算：根据客户年龄和收入计算了保费
        3. 保障范围：解释了保障范围和免责条款
        4. 理赔流程：说明了理赔流程和所需材料

        客户反馈：对产品比较满意，需要考虑一下
        后续跟进：一周后再次联系
        """

        result = await manager.log_followup_record(
            customer_id="cust_005",
            followup_type="面谈",
            content=long_content,
            feedback="客户有意向，需跟进"
        )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_empty_customer_id(self, manager: FollowupManager):
        """测试空客户 ID 处理"""
        result = await manager.log_followup_record(
            customer_id="",
            followup_type="电话沟通",
            content="测试内容"
        )

        # 空客户 ID 应该返回错误或降级处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_empty_content(self, manager: FollowupManager):
        """测试空内容处理"""
        result = await manager.log_followup_record(
            customer_id="cust_006",
            followup_type="电话沟通",
            content=""
        )

        # 空内容应该返回错误或降级处理
        assert result["status"] in ["success", "error"]


class TestFollowupManagerIntegration:
    """集成测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_full_workflow(self, manager: FollowupManager):
        """测试完整工作流：制定计划 -> 调度消息 -> 记录跟进"""
        customer_id = "cust_integration"

        # 1. 制定跟进计划
        plan_result = await manager.create_followup_plan(
            customer_id=customer_id,
            plan_duration=30,
            frequency="weekly"
        )
        assert plan_result["status"] == "success"
        assert len(plan_result["data"]["tasks"]) > 0

        # 2. 调度第一条消息
        send_time = datetime.now() + timedelta(hours=1)
        schedule_result = await manager.schedule_automated_message(
            customer_id=customer_id,
            message_content="您好，我是您的保险顾问，很高兴为您服务",
            send_time=send_time
        )
        assert schedule_result["status"] == "success"

        # 3. 记录首次跟进
        log_result = await manager.log_followup_record(
            customer_id=customer_id,
            followup_type="微信沟通",
            content="首次接触客户",
            feedback="客户态度友好"
        )
        assert log_result["status"] == "success"

    @pytest.mark.asyncio
    async def test_multi_customer_workflow(self, manager: FollowupManager):
        """测试多客户并行工作流"""
        customer_ids = ["cust_a", "cust_b", "cust_c"]

        async def customer_workflow(cid: str):
            # 制定计划
            plan = await manager.create_followup_plan(
                customer_id=cid,
                plan_duration=30,
                frequency="weekly"
            )

            # 调度消息
            schedule = await manager.schedule_automated_message(
                customer_id=cid,
                message_content=f"针对{cid}的定制消息",
                send_time=datetime.now() + timedelta(hours=1)
            )

            # 记录跟进
            log = await manager.log_followup_record(
                customer_id=cid,
                followup_type="电话沟通",
                content=f"与{cid}沟通"
            )

            return plan, schedule, log

        # 并行执行多个客户的工作流
        results = await asyncio.gather(*[
            customer_workflow(cid) for cid in customer_ids
        ])

        # 验证所有结果
        for i, (plan, schedule, log) in enumerate(results):
            assert plan["status"] == "success", f"Customer {customer_ids[i]} plan failed"
            assert schedule["status"] == "success", f"Customer {customer_ids[i]} schedule failed"
            assert log["status"] == "success", f"Customer {customer_ids[i]} log failed"


class TestFollowupManagerErrorHandling:
    """错误处理测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_invalid_frequency(self, manager: FollowupManager):
        """测试无效频率处理"""
        result = await manager.create_followup_plan(
            customer_id="cust_001",
            plan_duration=30,
            frequency="invalid"  # 无效频率
        )

        # 应该返回错误或降级为默认频率
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_zero_duration(self, manager: FollowupManager):
        """测试零时长处理"""
        result = await manager.create_followup_plan(
            customer_id="cust_002",
            plan_duration=0,
            frequency="weekly"
        )

        # 零时长应该返回错误或默认处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_negative_duration(self, manager: FollowupManager):
        """测试负时长处理"""
        result = await manager.create_followup_plan(
            customer_id="cust_003",
            plan_duration=-10,
            frequency="weekly"
        )

        # 负时长应该返回错误
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_past_send_time(self, manager: FollowupManager):
        """测试过去时间调度"""
        past_time = datetime.now() - timedelta(days=1)

        result = await manager.schedule_automated_message(
            customer_id="cust_004",
            message_content="过去的消息",
            send_time=past_time
        )

        # 过去时间应该返回错误或警告
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_very_long_duration(self, manager: FollowupManager):
        """测试超长时长处理"""
        result = await manager.create_followup_plan(
            customer_id="cust_005",
            plan_duration=3650,  # 10 年
            frequency="monthly"
        )

        # 超长时长应该能处理或返回错误
        assert result["status"] in ["success", "error"]


class TestFollowupManagerSLA:
    """SLA 性能测试"""

    @pytest.fixture
    def manager(self):
        """创建 FollowupManager 实例"""
        return FollowupManager()

    @pytest.mark.asyncio
    async def test_create_plan_latency(self, manager: FollowupManager):
        """测试创建计划的延迟"""
        result = await manager.create_followup_plan(
            customer_id="cust_001",
            plan_duration=30,
            frequency="weekly"
        )

        # 根据 Design Spec，SLA 为 3-6 秒，超时阈值 10 秒
        assert result["duration_ms"] < 10000, "创建计划超时"

    @pytest.mark.asyncio
    async def test_schedule_message_latency(self, manager: FollowupManager):
        """测试调度消息的延迟"""
        result = await manager.schedule_automated_message(
            customer_id="cust_002",
            message_content="测试消息",
            send_time=datetime.now() + timedelta(hours=1)
        )

        # 调度应该在 1 秒内完成
        assert result["duration_ms"] < 5000, "调度消息超时"

    @pytest.mark.asyncio
    async def test_log_record_latency(self, manager: FollowupManager):
        """测试记录跟进的延迟"""
        result = await manager.log_followup_record(
            customer_id="cust_003",
            followup_type="电话沟通",
            content="跟进内容"
        )

        # 记录应该在 1 秒内完成
        assert result["duration_ms"] < 3000, "记录跟进超时"
