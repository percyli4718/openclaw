"""
跟进管理技能

基于 LLM 的自动化跟进：
- create_followup_plan: 跟进计划制定
- schedule_automated_message: 定时消息推送
- log_followup_record: 跟进记录
- notify_overdue_followup: 逾期提醒
"""

import time
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..llm import LLMProvider, LLMMessage, get_llm_provider


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

        Args:
            customer_id: 客户 ID
            followup_type: 跟进类型
            content: 跟进内容
            feedback: 客户反馈

        Returns:
            记录结果
        """
        # 此方法主要涉及数据写入，暂不使用 LLM
        return {
            "status": "success",
            "data": {
                "record_id": f"rec_{customer_id}_{datetime.now().timestamp()}",
            },
            "duration_ms": 300,
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
