# TODOS - 保客通 AI+ 保险获客系统

## 产品设计完善

### Hermes Agent 技能实现
- [ ] #1: `generate_wechat_copywriting` - 朋友圈文案生成技能
- [ ] #2: `generate_short_video_script` - 短视频脚本生成技能
- [ ] #3: `generate_poster_copywriting` - 海报文案生成技能
- [ ] #4: `analyze_customer_profile` - 客户画像分析技能
- [ ] #5: `segment_customers` - 客户分层技能
- [ ] #6: `create_followup_plan` - 跟进计划制定技能
- [ ] #7: `schedule_automated_message` - 定时消息推送技能

### UI 状态矩阵实现
- [ ] #8: 内容生成模块 5 状态 (Loading/Empty/Success/Error/Partial)
- [ ] #9: 客户画像模块 5 状态
- [ ] #10: 自动化跟进模块 5 状态

---

## 技术架构

### 数据隔离与安全
- [ ] #11: PostgreSQL RLS (Row-Level Security) 实现
- [ ] #12: 敏感数据 AES-256 加密 (手机号/身份证/地址)
- [ ] #13: Redis Cluster 高可用配置
- [ ] #14: Circuit Breaker 熔断器模式 (AI 调用)

### AI 调用优化
- [ ] #15: 混合 AI 部署 (云端 Claude API + 本地 Ollama)
- [ ] #16: AI 调用超时降级策略
- [ ] #17: 话术合规审核工作流

---

## 功能开发

### MVP 功能 (P0)
- [ ] #18: 朋友圈文案生成 (Web + 小程序)
- [ ] #19: 短视频脚本生成
- [ ] #20: 客户标签管理
- [ ] #21: 客户分层分析
- [ ] #22: 跟进计划制定
- [ ] #23: 定时消息推送

### V2 功能 (P1)
- [ ] #24: 海报文案生成
- [ ] #25: 话术模板库 (100+ 模板)
- [ ] #26: 需求预测 AI
- [ ] #27: 相似客户向量检索
- [ ] #28: 跟进逾期提醒
- [ ] #29: 获客效果分析面板
- [ ] #30: A/B 测试功能

---

## 多端适配

- [ ] #31: Web 端 (H5/PC) 基础框架
- [ ] #32: 微信小程序适配
- [ ] #33: iOS App (uni-app x)
- [ ] #34: Android App (uni-app x)
- [ ] #35: 鸿蒙 App (uni-app x)
- [ ] #36: 平板横屏布局适配

---

## 测试策略

### 单元测试 (pytest)
- [ ] #37: 内容生成技能测试
- [ ] #38: 客户分析技能测试
- [ ] #39: 跟进管理技能测试
- [ ] #40: 数据隔离测试 (租户 A 不可见租户 B 数据)

### 集成测试 (Testcontainers)
- [ ] #41: PostgreSQL 集成测试
- [ ] #42: Redis 集成测试
- [ ] #43: Qdrant 向量检索测试

### E2E 测试 (Playwright)
- [ ] #44: 主流程测试 (生成文案→发送→跟进)
- [ ] #45: 小程序端到端测试

---

## 合规与审计

- [ ] #46: 话术敏感词过滤
- [ ] #47: 合规模型审核 (AI 语义分析)
- [ ] #48: 审计日志记录 (所有 AI 生成操作)
- [ ] #49: 微信小程序资质申请

---

## 文档

- [ ] #50: API 接口文档 (OpenAPI/Swagger)
- [ ] #51: 部署指南 (Docker Compose)
- [ ] #52: 面试演示脚本
- [ ] #53: 用户操作手册

---

## 软件全生命周期流程说明

### 已完成的生命周期文档

| 文档 | 路径 | 说明 |
|------|------|------|
| Design Spec | `docs/plans/2026-04-15-baoke-tong-design.md` | 技术可行性、边界条件、风险识别 |
| Implementation Plan | `docs/plans/2026-04-15-baoke-tong-plan.md` | 9 阶段实施计划 |
| TODOS.md | `TODOS.md` | 产品待办 + 技术待办 |
| 面试 Q&A | `docs/interview/baoke-tong-qna.md` | 与 resume.md 对应的面试问答 |
| 演示脚本 | `docs/interview/demo-script.md` | 15-20 分钟面试演示流程 |

### Superpowers + gstack 工作流程

```
阶段 0: 需求澄清 → 阶段 1: 计划与审查 → 阶段 2: 隔离环境 → 阶段 3: 编码实现 → 阶段 4: 调试验证 → 阶段 5: 质量门禁 → 阶段 6: 发布
```

---

*Last updated: 2026-04-16*
