# TODOS - OpenClaw 企业级 Agent 编排系统

## 安全审计修复 (2026-04-15 CSO Audit)

### CRITICAL (需立即修复)
- [ ] #1: Docker Compose 硬编码 Qdrant API Key (docker-compose.yml:45)
  - 修复：使用 `${QDRANT_API_KEY:-$(openssl rand -hex 16)}`
- [ ] #2: Docker Compose 硬编码 Milvus token (docker-compose.yml:68)
  - 修复：使用 `${MILVUS_TOKEN:-changeit_now}`
- [ ] #3: Docker Compose 硬编码 Postgres 凭证 (docker-compose.yml:95)
  - 修复：使用 `${POSTGRES_PASSWORD:-$(openssl rand -hex 16)}`

### HIGH (近期修复)
- [ ] #4: FastAPI 端点无认证机制 (openclaw/api/routes.py:25)
  - 修复：添加 API Key 认证中间件
- [ ] #5: CORS 允许所有来源 (openclaw/main.py:32)
  - 修复：限制为具体域名列表

### MEDIUM (计划修复)
- [ ] #6: Redis 无密码保护 (docker-compose.yml:110)
  - 修复：添加 requirepass 配置
- [ ] #7: LangFuse 公钥/密钥硬编码 (docker-compose.yml:135)
  - 修复：`openssl rand -hex 32` 生成随机密钥

---

## 功能完善

### LangGraph 状态机
- [ ] 实现真实的 LLM 调用（当前为 Mock）
- [ ] 添加更多任务类型支持（数据查询、文档处理、审批流程）
- [ ] 实现动态任务拆解和并行执行

### 50+ 工具库
- [ ] 消息通知类：企业微信/钉钉/飞书/短信/邮件（10 个）
- [ ] 数据查询类：MySQL/PostgreSQL/Oracle/MongoDB/Redis/API 通用调用（15 个）
- [ ] 文档处理类：OCR/PDF 解析/Excel 读取/Word 解析（10 个）
- [ ] 审批流程类：请假/报销/采购/合同/用印（15 个）

### Harness/Context Engineering
- [ ] 完善 AGENTS.md 管理器（支持多 Agent 上下文隔离）
- [ ] 实现 Hooks 生命周期（pre_task/post_task/pre_tool_call/post_tool_call）
- [ ] 添加 Sub-agent 编排框架

### 低代码配置
- [ ] 可视化流程编排界面
- [ ] 工具 Schema 编辑器
- [ ] Agent 模板配置界面
- [ ] AI 辅助配置生成

---

## 代码质量
- [ ] 添加 LangGraph 状态机单元测试
- [ ] 添加工具注册集成测试
- [ ] 添加 Hooks 框架端到端测试
- [ ] 添加 FastAPI 接口测试

---

## 文档
- [ ] 补充 API 接口文档（OpenAPI/Swagger）
- [ ] 编写部署指南（Docker Compose / Kubernetes）
- [ ] 添加面试演示脚本
- [ ] 编写工具接入指南

---

## 性能优化
- [ ] 工具调用并发执行（asyncio.gather）
- [ ] 向量检索缓存（Redis 缓存 Top-K 结果）
- [ ] LangGraph 状态序列化优化（支持断点续传）

---

## 可观测性
- [ ] 集成 LangFuse 链路追踪
- [ ] 添加自定义指标（工具调用次数、成功率、延迟）
- [ ] 实现 Trace 可视化查询

---

*Last updated: 2026-04-15*
