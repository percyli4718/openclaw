# OpenClaw 企业级 Agent 编排系统

> 基于 LangGraph + Harness/Context Engineering 的企业级 Agent 编排平台

## 核心能力

- **LangGraph 状态机**: 任务拆解、状态流转、工具调度，支持 10+ Agent 并行协同
- **50+ 预置工具**: 消息通知、数据查询、文档处理、审批流程
- **Harness/Context Engineering**: AGENTS.md 持久化、Hooks 生命周期、分层上下文治理
- **低代码配置**: 新场景接入周期 2 天→2 小时

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│   (企业微信/钉钉/飞书/Web 管理台/H5 移动端)                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway Layer                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                Agent Orchestration Layer                │
│   LangGraph State Machine + Planner/Executor/Reviewer   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Tool Layer (50+)                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                Knowledge Layer                          │
│   AGENTS.md + Vector DB + Client DB                     │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m openclaw.main
```

## 项目结构

```
openclaw/
├── openclaw/           # 核心编排引擎
│   ├── orchestration/  # LangGraph 状态机
│   ├── tools/          # 50+ 预置工具
│   ├── context/        # Harness/Context Engineering
│   ├── retrieval/      # RAG 知识检索
│   ├── configurator/   # 低代码配置
│   └── observability/  # Trace 记录 + 监控
├── tests/              # 单元测试
├── docs/               # 文档
└── examples/           # 示例场景
```

## 核心指标

| 指标 | 目标值 |
|------|--------|
| 新场景接入周期 | ≤2 小时 |
| 决策准确率 | ≥96% |
| 客户人力成本降低 | 50% |
| 运营效率提升 | 3 倍 |

## License

MIT
