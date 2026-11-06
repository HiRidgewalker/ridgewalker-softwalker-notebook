---
title: "UI 术语与设计风格笔记"
---

# UI 术语与设计风格笔记

> 由旧稿重新整理版本，从单一的 "Hug 概念解释" 扩展为完整的 UI 设计术语速查 + 设计风格分类扫盲。
> 旧稿目录已清理，当前以本文为准。
> Figma 风格确认五大维度见 [Figma笔记](../figma/figma.md)。

---

## 1. Figma Auto Layout 三种尺寸模式

这是 Auto Layout 最核心的三个概念，原笔记中已有详细举例，下面是**完整对比 + 前端类比**。

| 模式 | 中文理解 | 谁决定大小 | 前端类比 |
|---|---|---|---|
| **Hug** | 包裹内容 | 内容决定 | `width: fit-content` / `display: inline-block` |
| **Fixed** | 固定尺寸 | 手动写死宽高 | `width: 200px`（绝对值） |
| **Fill container** | 填充父容器 | 父容器决定 | `width: 100%` / `flex: 1` |

### 1.1 Hug（包裹内容）

**典型场景**：按钮、Tag、标签、气泡、输入框自适应宽度

**实战技巧**：

- 做自适应按钮：文本用 Hug → 按钮 Frame 用 Hug → 加 padding → 自动按钮组件
- 限制最大宽度：外层 `Fixed`，内层 `Hug`（类比 CSS `max-width` 思路）

**常见误区 ⚠️**：

> 为什么我的 Auto Layout 一直变大？

通常原因：子元素是 Hug → 内容变多 → 父容器跟着变 → 父容器 Hug → 一路向上传染。

**记忆口诀**：Hug = 抱住内容不松手 🤗（内容多抱大一点，内容少抱小一点）

### 1.2 Fixed（固定）

- 写死宽高，不会随内容/父容器变化
- 适合：固定尺寸图标、固定高度 Header、像素级还原的画板

### 1.3 Fill container（填充父容器）

- 拉伸占满父容器剩余空间
- 适合：表格列宽、Grid 子项、卡片内文区
- 与 `flex: 1` 等价，多个 `Fill` 元素按比例分配剩余空间

### 1.4 三者嵌套示例

```
父 Frame（Horizontal Auto Layout）
├── 子 A: Fixed 100×100     ← 固定头像
├── 子 B: Fill container    ← 自适应文字区
└── 子 C: Hug               ← 右侧按钮
```

---

## 2. Auto Layout 其他核心概念

| 概念 | 说明 |
|---|---|
| **Direction** | Horizontal（横排）/ Vertical（竖排）/ **Wrap**（换行，类比 flex-wrap） |
| **Item Spacing** | 子元素之间的间距（类比 `gap`） |
| **Padding** | 父容器内边距（类比 CSS `padding`） |
| **Align** | 子元素对齐方式（Left / Center / Right / Stretch） |
| **Counter Axis Align** | 垂直方向对齐（Min / Center / Max / Baseline） |
| **Absolute Position** | 取消 Auto Layout 影响，子元素自由定位 |

---

## 3. 常用 UI 术语速查表

### 3.1 基础结构

| 术语 | 一句话解释 |
|---|---|
| **Frame** | Figma 的基础画板容器，可嵌套、可设尺寸模式 |
| **Group** | 把多个元素编组（不创建新容器，不能独立设尺寸模式） |
| **Layer / Object** | 任意元素统称（形状、文字、图片、组件实例等） |
| **Page** | 一个 Figma 文件可以有多个 Page（设计稿、原型、组件库分开） |

### 3.2 复用与组件化

| 术语 | 一句话解释 |
|---|---|
| **Component** | 可复用的主组件（类似 React 组件本体） |
| **Instance** | Component 的实例副本（类似 React 组件实例） |
| **Variant** | Component 的多状态变体（按钮的 default/hover/disabled） |
| **Properties** | Component 暴露的可配置项（文字、icon、状态） |
| **Design System** | 一整套 Component + Token + 规范的合集 |

### 3.3 约束与变量

| 术语 | 一句话解释 |
|---|---|
| **Constraints** | 父容器 resize 时，子元素的吸附规则（Left / Right / Center / Left&Right / Scale） |
| **Variables** | 设计变量（颜色 / 字号 / 间距），是 Design Token 的 Figma 落地 |
| **Modes** | Variables 的多模式（亮 / 暗主题、品牌 A / 品牌 B） |
| **Token** | 设计原子（颜色 / 字号 / 间距 / 圆角等），Variables 是其载体 |

### 3.4 原型与交互

| 术语 | 一句话解释 |
|---|---|
| **Prototype** | 把画稿之间的跳转、过渡、手势连起来形成可点击流程 |
| **Hotspot** | 触发跳转的热点区域 |
| **Flow** | 多个画稿之间的跳转关系图 |
| **Smart Animate** | 自动补间动画（类似 CSS transition） |
| **Overlay** | 弹层 / 浮层的展示方式 |

### 3.5 形状与效果

| 术语 | 一句话解释 |
|---|---|
| **Boolean Operation** | 布尔运算（Union / Subtract / Intersect / Exclude），组合形状 |
| **Mask** | 遮罩，只显示指定形状范围内的内容 |
| **Effect** | 阴影 / 模糊 / 内阴影 / 玻璃模糊等视觉效果 |
| **Blend Mode** | 混合模式（Multiply / Screen / Overlay 等） |

---

## 4. 设计风格分类扫盲

按时间 / 流行度排列，每个风格给出**特点 + 适用产品**。

| 风格 | 视觉特点 | 典型适用 |
|---|---|---|
| **极简主义（Minimalism）** | 大留白、克制配色、强排版 | 工具类 SaaS、Apple 生态、高端品牌 |
| **瑞士风（Swiss / International）** | 网格、Helvetica、无衬线、几何 | 出版物、政府 / 企业官网 |
| **拟物（Skeuomorphism）** | 模拟现实质感（皮革、木纹、阴影） | 已过时，仅复古设计 / 特定游戏 |
| **扁平化（Flat Design）** | 无渐变无阴影、纯色块 | 通用，是 2014 后主流 |
| **新拟物（Neumorphism）** | 低对比、单光源阴影、凸起 / 凹陷感 | 概念稿、特效作品，不适合长内容阅读 |
| **玻璃拟态（Glassmorphism）** | 半透明、模糊背景、彩色光晕 | 营销页、登录页、Apple 风 |
| **孟菲斯（Memphis）** | 几何拼贴、撞色、波点、锯齿 | 创意品牌、儿童 / 玩具、文创 |
| **Y2K** | 紫粉霓虹、金属感、2000 年代电脑元素 | 时尚、美妆、亚文化 |
| **赛博朋克（Cyberpunk）** | 霓虹、故障、暗黑 + 强光 | 游戏、电竞、科技品牌 |
| **暗黑模式（Dark Mode）** | 深色背景、低饱和高亮 | 已是标配而非风格，工具 / 影音 / 开发者产品必做 |
| **极光（Aurora）** | 渐变光晕、流体感 | 2020~2024 营销页常见 |
| **等距 2.5D（Isometric）** | 等距投影、几何立体 | 解释型插画、数据可视化、引导页 |

### 选型速记

- **B2B SaaS / 工具**：极简 + 暗黑双模
- **消费 / 内容**：玻璃拟态 + 渐变极光
- **游戏 / 二次元**：赛博 / Y2K / 角色化
- **品牌官网 / 营销**：根据品牌故事挑，孟菲斯 / 极简 / 极光 都行
- **儿童 / 教育**：孟菲斯 / 扁平 + 高饱和

---

## 5. 前端视角的 UI 设计思维映射

| 前端概念 | Figma 对应 |
|---|---|
| `display: flex` | Auto Layout |
| `flex-direction` | Direction (Horizontal/Vertical) |
| `gap` | Item Spacing |
| `padding` | Padding |
| `flex: 1` | Fill container |
| `width: fit-content` | Hug |
| `position: absolute` | Absolute Position |
| `box-shadow` | Effect → Drop Shadow |
| `backdrop-filter: blur` | Effect → Background Blur（玻璃拟态） |
| `transition` | Smart Animate |
| 组件 props | Component Properties |
| Theme / CSS 变量 | Variables + Modes |

> 理解了这层映射，前端工程师看 Figma 文件几乎零学习成本。