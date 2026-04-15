# OpenClaw 企业级 Agent 编排系统

## 项目说明
企业级 Agent 编排系统 - 基于 LangGraph + Harness/Context Engineering

## 项目范围
1. **OpenClaw 企业级 Agent 编排系统**（一人公司/顾问）- 当前进行中
2. 5 家中小企业客户定制交付
3. 50+ 预置工具（消息通知、数据查询、文档处理、审批流程）

## 覆盖要求
- 95% 覆盖核心功能
- 约束：本地笔记本无多集群环境（与生产环境的主要差异）

---

# Superpowers + gstack 完整工作流程

## 流程总览（含文档输出）

```
阶段 0: 需求澄清 → 阶段 1: 计划与审查 → 阶段 2: 隔离环境 → 阶段 3: 编码实现 → 阶段 4: 调试验证 → 阶段 5: 质量门禁 → 阶段 6: 发布
     ↓                    ↓                     ↓                  ↓                    ↓                   ↓
  Product Brief      Design Spec          Implementation       Source Code        Test/QA Report    GitHub Release
  (office-hours)     (brainstorming)      Plan (writing-plans)                     + Security Audit
```

## 详细流程

### 【阶段 0：需求澄清】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 0a. 商业角度需求 | gstack: `/office-hours` | Product Brief | YC 六问：谁在用、什么问题、现有方案、为什么现在、如何获客、如何赚钱 |
| 0b. 工程角度需求 | Superpowers: `brainstorming` | Design Spec (`docs/plans/YYYY-MM-DD-<topic>-design.md`) | 技术可行性、边界条件、风险识别、Spec Review Loop |

**执行顺序**：先 `/office-hours` 输出 Product Brief，再 `brainstorming` 基于 Product Brief 输出 Design Spec

### 【阶段 1：计划与审查】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 1. 计划撰写 | Superpowers: `writing-plans` | Implementation Plan | 基于 Design Spec 输出实施计划，含任务拆解 |
| 2. 多视角审查 | gstack: `/autoplan` | Reviewed Plan | 自动执行 CEO + Design + Eng 三视角审查 |

### 【阶段 2：隔离环境】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 3. 工作区隔离 | Superpowers: `using-git-worktrees` | Git Worktree + Branch | 创建项目分支，独立于当前 workspace |

### 【阶段 3：编码实现】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 4. 任务拆解 + 编码 | Superpowers: `subagent-driven-development` | Source Code + Commits | 分派子代理执行任务，每个任务内部采用 TDD |
| 4a. TDD 循环 | Superpowers: `test-driven-development` | Tests + Implementation | Red-Green-Refactor 循环 |

### 【阶段 4：调试与验证】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 5. 调试 | Superpowers: `systematic-debugging` | Fixed Code | 系统性调试问题 |
| 6. 完成验证 | Superpowers: `verification-before-completion` | Verification Report | 确保交付质量 |

### 【阶段 5：质量门禁】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 7. 真实环境验证 | gstack: `/qa` | QA Report | 功能验证 |
| 8. 代码审查 | Superpowers: `requesting-code-review` | Code Review Approved | 确保代码质量符合生产标准 |
| 9. 安全审计 | gstack: `/cso` | Security Audit Passed | 发布前安全审计（必须） |

### 【阶段 6：发布】
| 步骤 | 工具/Skill | 输出 | 说明 |
|------|-----------|------|------|
| 10. 发布 | gstack: `/ship` | GitHub Release | 推送到 GitHub |

---

## 5 个关键交接点

| 交接点 | 前置条件 | 后置条件 |
|--------|---------|---------|
| 1. 需求→计划 | 商业/工程需求明确 | 计划撰写启动 |
| 2. 计划→隔离 | 三视角审查通过 | worktree 创建 |
| 3. 隔离→编码 | 工作区就绪 | subagent 任务分派 |
| 4. 编码→验证 | 功能实现完成 | 调试/验证启动 |
| 5. 验证→发布 | QA/安全/审查全部通过 | 发布到 GitHub |

---

## 技能分工

### Superpowers（思考与流程层）
- 触发方式：自动触发
- 负责：brainstorming、writing-plans、using-git-worktrees、subagent-driven-development、test-driven-development、systematic-debugging、verification-before-completion、requesting-code-review

### gstack（执行与外部世界层）
- 触发方式：斜杠命令手动触发
- 负责：/office-hours、/autoplan、/qa、/cso、/ship、/browse

## 浏览器规则
- 使用 `/browse` 作为唯一浏览器入口
- 禁止使用 `mcp__claude-in-chrome__*` 操作浏览器

---

## Available Skills
/office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review, /design-consultation, /design-shotgun, /design-html, /review, /ship, /land-and-deploy, /canary, /benchmark, /browse, /qa, /qa-only, /design-review, /setup-browser-cookies, /setup-deploy, /retro, /investigate, /document-release, /codex, /cso, /autoplan, /pair-agent, /careful, /freeze, /guard, /unfreeze, /gstack-upgrade, /learn
