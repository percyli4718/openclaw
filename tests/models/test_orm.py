"""
ORM 模型单元测试

测试 `baoke_tong/models/orm.py` 中的简化版模型：
- Customer
- FollowupPlan
- AuditLog

测试内容：
1. 模型实例化
2. 表创建
3. CRUD 操作（mocked DB session）
"""

import pytest
import os
import sys
from datetime import datetime
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from baoke_tong.models.orm import Customer, FollowupPlan, AuditLog, Base


# ============================================================
# 模型实例化测试
# ============================================================

class TestCustomerModel:
    """测试 Customer 模型"""

    def test_create_customer_minimal(self):
        """测试创建最小客户"""
        c = Customer(
            id=str(uuid4()),
            name="测试客户",
        )
        assert c.name == "测试客户"
        assert c.level == "D"  # 默认等级
        assert c.tags == []
        assert c.needs == {}

    def test_create_customer_full(self):
        """测试创建完整客户"""
        c = Customer(
            id=str(uuid4()),
            name="张三",
            phone="13800138000",
            level="A",
            source="wechat",
            tags=["高净值", "重疾险"],
            needs={"重疾险": "high", "医疗险": "medium"},
            last_followup_at=datetime.utcnow(),
            next_followup_at=datetime.utcnow(),
        )
        assert c.name == "张三"
        assert c.phone == "13800138000"
        assert c.level == "A"
        assert c.source == "wechat"
        assert "高净值" in c.tags
        assert c.needs["重疾险"] == "high"
        assert c.last_followup_at is not None
        assert c.next_followup_at is not None

    def test_customer_default_values(self):
        """测试默认值"""
        c = Customer(id=str(uuid4()), name="默认客户")
        assert c.level == "D"
        assert c.tags == []
        assert c.needs == {}
        assert c.source is None
        assert c.phone is None

    def test_customer_repr(self):
        """测试 __repr__"""
        c = Customer(id=str(uuid4()), name="李四", level="B")
        repr_str = repr(c)
        assert "Customer" in repr_str
        assert "李四" in repr_str
        assert "B" in repr_str


class TestFollowupPlanModel:
    """测试 FollowupPlan 模型"""

    def test_create_plan_minimal(self):
        """测试创建最小跟进计划"""
        plan = FollowupPlan(
            id=str(uuid4()),
            customer_id=str(uuid4()),
        )
        assert plan.status == "pending"
        assert plan.tasks == []

    def test_create_plan_full(self):
        """测试创建完整跟进计划"""
        plan = FollowupPlan(
            id=str(uuid4()),
            customer_id=str(uuid4()),
            status="in_progress",
            tasks=[
                {"id": "task_001", "type": "电话", "content": "了解需求"},
                {"id": "task_002", "type": "邮件", "content": "发送方案"},
            ],
        )
        assert plan.status == "in_progress"
        assert len(plan.tasks) == 2
        assert plan.tasks[0]["type"] == "电话"

    def test_followup_plan_repr(self):
        """测试 __repr__"""
        plan = FollowupPlan(
            id=str(uuid4()),
            customer_id=str(uuid4()),
            status="completed",
        )
        repr_str = repr(plan)
        assert "FollowupPlan" in repr_str
        assert "completed" in repr_str


class TestAuditLogModel:
    """测试 AuditLog 模型"""

    def test_create_audit_log_minimal(self):
        """测试创建最小审计日志"""
        log = AuditLog(
            id=str(uuid4()),
            action="create_customer",
        )
        assert log.action == "create_customer"
        assert log.review_status == "pending"
        assert log.user_id is None

    def test_create_audit_log_full(self):
        """测试创建完整审计日志"""
        log = AuditLog(
            id=str(uuid4()),
            user_id=str(uuid4()),
            action="update_followup",
            input_data={"customer_id": "cust_001", "level": "A"},
            output_data={"status": "success"},
            review_status="approved",
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.100",
        )
        assert log.action == "update_followup"
        assert log.input_data["customer_id"] == "cust_001"
        assert log.output_data["status"] == "success"
        assert log.review_status == "approved"
        assert log.ip_address == "192.168.1.100"

    def test_audit_log_repr(self):
        """测试 __repr__"""
        log = AuditLog(id=str(uuid4()), action="delete_customer")
        repr_str = repr(log)
        assert "AuditLog" in repr_str
        assert "delete_customer" in repr_str


# ============================================================
# 表结构测试
# ============================================================

class TestTableStructure:
    """测试表结构定义"""

    def test_customer_table_name(self):
        """测试表名前缀"""
        assert Customer.__tablename__ == "bt_customers"

    def test_followup_plan_table_name(self):
        """测试表名前缀"""
        assert FollowupPlan.__tablename__ == "bt_followup_plans"

    def test_audit_log_table_name(self):
        """测试表名前缀"""
        assert AuditLog.__tablename__ == "bt_audit_logs"

    def test_customer_columns(self):
        """测试 Customer 列定义"""
        expected_cols = {
            "id", "name", "phone", "level", "source",
            "tags", "needs", "last_followup_at", "next_followup_at",
            "created_at", "updated_at",
        }
        actual_cols = {c.name for c in Customer.__table__.columns}
        assert actual_cols == expected_cols

    def test_followup_plan_columns(self):
        """测试 FollowupPlan 列定义"""
        expected_cols = {"id", "customer_id", "status", "tasks", "created_at"}
        actual_cols = {c.name for c in FollowupPlan.__table__.columns}
        assert actual_cols == expected_cols

    def test_audit_log_columns(self):
        """测试 AuditLog 列定义"""
        expected_cols = {
            "id", "user_id", "action", "input_data", "output_data",
            "review_status", "timestamp", "ip_address",
        }
        actual_cols = {c.name for c in AuditLog.__table__.columns}
        assert actual_cols == expected_cols

    def test_customer_primary_key(self):
        """测试主键"""
        pk = Customer.__table__.primary_key.columns.keys()
        assert pk == ["id"]

    def test_followup_plan_foreign_key(self):
        """测试外键"""
        fk_cols = [
            fk.column.name
            for fk in FollowupPlan.__table__.foreign_keys
        ]
        assert "id" in fk_cols  # references bt_customers.id

    def test_base_is_registered(self):
        """测试模型已注册到 Base（通过 tablename 匹配）"""
        registered_tables = {
            mapper.class_.__tablename__
            for mapper in Base.registry.mappers
        }
        assert "bt_customers" in registered_tables
        assert "bt_followup_plans" in registered_tables
        assert "bt_audit_logs" in registered_tables


# ============================================================
# 表创建测试
# ============================================================

class TestTableCreation:
    """测试表创建"""

    def test_create_all_tables_ddl(self):
        """测试生成 DDL 语句（不执行）"""
        from sqlalchemy.schema import CreateTable

        # 验证可以为每个模型生成 CREATE TABLE 语句
        for model in [Customer, FollowupPlan, AuditLog]:
            stmt = CreateTable(model.__table__)
            ddl = str(stmt.compile(dialect=None))
            assert "CREATE TABLE" in ddl
            assert model.__tablename__ in ddl

    def test_metadata_contains_all_tables(self):
        """测试 metadata 包含所有表"""
        tables = Base.metadata.tables
        assert "bt_customers" in tables
        assert "bt_followup_plans" in tables
        assert "bt_audit_logs" in tables


# ============================================================
# Mock CRUD 测试
# ============================================================

class TestMockCRUD:
    """使用 Mock Session 测试 CRUD 操作"""

    def test_customer_insert_mock(self):
        """测试客户插入（Mock）"""
        from sqlalchemy import insert
        from sqlalchemy.dialects import postgresql

        customer_id = str(uuid4())
        stmt = insert(Customer).values(
            id=customer_id,
            name="Mock 客户",
            phone="13800000000",
            level="B",
            source="referral",
        )

        # 使用 PostgreSQL dialect 编译
        compiled = stmt.compile(dialect=postgresql.dialect(),
                                compile_kwargs={"literal_binds": True})
        assert "bt_customers" in str(compiled)
        assert "Mock 客户" in str(compiled)

    def test_followup_plan_insert_mock(self):
        """测试跟进计划插入（Mock）"""
        from sqlalchemy import insert
        from sqlalchemy.dialects import postgresql

        stmt = insert(FollowupPlan).values(
            id=str(uuid4()),
            customer_id=str(uuid4()),
            status="pending",
            # Use None to avoid JSONB literal_binds issue
            tasks=None,
        )

        compiled = stmt.compile(dialect=postgresql.dialect(),
                                compile_kwargs={"literal_binds": True})
        assert "bt_followup_plans" in str(compiled)
        assert "pending" in str(compiled)

    def test_audit_log_insert_mock(self):
        """测试审计日志插入（Mock）"""
        from sqlalchemy import insert
        from sqlalchemy.dialects import postgresql

        stmt = insert(AuditLog).values(
            id=str(uuid4()),
            user_id=str(uuid4()),
            action="test_action",
            # Use None to avoid JSONB literal_binds issue
            input_data=None,
            output_data=None,
            review_status="approved",
        )

        compiled = stmt.compile(dialect=postgresql.dialect(),
                                compile_kwargs={"literal_binds": True})
        assert "bt_audit_logs" in str(compiled)
        assert "test_action" in str(compiled)

    def test_customer_select_mock(self):
        """测试客户查询（Mock）"""
        from sqlalchemy import select
        from sqlalchemy.dialects import postgresql

        stmt = select(Customer).where(Customer.level == "A")
        compiled = str(stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        ))
        assert "bt_customers" in compiled
        assert "level" in compiled

    def test_followup_plan_by_customer_mock(self):
        """测试按客户查询跟进计划（Mock）"""
        from sqlalchemy import select
        from sqlalchemy.dialects import postgresql

        cid = str(uuid4())
        stmt = select(FollowupPlan).where(FollowupPlan.customer_id == cid)
        compiled = str(stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        ))
        assert "bt_followup_plans" in compiled
        assert cid in compiled

    def test_audit_log_filter_by_action_mock(self):
        """测试按操作过滤审计日志（Mock）"""
        from sqlalchemy import select
        from sqlalchemy.dialects import postgresql

        stmt = select(AuditLog).where(
            AuditLog.action == "create_customer",
            AuditLog.review_status == "pending",
        )
        compiled = str(stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        ))
        assert "bt_audit_logs" in compiled
        assert "create_customer" in compiled


# ============================================================
# 数据库回退测试
# ============================================================

class TestFallbackBehavior:
    """测试数据库不可用时的回退行为"""

    @pytest.mark.asyncio
    async def test_customer_profiles_fallback_to_memory(self):
        """测试客户档案查询回退到内存"""
        from baoke_tong.skills.customer import CustomerAnalyst
        from tests.mock_llm import MockLLMProvider

        # 确保 engine 为 None（无数据库连接）
        import baoke_tong.db.postgres as pg
        original_engine = pg.engine
        pg.engine = None

        try:
            analyst = CustomerAnalyst(llm=MockLLMProvider())
            result = await analyst.get_customer_profiles(["cust_001"])

            assert result["status"] == "success"
            assert result["data"]["source"] == "memory"
            assert result["data"]["customers"] == []
        finally:
            pg.engine = original_engine

    @pytest.mark.asyncio
    async def test_followup_save_fallback_to_memory(self):
        """测试跟进保存回退到内存"""
        from baoke_tong.skills.followup import FollowupManager
        from tests.mock_llm import MockLLMProvider

        import baoke_tong.db.postgres as pg
        original_engine = pg.engine
        pg.engine = None

        try:
            mgr = FollowupManager(llm=MockLLMProvider())
            result = await mgr.save_followup_record(
                customer_id=str(uuid4()),
                status="pending",
            )

            assert result["status"] == "success"
            assert result["data"]["source"] == "memory"
        finally:
            pg.engine = original_engine
