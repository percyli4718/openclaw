"""
客户分析技能

基于 LLM 的保险客户画像分析：
- analyze_customer_profile: 客户画像分析
- segment_customers: 客户分层
- predict_insurance_needs: 需求预测
- search_similar_customers: 相似客户检索
- get_customer_profiles: 从数据库获取客户档案（新增）
"""

import time
import json
import re
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from ..llm import LLMProvider, LLMMessage, get_llm_provider

logger = logging.getLogger(__name__)


class CustomerAnalyst:
    """保险客户分析师"""

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

    async def analyze_customer_profile(
        self,
        customer_id: str,
        basic_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        分析客户画像

        Args:
            customer_id: 客户 ID
            basic_info: 基本信息 (年龄/职业/收入等)

        Returns:
            包含客户标签的字典
        """
        start = time.time()

        info_str = ", ".join(f"{k}: {v}" for k, v in basic_info.items())
        prompt = "\n".join([
            "你是一名资深保险客户分析师。请根据以下客户信息生成客户画像标签。",
            "",
            f"客户信息：{info_str}",
            "",
            "输出格式（JSON）：",
            '{"tags": ["...", "..."], "risk_profile": "稳健型/激进型/保守型", "insurance_awareness": "高/中/低"}',
        ])

        response = await self.llm.chat(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.3,
        )

        data = self._parse_profile(response.text)

        return {
            "status": "success",
            "data": {"customer_id": customer_id, **data},
            "duration_ms": int((time.time() - start) * 1000),
        }

    async def segment_customers(
        self,
        customer_ids: List[str],
        profiles: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        客户分层

        Args:
            customer_ids: 客户 ID 列表
            profiles: 可选的客户画像列表

        Returns:
            分层结果
        """
        start = time.time()

        profile_info = ""
        if profiles:
            profile_info = "\n" + "\n".join(
                f"客户 {cid}: {json.dumps(p, ensure_ascii=False)}"
                for cid, p in zip(customer_ids, profiles)
            )

        prompt = "\n".join([
            f"你是一名保险客户运营专家。请将以下 {len(customer_ids)} 位客户进行分层。",
            f"客户 ID: {', '.join(customer_ids)}",
            profile_info,
            "",
            "输出格式（JSON）：",
            '{"高价值": ["cust_001"], "潜力": ["cust_002"], "一般": ["cust_003"]}',
        ])

        response = await self.llm.chat(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.3,
        )

        segments = self._parse_segments(response.text)

        return {
            "status": "success",
            "data": {"segments": segments},
            "duration_ms": int((time.time() - start) * 1000),
        }

    async def predict_insurance_needs(
        self,
        customer_id: str,
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        预测保险需求

        Args:
            customer_id: 客户 ID
            profile: 客户画像

        Returns:
            需求预测结果
        """
        start = time.time()

        profile_str = json.dumps(profile, ensure_ascii=False)
        prompt = "\n".join([
            "你是一名保险需求分析师。请根据以下客户画像预测其保险需求。",
            "",
            f"客户画像：{profile_str}",
            "",
            "输出格式（JSON 数组）：",
            '[{"type": "重疾险", "priority": "高", "reason": "..."}]',
        ])

        response = await self.llm.chat(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.3,
        )

        needs = self._parse_needs(response.text)

        return {
            "status": "success",
            "data": {"customer_id": customer_id, "needs": needs},
            "duration_ms": int((time.time() - start) * 1000),
        }

    # ---- 解析辅助方法 ----

    @staticmethod
    def _parse_profile(text: str) -> dict:
        """解析客户画像 JSON"""
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "tags": data.get("tags", ["未知"]),
                    "risk_profile": data.get("risk_profile", "稳健型"),
                    "insurance_awareness": data.get("insurance_awareness", "中"),
                }
            except json.JSONDecodeError:
                pass
        return {
            "tags": ["未知"],
            "risk_profile": "稳健型",
            "insurance_awareness": "中",
        }

    @staticmethod
    def _parse_segments(text: str) -> dict:
        """解析分层结果 JSON"""
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {}

    @staticmethod
    def _parse_needs(text: str) -> list:
        """解析需求预测 JSON 数组"""
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                items = json.loads(match.group())
                if isinstance(items, list):
                    return items
            except json.JSONDecodeError:
                pass
        return []

    async def get_customer_profiles(
        self,
        customer_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        从数据库获取客户档案

        优先使用 PostgreSQL 数据，如果数据库不可用则回退到内存。

        Args:
            customer_ids: 客户 ID 列表。None 表示获取所有客户。

        Returns:
            客户档案列表
        """
        start = time.time()

        # 尝试从数据库获取
        db_customers = await self._get_customers_from_db(customer_ids)
        if db_customers is not None:
            return {
                "status": "success",
                "data": {"customers": db_customers, "source": "database"},
                "duration_ms": int((time.time() - start) * 1000),
            }

        # 回退到内存数据
        in_memory = self._get_customers_from_memory(customer_ids)
        return {
            "status": "success",
            "data": {"customers": in_memory, "source": "memory"},
            "duration_ms": int((time.time() - start) * 1000),
        }

    @staticmethod
    async def _get_customers_from_db(
        customer_ids: Optional[List[str]],
    ) -> Optional[List[Dict[str, Any]]]:
        """从数据库查询客户，失败时返回 None"""
        try:
            from ..db import engine
            from ..models.orm import Customer
            from sqlalchemy import select

            if engine is None:
                return None

            async with engine.connect() as conn:
                stmt = select(Customer)
                if customer_ids:
                    uuids = [UUID(cid) for cid in customer_ids]
                    stmt = stmt.where(Customer.id.in_(uuids))

                result = await conn.execute(stmt)
                rows = result.fetchall()
                return [
                    {
                        "id": str(row.Customer.id),
                        "name": row.Customer.name,
                        "phone": row.Customer.phone,
                        "level": row.Customer.level,
                        "source": row.Customer.source,
                        "tags": row.Customer.tags or [],
                        "needs": row.Customer.needs or {},
                        "last_followup_at": (
                            row.Customer.last_followup_at.isoformat()
                            if row.Customer.last_followup_at else None
                        ),
                        "next_followup_at": (
                            row.Customer.next_followup_at.isoformat()
                            if row.Customer.next_followup_at else None
                        ),
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.debug(f"数据库查询失败，回退到内存模式：{e}")
            return None

    @staticmethod
    def _get_customers_from_memory(
        customer_ids: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """从内存返回模拟数据"""
        # 这里可以接入 Redis 缓存或其他内存存储
        # 当前返回空列表表示内存模式无数据
        return []
