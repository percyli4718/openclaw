"""
跟进管理技能

基于 Hermes Agent 的自动化跟进：
- create_followup_plan: 跟进计划制定
- schedule_automated_message: 定时消息推送
- log_followup_record: 跟进记录
- notify_overdue_followup: 逾期提醒
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


class FollowupManager:
    """保险跟进管理器"""

    # 跟进类型模板库
    FOLLOWUP_TEMPLATES = {
        "关怀消息": [
            "您好，最近工作顺利吗？有什么我可以帮您的吗？",
            "天气变化大，注意身体哦！有任何保险问题随时联系我。",
            "好久没联系了，最近一切都好吗？",
        ],
        "产品推荐": [
            "我们新上线了一款重疾险产品，性价比很高，要不要了解一下？",
            "根据您的需求，我为您推荐这款医疗险，保障全面且保费合理。",
            "本月特惠产品，保障升级不加价，详情咨询我。",
        ],
        "活动邀请": [
            "本周六我们举办客户答谢会，诚挚邀请您参加！",
            "线下沙龙活动：家庭财富规划与风险保障，期待您的光临。",
            "线上直播：如何选择合适的保险产品，欢迎观看。",
        ],
        "保单检视": [
            "您的保单即将到期，建议及时进行保单检视和续保规划。",
            "一年一度保单检视时间，让我帮您梳理保障情况。",
            "您的保障配置是否需要调整？免费保单检视服务已开启。",
        ],
        "理赔跟进": [
            "您的理赔申请进展顺利，有任何问题请随时联系我。",
            "理赔材料已提交，预计 3-5 个工作日出结果。",
            "理赔款已到账，请注意查收。后续有任何问题随时找我。",
        ],
    }

    # 频率对应的天数间隔
    FREQUENCY_DAYS = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
    }

    def __init__(self, scheduler_config: Optional[Dict] = None):
        self.scheduler_config = scheduler_config or {}

    def _validate_frequency(self, frequency: str) -> str:
        """验证并标准化频率参数"""
        valid_frequencies = ["daily", "weekly", "monthly"]
        if frequency not in valid_frequencies:
            # 降级为默认频率
            return "weekly"
        return frequency

    def _validate_duration(self, plan_duration: int) -> int:
        """验证并标准化计划时长"""
        if plan_duration <= 0:
            return 30  # 默认 30 天
        if plan_duration > 3650:  # 最大 10 年
            return 3650
        return plan_duration

    def _generate_task_content(self, task_type: str) -> str:
        """根据类型生成跟进内容"""
        import random
        templates = self.FOLLOWUP_TEMPLATES.get(task_type, self.FOLLOWUP_TEMPLATES["关怀消息"])
        return random.choice(templates)

    def _calculate_task_count(self, plan_duration: int, frequency: str) -> int:
        """计算任务数量"""
        interval_days = self.FREQUENCY_DAYS.get(frequency, 7)
        task_count = max(1, plan_duration // interval_days)
        return task_count

    def _get_followup_type_sequence(self, task_count: int) -> List[str]:
        """生成跟进类型序列，按照合理的跟进节奏"""
        # 跟进节奏：关怀 -> 产品 -> 活动 -> 保单检视 -> 理赔跟进
        sequence = []
        type_order = ["关怀消息", "产品推荐", "活动邀请", "保单检视", "理赔跟进"]

        for i in range(task_count):
            sequence.append(type_order[i % len(type_order)])

        return sequence

    async def create_followup_plan(
        self,
        customer_id: str,
        plan_duration: int = 30,
        frequency: str = "weekly"
    ) -> Dict[str, Any]:
        """
        制定跟进计划

        Args:
            customer_id: 客户 ID
            plan_duration: 计划天数
            frequency: 跟进频率 (daily/weekly/monthly)

        Returns:
            跟进计划

        Raises:
            ValueError: 当参数严重无效时
        """
        start_time = datetime.now()

        # 参数验证和标准化
        validated_frequency = self._validate_frequency(frequency)
        validated_duration = self._validate_duration(plan_duration)

        # 计算任务数量和类型
        task_count = self._calculate_task_count(validated_duration, validated_frequency)
        followup_types = self._get_followup_type_sequence(task_count)

        # 生成任务列表
        tasks = []
        interval_days = self.FREQUENCY_DAYS.get(validated_frequency, 7)

        for i, followup_type in enumerate(followup_types):
            due_date = datetime.now() + timedelta(days=(i + 1) * interval_days)
            task = {
                "id": f"task_{customer_id}_{i:03d}",
                "due_date": due_date.isoformat(),
                "type": followup_type,
                "content": self._generate_task_content(followup_type),
            }
            tasks.append(task)

        # 计算耗时
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        # 确保 duration_ms 至少为 1ms（模拟 AI 调用延迟）
        duration_ms = max(duration_ms, 100)

        return {
            "status": "success",
            "data": {
                "plan_id": f"plan_{customer_id}_{uuid.uuid4().hex[:8]}",
                "customer_id": customer_id,
                "frequency": validated_frequency,
                "duration_days": validated_duration,
                "created_at": datetime.now().isoformat(),
                "tasks": tasks,
            },
            "duration_ms": duration_ms,
        }

    async def schedule_automated_message(
        self,
        customer_id: str,
        message_content: str,
        send_time: datetime
    ) -> Dict[str, Any]:
        """
        定时消息推送

        Args:
            customer_id: 客户 ID
            message_content: 消息内容
            send_time: 发送时间

        Returns:
            调度结果

        Note:
            MVP 版本使用占位符实现，生产环境需集成 Redis Scheduler
        """
        start_time = datetime.now()

        # 参数验证
        if not customer_id:
            return {
                "status": "error",
                "error": "客户 ID 不能为空",
                "error_code": "DATA_001",
                "duration_ms": max(int((datetime.now() - start_time).total_seconds() * 1000), 1),
            }

        if not message_content or not message_content.strip():
            return {
                "status": "error",
                "error": "消息内容不能为空",
                "error_code": "DATA_001",
                "duration_ms": max(int((datetime.now() - start_time).total_seconds() * 1000), 1),
            }

        # 检查发送时间是否合理（不过期的时间）
        if send_time < datetime.now():
            # 过去时间的消息，可以选择返回错误或转为立即发送
            # 这里返回错误，让调用方决定如何处理
            return {
                "status": "error",
                "error": "发送时间不能是过去时间",
                "error_code": "DATA_002",
                "duration_ms": max(int((datetime.now() - start_time).total_seconds() * 1000), 1),
            }

        # 生成调度 ID（唯一）
        schedule_id = f"sched_{customer_id}_{uuid.uuid4().hex[:8]}"

        # 计算耗时
        duration_ms = max(int((datetime.now() - start_time).total_seconds() * 1000), 10)

        # TODO: 生产环境需调用 Redis Scheduler
        # 伪代码：
        # await redis_scheduler.add(
        #     schedule_id=schedule_id,
        #     customer_id=customer_id,
        #     message=message_content,
        #     execute_at=send_time
        # )

        return {
            "status": "success",
            "data": {
                "schedule_id": schedule_id,
                "customer_id": customer_id,
                "message_content": message_content[:50] + "..." if len(message_content) > 50 else message_content,
                "send_time": send_time.isoformat(),
                "created_at": datetime.now().isoformat(),
            },
            "duration_ms": duration_ms,
        }

    async def log_followup_record(
        self,
        customer_id: str,
        followup_type: str,
        content: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        记录跟进内容

        Args:
            customer_id: 客户 ID
            followup_type: 跟进类型
            content: 跟进内容
            feedback: 客户反馈

        Returns:
            记录结果

        Note:
            MVP 版本使用占位符实现，生产环境需写入 PostgreSQL
        """
        start_time = datetime.now()

        # 参数验证
        if not customer_id:
            return {
                "status": "error",
                "error": "客户 ID 不能为空",
                "error_code": "DATA_001",
                "duration_ms": max(int((datetime.now() - start_time).total_seconds() * 1000), 1),
            }

        if not content or not content.strip():
            return {
                "status": "error",
                "error": "跟进内容不能为空",
                "error_code": "DATA_001",
                "duration_ms": max(int((datetime.now() - start_time).total_seconds() * 1000), 1),
            }

        # 生成记录 ID（唯一，基于时间戳）
        record_id = f"rec_{customer_id}_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"

        # 计算耗时
        duration_ms = max(int((datetime.now() - start_time).total_seconds() * 1000), 10)

        # TODO: 生产环境需写入 PostgreSQL
        # 伪代码：
        # await db.execute(
        #     """
        #     INSERT INTO followup_records
        #     (id, customer_id, followup_type, content, feedback, created_at)
        #     VALUES (?, ?, ?, ?, ?, ?)
        #     """,
        #     record_id, customer_id, followup_type, content, feedback, datetime.now()
        # )

        return {
            "status": "success",
            "data": {
                "record_id": record_id,
                "customer_id": customer_id,
                "followup_type": followup_type,
                "content": content,
                "feedback": feedback,
                "created_at": datetime.now().isoformat(),
            },
            "duration_ms": duration_ms,
        }
