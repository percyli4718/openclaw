"""
保客通 (BaokeTong) 技能层 ORM 模型

简化版客户/跟进/审计模型，用于 skills 层快速读写。
与 models/__init__.py 中的多租户综合模型互补，使用 `bt_` 前缀避免表名冲突。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

# 使用独立的 Base，避免与多租户综合模型冲突
Base = declarative_base()


# ============================================================
# 客户模型 (技能层)
# ============================================================

class Customer(Base):
    """
    客户模型 — 技能层简化版

    字段：
    - id: 主键 (UUID)
    - name: 姓名
    - phone: 电话 (明文存储，生产环境应加密)
    - level: 客户等级 (A/B/C/D)
    - source: 来源渠道
    - tags: 标签列表 (JSONB)
    - needs: 需求分析 (JSONB)
    - last_followup_at: 上次跟进时间
    - next_followup_at: 下次跟进时间
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = 'bt_customers'

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    level: Mapped[str] = mapped_column(String(10), default="D")  # A/B/C/D
    source: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    needs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    last_followup_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_followup_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Python-level defaults (mapped_column default only applies on flush)
        if self.level is None:
            self.level = "D"
        if self.tags is None:
            self.tags = []
        if self.needs is None:
            self.needs = {}

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.name}, level={self.level})>"


# ============================================================
# 跟进计划模型 (技能层)
# ============================================================

class FollowupPlan(Base):
    """
    跟进计划模型 — 技能层简化版

    字段：
    - id: 主键 (UUID)
    - customer_id: 客户 ID (外键)
    - status: 状态 (pending/in_progress/completed/cancelled)
    - tasks: 任务列表 (JSONB)
    - created_at: 创建时间
    """
    __tablename__ = 'bt_followup_plans'

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey('bt_customers.id', ondelete='CASCADE'), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    tasks: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.status is None:
            self.status = "pending"
        if self.tasks is None:
            self.tasks = []

    def __repr__(self) -> str:
        return f"<FollowupPlan(id={self.id}, customer_id={self.customer_id}, status={self.status})>"


# ============================================================
# 审计日志模型 (技能层)
# ============================================================

class AuditLog(Base):
    """
    审计日志模型 — 技能层简化版

    字段：
    - id: 主键 (UUID)
    - user_id: 操作用户 ID
    - action: 操作名称
    - input_data: 输入数据 (JSONB)
    - output_data: 输出数据 (JSONB)
    - review_status: 审核状态
    - timestamp: 操作时间
    - ip_address: IP 地址
    """
    __tablename__ = 'bt_audit_logs'

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    review_status: Mapped[str] = mapped_column(String(50), default="pending")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(INET)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.review_status is None:
            self.review_status = "pending"

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"
