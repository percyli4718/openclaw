# 保客通 Frontend (uni-app)

保客通 AI+ 保险获客系统的 uni-app 前端实现。

## 技术栈

- **框架**: uni-app (Vue 3 + TypeScript)
- **状态管理**: Pinia
- **UI 组件**: uView UI 2.0 (待集成)
- **样式**: SCSS
- **目标平台**: H5、微信小程序、iOS/Android App

## 项目结构

```
frontend/
├── manifest.json           # uni-app 配置
├── pages.json              # 页面路由配置
├── package.json            # 依赖配置
├── tsconfig.json           # TypeScript 配置
├── App.vue                 # 应用入口
├── main.ts                 # 入口文件
└── src/
    ├── pages/              # 页面
    │   ├── index/          # 首页
    │   ├── content-gen/    # 内容生成
    │   ├── customer/       # 客户管理
    │   └── followup/       # 跟进管理
    ├── components/         # 组件
    │   ├── UiState.vue     # UI 状态矩阵组件
    │   └── Skeleton.vue    # 骨架屏组件
    ├── stores/             # Pinia 状态管理
    │   ├── app.ts          # 应用全局状态
    │   ├── contentGen.ts   # 内容生成状态
    │   ├── customer.ts     # 客户管理状态
    │   └── followup.ts     # 跟进管理状态
    ├── services/           # API 服务
    │   ├── api.ts          # API 接口定义
    │   ├── types.ts        # 类型定义
    │   └── index.ts        # 统一导出
    ├── utils/              # 工具函数
    │   ├── date.ts         # 日期工具
    │   ├── validate.ts     # 验证工具
    │   └── index.ts        # 统一导出
    ├── styles/             # 样式
    │   ├── variables.scss  # 变量定义
    │   └── mixins.scss     # Mixins
    └── env.d.ts            # 类型声明
```

## 开发指南

### 安装依赖

```bash
cd frontend
npm install
```

### 运行项目

```bash
# H5 开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

### 构建项目

```bash
# H5 构建
npm run build:h5

# 微信小程序构建
npm run build:mp-weixin
```

### 类型检查

```bash
npm run type-check
```

## 核心功能

### 1. UI 状态矩阵 (Design Spec Section 9)

实现了完整的 UI 状态矩阵，统一处理 5 种状态：

| 状态 | 触发条件 | UI 表现 |
|------|---------|--------|
| Loading | 点击"生成"后 | 骨架屏 + 进度条 |
| Empty | 首次进入/无数据 | 引导文案 + 示例 |
| Success | 生成完成 | 内容展示 |
| Error | AI 调用失败 | 错误提示 + 重试 |
| Partial | 部分成功 | 展示可用结果 + 失败提示 |

使用方式：
```vue
<UiState
  :state="uiState"
  :loading-text="loadingText"
  :empty-title="emptyTitle"
  @action="handleGenerate"
  @retry="handleRetry"
>
  <template #content>
    <!-- Success 状态的内容 -->
  </template>
</UiState>
```

### 2. Pinia 状态管理

- `useAppStore`: 应用全局状态（登录、用户信息）
- `useContentGenStore`: 内容生成状态
- `useCustomerStore`: 客户管理状态
- `useFollowupStore`: 跟进管理状态

### 3. API 服务层

统一的 API 封装，包含：
- 请求/响应拦截器
- Token 自动注入
- 错误统一处理
- 类型安全的 API 定义

## 设计规范

遵循 `DESIGN.md` 中的设计规范：
- 主色调：蓝色系 (#2563eb)
- 字体：系统字体栈
- 圆角：8px-12px
- 阴影：轻盈的阴影系统
- 间距：4px 倍数尺度

## 多端适配

- H5：响应式布局，适配 PC/移动端浏览器
- 微信小程序：遵循小程序设计规范
- App：uni-app x 编译原生 iOS/Android/鸿蒙

## 待办事项

- [ ] 集成 uView UI 组件库
- [ ] 实现登录/注册页
- [ ] 实现客户详情页
- [ ] 实现设置页
- [ ] 实现数据分析页
- [ ] 添加 TabBar 图标资源
- [ ] 完善错误边界处理
- [ ] 添加性能优化（虚拟列表、图片懒加载）
