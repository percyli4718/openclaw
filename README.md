# 保客通 (BaokeTong) - AI+ 保险获客系统

> 基于 Hermes Agent 的保险行业 AI 获客系统 - 采用"智能体 + 培训 + 课程 + 企业深度服务"四位一体模式

## 核心功能

- **智能体获客内容生成**: 朋友圈文案、短视频脚本、海报文案自动生成（内置合规审核）
- **AI 客户画像分析**: 客户标签管理、分层分析、需求预测
- **自动化跟进**: 跟进计划制定、定时消息推送、跟进记录
- **数据驱动策略优化**: 获客效果分析、A/B 测试、策略推荐
- **多租户 SaaS 架构**: 行级安全隔离 (RLS)、敏感数据 AES-256 加密

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层（uni-app）                      │
│   Web 端 + 微信小程序 + iOS/Android/鸿蒙 App + 平板适配    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                   │
│               认证鉴权 / 限流 / 请求路由                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                Hermes Agent 核心层                        │
│   技能引擎 (Skills) + 记忆系统 (Memory) + 工具注册表       │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   │ 内容生成    │  │ 客户分析    │  │ 跟进管理    │
│   │ + 合规审核  │  │ + 画像检索  │  │ + 定时调度  │
│   └─────────────┘  └─────────────┘  └─────────────┘
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                              │
│   PostgreSQL (业务数据+RLS) + Redis (缓存) + Qdrant (向量)│
└─────────────────────────────────────────────────────────┘
```

## 部署模式

| 客户类型 | 部署模式 | 定价 |
|---------|---------|------|
| 小微客户（个人/小团队） | SaaS 多租户，共享数据库 | 2999 元/年 |
| 中型客户（50 人 + 团队） | 独立 database，共享实例 | 19999 元/年 |
| 大型客户（企业级） | 私有化部署，独立 PostgreSQL | 50000 元/年起 |

## 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 一键启动所有服务
./scripts/start.sh start

# 2. 查看服务状态
./scripts/start.sh status

# 3. 查看实时日志
./scripts/start.sh logs

# 4. 停止服务
./scripts/start.sh stop
```

### 方式二：本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
export ENCRYPTION_KEY="your-32-byte-encryption-key!!!!"
export SECRET_KEY="your-secret-key"
export ANTHROPIC_API_KEY="your-api-key"

# 3. 启动服务
python -m baoke_tong.main
```

### 方式三：Docker 直接运行

```bash
# 构建并运行
docker build -f infra/Dockerfile.backend -t baoke-tong:latest .
docker run -p 8000:8000 --env-file .env baoke-tong:latest
```

## 项目结构

```
baoke-tong/
├── frontend/               # uni-app 前端
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── services/      # API 服务
│   │   └── utils/         # 工具函数
│   ├── manifest.json      # uni-app 配置
│   └── pages.json         # 页面路由配置
├── baoke_tong/            # Python 后端核心
│   ├── skills/            # 保险行业技能
│   │   ├── content_gen.py # 内容生成（文案/脚本/海报）
│   │   ├── customer.py    # 客户分析（画像/分层/需求预测）
│   │   ├── followup.py    # 跟进管理（计划/调度/记录）
│   │   └── compliance.py  # 合规审核（敏感词/AI 语义/审计）
│   ├── models/            # SQLAlchemy ORM 模型
│   ├── config/            # 配置管理
│   ├── memory/            # 记忆系统
│   ├── tools/             # 工具注册表
│   └── main.py            # FastAPI 应用入口
├── tests/                  # 测试
│   ├── skills/            # 技能单元测试
│   ├── models/            # 模型测试
│   └── api/               # API 集成测试
├── infra/                  # 基础设施配置
│   ├── docker-compose.yml  # Docker Compose 配置
│   ├── Dockerfile.backend  # 后端 Dockerfile
│   └── sql/
│       └── init.sql       # 数据库初始化脚本 (RLS+ 加密)
├── scripts/                # 辅助脚本
│   ├── test.sh            # 测试脚本
│   └── start.sh           # 一键启动脚本
├── docs/                   # 文档
│   ├── plans/             # 实施计划
│   ├── specs/             # Design Spec
│   └── interview/         # 面试文档
├── pytest.ini              # pytest 配置
├── requirements.txt        # Python 依赖
└── README.md               # 本文件
```

## API 文档

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/api/v1/skills/content-gen` | GET | 内容生成 API |
| `/api/v1/skills/customer` | GET | 客户分析 API |
| `/api/v1/skills/followup` | GET | 跟进管理 API |

### 示例请求

```bash
# 健康检查
curl http://localhost:8000/

# 内容生成
curl http://localhost:8000/api/v1/skills/content-gen
```

## 测试

### 运行所有测试

```bash
# 使用测试脚本
./scripts/test.sh

# 或直接用 pytest
pytest

# 生成覆盖率报告
pytest --cov=baoke_tong --cov-report=html
```

### 测试覆盖率要求

- 单元测试覆盖率：> 85%
- 核心技能覆盖率：100%

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POSTGRES_PASSWORD` | PostgreSQL 密码 | `baoke_tong_dev_password` |
| `REDIS_PASSWORD` | Redis 密码 | `baoke_tong_redis_password` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `ENCRYPTION_KEY` | 数据加密密钥 (32 字节) | - |
| `SECRET_KEY` | 应用密钥 | - |
| `APP_ENV` | 应用环境 | `development` |

## 核心指标

| 指标 | 目标值 |
|------|--------|
| MVP 发布 | 2 个月 |
| 付费客户 | 10 家（3 个月） |
| 客户续费率 | > 60% |
| 标杆案例 | 3 个（4 个月） |

## 开发与贡献

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/your-org/baoke-tong.git
cd baoke-tong

# 安装依赖
pip install -r requirements.txt

# 运行测试
./scripts/test.sh
```

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 提交代码
git add .
git commit -m "feat: add your feature"

# 推送并创建 PR
git push origin feature/your-feature
```

## License

MIT
