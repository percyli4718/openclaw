# 保客通 (BaokeTong) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 Hermes Agent 的 AI+ 保险获客系统，覆盖内容生成、客户画像、自动化跟进三大核心能力

**Architecture:** Python 3.11 + Hermes Agent + FastAPI + uni-app, Docker Compose 本地部署

**Tech Stack:** Python 3.11, Hermes Agent, FastAPI, uni-app (Vue 3 + TypeScript), PostgreSQL, Redis, Qdrant, Docker Compose

---

## File Structure Overview

```
baoke-tong/
├── frontend/                    # uni-app 前端
│   ├── src/
│   │   ├── pages/              # 页面
│   │   │   ├── index/          # 首页
│   │   │   ├── content-gen/    # 获客内容生成
│   │   │   ├── customer/       # 客户管理
│   │   │   └── followup/       # 跟进管理
│   │   ├── components/         # 组件
│   │   ├── services/           # API 服务
│   │   ├── stores/             # Pinia 状态管理
│   │   └── utils/              # 工具函数
│   ├── manifest.json           # uni-app 配置
│   └── pages.json              # 页面路由配置
├── backend/                     # Hermes Agent 后端
│   ├── baoke_tong/
│   │   ├── skills/             # 保险行业技能
│   │   │   ├── content_gen.py  # 内容生成技能
│   │   │   ├── customer.py     # 客户分析技能
│   │   │   └── followup.py     # 跟进管理技能
│   │   ├── tools/              # 工具注册表
│   │   ├── memory/             # 记忆系统
│   │   ├── config/             # 配置管理
│   │   └── main.py             # 服务入口
│   ├── api/                    # FastAPI 路由
│   ├── models/                 # 数据模型
│   └── tests/                  # 测试
├── infra/                       # 基础设施配置
│   ├── docker-compose.yml       # SaaS 部署
│   └── docker-compose.private.yml  # 私有化部署
├── docs/                        # 文档
│   ├── plans/                   # 本计划目录
│   ├── specs/                   # Design Spec
│   └── interview/               # 面试演示脚本
└── scripts/                     # 辅助脚本
    ├── init-data.sh
    └── demo.sh
```

---

## Phase 1: Hermes Agent 核心技能（预计 4 小时）

### Task 1.1: 内容生成技能实现

**Files:**
- `baoke_tong/skills/content_gen.py` (已创建框架)
- `tests/skills/test_content_gen.py`

- [ ] **Step 1: 实现朋友圈文案生成**

```python
async def generate_wechat_copywriting(
    self,
    product_name: str,
    product_type: str,
    target_audience: Optional[str] = None,
    tone: str = "专业",
    count: int = 3
) -> Dict[str, Any]:
    # 调用 Hermes Agent 技能执行
    # 输入输出 Schema 遵循 Design Spec Section 10
```

Expected: 返回 3 条文案，每条包含 content/hashtags/score

- [ ] **Step 2: 实现短视频脚本生成**
- [ ] **Step 3: 实现海报文案生成**
- [ ] **Step 4: 添加单元测试**

```python
# tests/skills/test_content_gen.py
async def test_generate_wechat_copywriting():
    generator = ContentGenerator()
    result = await generator.generate_wechat_copywriting(
        product_name="健康保",
        product_type="重疾险",
        tone="专业",
        count=3
    )
    assert result["status"] == "success"
    assert len(result["data"]["copies"]) == 3
```

---

## Phase 2: 客户分析技能（预计 3 小时）

### Task 2.1: 客户画像分析

**Files:**
- `baoke_tong/skills/customer.py` (已创建框架)
- `tests/skills/test_customer.py`

- [ ] **Step 1: 实现客户画像分析**
- [ ] **Step 2: 实现客户分层**
- [ ] **Step 3: 实现需求预测**
- [ ] **Step 4: 添加单元测试**

---

## Phase 3: 跟进管理技能（预计 3 小时）

### Task 3.1: 自动化跟进

**Files:**
- `baoke_tong/skills/followup.py` (已创建框架)
- `tests/skills/test_followup.py`

- [ ] **Step 1: 实现跟进计划制定**
- [ ] **Step 2: 实现定时消息推送**
- [ ] **Step 3: 实现跟进记录**
- [ ] **Step 4: 添加单元测试**

---

## Phase 4: 数据库基础设施（预计 2 小时）

### Task 4.1: PostgreSQL + RLS

**Files:**
- `infra/docker-compose.yml`
- `backend/models/customer.py`

- [ ] **Step 1: 配置 Docker Compose**

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: baoke_tong
      POSTGRES_USER: baoke
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
```

- [ ] **Step 2: 实现 RLS (Row-Level Security)**

```sql
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON customers
    FOR ALL USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

---

## Phase 5: FastAPI 接口层（预计 2 小时）

### Task 5.1: API 路由

**Files:**
- `backend/api/routes.py`
- `backend/main.py`

- [ ] **Step 1: 创建内容生成 API**
- [ ] **Step 2: 创建客户分析 API**
- [ ] **Step 3: 创建跟进管理 API**
- [ ] **Step 4: 添加认证中间件**

---

## Phase 6: uni-app 前端（预计 8 小时）

### Task 6.1: 项目脚手架

**Files:**
- `frontend/manifest.json`
- `frontend/pages.json`

- [ ] **Step 1: 初始化 uni-app 项目**
- [ ] **Step 2: 配置 uView UI**
- [ ] **Step 3: 创建首页**
- [ ] **Step 4: 创建内容生成页面**

### Task 6.2: UI 状态矩阵实现

- [ ] **Step 1: 内容生成模块 5 状态**
  - Loading: 骨架屏 + 进度条
  - Empty: 引导文案 + 示例
  - Success: 文案卡片展示
  - Error: 错误提示 + 重试
  - Partial: 部分成功处理

- [ ] **Step 2: 客户画像模块 5 状态**
- [ ] **Step 3: 跟进管理模块 5 状态**

---

## Phase 7: 合规审核工作流（预计 2 小时）

### Task 7.1: 话术合规审核

**Files:**
- `baoke_tong/skills/compliance.py`

- [ ] **Step 1: 敏感词过滤**
- [ ] **Step 2: AI 语义审核**
- [ ] **Step 3: 审计日志记录**

---

## Phase 8: 测试与质量门禁（预计 3 小时）

### Task 8.1: 单元测试

- [ ] **Step 1: 技能单元测试 (>85% 覆盖率)**
- [ ] **Step 2: 集成测试 (Testcontainers)**
- [ ] **Step 3: E2E 测试 (Playwright)**

---

## Phase 9: 部署与发布（预计 1 小时）

### Task 9.1: Docker Compose 部署

- [ ] **Step 1: 编写 docker-compose.yml**
- [ ] **Step 2: 编写私有化部署配置**
- [ ] **Step 3: 测试一键启动**

---

## 预计总时间：25 小时

| 阶段 | 预计时间 | 交付物 |
|------|---------|--------|
| Phase 1: Hermes Agent 核心技能 | 4 小时 | 内容生成技能 |
| Phase 2: 客户分析技能 | 3 小时 | 客户画像技能 |
| Phase 3: 跟进管理技能 | 3 小时 | 自动化跟进技能 |
| Phase 4: 数据库基础设施 | 2 小时 | PostgreSQL + RLS |
| Phase 5: FastAPI 接口层 | 2 小时 | REST API |
| Phase 6: uni-app 前端 | 8 小时 | Web + 小程序 |
| Phase 7: 合规审核 | 2 小时 | 话术审核工作流 |
| Phase 8: 测试 | 3 小时 | 测试套件 |
| Phase 9: 部署 | 1 小时 | Docker Compose |

---

## 成功标准

- [ ] 所有内容生成技能通过测试
- [ ] 客户分析准确率 > 85%
- [ ] UI 状态矩阵完整实现
- [ ] 数据隔离验证通过 (RLS 测试)
- [ ] 合规审核工作流正常运行
- [ ] 单元测试覆盖率 > 85%
