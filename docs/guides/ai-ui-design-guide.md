# AI 驱动的多端 UI/UX 设计完全指南

> 小白也能看懂的 UI 设计生成指南 - 基于 awesome-design-md + AI Agent  
> 适用平台：H5、Android、iOS、平板、鸿蒙

**版本**：v1.0  
**最后更新**：2026 年 4 月 16 日  
**适用项目**：所有需要前端 UI/UX 设计的项目

---

## 目录

1. [为什么需要这个指南](#为什么需要这个指南)
2. [核心概念：DESIGN.md 是什么](#核心概念-designmd-是什么)
3. [awesome-design-md 项目介绍](#awesome-design-md-项目介绍)
4. [5 分钟快速上手](#5 分钟快速上手)
5. [多端设计规范](#多端设计规范)
6. [保客通设计实战](#保客通设计实战)
7. [常见问题 FAQ](#常见问题-faq)
8. [附录：可复用技能命令](#附录可复用技能命令)

---

## 为什么需要这个指南

### 你可能遇到的问题

```
❌ 找了设计师，但沟通成本太高，改来改去都不是想要的
❌ 网上找模板，风格不统一，东拼西凑很丑
❌ 让 AI 生成 UI，每次风格都不一样，没有一致性
❌ 要做多端适配（H5/iOS/Android/鸿蒙），不知道从何下手
```

### 这个指南能帮你

```
✅ 10 分钟生成专业级 UI 设计稿（PNG + HTML 可交互原型）
✅ 风格统一，所有页面遵循同一套设计规范
✅ 一次设计，多端自动适配
✅ 不需要懂 Figma/Sketch，只需要会打字
```

---

## 核心概念：DESIGN.md 是什么

### 一句话解释

**DESIGN.md** = AI 能看懂的"设计风格说明书"

### 类比理解

| 文档类型 | 谁读的 | 作用 | 类比 |
|---------|--------|------|------|
| `README.md` | 人类开发者 | 说明项目是什么 | 产品说明书 |
| `AGENTS.md` | AI Agent | 说明如何构建项目 | 施工图纸 |
| `DESIGN.md` | AI Agent | 说明项目应该长什么样 | **装修风格手册** |

### DESIGN.md 包含什么

```
DESIGN.md
├── 1. 视觉主题与氛围（比如：专业可信、现代 SaaS、蓝色系）
├── 2. 颜色 Palette（主色、功能色、中性色的 hex 值和用途）
├── 3. 字体规则（字号、字重、行高）
├── 4. 组件样式（按钮、卡片、导航、表格的具体样式）
├── 5. 布局原则（间距、网格、留白）
├── 6. 阴影与层级（深浅、前后关系）
├── 7. Do's and Don'ts（设计护栏）
├── 8. 响应式规则（多端适配）
└── 9. Agent Prompt 指南（快速使用模板）
```

### 为什么是 Markdown 格式

- **LLM 最容易理解**：大语言模型训练数据中大量 Markdown
- **人类也能读**：不需要特殊工具，记事本就能打开
- **无需配置**：不需要 JSON Schema、不需要 Figma 导出

---

## awesome-design-md 项目介绍

### 项目地址

https://github.com/VoltAgent/awesome-design-md

### 这是什么

一个收集了 **66+ 个知名品牌 DESIGN.md** 的仓库，你可以直接复制使用。

### 收录的品牌

| 分类 | 代表品牌 |
|------|---------|
| **AI & LLM** | Claude, Cohere, ElevenLabs, Mistral, Ollama, xAI |
| **开发者工具** | Cursor, Vercel, Raycast, Warp, Superhuman |
| **后端/DevOps** | Supabase, MongoDB, Sentry, ClickHouse |
| **SaaS/生产力** | Linear, Notion, Intercom, Zapier |
| **金融科技** | Stripe, Coinbase, Binance, Revolut |
| **消费品牌** | Apple, Nike, Airbnb, Tesla, Spotify |

### 如何使用

```bash
# 1. 复制你喜欢的品牌的 DESIGN.md
# 比如你喜欢 Linear 的风格：
curl -o DESIGN.md https://getdesign.md/linear.app/design-md

# 2. 告诉 AI
"使用 DESIGN.md 风格，创建一个仪表盘页面"

# 3. 得到结果
- PNG 设计稿
- HTML 可交互原型
```

---

## 5 分钟快速上手

### 步骤 1：准备环境

```bash
# 确保你有 Claude Code 或类似的 AI 工具
# 确保安装了 gstack 技能包
```

### 步骤 2：选择设计风格

去 https://getdesign.md/ 浏览可用的 DESIGN.md

**推荐选择**：
| 你的项目类型 | 推荐风格 |
|-------------|---------|
| 企业后台/SaaS | Linear, Stripe, Supabase |
| C 端产品 | Notion, Airbnb, Spotify |
| 金融科技 | Stripe, Coinbase, Revolut |
| 开发者工具 | Vercel, Cursor, Raycast |

### 步骤 3：复制 DESIGN.md

```bash
# 以保客通为例，我们融合了多个品牌风格
# 你可以直接复制保客通的 DESIGN.md
cp /path/to/baoke-tong/DESIGN.md /your/project/
```

### 步骤 4：生成设计稿

告诉 AI：

```
使用 DESIGN.md 风格，生成一个 [页面类型] 的设计稿。

要求：
- 页面功能：[描述页面是做什么的]
- 目标用户：[谁会使用这个页面]
- 核心元素：[需要包含哪些内容]
- 多端适配：H5 + iOS + Android + 鸿蒙
```

### 步骤 5：查看结果

AI 会生成：
- **PNG 截图**：静态设计稿，方便预览
- **HTML 原型**：可交互原型，用浏览器打开

---

## 多端设计规范

### 为什么需要多端适配

```
同一个 APP，在不同设备上的展示方式不同：
- 手机竖屏 vs 平板横屏
- iOS 的圆角风格 vs Android 的 Material Design
- 鸿蒙的原子化服务卡片
```

### 保客通多端适配规则

```css
/* 断点定义 */
:root {
  --breakpoint-mobile: 375px;    /* 手机 */
  --breakpoint-tablet: 768px;    /* 平板 */
  --breakpoint-desktop: 1024px;  /* 桌面 */
}

/* 手机 - 竖屏单列布局 */
@media (max-width: 767px) {
  .container { padding: 16px; }
  .card { margin-bottom: 16px; }
  .navbar { height: 56px; }
  .button { height: 44px; } /* 最小触摸目标 */
}

/* 平板 - 横屏双列布局 */
@media (min-width: 768px) and (max-width: 1023px) {
  .container { padding: 24px; }
  .card { margin-bottom: 24px; }
  .grid { grid-template-columns: 1fr 1fr; }
}

/* 桌面 - 多列复杂布局 */
@media (min-width: 1024px) {
  .container { max-width: 1440px; margin: 0 auto; }
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* 鸿蒙原子化服务卡片 */
/* 特定尺寸：2x2, 2x4, 4x4 网格 */
.harmony-card-2x2 {
  width: 160px;
  height: 160px;
  border-radius: 16px;
}
```

### 各平台设计规范参考

| 平台 | 官方文档 | 关键差异 |
|------|---------|---------|
| **H5** | W3C 标准 | 响应式布局，触摸优先 |
| **iOS** | Human Interface Guidelines | 圆角更大、毛玻璃效果、底部导航 |
| **Android** | Material Design 3 | 卡片阴影、悬浮按钮、顶部导航 |
| **鸿蒙** | HarmonyOS Design | 原子化服务卡片、流转动画 |

---

## 保客通设计实战

### 已生成的设计稿清单

| 页面类型 | HTML 原型 | PNG 截图 | 说明 |
|---------|----------|---------|------|
| **首页模块 (3 个)** |
| 内容生成中心 | ✅ `content-gen-homepage.html` | ✅ `content-gen-variant-A.png` | 朋友圈/短视频/海报文案生成 |
| 客户画像管理 | ✅ `customer-homepage-wireframe.html` | ✅ `customer-variant-B.png` | 客户列表、标签、分层 |
| 跟进管理 | ✅ `followup-homepage.html` | ✅ `followup-variant-C.png` | 跟进计划、待办、日历 |
| **核心功能页面 (7 个)** |
| 登录/注册页 | ✅ `login-page.html` | ✅ `login-page.png`, `register-page.png` | 左右分栏品牌展示 + 表单 |
| 客户详情页 | ✅ `customer-detail.html` | ✅ `customer-detail.png` | 三栏布局、时间线跟进记录 |
| 设置页 | ✅ `settings-page.html` | ✅ 5 张 PNG（账户/安全/通知/AI/企业） | 左侧导航右侧内容 |
| 数据分析仪表盘 | ✅ `analytics-page.html` | ✅ `analytics-page.png` | 数据卡片 + 图表 + 表格 |
| 工作台/首页仪表盘 | ✅ `dashboard.html` | - | 用户登录后第一个页面 |
| 帮助中心/FAQ | ✅ `help-center.html` | - | 手风琴式问题列表 |
| 内容详情页 | ✅ `content-detail-page.html` | - | 朋友圈文案/短视频脚本详情 |
| 会员订阅/定价页 | ✅ `finalized.html` | - | 3 个价格方案对比 |

### 设计稿位置

```
~/.gstack/projects/percyli4718-openclaw/designs/
├── baoke-tong-homepage-20260416/   # 首页模块
└── baoke-tong-pages-20260416/      # 功能页面
```

### 如何查看

```bash
# 用浏览器打开 HTML 原型
open ~/.gstack/projects/percyli4718-openclaw/designs/baoke-tong-pages-20260416/login-page.html
```

---

## 常见问题 FAQ

### Q1: 我没有设计背景，怎么判断设计好不好看？

**A**: 遵循 3 个简单原则：
1. **对齐**：所有元素要么左对齐，要么居中对齐
2. **留白**：元素之间间距不小于 16px
3. **颜色**：全页不超过 5 种主色

### Q2: AI 生成的设计稿，能直接用于开发吗？

**A**: 
- **HTML 原型**：可以作为开发参考，但需要手写生产代码
- **PNG 截图**：可以给设计师作为灵感参考
- **DESIGN.md**：可以作为团队的设计规范文档

### Q3: 我想要别的品牌风格怎么办？

**A**: 去 https://getdesign.md/ 复制你喜欢的品牌的 DESIGN.md，然后告诉 AI "使用新的 DESIGN.md 风格"

### Q4: 多端适配是怎么工作的？

**A**: 
1. AI 生成设计稿时，会自动考虑不同屏幕尺寸
2. HTML 原型中包含响应式 CSS
3. 开发时使用 uni-app 等跨平台框架，一套代码编译多端

### Q5: 设计稿不满意怎么办？

**A**: 
1. 告诉 AI 具体哪里不满意（比如"按钮太小"、"颜色太亮"）
2. AI 会生成迭代版本
3. 可以要求生成多个变体（variant）供选择

### Q6: 页面之间有交互跳转吗？

**A**: 
**有！** 所有 HTML 原型都已添加统一的导航栏，支持页面间跳转：

```
✅ 顶部导航栏：工作台 | 内容生成 | 客户管理 | 跟进管理 | 数据分析 | 帮助中心 | 设置
✅ 搜索框：支持关键词搜索（演示模式）
✅ 通知按钮：显示未读通知数
✅ 用户菜单：点击跳转到设置页面

📍 快速查看所有页面：打开 `index.html` 演示索引页
```

### Q7: HTML 原型和真实 App 有什么区别？

**A**: 

| 功能 | HTML 原型 | 真实 App |
|------|----------|---------|
| 页面跳转 | ✅ 支持 | ✅ 支持 |
| 按钮点击 | ✅ 支持（部分演示） | ✅ 完整功能 |
| 表单提交 | ⚠️ 演示模式 | ✅ 完整功能 |
| 数据持久化 | ❌ 无 | ✅ 有 |
| API 调用 | ❌ 无 | ✅ 有 |
| 状态管理 | ❌ 简单 | ✅ 完整 |

**HTML 原型的用途**：
- ✅ 设计评审：确认 UI 风格和布局
- ✅ 交互演示：给客户/团队展示产品流程
- ✅ 开发参考：前端工程师照着实现

---

## 附录：可复用技能命令

### /ai-ui-design 命令（推荐）

**用途**：一键生成 UI 设计稿

**使用方法**：
```
/ai-ui-design --page 登录页 --style Linear --variants 3
```

**参数**：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--page` | 页面类型（登录页/仪表盘/详情页等） | 必填 |
| `--style` | 设计风格（Linear/Stripe/Supabase 等） | DESIGN.md |
| `--variants` | 生成几个变体 | 3 |
| `--platform` | 目标平台（h5/ios/android/harmony） | all |
| `--output` | 输出目录 | `~/.gstack/designs/{project}-{date}/` |

**输出**：
- PNG 设计稿 × N 个变体
- HTML 可交互原型
- DESIGN.md 设计规范

---

## 后续项目全局设置

### 方法 1：项目级 DESIGN.md（推荐）

每个项目根目录放一个 `DESIGN.md`：

```bash
# 项目 A
/project-a/DESIGN.md

# 项目 B
/project-b/DESIGN.md
```

### 方法 2：全局技能命令

将 `/ai-ui-design` 添加到你的 Claude Code 技能库：

```bash
# 位置：~/.claude/skills/ai-ui-design/SKILL.md
# 任何项目都可以使用
/ai-ui-design --page 仪表盘 --style Stripe
```

### 方法 3：设计系统复用

建立个人设计系统库：

```
~/design-systems/
├── linear-style/
│   ├── DESIGN.md
│   └── components/
├── stripe-style/
│   ├── DESIGN.md
│   └── components/
└── notion-style/
    ├── DESIGN.md
    └── components/
```

---

## 总结

### 核心流程

```
选择风格 (awesome-design-md)
    ↓
复制 DESIGN.md
    ↓
告诉 AI 生成需求
    ↓
得到 PNG + HTML
    ↓
确认或迭代
    ↓
交付开发
```

### 关键要点

1. **DESIGN.md 是核心**：它定义了设计风格，AI 照着它生成
2. **多端适配要提前考虑**：在 prompt 里说明需要适配的平台
3. **迭代是正常的**：第一版不满意很正常，告诉 AI 具体改哪里
4. **HTML 原型比 PNG 更有用**：可以交互，能看到真实效果

### 下一步

- 尝试为其他项目生成设计稿
- 创建你自己的 DESIGN.md
- 将 `/ai-ui-design` 命令分享给团队

---

**文档版本**：v1.0  
**维护者**：保客通团队  
**反馈**：欢迎提 Issue 或 PR