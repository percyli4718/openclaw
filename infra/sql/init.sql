-- ============================================================
-- 保客通 (BaokeTong) 数据库初始化脚本
-- PostgreSQL 15+
-- ============================================================

-- 启用加密扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- 1. 基础表结构
-- ============================================================

-- 租户表
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(tenant_id, email)
);

-- 客户表（敏感数据加密）
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- 基本信息
    name VARCHAR(255) NOT NULL,

    -- 敏感数据加密存储（AES-256）
    phone_encrypted BYTEA NOT NULL,
    id_card_encrypted BYTEA,
    address_encrypted BYTEA,

    -- 客户画像标签（JSONB）
    tags JSONB DEFAULT '[]'::jsonb,
    segment VARCHAR(50), -- 客户分层：high_value, medium_value, low_value
    occupation VARCHAR(255),
    age INTEGER,
    gender VARCHAR(10),

    -- 保险需求分析
    insurance_needs JSONB DEFAULT '[]'::jsonb,
    risk_profile VARCHAR(50),

    -- 向量索引引用（Qdrant 中的向量 ID）
    vector_id BIGINT,

    -- 元数据
    source VARCHAR(50) DEFAULT 'manual', -- 来源：manual, import, api
    owner_id UUID REFERENCES users(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_customers_tenant_id (tenant_id),
    INDEX idx_customers_segment (segment),
    INDEX idx_customers_tags USING GIN(tags),
    INDEX idx_customers_owner (owner_id)
);

-- 跟进记录表
CREATE TABLE IF NOT EXISTS followups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- 关联
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),

    -- 跟进内容
    type VARCHAR(50) NOT NULL, -- 类型：call, message, meeting, note
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'completed', -- completed, pending, cancelled

    -- 定时任务
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- 客户反馈
    feedback TEXT,
    sentiment VARCHAR(50), -- positive, neutral, negative

    -- 元数据
    channel VARCHAR(50), -- wechat, phone, email, meeting
    priority INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_followups_tenant_id (tenant_id),
    INDEX idx_followups_customer (customer_id),
    INDEX idx_followups_user (user_id),
    INDEX idx_followups_scheduled (scheduled_at),
    INDEX idx_followups_status (status)
);

-- 内容生成记录表
CREATE TABLE IF NOT EXISTS content_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- 关联
    user_id UUID REFERENCES users(id),

    -- 生成内容
    type VARCHAR(50) NOT NULL, -- wechat_copy, video_script, poster_copy
    input_params JSONB NOT NULL,
    output_content JSONB NOT NULL,

    -- 质量评估
    quality_score DECIMAL(3,2),
    is_selected BOOLEAN DEFAULT FALSE,

    -- 使用统计
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- 合规审核
    compliance_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    compliance_reviewed_at TIMESTAMP WITH TIME ZONE,
    compliance_reviewer_id UUID REFERENCES users(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_content_tenant_id (tenant_id),
    INDEX idx_content_type (type),
    INDEX idx_content_compliance (compliance_status)
);

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,

    -- 操作信息
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,

    -- 请求详情
    request_payload JSONB,
    response_payload JSONB,

    -- 安全信息
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_audit_logs_tenant_id (tenant_id),
    INDEX idx_audit_logs_user (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_created (created_at)
);

-- ============================================================
-- 2. 加密函数（AES-256）
-- ============================================================

-- 加密函数
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(plain_text TEXT, encryption_key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(plain_text, encryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 解密函数
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data BYTEA, encryption_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_data, encryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- 3. 触发器函数（自动更新时间戳）
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加更新时间戳触发器
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_followups_updated_at
    BEFORE UPDATE ON followups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_generations_updated_at
    BEFORE UPDATE ON content_generations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 4. 行级安全策略 (RLS)
-- ============================================================

-- 启用 RLS
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE followups ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 租户隔离策略：租户只能访问自己的数据

-- tenants 表策略
CREATE POLICY tenant_isolation_tenants ON tenants
    FOR ALL
    USING (id = current_setting('app.current_tenant')::uuid);

-- users 表策略
CREATE POLICY tenant_isolation_users ON users
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- customers 表策略（核心敏感数据表）
CREATE POLICY tenant_isolation_customers ON customers
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- followups 表策略
CREATE POLICY tenant_isolation_followups ON followups
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- content_generations 表策略
CREATE POLICY tenant_isolation_content ON content_generations
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- audit_logs 表策略
CREATE POLICY tenant_isolation_audit ON audit_logs
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- ============================================================
-- 5. 应用层租户上下文设置函数
-- ============================================================

-- 设置当前租户（由 FastAPI 中间件调用）
CREATE OR REPLACE FUNCTION set_current_tenant(tenant_uuid UUID)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('SET LOCAL app.current_tenant = %L', tenant_uuid::text);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 获取当前租户
CREATE OR REPLACE FUNCTION get_current_tenant()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_tenant')::uuid;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 6. 初始化默认数据（仅用于开发/测试）
-- ============================================================

-- 插入默认租户（仅当不存在时）
INSERT INTO tenants (id, name, api_key)
SELECT
    '00000000-0000-0000-0000-000000000001'::uuid,
    '默认租户',
    'sk_dev_baoke_tong_default_api_key_change_in_production'
WHERE NOT EXISTS (SELECT 1 FROM tenants WHERE id = '00000000-0000-0000-0000-000000000001'::uuid);

-- 插入默认管理员用户（密码：admin123，仅用于开发/测试）
INSERT INTO users (id, tenant_id, email, password_hash, name, role)
SELECT
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000001'::uuid,
    'admin@baoke-tong.dev',
    crypt('admin123', gen_salt('bf')),
    '系统管理员',
    'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@baoke-tong.dev');

-- ============================================================
-- 7. 注释说明
-- ============================================================

COMMENT ON TABLE customers IS '客户信息表（敏感数据 AES-256 加密）';
COMMENT ON COLUMN customers.phone_encrypted IS '加密的手机号';
COMMENT ON COLUMN customers.id_card_encrypted IS '加密的身份证号';
COMMENT ON COLUMN customers.address_encrypted IS '加密的地址';
COMMENT ON COLUMN customers.segment IS '客户分层：high_value, medium_value, low_value';
COMMENT ON COLUMN customers.vector_id IS 'Qdrant 向量数据库中的向量 ID';

COMMENT ON TABLE followups IS '客户跟进记录表';
COMMENT ON COLUMN followups.sentiment IS '客户情感分析：positive, neutral, negative';

COMMENT ON TABLE content_generations IS 'AI 内容生成记录表';
COMMENT ON COLUMN content_generations.compliance_status IS '合规审核状态';

COMMENT ON TABLE audit_logs IS '安全审计日志表';
