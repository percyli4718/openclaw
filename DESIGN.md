# 保客通 (BaokeTong) DESIGN.md

**版本**：v0.1.0  
**日期**：2026 年 4 月 16 日  
**产品定位**：AI+ 保险获客系统 - "智能体 + 培训 + 课程 + 企业深度服务"四位一体

---

## 1. Visual Theme & Atmosphere

### 设计哲学
- **专业可信**：保险行业需要建立用户信任，避免过度娱乐化
- **现代 SaaS**：采用 2026 年主流的 SaaS 仪表板设计语言
- **蓝色系主色调**：传递专业、稳重、科技感
- **充足留白**：降低信息密度，提升可读性

### 视觉关键词
```
专业 | 可信 | 清爽 | 高效 | 现代
```

### 设计对标
- Linear 的极简专业感
- Stripe 的可信金融科技风格
- Supabase 的开发者友好暗色调

---

## 2. Color Palette & Roles

### 主色调
| 名称 | Hex | 用途 |
|------|-----|------|
| `primary-50` | #eff6ff | 背景高亮 |
| `primary-100` | #dbeafe | 边框、hover 背景 |
| `primary-500` | #3b82f6 | 主按钮、链接 |
| `primary-600` | #2563eb | 主按钮 hover、导航栏 |
| `primary-700` | #1d4ed8 | 导航栏渐变 |
| `primary-900` | #1e3a8a | 文字强调 |

### 功能色
| 名称 | Hex | 用途 |
|------|-----|------|
| `success-500` | #16a34a | 成功状态、完成标签 |
| `warning-500` | #d97706 | 警告状态、待跟进 |
| `danger-500` | #ef4444 | 错误状态、已逾期 |
| `info-500` | #0ea5e9 | 信息提示 |

### 中性色
| 名称 | Hex | 用途 |
|------|-----|------|
| `slate-50` | #f8fafc | 页面背景 |
| `slate-100` | #f1f5f9 | 卡片背景 |
| `slate-200` | #e2e8f0 | 边框 |
| `slate-400` | #94a3b8 | 次要文字 |
| `slate-600` | #475569 | 正文文字 |
| `slate-900` | #0f172a | 标题文字 |

### 渐变色
```css
/* 导航栏渐变 */
background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);

/* 卡片渐变 (可选) */
background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
```

---

## 3. Typography Rules

### 字体栈
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
             'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
```

### 字号层级
| 用途 | 字号 | 字重 | 行高 |
|------|------|------|------|
| 页面标题 | 28px | 700 | 1.2 |
| 模块标题 | 24px | 600 | 1.3 |
| 卡片标题 | 18px | 600 | 1.4 |
| 正文 | 15px | 400 | 1.5 |
| 次要文字 | 14px | 400 | 1.5 |
| 辅助文字 | 13px | 400 | 1.4 |
| 标签/徽章 | 12px | 500 | 1.3 |

### 字重使用规范
- `font-weight: 400` - 正文、次要文字
- `font-weight: 500` - 按钮、标签、中等强调
- `font-weight: 600` - 标题、导航激活状态
- `font-weight: 700` - 页面大标题、关键数据

---

## 4. Component Stylings

### 按钮
```css
/* 主按钮 */
.btn-primary {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  border: none;
  transition: all 0.2s;
}
.btn-primary:hover {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

/* 次按钮 */
.btn-secondary {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
```

### 卡片
```css
.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}
.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 大卡片 (功能入口) */
.card-large {
  padding: 32px;
  min-height: 280px;
  display: flex;
  flex-direction: column;
}
```

### 导航栏
```css
.navbar {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  height: 64px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-item {
  color: rgba(255, 255, 255, 0.85);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}
.nav-item.active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  font-weight: 500;
}
```

### 表格
```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 2px solid #e2e8f0;
}
.table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}
.table tr:hover {
  background: #f8fafc;
}
```

### 标签/徽章
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
}
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-green { background: #dcfce7; color: #166534; }
.badge-yellow { background: #fef3c7; color: #92400e; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-purple { background: #ede9fe; color: #5b21b6; }
```

### 输入框
```css
.input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s;
}
.input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
```

---

## 5. Layout Principles

### 间距尺度
```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
}
```

### 页面布局
- **顶部导航**：固定高度 64px，sticky 定位
- **页面边距**：两侧 32px，移动端 16px
- **卡片间距**：24px (桌面端)，16px (移动端)
- **内容最大宽度**：1440px

### 留白哲学
- 卡片内部 padding 不小于 24px
- 模块之间间距不小于 32px
- 避免信息过载，每屏聚焦 3-5 个核心元素

---

## 6. Depth & Elevation

### 阴影系统
```css
.shadow-sm { box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); }
.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.shadow-md { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.shadow-lg { box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1); }
.shadow-xl { box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15); }
```

### 表面层级
| 层级 | 用途 | 阴影 |
|------|------|------|
| Level 0 | 页面背景 | none |
| Level 1 | 卡片、表格 | shadow-sm |
| Level 2 | 导航栏、浮动元素 | shadow |
| Level 3 | 下拉菜单、弹窗 | shadow-lg |
| Level 4 | Toast、Tooltip | shadow-xl |

---

## 7. Do's and Don'ts

### ✅ Do
- 使用蓝色系作为主色调
- 保持充足的留白和呼吸感
- 使用圆角（8px-12px）传递友好感
- 用颜色区分状态（成功/警告/错误）
- 保持一致的间距尺度

### ❌ Don't
- 避免使用超过 5 种主色
- 避免过小的字号（正文不小于 14px）
- 避免纯黑文字（使用 slate-900 代替）
- 避免过重的阴影（保持轻盈感）
- 避免过多的动画效果（保持专业感）

---

## 8. Responsive Behavior

### 断点
```css
/* 移动端 */
@media (max-width: 640px) {
  .navbar { padding: 0 16px; }
  .card { padding: 16px; }
  .table { font-size: 13px; }
}

/* 平板端 */
@media (max-width: 1024px) {
  .card-large { min-height: 240px; }
}

/* 桌面端 */
@media (min-width: 1025px) {
  .container { max-width: 1440px; margin: 0 auto; }
}
```

### 触摸目标
- 按钮最小高度：44px
- 表格行最小高度：48px
- 图标点击区域：最小 44x44px

---

## 9. Agent Prompt Guide

### 快速 Prompt 模板
```
使用保客通 DESIGN.md 风格，创建一个 [页面类型] 页面。

要求：
- 主色调：#2563eb (蓝色系)
- 风格：现代 SaaS 仪表板，专业商务
- 布局：[顶部导航 + 卡片布局 / 列表布局 / 混合布局]
- 组件：[按钮/卡片/表格/表单等]
- 状态：[Loading/Empty/Success/Error/Partial]

参考已有的内容生成中心、客户画像管理、跟进管理模块设计风格。
```

### 颜色速查
| 用途 | 颜色 |
|------|------|
| 主按钮 | #2563eb |
| 导航栏 | linear-gradient(#1e40af, #3b82f6) |
| 成功 | #16a34a |
| 警告 | #d97706 |
| 错误 | #ef4444 |
| 边框 | #e2e8f0 |
| 卡片背景 | white |
| 页面背景 | #f8fafc |

---

## 附录：已生成的设计稿

| 模块 | HTML 原型 | PNG 截图 |
|------|---------|----------|
| 内容生成中心 | `content-gen-homepage.html` | `content-gen-variant-A.png` |
| 客户画像管理 | `customer-homepage-wireframe.html` | `customer-variant-B.png` |
| 跟进管理 | `followup-homepage.html` | `followup-variant-C.png` |

**设计稿位置**：`~/.gstack/projects/percyli4718-openclaw/designs/baoke-tong-homepage-20260416/`

---

**文档状态**：v0.1.0 初稿完成
**下一步**：将此 DESIGN.md 作为后续所有 UI 生成的约束条件
