"""
RLS 行级安全策略集成测试

使用 Testcontainers 启动真实的 PostgreSQL 容器
验证 RLS 策略是否正确生效

依赖：testcontainers[postgresql]
"""

import pytest
import os
from uuid import uuid4

# 跳过测试如果没有安装 testcontainers
testcontainers = pytest.importorskip("testcontainers.postgres")

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session


@pytest.fixture(scope="module")
def postgres_container():
    """启动 PostgreSQL 测试容器"""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def db_engine(postgres_container):
    """创建数据库引擎"""
    engine = create_engine(postgres_container.get_connection_url())

    # 读取并执行 init.sql
    init_sql_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'infra', 'sql', 'init.sql'
    )

    with open(init_sql_path, 'r', encoding='utf-8') as f:
        init_sql = f.read()

    with engine.connect() as conn:
        conn.execute(text(init_sql))
        conn.commit()

    return engine


@pytest.fixture
def session(db_engine) -> Session:
    """创建数据库会话"""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


def set_tenant_context(session: Session, tenant_id: str):
    """设置租户上下文（模拟应用层行为）"""
    session.execute(text(f"SET LOCAL app.current_tenant = '{tenant_id}'"))


class TestRLSPolicy:
    """测试 RLS 行级安全策略"""

    def test_rls_enabled_on_tables(self, session):
        """测试 RLS 已在表上启用"""
        result = session.execute(text("""
            SELECT tablename, rowsecurity
            FROM pg_tables
            WHERE schemaname = 'public'
            AND rowsecurity = true
        """))
        tables_with_rls = [row[0] for row in result.fetchall()]

        # 验证核心表已启用 RLS
        assert 'customers' in tables_with_rls
        assert 'users' in tables_with_rls
        assert 'followups' in tables_with_rls
        assert 'content_generations' in tables_with_rls
        assert 'audit_logs' in tables_with_rls

    def test_tenant_isolation_policy_exists(self, session):
        """测试租户隔离策略存在"""
        result = session.execute(text("""
            SELECT schemaname, tablename, policyname
            FROM pg_policies
            WHERE schemaname = 'public'
        """))
        policies = result.fetchall()

        # 验证每个表都有租户隔离策略
        policy_tables = [row[1] for row in policies]
        assert 'customers' in policy_tables
        assert 'users' in policy_tables

    def test_tenant_isolation_customers(self, session):
        """测试客户表租户隔离"""
        tenant_a_id = str(uuid4())
        tenant_b_id = str(uuid4())

        # 创建租户
        session.execute(text(f"""
            INSERT INTO tenants (id, name, api_key)
            VALUES ('{tenant_a_id}', '租户 A', 'key_a')
        """))
        session.execute(text(f"""
            INSERT INTO tenants (id, name, api_key)
            VALUES ('{tenant_b_id}', '租户 B', 'key_b')
        """))
        session.commit()

        # 租户 A 插入客户
        set_tenant_context(session, tenant_a_id)
        session.execute(text("""
            INSERT INTO customers (id, tenant_id, name, phone_encrypted)
            VALUES (gen_random_uuid(), :tenant_id, '客户 A',
                    pgp_sym_encrypt('13800138000', 'test_key'))
        """))
        session.commit()

        # 切换到租户 B，尝试查询租户 A 的数据
        set_tenant_context(session, tenant_b_id)
        result = session.execute(text("SELECT * FROM customers"))
        customers_b = result.fetchall()

        # 租户 B 应该看不到租户 A 的数据
        assert len(customers_b) == 0

        # 租户 B 插入自己的客户
        session.execute(text("""
            INSERT INTO customers (id, tenant_id, name, phone_encrypted)
            VALUES (gen_random_uuid(), :tenant_id, '客户 B',
                    pgp_sym_encrypt('13900139000', 'test_key'))
        """))
        session.commit()

        # 租户 B 只能看到自己的数据
        result = session.execute(text("SELECT * FROM customers"))
        customers_b = result.fetchall()
        assert len(customers_b) == 1

    def test_tenant_isolation_users(self, session):
        """测试用户表租户隔离"""
        tenant_a_id = str(uuid4())
        tenant_b_id = str(uuid4())

        # 创建租户
        session.execute(text(f"""
            INSERT INTO tenants (id, name, api_key)
            VALUES ('{tenant_a_id}', '租户 A', 'key_a')
        """))
        session.execute(text(f"""
            INSERT INTO tenants (id, name, api_key)
            VALUES ('{tenant_b_id}', '租户 B', 'key_b')
        """))
        session.commit()

        # 为租户 A 创建用户
        set_tenant_context(session, tenant_a_id)
        session.execute(text("""
            INSERT INTO users (id, tenant_id, email, password_hash)
            VALUES (gen_random_uuid(), :tenant_id, 'user_a@test.com', 'hashed')
        """))
        session.commit()

        # 切换到租户 B，尝试查询
        set_tenant_context(session, tenant_b_id)
        result = session.execute(text("SELECT * FROM users"))
        users_b = result.fetchall()

        # 租户 B 应该看不到租户 A 的用户
        assert len(users_b) == 0

    def test_set_current_tenant_function(self, session):
        """测试设置租户上下文函数"""
        tenant_id = str(uuid4())

        # 创建租户
        session.execute(text(f"""
            INSERT INTO tenants (id, name, api_key)
            VALUES ('{tenant_id}', '测试租户', 'test_key')
        """))
        session.commit()

        # 使用函数设置租户
        session.execute(text(f"SELECT set_current_tenant('{tenant_id}'::uuid)"))
        session.commit()

        # 验证上下文已设置
        result = session.execute(text("SELECT get_current_tenant()"))
        current_tenant = result.fetchone()[0]
        assert str(current_tenant) == tenant_id


class TestEncryptionFunctions:
    """测试数据库加密函数"""

    def test_encrypt_decrypt_functions(self, session):
        """测试加密/解密 SQL 函数"""
        phone = "13800138000"
        encryption_key = "test_encryption_key"

        # 测试加密
        result = session.execute(text("""
            SELECT pgp_sym_encrypt(:data, :key)
        """), {"data": phone, "key": encryption_key})
        encrypted = result.fetchone()[0]

        # 测试解密
        result = session.execute(text("""
            SELECT pgp_sym_decrypt(:encrypted, :key)
        """), {"encrypted": encrypted, "key": encryption_key})
        decrypted = result.fetchone()[0]

        assert decrypted == phone


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
