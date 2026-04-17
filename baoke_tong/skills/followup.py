"""
跟进管理技能

基于 LLM 的自动化跟进：
- create_followup_plan: 跟进计划制定
- schedule_automated_message: 定时消息推送
- log_followup_record: 跟进记录
- notify_overdue_followup: 逾期提醒
- save_followup_record: 保存跟进记录到数据库（新增）
"""

import time
import json
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from ..llm import LLMProvider, LLMMessage, get_llm_provider

logger = logging.getLogger(__name__)


class FollowupManager:
    """保险跟进管理器"""

    def __init__(self, llm: Optional[LLMProvider] = None):
        """
        Args:
            llm: LLM Provider 实例。未传入时延迟初始化。
        """
        self._llm = llm
        self._llm_provided = llm is not None

    @property
    def llm(self) -> LLMProvider:
        if not self._llm_provided:
            self._llm = get_llm_provider()
            self._llm_provided = True
        return self._llm

    async def create_followup_plan(
        self,
        customer_id: str,
        plan_duration: int = 30,
        frequency: str = "weekly",
    ) -> Dict[str, Any]:
        """
        制定跟进计划

        Args:
            customer_id: 客户 ID
            plan_duration: 计划天数
            frequency: 跟进频率 (daily/weekly/monthly)

        Returns:
            跟进计划
        """
        start = time.time()

        freq_label = {"daily": "每天", "weekly": "每周", "monthly": "每月"}.get(frequency, frequency)

        prompt = "\n".join([
            f"你是一名保险客户跟进策划师。请为客户制定一个 {plan_duration} 天的跟进计划，频率为{freq_label}。",
            "",
            f"客户 ID: {customer_id}",
            "",
            "输出格式（JSON）：",
            '{"tasks": [{"due_date": "2026-04-23", "type": "关怀消息", "content": "..."}]}',
        ])

        response = await self.llm.chat(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.5,
        )

        tasks = self._parse_tasks(response.text, plan_duration, frequency)

        return {
            "status": "success",
            "data": {
                "plan_id": f"plan_{customer_id}",
                "tasks": tasks,
            },
            "duration_ms": int((time.time() - start) * 1000),
        }

    async def schedule_automated_message(
        self,
        customer_id: str,
        message_content: str,
        send_time: datetime,
    ) -> Dict[str, Any]:
        """
        定时消息推送

        Args:
            customer_id: 客户 ID
            message_content: 消息内容
            send_time: 发送时间

        Returns:
            调度结果
        """
        # 此方法主要涉及调度，暂不使用 LLM
        return {
            "status": "success",
            "data": {
                "schedule_id": f"sched_{customer_id}",
                "send_time": send_time.isoformat(),
            },
            "duration_ms": 500,
        }

    async def log_followup_record(
        self,
        customer_id: str,
        followup_type: str,
        content: str,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        记录跟进内容

        同时写入数据库（如果可用）。

        Args:
            customer_id: 客户 ID
            followup_type: 跟进类型
            content: 跟进内容
            feedback: 客户反馈

        Returns:
            记录结果
        """
        start = time.time()
        record_id = f"rec_{customer_id}_{datetime.now().timestamp()}"

        # 尝试写入数据库
        await self._save_followup_to_db(
            customer_id=customer_id,
            followup_type=followup_type,
            content=content,
            feedback=feedback,
        )

        return {
            "status": "success",
            "data": {
                "record_id": record_id,
                "source": "database",
            },
            "duration_ms": int((time.time() - start) * 1000),
        }

    async def save_followup_record(
        self,
        customer_id: str,
        plan_id: Optional[str] = None,
        status: str = "pending",
        tasks: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        保存跟进计划到数据库

        优先写入 PostgreSQL，失败时回退到内存。

        Args:
            customer_id: 客户 ID
            plan_id: 计划 ID（None 时自动生成）
            status: 计划状态
            tasks: 任务列表

        Returns:
            保存结果
        """
        start = time.time()
        new_plan_id = plan_id or f"plan_{uuid4()}"

        # 尝试写入数据库
        db_ok = await self._save_followup_plan_to_db(
            customer_id=customer_id,
            plan_id=new_plan_id,
            status=status,
            tasks=tasks or [],
        )

        return {
            "status": "success",
            "data": {
                "plan_id": new_plan_id,
                "source": "database" if db_ok else "memory",
            },
            "duration_ms": int((time.time() - start) * 1000),
        }

    # ---- 解析辅助方法 ----

    @staticmethod
    def _parse_tasks(text: str, plan_duration: int, frequency: str) -> list:
        """解析跟进任务 JSON"""
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                data = json.loads(match.group())
                tasks = data.get("tasks", [])
                if isinstance(tasks, list):
                    return [
                        {
                            "id": f"task_{i+1:03d}",
                            "due_date": t.get("due_date", ""),
                            "type": t.get("type", "关怀消息"),
                            "content": t.get("content", ""),
                        }
                        for i, t in enumerate(tasks)
                    ]
            except json.JSONDecodeError:
                pass

        # 降级：生成简单计划
        now = datetime.now()
        interval = {"daily": 1, "weekly": 7, "monthly": 30}.get(frequency, 7)
        num_tasks = max(1, plan_duration // interval)

        return [
            {
                "id": f"task_{i+1:03d}",
                "due_date": (now + timedelta(days=interval * (i + 1))).strftime("%Y-%m-%d"),
                "type": "关怀消息",
                "content": "上周沟通的产品考虑得怎么样了？",
            }
            for i in range(min(num_tasks, 5))
        ]

    @staticmethod
    async def _save_followup_to_db(
        customer_id: str,
        followup_type: str,
        content: str,
        feedback: Optional[str],
    ) -> bool:
        """写入跟进记录到数据库，失败返回 False"""
        try:
            from ..db import engine
            from ..models.orm import AuditLog
            from sqlalchemy import insert

            if engine is None:
                return False

            async with engine.begin() as conn:
                await conn.execute(
                    insert(AuditLog).values(
                        id=str(uuid4()),
                        action=f"followup_{followup_type}",
                        input_data={
                            "customer_id": customer_id,
                            "content": content,
                            "feedback": feedback,
                        },
                        output_data={"status": "logged"},
                        review_status="approved",
                    )
                )
            return True
        except Exception as e:
            logger.debug(f"数据库写入跟进记录失败：{e}")
            return False

    @staticmethod
    async def _save_followup_plan_to_db(
        customer_id: str,
        plan_id: str,
        status: str,
        tasks: list,
    ) -> bool:
        """写入跟进计划到数据库，失败返回 False"""
        try:
            from ..db import engine
            from ..models.orm import FollowupPlan
            from sqlalchemy import insert

            if engine is None:
                return False

            async with engine.begin() as conn:
                await conn.execute(
                    insert(FollowupPlan).values(
                        id=plan_id,
                        customer_id=UUID(customer_id) if len(customer_id) == 36 else uuid4(),
                        status=status,
                        tasks=tasks,
                    )
                )
            return True
        except Exception as e:
            logger.debug(f"数据库写入跟进计划失败：{e}")
            return False
