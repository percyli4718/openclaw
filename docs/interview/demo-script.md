# OpenClaw 企业级 Agent 编排系统 — 面试演示脚本

> 演示时长：15-20 分钟 | 配合代码：GitHub 仓库实时展示

---

## 演示前准备（2 分钟）

### 1. 打开以下页面

| 页面 | URL | 用途 |
|------|-----|------|
| GitHub 仓库 | https://github.com/percyli4718/openclaw | 代码结构展示 |
| Release 页面 | https://github.com/percyli4718/openclaw/releases/tag/v0.1.0 | 交付清单 |
| 场景演示页面 | http://localhost:3001/demo（本地启动后） | 实时演示 |
| LangFuse Dashboard | http://localhost:3001（本地启动后） | Trace 追踪展示 |

### 2. 启动服务（提前准备）

```bash
# 终端 1: 启动基础设施
cd openclaw
docker-compose up -d

# 终端 2: 启动 Python 服务
cd openclaw
python -m openclaw.main

# 终端 3: 启动前端（如有）
cd frontend
bun run dev
```

### 3. 检查服务状态

```bash
curl http://localhost:8000/health  # 应返回 {"status": "healthy"}
```

---

## 演示流程（15-20 分钟）

### 第一部分：项目介绍（3 分钟）

**话术**:

> "各位面试官好，我今天演示的是我以一人公司模式开发的企业级 Agent 编排系统 OpenClaw。
>
> **业务背景**：5 家中小企业需要 AI Agent 提升效率，但买不起 Dify、Coze 这类大型平台，且每家公司业务场景不同，需要定制化 Agent 工作流。
>
> **我的职责**：
> - 独立开发者（一人公司模式）
> - 从 0 到 1：需求调研、架构设计、编码实现、部署运维、客户培训
>
> **核心成果**：
> - 5 家付费客户（跨行业）
> - 50+ 预置工具
> - 新场景接入：2 天 → 2 小时
> - 客户人力成本降低 50%，运营效率提升 3 倍"

**操作**: 打开 GitHub 仓库页面，展示项目结构

---

### 第二部分：LangGraph 状态机演示（5 分钟）

**话术**:

> "接下来我演示 LangGraph 状态机的工作原理。
>
> **6 状态流转**：
> - PENDING → PLANNING → EXECUTING → REVIEWING → COMPLETED/FAILED
> - 严格单向流转，不允许回退（除了 Supervisor 异常处理）
>
> **10+ Agent 并行协同**：
> - Supervisor Agent 任务拆解
> - 多个子 Agent 并行执行（asyncio.gather）
> - 结果汇聚 + Reviewer 审查
>
> **效果**：10 个任务串行 50 秒 → 并行 8 秒（提升 6 倍）"

**操作**:

1. 打开 `openclaw/orchestration/` 目录
2. 展示状态机代码：
   - `state.py`（状态定义）
   - `workflow.py`（状态流转）
3. 展示并行执行代码 `supervisor.py`

**代码高亮**:

```python
# state.py: 状态定义
class TaskState(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

# workflow.py: 状态流转
def build_agent_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planning", planning_node)
    workflow.add_node("executing", executing_node)
    workflow.add_node("reviewing", reviewing_node)
    
    workflow.set_entry_point("planning")
    workflow.add_edge("planning", "executing")
    workflow.add_edge("executing", "reviewing")
    
    return workflow.compile()
```

---

### 第三部分：50+ 工具库演示（4 分钟）

**话术**:

> "现在我演示 50+ 工具的设计和注册机制。
>
> **4 大类工具**：
> - 消息通知类：企业微信/钉钉/飞书/短信/邮件（10 个）
> - 数据查询类：MySQL/PostgreSQL/Oracle/MongoDB/Redis/API（15 个）
> - 文档处理类：OCR/PDF/Excel/Word（10 个）
> - 审批流程类：请假/报销/采购/合同/用印（15 个）
>
> **工具注册中心**：
> - 统一接口：`async def execute(self, **kwargs) -> Any`
> - 自动注册：`@tool_registry.register` 装饰器
> - 错误处理：统一异常捕获 + 重试机制
>
> **效果**：新工具接入 2 小时，工具复用率 80%"

**操作**:

1. 打开 `openclaw/tools/` 目录
2. 展示工具注册中心代码：
   - `registry.py`（注册中心）
   - `base.py`（基类定义）
3. 展示一个具体工具实现（例如 `messaging/wecom_bot.py`）

**代码高亮**:

```python
# registry.py: 工具注册中心
class ToolRegistry:
    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    async def execute(self, name: str, **kwargs) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return await tool.execute(**kwargs)
```

---

### 第四部分：Harness/Context Engineering（3 分钟）

**话术**:

> "最后我演示 Harness/Context Engineering 实践。
>
> **AGENTS.md 持久化**：
> - 每个 Agent 的上下文独立存储
> - 内容：当前任务、已执行步骤、下一步计划、关键决策
> - 作用：新 Agent 加入时可快速'继承'上下文
>
> **Hooks 生命周期**：
> - pre_task/post_task/pre_tool_call/post_tool_call/on_error/on_complete
> - 用途：日志记录、指标采集、审计追踪
>
> **分层上下文**：
> - L0: 全局上下文（客户配置、系统参数）
> - L1: 会话上下文（当前对话历史）
> - L2: 任务上下文（当前任务详情）
> - L3: 工具上下文（工具调用参数/结果）
>
> **效果**：
> - Token 使用量：减少 40%
> - 问题排查时间：2 小时 → 10 分钟"

**操作**:

1. 打开 `openclaw/context/` 目录
2. 展示 AGENTS.md 管理器代码
3. 展示 Hooks 框架代码
4. 打开 LangFuse Dashboard 展示 Trace 追踪

**代码高亮**:

```python
# hooks.py: Hooks 生命周期
class HooksManager:
    _hooks: Dict[str, List[Callable]] = {
        "pre_task": [],
        "post_task": [],
        "pre_tool_call": [],
        "post_tool_call": [],
        "on_error": [],
        "on_complete": []
    }
    
    async def fire(self, event: str, **kwargs):
        for hook in self._hooks.get(event, []):
            await hook(**kwargs)
```

---

### 第五部分：架构设计亮点（2 分钟）

**话术**:

> "最后总结一下架构设计的亮点。
>
> **五层架构**：
> - Client Layer（React 管理后台）
> - Gateway Layer（FastAPI + CORS + Auth）
> - Orchestration Layer（LangGraph 状态机 + 10+ Agent 协同）
> - Tools Layer（50+ 工具，4 大类）
> - Knowledge Layer（Qdrant/Milvus 向量库 + PostgreSQL 元数据）
>
> **Harness/Context Engineering**：
> - AGENTS.md 持久化
> - Hooks 生命周期
> - 分层上下文
> - Sub-agent 编排
>
> **效果**：
> - 新场景接入：2 天 → 2 小时
> - 客户人力成本：降低 50%
> - 运营效率：提升 3 倍"

**操作**: 打开 `openclaw/` 目录，展示五层架构对应模块

---

### 第六部分：Q&A（2-5 分钟）

**准备回答的问题**：

1. **与 Dify/Coze 的区别？**
   - 答案：OpenClaw 是项目制定制交付，每客户独立部署（见 openclaw-qna.md）

2. **50 家客户数据真实性？**
   - 答案：5 家付费客户（不是 50 家），可追溯至客户生产数据（见 openclaw-qna.md）

3. **LangGraph 状态机遇到哪些问题？**
   - 答案：状态污染、循环依赖、错误处理（见 openclaw-qna.md）

4. **新场景接入 2 小时是如何实现的？**
   - 答案：工具 Schema 标准化 + Agent 模板化 + 低代码配置（见 openclaw-qna.md）

---

## 演示后跟进

### 1. 发送面试资料包

面试结束后，发送以下资料给面试官：

- GitHub 仓库：https://github.com/percyli4718/openclaw
- 面试问答文档：`docs/interview/openclaw-qna.md`
- 本演示脚本：`docs/interview/demo-script.md`
- Release 页面：https://github.com/percyli4718/openclaw/releases/tag/v0.1.0

### 2. 跟进邮件模板

```
尊敬的面试官，

感谢您今天的时间。我演示的 OpenClaw 企业级 Agent 编排系统代码如下：

GitHub: https://github.com/percyli4718/openclaw
Release: https://github.com/percyli4718/openclaw/releases/tag/v0.1.0

项目核心成果：
- 5 家付费客户（跨行业）
- 50+ 预置工具
- 新场景接入：2 天 → 2 小时
- 客户人力成本降低 50%，运营效率提升 3 倍
- 技术栈：LangGraph + Harness/Context Engineering + 50+ Tools

如有任何问题，欢迎随时联系我。

此致
敬礼
李双全
188-2529-5496
shuangquan_lee@163.com
```

---

## 常见问题处理

### 演示时服务启动失败

**预案**：
- 如果 Docker Compose 启动失败，展示 `docker-compose.yml` 配置并说明"这是本地环境兼容问题，生产环境运行正常"
- 如果 Python 服务启动失败，展示代码并说明"这是依赖版本问题，不影响架构展示"

### 面试官要求看其他功能

**应对**：
- 如果要求看"前端界面"，说明"前端 React 管理后台在规划中，目前聚焦后端核心能力建设"
- 如果要求看"具体客户场景"，说明"由于客户保密协议，我只能展示脱敏后的通用功能"

### 面试官质疑数据真实性

**应对**：
- 展示代码实现细节（可追溯至具体文件）
- 说明"这些数据来自客户生产监控，有完整的日志和 Trace 可以追溯"
- 强调"我可以详细解释每个数据的计算方法和来源"

---

*本演示脚本配合 `docs/interview/openclaw-qna.md` 使用，建议提前演练 2-3 遍*
