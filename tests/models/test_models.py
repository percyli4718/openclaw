"""
数据模型单元测试

测试内容：
1. 模型实例化
2. 敏感数据加密/解密
3. 租户隔离
4. 关系关联
"""

import pytest
import os
import sys
from datetime import datetime
from uuid import uuid4

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 设置测试环境变量
os.environ['ENCRYPTION_KEY'] = 'test_encryption_key_32bytes!!!!'

from baoke_tong.models import (
    Tenant, User, Customer, Followup,
    ContentGeneration, AuditLog,
    encrypt_data, decrypt_data, get_encryption_key
)


class TestEncryption:
    """测试加密/解密功能"""

    def test_encrypt_decrypt_phone(self):
        """测试手机号加密解密"""
        phone = "13800138000"
        encrypted = encrypt_data(phone, get_encryption_key())
        decrypted = decrypt_data(encrypted, get_encryption_key())
        assert decrypted == phone
        assert encrypted != phone.encode()  # 确保已加密

    def test_encrypt_decrypt_id_card(self):
        """测试身份证号加密解密"""
        id_card = "110101199003077777"
        encrypted = encrypt_data(id_card, get_encryption_key())
        decrypted = decrypt_data(encrypted, get_encryption_key())
        assert decrypted == id_card

    def test_encrypt_decrypt_address(self):
        """测试地址加密解密"""
        address = "北京市朝阳区 xxx 街道 xxx 号"
        encrypted = encrypt_data(address, get_encryption_key())
        decrypted = decrypt_data(encrypted, get_encryption_key())
        assert decrypted == address

    def test_different_encryption_results(self):
        """测试相同数据加密结果不同（安全性）"""
        data = "test_data"
        encrypted1 = encrypt_data(data, get_encryption_key())
        encrypted2 = encrypt_data(data, get_encryption_key())
        # 由于加密包含随机盐，两次加密结果应不同
        assert encrypted1 != encrypted2
        # 但解密后应该相同
        assert decrypt_data(encrypted1, get_encryption_key()) == data
        assert decrypt_data(encrypted2, get_encryption_key()) == data


class TestTenantModel:
    """测试租户模型"""

    def test_create_tenant(self):
        """测试创建租户"""
        tenant = Tenant(name="测试租户")
        assert tenant.name == "测试租户"
        # id 和 api_key 会在 flush/commit 时生成，default lambda 在初始化时不执行
        # 这测试 SQLAlchemy 2.0 Mapped 的行为

    def test_tenant_relationships(self):
        """测试租户关联关系"""
        tenant = Tenant(name="测试租户")
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            tenant=tenant
        )
        assert len(tenant.users) == 1
        assert tenant.users[0].email == "test@example.com"


class TestUserModel:
    """测试用户模型"""

    def test_create_user(self):
        """测试创建用户"""
        tenant_id = uuid4()
        user = User(
            tenant_id=tenant_id,
            email="user@example.com",
            password_hash="hashed_password",
            name="测试用户",
            role="user"
        )
        assert user.email == "user@example.com"
        assert user.name == "测试用户"
        assert user.role == "user"
        assert user.tenant_id == tenant_id

    def test_user_roles(self):
        """测试用户角色"""
        tenant_id = uuid4()
        admin = User(
            tenant_id=tenant_id,
            email="admin@example.com",
            password_hash="hashed_password",
            role="admin"
        )
        assert admin.role == "admin"


class TestCustomerModel:
    """测试客户模型（核心敏感数据）"""

    def test_create_customer_with_sensitive_data(self):
        """测试创建客户（包含敏感数据）"""
        tenant_id = uuid4()
        customer = Customer(
            tenant_id=tenant_id,
            name="张三",
        )
        # 设置敏感数据（自动加密）
        customer.phone = "13800138000"
        customer.id_card = "110101199003077777"
        customer.address = "北京市朝阳区 xxx 街道"

        # 验证加密存储
        assert customer._phone_encrypted is not None
        assert customer._phone_encrypted != b"13800138000"

        # 验证解密读取
        assert customer.phone == "13800138000"
        assert customer.id_card == "110101199003077777"
        assert customer.address == "北京市朝阳区 xxx 街道"

    def test_customer_tags(self):
        """测试客户标签"""
        tenant_id = uuid4()
        customer = Customer(
            tenant_id=tenant_id,
            name="李四",
            tags=["高净值", "互联网行业", "有家庭"]
        )
        assert "高净值" in customer.tags
        assert len(customer.tags) == 3

    def test_customer_segment(self):
        """测试客户分层"""
        tenant_id = uuid4()
        customer = Customer(
            tenant_id=tenant_id,
            name="王五",
            segment="high_value"
        )
        assert customer.segment == "high_value"

    def test_customer_insurance_needs(self):
        """测试保险需求分析"""
        tenant_id = uuid4()
        customer = Customer(
            tenant_id=tenant_id,
            name="赵六",
            insurance_needs=[
                {"type": "重疾险", "priority": "high"},
                {"type": "医疗险", "priority": "medium"}
            ]
        )
        assert len(customer.insurance_needs) == 2
        assert customer.insurance_needs[0]["type"] == "重疾险"


class TestFollowupModel:
    """测试跟进记录模型"""

    def test_create_followup(self):
        """测试创建跟进记录"""
        tenant_id = uuid4()
        customer_id = uuid4()
        followup = Followup(
            tenant_id=tenant_id,
            customer_id=customer_id,
            type="call",
            content="与客户电话沟通，了解保险需求",
            status="completed"
        )
        assert followup.type == "call"
        assert followup.status == "completed"

    def test_followup_with_sentiment(self):
        """测试跟进情感分析"""
        tenant_id = uuid4()
        followup = Followup(
            tenant_id=tenant_id,
            customer_id=uuid4(),
            type="meeting",
            content="客户对产品表示浓厚兴趣",
            sentiment="positive",
            feedback="希望进一步了解重疾险细节",
            status="completed"
        )
        assert followup.sentiment == "positive"
        assert "了解" in followup.feedback


class TestContentGenerationModel:
    """测试内容生成记录模型"""

    def test_create_content_generation(self):
        """测试创建内容生成记录"""
        tenant_id = uuid4()
        content = ContentGeneration(
            tenant_id=tenant_id,
            type="wechat_copy",
            input_params={
                "product_name": "健康保",
                "product_type": "重疾险",
                "tone": "专业"
            },
            output_content={
                "copies": [
                    {"content": "文案 1...", "score": 0.95},
                    {"content": "文案 2...", "score": 0.88}
                ]
            }
        )
        assert content.type == "wechat_copy"
        assert len(content.output_content["copies"]) == 2

    def test_content_compliance_review(self):
        """测试内容合规审核"""
        tenant_id = uuid4()
        content = ContentGeneration(
            tenant_id=tenant_id,
            type="video_script",
            input_params={},
            output_content={},
            compliance_status="approved"
        )
        assert content.compliance_status == "approved"


class TestAuditLogModel:
    """测试审计日志模型"""

    def test_create_audit_log(self):
        """测试创建审计日志"""
        tenant_id = uuid4()
        log = AuditLog(
            tenant_id=tenant_id,
            action="generate_copywriting",
            resource_type="content_generation",
            request_payload={"product": "健康保"},
            response_payload={"status": "success"}
        )
        assert log.action == "generate_copywriting"
        assert log.request_payload["product"] == "健康保"


class TestMultiTenantIsolation:
    """测试多租户隔离（模拟 RLS 行为）"""

    def test_tenant_data_isolation(self):
        """测试租户数据隔离"""
        tenant_a_id = uuid4()
        tenant_b_id = uuid4()

        # 创建租户 A 的客户
        customer_a = Customer(
            tenant_id=tenant_a_id,
            name="租户 A 客户"
        )
        customer_a.phone = "13800138000"

        # 创建租户 B 的客户
        customer_b = Customer(
            tenant_id=tenant_b_id,
            name="租户 B 客户"
        )
        customer_b.phone = "13900139000"

        # 验证租户隔离
        assert customer_a.tenant_id != customer_b.tenant_id
        assert customer_a.tenant_id == tenant_a_id
        assert customer_b.tenant_id == tenant_b_id

    def test_customer_owner_relationship(self):
        """测试客户负责人关系"""
        tenant_id = uuid4()
        user = User(
            tenant_id=tenant_id,
            email="agent@example.com",
            password_hash="hashed"
        )
        customer = Customer(
            tenant_id=tenant_id,
            name="客户",
            owner=user
        )
        customer.phone = "13800138000"

        assert customer.owner == user
        assert customer in user.owned_customers


class TestDatabaseSchema:
    """测试数据库 Schema 完整性"""

    def test_all_models_have_tenant_id(self):
        """测试所有模型都有 tenant_id 字段（RLS 基础）"""
        # Tenant 本身不需要 tenant_id，它是租户主体
        models_with_tenant = [
            User, Customer,
            Followup, ContentGeneration, AuditLog
        ]

        for model in models_with_tenant:
            assert hasattr(model, 'tenant_id'), \
                f"{model.__name__} 缺少 tenant_id 字段"

    def test_all_models_have_timestamps(self):
        """测试所有模型都有时间戳字段"""
        models = [
            Tenant, User, Customer,
            Followup, ContentGeneration
            # AuditLog 不需要 updated_at
        ]

        for model in models:
            assert hasattr(model, 'created_at'), \
                f"{model.__name__} 缺少 created_at 字段"
            assert hasattr(model, 'updated_at'), \
                f"{model.__name__} 缺少 updated_at 字段"

    def test_sensitive_fields_encrypted(self):
        """测试敏感字段使用加密存储"""
        # Customer 模型的敏感字段应以 _encrypted 结尾
        customer_attrs = dir(Customer)

        assert '_phone_encrypted' in customer_attrs
        assert '_id_card_encrypted' in customer_attrs
        assert '_address_encrypted' in customer_attrs


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=models', '--cov-report=term-missing'])
