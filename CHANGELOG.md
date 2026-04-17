# Changelog

所有重要的项目变更都将记录在此文件中。

## [v0.2.0.0] - 2026-04-16

### Added
- **Phase 1-3: Hermes Agent 核心技能完整实现**
  - 内容生成技能 (content_gen.py): 朋友圈文案/短视频脚本/海报文案生成，88 测试通过
  - 客户分析技能 (customer.py): 客户画像分析/客户分层/需求预测，19 测试通过
  - 跟进管理技能 (followup.py): 跟进计划/定时推送/跟进记录，32 测试通过
  - 合规审核技能 (compliance.py): 敏感词过滤/AI 语义审核/审计日志，17 测试通过
- **Phase 4: 数据库基础设施**
  - PostgreSQL + RLS 行级安全策略 (租户数据隔离)
  - SQLAlchemy ORM 模型 (6 张核心表 + 敏感数据 AES-256 加密)
  - Qdrant 向量数据库配置
- **Phase 5: FastAPI 接口层**
  - 11 个 REST API 端点 (内容生成/客户分析/跟进管理)
  - JWT 认证中间件 + 租户上下文中间件 + 限流熔断中间件
  - Pydantic Schema 输入输出验证 (遵循 Design Spec Section 10)
- **Phase 6: uni-app 前端**
  - 4 个核心页面 (首页/内容生成/客户管理/跟进管理)
  - UI 状态矩阵组件 (Loading/Empty/Success/Error/Partial)
  - Pinia 状态管理 + API 服务层
- **Phase 7: 测试与质量门禁**
  - 88 个单元测试，覆盖率 89.41%
  - pytest 配置 + 一键测试脚本
- **Phase 8: 部署与发布**
  - Docker Compose 配置 (SaaS + 私有化部署双模式)
  - 一键启动脚本 (start.sh) + 一键测试脚本 (test.sh)

### Changed
- VERSION: 0.1.0.0 → 0.2.0.0 (MVP 完整功能交付)

## [v0.1.0] - 2026-04-16

### Added
- 保客通 AI+ 保险获客系统初始版本
- 基于 Hermes Agent 的保险行业技能框架
- 智能体获客内容生成功能 (朋友圈文案、短视频脚本、海报文案)
- AI 客户画像分析功能 (客户标签、分层分析、需求预测)
- 自动化跟进功能 (跟进计划、定时消息、跟进记录)
- 数据驱动策略优化功能 (获客效果分析、A/B 测试)

### 技术架构
- uni-app + Vue 3 + TypeScript 多端框架 (Web/小程序/iOS/Android/鸿蒙)
- FastAPI + Hermes Agent 后端服务
- PostgreSQL (业务数据) + Redis (缓存) + Qdrant (向量检索)
- SaaS 多租户 + 私有化部署双模式支持

### 安全与合规
- PostgreSQL RLS (Row-Level Security) 数据隔离
- 敏感数据 AES-256 加密 (手机号/身份证/地址)
- Redis Cluster 高可用配置
- Circuit Breaker 熔断器模式 (AI 调用)
- 话术合规审核工作流 (敏感词过滤 +AI 语义分析 + 人工抽检)
- 审计日志记录 (所有 AI 生成操作可追溯)

### 文档
- README.md: 项目概述、架构说明、核心指标
- CLAUDE.md: Superpowers + gstack 工作流程
- docs/plans/2026-04-15-baoke-tong-design.md: Design Spec (含三视角审查)
- docs/plans/2026-04-15-baoke-tong-plan.md: 实施计划
- TODOS.md: 产品待办 + 技术待办清单
- docs/interview/: 面试文档目录

### 商业模式
- 四位一体：智能体 + 培训 + 课程 + 企业深度服务
- 三种客户类型：小微 (2999 元/年)、中型 (19999 元/年)、大型 (50000 元/年起)

### 核心指标目标
- MVP 发布：2 个月
- 付费客户：10 家 (3 个月内)
- 客户续费率：> 60%
- 标杆案例：3 个 (4 个月内)

### Known Issues
- UI 状态矩阵待实现 (Loading/Empty/Success/Error/Partial)
- Hermes Agent 技能需完整实现 (7 个核心技能)
- 多端适配待完成 (小程序/iOS/Android/鸿蒙)
- 微信小程序资质待申请
