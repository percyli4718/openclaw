"""
保客通 (BaokeTong) 数据模型 - SQLAlchemy ORM

遵循 Design Spec Section 11：
- 多租户数据隔离（tenant_id + RLS）
- 敏感数据加密（AES-256）
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey,
    Text, Numeric, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
import os

Base = declarative_base()


# ============================================================
# 加密工具函数
# ============================================================

def get_encryption_key() -> str:
    """从环境变量获取加密密钥"""
    return os.environ.get(
        'ENCRYPTION_KEY',
        'baoke_tong_encryption_key_32bytes!'
    )


def encrypt_data(plain_text: str, encryption_key: str) -> bytes:
    """
    使用 Fernet 加密敏感数据
    """
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64

    # 从密钥派生 Fernet 密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'baoke_tong_salt',  # 生产环境应使用随机 salt
        iterations=100000,
    )
    derived_key = kdf.derive(encryption_key.encode())

    # Base64 编码为 Fernet 密钥
    fernet_key = base64.urlsafe_b64encode(derived_key)
    f = Fernet(fernet_key)
    return f.encrypt(plain_text.encode())


def decrypt_data(encrypted_data: bytes, encryption_key: str) -> str:
    """解密敏感数据"""
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'baoke_tong_salt',
        iterations=100000,
    )
    derived_key = kdf.derive(encryption_key.encode())
    fernet_key = base64.urlsafe_b64encode(derived_key)
    f = Fernet(fernet_key)
    return f.decrypt(encrypted_data).decode()


# ============================================================
# 租户模型
# ============================================================

class Tenant(Base):
    """租户模型"""
    __tablename__ = 'tenants'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, default=lambda: str(uuid4()))
    status: Mapped[str] = mapped_column(String(50), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    users = relationship('User', back_populates='tenant', cascade='all, delete-orphan')
    customers = relationship('Customer', back_populates='tenant', cascade='all, delete-orphan')
    followups = relationship('Followup', back_populates='tenant', cascade='all, delete-orphan')
    content_generations = relationship('ContentGeneration', back_populates='tenant', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='tenant', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name})>"


# ============================================================
# 用户模型
# ============================================================

class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default='user')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    tenant = relationship('Tenant', back_populates='users')
    owned_customers = relationship('Customer', back_populates='owner')
    followups = relationship('Followup', back_populates='user')
    content_generations = relationship('ContentGeneration', foreign_keys='ContentGeneration.user_id', back_populates='user')
    audit_logs = relationship('AuditLog', foreign_keys='AuditLog.user_id', back_populates='user')

    __table_args__ = (
        Index('idx_users_tenant_id', 'tenant_id'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


# ============================================================
# 客户模型（核心敏感数据）
# ============================================================

class Customer(Base):
    """
    客户模型

    敏感数据加密：
    - phone_encrypted: 手机号 AES-256 加密
    - id_card_encrypted: 身份证号 AES-256 加密
    - address_encrypted: 地址 AES-256 加密
    """
    __tablename__ = 'customers'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)

    # 基本信息
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 敏感数据（加密存储）
    _phone_encrypted: Mapped[bytes] = mapped_column('phone_encrypted', String, nullable=False)
    _id_card_encrypted: Mapped[Optional[bytes]] = mapped_column('id_card_encrypted', String)
    _address_encrypted: Mapped[Optional[bytes]] = mapped_column('address_encrypted', String)

    # 客户画像标签
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    segment: Mapped[Optional[str]] = mapped_column(String(50))  # high_value, medium_value, low_value
    occupation: Mapped[Optional[str]] = mapped_column(String(255))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(10))

    # 保险需求分析
    insurance_needs: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=list)
    risk_profile: Mapped[Optional[str]] = mapped_column(String(50))

    # 向量索引引用
    vector_id: Mapped[Optional[int]] = mapped_column(Integer)

    # 元数据
    source: Mapped[str] = mapped_column(String(50), default='manual')
    owner_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tenant = relationship('Tenant', back_populates='customers')
    owner = relationship('User', back_populates='owned_customers')
    followups = relationship('Followup', back_populates='customer', cascade='all, delete-orphan')

    # 混合属性：敏感数据自动加密/解密
    @hybrid_property
    def phone(self) -> str:
        """解密手机号"""
        return decrypt_data(self._phone_encrypted, get_encryption_key())

    @phone.setter
    def phone(self, value: str):
        """加密手机号"""
        self._phone_encrypted = encrypt_data(value, get_encryption_key())

    @hybrid_property
    def id_card(self) -> Optional[str]:
        """解密身份证号"""
        if self._id_card_encrypted:
            return decrypt_data(self._id_card_encrypted, get_encryption_key())
        return None

    @id_card.setter
    def id_card(self, value: str):
        """加密身份证号"""
        self._id_card_encrypted = encrypt_data(value, get_encryption_key()) if value else None

    @hybrid_property
    def address(self) -> Optional[str]:
        """解密地址"""
        if self._address_encrypted:
            return decrypt_data(self._address_encrypted, get_encryption_key())
        return None

    @address.setter
    def address(self, value: str):
        """加密地址"""
        self._address_encrypted = encrypt_data(value, get_encryption_key()) if value else None

    __table_args__ = (
        Index('idx_customers_tenant_id', 'tenant_id'),
        Index('idx_customers_segment', 'segment'),
        Index('idx_customers_owner', 'owner_id'),
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.name})>"


# ============================================================
# 跟进记录模型
# ============================================================

class Followup(Base):
    """客户跟进记录模型"""
    __tablename__ = 'followups'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)

    # 关联
    customer_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))

    # 跟进内容
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # call, message, meeting, note
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='completed')

    # 定时任务
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 客户反馈
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50))  # positive, neutral, negative

    # 元数据
    channel: Mapped[Optional[str]] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tenant = relationship('Tenant', back_populates='followups')
    customer = relationship('Customer', back_populates='followups')
    user = relationship('User', back_populates='followups')

    __table_args__ = (
        Index('idx_followups_tenant_id', 'tenant_id'),
        Index('idx_followups_customer', 'customer_id'),
        Index('idx_followups_user', 'user_id'),
        Index('idx_followups_scheduled', 'scheduled_at'),
        Index('idx_followups_status', 'status'),
    )

    def __repr__(self) -> str:
        return f"<Followup(id={self.id}, type={self.type})>"


# ============================================================
# 内容生成记录模型
# ============================================================

class ContentGeneration(Base):
    """AI 内容生成记录模型"""
    __tablename__ = 'content_generations'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)

    # 关联
    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))

    # 生成内容
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # wechat_copy, video_script, poster_copy
    input_params: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output_content: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # 质量评估
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)

    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 合规审核
    compliance_status: Mapped[str] = mapped_column(String(50), default='pending')
    compliance_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    compliance_reviewer_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系 - 使用 foreign_keys 明确指定外键
    tenant = relationship('Tenant', back_populates='content_generations')
    user = relationship('User', foreign_keys=[user_id], back_populates='content_generations')
    reviewer = relationship('User', foreign_keys=[compliance_reviewer_id])

    __table_args__ = (
        Index('idx_content_tenant_id', 'tenant_id'),
        Index('idx_content_type', 'type'),
        Index('idx_content_compliance', 'compliance_status'),
    )

    def __repr__(self) -> str:
        return f"<ContentGeneration(id={self.id}, type={self.type})>"


# ============================================================
# 审计日志模型
# ============================================================

class AuditLog(Base):
    """安全审计日志模型"""
    __tablename__ = 'audit_logs'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)

    # 操作信息
    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))

    # 请求详情
    request_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    response_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # 安全信息
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # 关系
    tenant = relationship('Tenant', back_populates='audit_logs')
    user = relationship('User', foreign_keys=[user_id], back_populates='audit_logs')

    __table_args__ = (
        Index('idx_audit_logs_tenant_id', 'tenant_id'),
        Index('idx_audit_logs_user', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"


# ============================================================
# 模型注册表
# ============================================================

MODELS = [
    Tenant,
    User,
    Customer,
    Followup,
    ContentGeneration,
    AuditLog,
]
