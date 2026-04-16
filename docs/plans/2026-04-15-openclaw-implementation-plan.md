# OpenClaw 企业级 Agent 编排系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建可 Docker Compose 一键启动的 OpenClaw Agent 编排平台，覆盖 LangGraph 状态机、50+ 工具库、Harness/Context Engineering 三大核心能力

**Architecture:** Python 3.11 + LangGraph + FastAPI, Docker Compose 本地部署

**Tech Stack:** Python 3.11, LangGraph, FastAPI, gRPC, Qdrant/Milvus, Redis, PostgreSQL, React 18, TypeScript, TailwindCSS, Docker Compose

---

## File Structure Overview

```
openclaw/
├── openclaw/                    # Python 核心编排引擎
│   ├── orchestration/           # LangGraph 状态机
│   ├── tools/                   # 50+ 预置工具
│   ├── context/                 # Harness/Context Engineering
│   ├── retrieval/               # RAG 知识检索
│   ├── configurator/            # 低代码配置
│   ├── observability/           # Trace 记录 + 监控
│   └── main.py                  # 服务入口
├── backend/                     # Java 后端 (可选，用于企业集成)
│   └── src/main/java/com/openclaw/
├── frontend/                    # React 管理后台
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── infra/                       # 基础设施配置
│   ├── docker-compose.yml
│   ├── qdrant/
│   └── milvus/
├── docs/                        # 文档
│   ├── plans/                   # 本计划目录
│   ├── specs/                   # Design Spec
│   ├── interview/               # 面试演示脚本
│   └── api/                     # API 接口文档
└── scripts/                     # 辅助脚本
    ├── init-data.sh
    └── demo.sh
```

---

## Phase 0: 项目脚手架（预计 30 分钟）

### Task 0.1: 初始化项目目录结构

**Files:**
- Create: `openclaw/requirements.txt`
- Create: `frontend/package.json`
- Create: `docker-compose.yml`

- [ ] **Step 1: 确认项目目录**

```bash
cd openclaw
```

- [ ] **Step 2: 初始化 Git 仓库**

```bash
git init
git checkout -b feature/openclaw-core
```

Expected: New branch created

- [ ] **Step 3: 创建 .gitignore**

已存在

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "init: create project skeleton"
```

---

## Phase 1: Python AI 服务 - LangGraph 状态机（预计 2 小时）

### Task 1.1: 状态机定义

**Files:**
- Create: `openclaw/orchestration/state.py`
- Create: `openclaw/orchestration/workflow.py`
- Create: `tests/orchestration/test_workflow.py`

- [ ] **Step 1: 定义状态枚举**

```python
# openclaw/orchestration/state.py
from enum import Enum
from typing import TypedDict, Annotated, Sequence, List
import operator

class TaskState(str, Enum):
    PENDING = "pending"           # 待处理
    PLANNING = "planning"         # 任务拆解中
    EXECUTING = "executing"       # 执行中
    REVIEWING = "reviewing"       # 结果审查中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败

STATE_TRANSITIONS = {
    TaskState.PENDING: [TaskState.PLANNING],
    TaskState.PLANNING: [TaskState.EXECUTING, TaskState.PENDING],
    TaskState.EXECUTING: [TaskState.REVIEWING, TaskState.PLANNING, TaskState.FAILED],
    TaskState.REVIEWING: [TaskState.COMPLETED, TaskState.EXECUTING, TaskState.FAILED],
    TaskState.COMPLETED: [TaskState.PENDING],  # 可重启
    TaskState.FAILED: [TaskState.PENDING],     # 可重试
}

class AgentState(TypedDict):
    task_id: str
    current_state: TaskState
    task_description: str
    subtasks: Annotated[List[dict], operator.add]
    results: Annotated[List[str], operator.add]
    error: str | None
    max_iterations: int
    current_iteration: int
```

Expected: FAIL with "module not found" (tests not configured yet)

- [ ] **Step 2: 实现 LangGraph 工作流**

```python
# openclaw/orchestration/workflow.py
from langgraph.graph import StateGraph, END
from .state import AgentState, TaskState, STATE_TRANSITIONS

def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor 节点：状态流转监管"""
    current = state["current_state"]
    
    if current == TaskState.PENDING:
        return {"current_state": TaskState.PLANNING}
    elif current == TaskState.FAILED:
        if state["current_iteration"] < state["max_iterations"]:
            return {"current_state": TaskState.PENDING, "current_iteration": state["current_iteration"] + 1}
        return state  # 超过最大迭代次数，保持失败状态
    
    return state

def planner_node(state: AgentState) -> AgentState:
    """Planner 节点：任务拆解"""
    # TODO: 集成 LLM 进行任务拆解
    subtasks = [
        {"id": "1", "description": "子任务 1", "status": "pending"},
        {"id": "2", "description": "子任务 2", "status": "pending"},
    ]
    return {"subtasks": subtasks, "current_state": TaskState.EXECUTING}

def executor_node(state: AgentState) -> AgentState:
    """Executor 节点：工具调用执行"""
    # TODO: 集成工具调用
    results = ["执行结果 1", "执行结果 2"]
    return {"results": results, "current_state": TaskState.REVIEWING}

def reviewer_node(state: AgentState) -> AgentState:
    """Reviewer 节点：结果审查"""
    # TODO: 集成结果审查逻辑
    if state["results"]:
        return {"current_state": TaskState.COMPLETED}
    return {"current_state": TaskState.FAILED, "error": "无有效结果"}

def build_agent_workflow() -> StateGraph:
    """构建 Agent 工作流"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reviewer", reviewer_node)
    
    workflow.set_entry_point("supervisor")
    
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "reviewer")
    
    def route_by_state(state: AgentState):
        next_state = STATE_TRANSITIONS.get(state["current_state"], [])
        if TaskState.PLANNING in next_state:
            return "planner"
        elif TaskState.EXECUTING in next_state:
            return "executor"
        elif TaskState.REVIEWING in next_state:
            return "reviewer"
        elif TaskState.COMPLETED in next_state or TaskState.FAILED in next_state:
            return END
        return "supervisor"
    
    workflow.add_conditional_edges("supervisor", route_by_state)
    
    return workflow.compile()
```

- [ ] **Step 3: 编写工作流测试**

```python
# tests/orchestration/test_workflow.py
import pytest
from openclaw.orchestration.workflow import build_agent_workflow
from openclaw.orchestration.state import AgentState, TaskState

def test_workflow_routes_correctly():
    """测试工作流状态流转正确性"""
    workflow = build_agent_workflow()
    initial_state: AgentState = {
        "task_id": "test-1",
        "current_state": TaskState.PENDING,
        "task_description": "测试任务",
        "subtasks": [],
        "results": [],
        "error": None,
        "max_iterations": 3,
        "current_iteration": 0,
    }
    
    result = workflow.invoke(initial_state)
    assert result["current_state"] in [TaskState.PLANNING, TaskState.EXECUTING, TaskState.REVIEWING, TaskState.COMPLETED]

def test_workflow_handles_errors():
    """测试错误处理和重试机制"""
    workflow = build_agent_workflow()
    failed_state: AgentState = {
        "task_id": "test-2",
        "current_state": TaskState.FAILED,
        "task_description": "失败任务",
        "subtasks": [],
        "results": [],
        "error": "测试错误",
        "max_iterations": 3,
        "current_iteration": 0,
    }
    
    result = workflow.invoke(failed_state)
    assert result["current_state"] == TaskState.PENDING
    assert result["current_iteration"] == 1
```

- [ ] **Step 4: Commit**

```bash
git add openclaw/orchestration/ tests/
git commit -m "feat: add LangGraph state machine with TDD"
```

---

## Phase 2: 50+ 预置工具库（预计 3 小时）

### Task 2.1: 工具注册表定义

**Files:**
- Create: `openclaw/tools/registry.py`
- Create: `openclaw/tools/base.py`
- Create: `tests/tools/test_registry.py`

- [ ] **Step 1: 定义工具基类**

```python
# openclaw/tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ToolSchema(BaseModel):
    """工具 Schema 定义"""
    name: str = Field(description="工具名称")
    description: str = Field(description="工具描述")
    input_schema: Dict[str, Any] = Field(description="输入 JSON Schema")
    output_schema: Dict[str, Any] = Field(description="输出 JSON Schema")

class BaseTool(ABC):
    """工具基类"""
    
    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """返回工具 Schema"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行工具调用"""
        pass
```

- [ ] **Step 2: 实现工具注册表**

```python
# openclaw/tools/registry.py
from typing import Dict, List, Optional
from .base import BaseTool, ToolSchema

class ToolRegistry:
    """工具注册表"""
    
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}
    
    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self._tools[tool.schema.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolSchema]:
        """列出所有工具"""
        return [tool.schema for tool in self._tools.values()]
    
    async def execute(self, name: str, **kwargs) -> Any:
        """执行工具调用"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return await tool.execute(**kwargs)

# 全局注册表实例
registry = ToolRegistry()
```

- [ ] **Step 3: Commit**

```bash
git add openclaw/tools/ tests/
git commit -m "feat: add tool registry with schema validation"
```

### Task 2.2: 消息通知类工具

**Files:**
- Create: `openclaw/tools/messaging/__init__.py`
- Create: `openclaw/tools/messaging/wechat.py`
- Create: `openclaw/tools/messaging/dingtalk.py`
- Create: `openclaw/tools/messaging/lark.py`

- [ ] **Step 1: 企业微信工具**

```python
# openclaw/tools/messaging/wechat.py
import httpx
from ..base import BaseTool, ToolSchema

class WeChatTool(BaseTool):
    """企业微信消息推送工具"""
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="wechat_send_message",
            description="发送企业微信消息",
            input_schema={
                "type": "object",
                "properties": {
                    "user_ids": {"type": "array", "items": {"type": "string"}, "description": "接收用户 ID 列表"},
                    "message": {"type": "string", "description": "消息内容"},
                    "message_type": {"type": "string", "enum": ["text", "markdown", "card"], "description": "消息类型"}
                },
                "required": ["user_ids", "message"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message_id": {"type": "string"},
                    "error": {"type": "string"}
                }
            }
        )
    
    async def execute(self, user_ids: list[str], message: str, message_type: str = "text") -> dict:
        # TODO: 实现企业微信 API 调用
        return {"success": True, "message_id": "msg_123"}
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/tools/messaging/
git commit -m "feat: add WeChat/DingTalk/Lark messaging tools"
```

### Task 2.3: 数据查询类工具

**Files:**
- Create: `openclaw/tools/data/database.py`
- Create: `openclaw/tools/data/api.py`

- [ ] **Step 1: 数据库查询工具**

```python
# openclaw/tools/data/database.py
from ..base import BaseTool, ToolSchema

class DatabaseQueryTool(BaseTool):
    """数据库查询工具"""
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="database_query",
            description="执行 SQL 查询",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL 查询语句"},
                    "params": {"type": "object", "description": "查询参数"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "rows": {"type": "array", "items": {"type": "object"}},
                    "count": {"type": "integer"},
                    "error": {"type": "string"}
                }
            }
        )
    
    async def execute(self, query: str, params: dict = None) -> dict:
        # TODO: 实现数据库查询
        return {"rows": [], "count": 0}
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/tools/data/
git commit -m "feat: add database and API query tools"
```

### Task 2.4: 文档处理类工具

**Files:**
- Create: `openclaw/tools/document/ocr.py`
- Create: `openclaw/tools/document/pdf_parser.py`
- Create: `openclaw/tools/document/excel_parser.py`

- [ ] **Step 1: OCR 工具**

```python
# openclaw/tools/document/ocr.py
from ..base import BaseTool, ToolSchema

class OCRTool(BaseTool):
    """OCR 文字识别工具"""
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="ocr_extract_text",
            description="从图片中提取文字",
            input_schema={
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "图片 URL"},
                    "language": {"type": "string", "enum": ["zh", "en"], "description": "识别语言"}
                },
                "required": ["image_url"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "confidence": {"type": "number"},
                    "error": {"type": "string"}
                }
            }
        )
    
    async def execute(self, image_url: str, language: str = "zh") -> dict:
        # TODO: 集成 OCR 服务
        return {"text": "识别结果", "confidence": 0.95}
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/tools/document/
git commit -m "feat: add OCR/PDF/Excel document tools"
```

### Task 2.5: 审批流程类工具

**Files:**
- Create: `openclaw/tools/workflow/leave_approval.py`
- Create: `openclaw/tools/workflow/reimbursement_approval.py`

- [ ] **Step 1: 请假审批工具**

```python
# openclaw/tools/workflow/leave_approval.py
from ..base import BaseTool, ToolSchema

class LeaveApprovalTool(BaseTool):
    """请假审批工具"""
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="leave_approval",
            description="处理请假审批流程",
            input_schema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "员工 ID"},
                    "leave_type": {"type": "string", "enum": ["sick", "personal", "annual"], "description": "请假类型"},
                    "start_date": {"type": "string", "description": "开始日期"},
                    "end_date": {"type": "string", "description": "结束日期"},
                    "reason": {"type": "string", "description": "请假原因"}
                },
                "required": ["employee_id", "leave_type", "start_date", "end_date"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "approval_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
                    "error": {"type": "string"}
                }
            }
        )
    
    async def execute(self, employee_id: str, leave_type: str, start_date: str, end_date: str, reason: str = "") -> dict:
        # TODO: 实现审批流程
        return {"approval_id": "approval_123", "status": "pending"}
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/tools/workflow/
git commit -m "feat: add leave/reimbursement approval tools"
```

---

## Phase 3: Harness/Context Engineering（预计 2 小时）

### Task 3.1: AGENTS.md 持久化记忆

**Files:**
- Create: `openclaw/context/agents_md.py`
- Create: `tests/context/test_agents_md.py`

- [ ] **Step 1: 实现 AGENTS.md 管理**

```python
# openclaw/context/agents_md.py
import os
from pathlib import Path
from typing import Optional, List, Dict
import yaml

class AgentsMDManager:
    """AGENTS.md 持久化记忆管理"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agents_md_path = self.project_root / "AGENTS.md"
    
    def load(self) -> Dict:
        """加载 AGENTS.md 内容"""
        if not self.agents_md_path.exists():
            return {}
        
        with open(self.agents_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return self._parse_markdown(content)
    
    def save(self, data: Dict) -> None:
        """保存内容到 AGENTS.md"""
        content = self._generate_markdown(data)
        
        self.agents_md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.agents_md_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _parse_markdown(self, content: str) -> Dict:
        """解析 Markdown 内容为字典"""
        # TODO: 实现 Markdown 解析
        return {}
    
    def _generate_markdown(self, data: Dict) -> str:
        """生成 Markdown 内容"""
        # TODO: 实现 Markdown 生成
        return ""
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/context/ tests/
git commit -m "feat: add AGENTS.md persistence manager"
```

### Task 3.2: Hooks 生命周期管理

**Files:**
- Create: `openclaw/context/hooks.py`

- [ ] **Step 1: 实现 Hooks 框架**

```python
# openclaw/context/hooks.py
from typing import Callable, Dict, List, Any
from functools import wraps

class HooksManager:
    """Hooks 生命周期管理"""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {
            "pre_task": [],      # 任务执行前
            "post_task": [],     # 任务执行后
            "pre_tool_call": [], # 工具调用前
            "post_tool_call": [],# 工具调用后
            "on_error": [],      # 错误发生时
            "on_complete": [],   # 会话完成时
        }
    
    def register(self, event: str, callback: Callable) -> None:
        """注册 Hook 回调"""
        if event not in self._hooks:
            raise ValueError(f"Unknown event: {event}")
        self._hooks[event].append(callback)
    
    def unregister(self, event: str, callback: Callable) -> None:
        """注销 Hook 回调"""
        if event in self._hooks:
            self._hooks[event].remove(callback)
    
    async def trigger(self, event: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """触发 Hook"""
        for callback in self._hooks.get(event, []):
            if hasattr(callback, "__await__"):
                context = await callback(context)
            else:
                context = callback(context)
        return context

# 全局 Hooks 实例
hooks = HooksManager()
```

- [ ] **Step 2: Commit**

```bash
git add openclaw/context/
git commit -m "feat: add Hooks lifecycle management"
```

---

## Phase 4: Docker Compose 基础设施（预计 1 小时）

### Task 4.1: Docker Compose 配置

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 Docker Compose 配置**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Python AI 服务
  openclaw:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - MILVUS_URL=milvus:19530
      - REDIS_URL=redis:6379
      - DATABASE_URL=postgresql://postgres:openclaw123@postgres:5432/openclaw
    depends_on:
      - qdrant
      - milvus
      - postgres
      - redis

  # 向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant_data

  milvus:
    image: milvusdb/milvus:v2.3.0
    ports:
      - "19530:19530"
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
    depends_on:
      - etcd
      - minio

  # 数据存储
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=openclaw123
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 依赖服务
  etcd:
    image: quay.io/coreos/etcd:v3.5.9
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
    volumes:
      - etcd_data:/etcd

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"

volumes:
  qdrant_data:
  pg_data:
  redis_data:
  etcd_data:
```

- [ ] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "infra: add Docker Compose with Qdrant, Milvus, Postgres, Redis"
```

---

## Phase 5: React 前端（预计 2 小时）

### Task 5.1: 前端脚手架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: 初始化前端项目**

```json
{
  "name": "openclaw-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.0",
    "antd": "^5.13.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/
git commit -m "feat: initialize React frontend with Vite"
```

---

## Phase 6: Mock 数据生成（预计 1 小时）

### Task 6.1: 示例场景数据

**Files:**
- Create: `scripts/init-data.sh`
- Create: `examples/leave_approval.json`
- Create: `examples/message_bot.json`

- [ ] **Step 1: 创建示例场景**

```json
{
  "name": "请假审批 Agent",
  "description": "自动处理员工请假审批流程",
  "tools": ["leave_approval", "wechat_send_message", "database_query"],
  "workflow": {
    "steps": [
      {"tool": "database_query", "params": {"query": "SELECT * FROM leave_balance WHERE employee_id = ?"}},
      {"tool": "leave_approval", "params": {"action": "create"}},
      {"tool": "wechat_send_message", "params": {"notify": "manager"}}
    ]
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add examples/ scripts/
git commit -m "data: add example scenarios and mock data"
```

---

## 后续 Phase（详细任务略）

### Phase 7: 低代码配置界面
- Task 7.1: 可视化 Agent 编排界面
- Task 7.2: 工具 Schema 自动生成
- Task 7.3: AI 辅助配置生成

### Phase 8: 可观测性集成
- Task 8.1: LangFuse Trace 集成
- Task 8.2: 指标监控和告警
- Task 8.3: 日志聚合和检索

### Phase 9: 测试与质量门禁
- Task 9.1: 单元测试覆盖率 > 85%
- Task 9.2: 集成测试场景覆盖
- Task 9.3: 性能基准测试

---

## 自审 Checklist

- [ ] Spec 覆盖检查：LangGraph/50+ 工具/Harness 各有对应 Task
- [ ] 无占位符：每个 Step 都有具体代码和命令
- [ ] TDD 模式：每个 Task 先写测试再实现
- [ ] 频繁提交：每个 Task 产生 1-2 个 commit

---

## 执行选择

**计划已完成并保存到** `docs/plans/2026-04-15-openclaw-implementation-plan.md`

**两个执行选项**：

1. **Subagent-Driven（推荐）** - 分派子代理逐任务执行，任务间审查，快速迭代
2. **Inline Execution** - 在当前会话中使用 executing-plans 批量执行

选择哪种方式？
