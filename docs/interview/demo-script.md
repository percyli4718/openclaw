# 保客通 (BaokeTong) AI+ 保险获客系统 — 面试演示脚本

> 演示时长：15-20 分钟 | 配合代码：GitHub 仓库实时展示

---

## 演示前准备（2 分钟）

### 1. 打开以下页面

| 页面 | URL | 用途 |
|------|-----|------|
| GitHub 仓库 | https://github.com/percyli4718/baoke-tong | 代码结构展示 |
| Release 页面 | https://github.com/percyli4718/baoke-tong/releases/tag/v0.1.0 | 交付清单 |
| Design Spec | docs/plans/2026-04-15-baoke-tong-design.md | 设计文档展示 |
| 实施计划 | docs/plans/2026-04-16-baoke-tong-implementation-plan.md | 计划展示 |

### 2. 启动服务（提前准备）

```bash
# 终端 1: 启动基础设施
cd baoke-tong
docker-compose up -d

# 终端 2: 启动 Python 服务
cd baoke-tong
python -m baoke_tong.main
```

### 3. 检查服务状态

```bash
curl http://localhost:8000/  # 应返回 {"status": "ok", "version": "0.1.0"}
```

---

## 演示流程（15-20 分钟）

### 第一部分：项目介绍（3 分钟）

**话术**:

> "各位面试官好，我今天演示的是我以一人公司模式开发的 AI+ 保险获客系统——保客通。
>
> **业务背景**：保险行业获客难，传统陌拜、转介绍效率低、成本高。代理人需要 AI 工具自动生成获客内容、7×24 小时自动化跟进。
>
> **保客通定位**：AI 保险顾问成长平台，采用'智能体 + 培训 + 课程 + 企业深度服务'四位一体模式。
>
> **目标客户**：保险代理人/经纪人、团队长、保险公司/经纪公司。
>
> **商业模式**：三种客户类型——小微 (2999 元/年)、中型 (19999 元/年)、大型 (50000 元/年起)。"

**代码展示**:
```bash
# 展示项目结构
tree -L 2

# 展示核心文件
cat README.md
cat docs/plans/2026-04-15-baoke-tong-design.md | head -50
```

---

### 第二部分：技术架构（3 分钟）

**话术**:

> "保客通基于 Hermes Agent 打造，技术架构分为 4 层：
>
> 1. **前端层**：uni-app + Vue 3 + TypeScript，一套代码编译多端（Web+ 小程序+App）
> 2. **API Gateway**：FastAPI，负责认证鉴权、限流、请求路由
> 3. **Hermes Agent 核心层**：技能引擎、记忆系统、工具注册表
> 4. **数据存储层**：PostgreSQL+Redis+Qdrant
>
> **部署模式**：SaaS 多租户 + 私有化部署双模式。"

**代码展示**:
```bash
# 展示技能目录
ls -la baoke_tong/skills/

# 展示技能实现
cat baoke_tong/skills/content_gen.py | head -50
```

---

### 第三部分：核心功能演示（5 分钟）

**功能 1：智能体获客内容生成**

**话术**:
> "这是朋友圈文案生成功能。用户输入保险产品名称、类型、目标客户，AI 自动生成 3 条文案。
>
> 每条文案包含：内容、话题标签、质量评分。用户可以编辑、复制、点赞、重新生成。"

**代码展示**:
```bash
# 展示技能输入输出 Schema
cat baoke_tong/skills/content_gen.py | grep -A 20 "generate_wechat_copywriting"
```

**功能 2：AI 客户画像分析**

**话术**:
> "客户画像分析功能。AI 根据客户基本信息，自动打标签、分层、预测保险需求。"

**功能 3：自动化跟进**

**话术**:
> "跟进计划制定功能。AI 根据客户分层制定跟进节奏，定时发送消息，自动记录跟进内容。"

---

### 第四部分：安全与合规（3 分钟）

**话术**:

> "保险行业对安全合规要求极高。保客通从 5 个层面保障：
>
> 1. **数据隔离**：PostgreSQL RLS 行级安全策略，租户数据隔离
> 2. **敏感数据加密**：AES-256 加密手机号/身份证/地址
> 3. **AI 调用安全**：Circuit Breaker 熔断器模式
> 4. **合规审核工作流**：AI 生成话术 → 敏感词过滤 → 合规模型审核 → 人工抽检
> 5. **审计日志**：所有 AI 生成操作可追溯"

**代码展示**:
```bash
# 展示 RLS 策略
cat docs/plans/2026-04-15-baoke-tong-design.md | grep -A 10 "Row-Level Security"

# 展示合规审核流程
cat docs/plans/2026-04-15-baoke-tong-design.md | grep -A 10 "合规审核工作流"
```

---

### 第五部分：UI 状态设计（2 分钟）

**话术**:

> "UI 状态采用 5 状态矩阵设计：Loading/Empty/Success/Error/Partial。
>
> 每个核心模块都有完整的状态处理，确保用户体验流畅。
>
> 比如内容生成模块：
> - Loading：骨架屏 + 进度条
> - Empty：引导文案 + 示例
> - Success：文案卡片展示
> - Error：错误提示 + 重试
> - Partial：部分成功处理"

**代码展示**:
```bash
# 展示 UI 状态矩阵
cat docs/plans/2026-04-15-baoke-tong-design.md | grep -A 20 "UI 状态矩阵"
```

---

### 第六部分：测试与质量（2 分钟）

**话术**:

> "测试策略采用金字塔模式：
>
> - **单元测试**：pytest，覆盖率目标>85%
> - **集成测试**：Testcontainers，核心流程 100%
> - **E2E 测试**：Playwright，主流程 100%
>
> 质量门禁：
> - QA 功能验证
> - 代码审查
> - 安全审计（CSO）"

---

### 第七部分：总结与 Q&A（2 分钟）

**话术**:

> "总结一下保客通项目：
>
> 1. **产品定位**：AI 保险顾问成长平台，四位一体商业模式
> 2. **技术架构**：Hermes Agent + FastAPI + uni-app
> 3. **核心功能**：内容生成、客户画像、自动化跟进
> 4. **安全合规**：5 层防护，审计日志可追溯
> 5. **交付质量**：测试覆盖率>85%，安全审计通过
>
> 项目周期：2 个月 MVP 发布
> 目标客户：10 家付费（3 个月内）
> 续费率目标：> 60%
>
> 以上就是保客通的演示，欢迎各位提问。"

---

## 面试 Q&A 准备

详见：`docs/interview/baoke-tong-qna.md`

### 常见问题：

1. **为什么选择 Hermes Agent 而不是 OpenClaw？**
   - 安全性：Hermes 无已知高危漏洞
   - 部署：单节点可运行，无需多集群
   - AI 能力：自进化技能系统

2. **如何保证数据隔离？**
   - PostgreSQL RLS 行级安全
   - 中型/大型客户独立 database

3. **合规审核如何工作？**
   - AI 生成 → 敏感词过滤 → AI 语义审核 → 人工抽检 10%

4. **商业模式是什么？**
   - 四位一体：智能体 + 培训 + 课程 + 企业深度服务

---

*Last updated: 2026-04-16*
