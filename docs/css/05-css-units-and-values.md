---
title: "CSS 单位与值笔记"
sidebar_position: 5
---

# CSS 单位与值笔记

> 本篇覆盖长度单位（px/em/rem/vh/vw/svh/dvh/lvh/百分比）、颜色（hex/rgb/hsl/命名色）、关键字、响应式适配。
> 详细规范：[MDN 长度单位](https://developer.mozilla.org/zh-CN/docs/Web/CSS/length)、[MDN 颜色](https://developer.mozilla.org/zh-CN/docs/Web/CSS/color_value)
> 配套 demo：[03_units.html](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/css/03_units.html)

---

## 1. 长度单位速查表

### 1.1 绝对单位

| 单位 | 含义 | 适用 |
| --- | --- | --- |
| `px` | 像素（CSS 像素 ≈ 1/96 英寸） | 边框、阴影、图标尺寸 |
| `pt` | 1/72 英寸 | 打印 |
| `cm` / `mm` / `in` | 物理尺寸 | 打印 |

### 1.2 相对单位（更常用）

| 单位 | 相对 | 适用 |
| --- | --- | --- |
| `%` | 父元素的对应属性 | 宽度/高度自适应 |
| `em` | **父元素**的 `font-size` | 文字/图标缩放 |
| `rem` | **根元素 `<html>`**的 `font-size` | **响应式首选** |
| `ex` | 字符 `x` 的高度 | 极少用 |
| `ch` | 字符 `0` 的宽度 | 等宽字体布局 |
| `lh` / `rlh` | 元素的 `line-height` | 行高相关布局 |
| `vw` / `vh` | 视口宽/高的 1% | 全屏布局 |
| `svw` / `svh` | 视口**最小**宽/高的 1% | 移动端防遮挡 |
| `lvw` / `lvh` | 视口**最大**宽/高的 1% | 移动端 |
| `dvw` / `dvh` | 视口**动态**宽/高的 1% | 移动端自适应 |
| `vmin` / `vmax` | 视口较小/较大边的 1% | 横竖屏适配 |

---

## 2. 重点单位详解

### 2.1 `px` vs `em` vs `rem`

```css
html   { font-size: 16px; }     /* 1rem = 16px */
.parent { font-size: 20px; }     /* 1em（子元素里）= 20px */
.div1  { font-size: 2rem; }      /* = 32px（基于 html） */
.div2  { font-size: 2em; }       /* = 40px（基于 parent，层层叠加） */
```

| 维度 | px | em | rem |
| --- | --- | --- | --- |
| 基准 | 固定像素 | **父元素** font-size | **根 html** font-size |
| 嵌套叠加 | 不叠加 | **会**叠加（容易乱） | 不叠加 |
| 推荐 | 边框、阴影 | 文字内部 | **响应式首选** |

#### rem 适配套路

```css
/* 套路 1：1rem = 10px（计算方便） */
html { font-size: 62.5%; }      /* 默认 16px × 0.625 = 10px */
.box { width: 10rem; }          /* = 100px */

/* 套路 2：配合 JS 动态设置（移动端响应式） */
document.documentElement.style.fontSize =
    (document.documentElement.clientWidth / 10) + 'px';
```

> **优势**：用户改浏览器字号 → 整站同步缩放（无障碍友好）。

### 2.2 视口单位 `vh` / `vw` / `svh` / `dvh` / `lvh`

```css
.full-page { height: 100vh; }     /* 占满视口高度 */
.full-page { width: 100vw; }      /* 占满视口宽度 */
```

#### 移动端 `vh` 的坑 ⚠️

手机浏览器的**地址栏**会动态出现/隐藏 → `100vh` 可能**大于**实际可见高度。

```css
/* ❌ 移动端会被地址栏遮挡内容 */
height: 100vh;

/* ✅ 改用 dvh（动态） */
height: 100dvh;

/* ✅ 或 svh（取最小，最安全） */
height: 100svh;
```

#### 4 种视口高度速记

| 单位 | 含义 | 何时用 |
| --- | --- | --- |
| `vh` | 传统视口高度 | **不推荐**（移动端有坑） |
| `svh` | **小**视口高度（地址栏显示时） | **稳定**优先 |
| `lvh` | **大**视口高度（地址栏隐藏时） | 极少用 |
| `dvh` | **动态**视口高度（实时变化） | 想要"完全填满" |

---

## 3. 颜色

### 3.1 4 种写法

```css
/* 1. 命名色（最少，但最直观） */
color: red;
color: transparent;
color: currentColor;     /* 取父元素的 color 值 */

/* 2. hex（最常用） */
color: #ff0000;          /* 红 */
color: #f00;             /* 简写：每两位相同才能简写 */
color: #ff000080;        /* 最后两位是 alpha（00=透明, ff=不透明） */

/* 3. rgb / rgba */
color: rgb(255, 0, 0);
color: rgba(255, 0, 0, 0.5);    /* alpha 0~1 */

/* 4. hsl / hsla（设计师友好：色相-饱和度-亮度） */
color: hsl(0, 100%, 50%);        /* 红 */
color: hsla(0, 100%, 50%, 0.5);
```

### 3.2 现代写法：`color()` 函数

```css
color: color(display-p3 1 0 0);       /* P3 广色域 */
color: oklch(70% 0.15 30);            /* OKLCH 感知均匀 */
```

> 浏览器支持逐渐完善，写复杂主题或图片相关色域时用。

### 3.3 系统颜色

```css
background: Canvas;        /* 系统背景色（深浅模式自动跟随） */
color: CanvasText;         /* 系统文字色 */
```

> 跟随系统的浅色/深色模式，**写一次适应两种主题**。

---

## 4. 关键字与特殊值

### 4.1 常见关键字

| 关键字 | 含义 |
| --- | --- |
| `inherit` | 继承父元素 |
| `initial` | 用属性的初始值（每个属性不同） |
| `unset` | 能继承就继承，不能就用初始值（综合 inherit/initial） |
| `revert` | 回到浏览器默认（像没写 CSS 一样） |
| `auto` | 浏览器自动算（margin: 0 auto 居中就是这个） |
| `none` | 关闭（如 border: none） |

### 4.2 数值类

```css
line-height: 1.5;          /* 无单位：相对 font-size */
line-height: 24px;         /* 有单位：固定 */
z-index: 999;              /* 整数 */
opacity: 0.5;              /* 0~1 */
flex: 1;                   /* grow=1, shrink=1, basis=0% */
```

---

## 5. 函数式值

### 5.1 计算：`calc()`

```css
width: calc(100% - 40px);        /* 减固定值 */
width: calc(50% + 20px);         /* 加固定值 */
height: calc(100vh - 60px);      /* 视口减导航 */
```

> `+` `-` 两侧必须有空格；`*` `/` 可以不要。

### 5.2 极值：`min()` / `max()` / `clamp()`

```css
/* min(多个值) 取最小 */
width: min(500px, 100%);         /* 不超过 500px，但不超过父容器 */

/* max(多个值) 取最大 */
width: max(300px, 50%);          /* 至少 300px，但不少于 50% */

/* clamp(最小, 偏好, 最大) 三段式（响应式神器） */
font-size: clamp(14px, 2vw, 24px);   /* 最小 14、随 2vw、最大 24 */
padding: clamp(8px, 4vw, 32px);
```

> `clamp()` 是写**流体排版**的最简洁方式——不用 JS 监听 resize。

### 5.3 颜色函数

```css
background: linear-gradient(red, blue);
background: radial-gradient(circle, red, blue);
color: color-mix(in srgb, red 50%, blue);     /* 颜色混合 */
```

---

## 6. 响应式适配

### 6.1 媒体查询（传统）

```css
/* 768px 以下（手机） */
@media (max-width: 768px) {
    .sidebar { display: none; }
}

/* 768px ~ 1024px（平板） */
@media (min-width: 769px) and (max-width: 1024px) {
    .layout { grid-template-columns: 1fr 1fr; }
}

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
    body { background: #111; color: #eee; }
}

/* 减少动画 */
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; }
}
```

### 6.2 现代写法：容器查询

```css
.card-container {
    container-type: inline-size;
    container-name: card;
}

@container card (min-width: 400px) {
    .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

> 容器查询是**组件级响应式**——根据父容器尺寸而不是视口尺寸改样式。

### 6.3 三种响应式思路对比

| 思路 | 方式 | 适合 |
| --- | --- | --- |
| 媒体查询 | `@media (min-width: ...)` | 整页响应式 |
| 容器查询 | `@container` | 组件复用 |
| 流式（`clamp()` / `auto-fit`） | CSS 自带 | 字体 / 间距 / 卡片网格 |

---

## 7. 常见坑

| 坑 | 说明 |
| --- | --- |
| `em` 层层叠加 | 子元素 `font-size: 1.2em` 会被父元素放大影响 |
| `100vh` 移动端遮挡 | 改用 `100dvh` / `100svh` |
| `100vw` 出现横向滚动条 | 含滚动条宽度；用 `width: 100%` 替代 |
| 颜色忘加 `#` | `color: ff0000` 无效，要 `#ff0000` |
| `rgba(0,0,0,0.5)` 想覆盖父背景 | 实际是**叠加**——和 `opacity` 不同 |
| `clamp()` 单位混用 | 三个值必须单位一致（或全 px / 全 rem） |
| 媒体查询断点乱 | 推荐断点：640 / 768 / 1024 / 1280 / 1536 |
