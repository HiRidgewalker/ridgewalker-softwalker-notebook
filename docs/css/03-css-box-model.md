---
title: "CSS 盒模型笔记"
sidebar_position: 3
---

# CSS 盒模型笔记

> 本篇覆盖盒模型结构、`box-sizing`、margin 折叠（同级/父子/脱离文档流）、padding、border。
> 详细规范：[MDN 盒模型](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/Building_blocks/The_box_model)
> 配套 demo：[01_box_model.html](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/css/01_box_model.html)（浏览器打开看效果）

---

## 1. 盒模型结构

每个元素都是一个"盒子"，由 4 层从外到内组成：

```
┌──────────── margin (外边距) ────────────┐
│ ┌─────────── border (边框) ───────────┐ │
│ │ ┌───────── padding (内边距) ───────┐ │ │
│ │ │ ┌──────── content (内容) ──────┐ │ │ │
│ │ │ │  width × height 决定的区域    │ │ │ │
│ │ │ └─────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

- **content**：元素的实际内容区（文字、图片、子元素）
- **padding**：内边距，content 到 border 的距离（**继承父元素 background**）
- **border**：边框
- **margin**：外边距，盒子与外界的距离（**完全透明**）

---

## 2. `box-sizing`：两种盒模型

### 2.1 标准盒模型（`content-box`，默认）

```css
div {
    box-sizing: content-box;
    width: 100px;
    padding: 20px;
    border: 10px solid;
    margin: 15px;
}
```

实际占位宽度 = 100 (content) + 20×2 (padding) + 10×2 (border) + 15×2 (margin) = **190px**

> `width` 只控制 content 宽度，padding/border 算额外。

### 2.2 替代盒模型（`border-box`，**推荐**）

```css
div {
    box-sizing: border-box;
    width: 100px;        /* width 已含 content + padding + border */
    padding: 20px;
    border: 10px solid;
    margin: 15px;
}
```

实际占位宽度 = 100 (width) + 15×2 (margin) = **130px**

> 改 padding/border 不会撑大盒子，**布局更可控**。

### 2.3 推荐全局设置

```css
*, *::before, *::after {
    box-sizing: border-box;
}
```

> **所有现代 CSS reset 都默认这样**。原因：`width: 50%` 就真的是父容器一半，不会因为 padding 撑大。

---

## 3. margin 折叠（Margin Collapsing）⭐ 面试必问

### 3.1 是什么

**相邻**块级元素在**垂直方向**的 margin 会"合并"成最大值（不是相加）。

**3 个前提条件**（缺一不可）：
1. 处于**普通文档流**
2. **块级**元素
3. **垂直方向**（top/bottom）

### 3.2 同级兄弟元素

```css
.box1 { margin-bottom: 50px; }
.box2 { margin-top: 30px; }
```

实际间距 = `max(50, 30)` = **50px**（不是 80px！）

**特殊情况（正负 margin）**：

| 情况 | 规则 |
| --- | --- |
| 两个都是正数 | 取最大 |
| 一正一负 | 相加 |
| 两个都是负数 | 取最小（绝对值最大） |

```css
.box1 { margin-bottom: 50px; }
.box2 { margin-top: -20px; }   /* 50 + (-20) = 30px */
```

### 3.3 父子元素

**情况 1：发生折叠**（父元素**没有** border / padding / overflow / display:flow-root）

```css
.parent { margin-top: 50px; }   /* 这俩会折叠 */
.child  { margin-top: 30px; }
```

整体向上移动 50px（取最大）。

**情况 2：阻止折叠**（父元素有以下任一）

```css
.parent {
    padding: 1px;          /* ✅ 有 padding */
    /* border: 1px solid;  /* ✅ 有 border */
    /* overflow: hidden;   /* ✅ 有 overflow */
    /* display: flow-root; /* ✅ 现代写法 */
}
```

→ 父 margin + 子 margin **不再合并**。

### 3.4 脱离文档流就不折叠

| 情况 | margin 折叠 | 是否影响布局 |
| --- | --- | --- |
| 普通文档流 | ✅ 会折叠 | ✅ 会影响 |
| `float: left/right` | ❌ 不折叠 | ✅ 影响 |
| `position: absolute` | ❌ 不折叠 | ❌ 不占空间 |
| `position: fixed` | ❌ 不折叠 | ❌ 不占空间 |

> **脱离文档流只作用于自身**——子元素 absolute，父元素依然在文档流；兄弟一个 absolute，另一个还在流里。

### 3.5 一句话速记

> **margin 折叠 = 普通文档流 + 块级 + 垂直**——破坏任一条件就不折叠。

---

## 4. padding / border 速记

### 4.1 padding

```css
padding: 10px;                  /* 四边 */
padding: 10px 20px;             /* 上下 | 左右 */
padding: 10px 20px 30px;        /* 上 | 左右 | 下 */
padding: 10px 20px 30px 40px;   /* 上 右 下 左（顺时针） */
```

| 注意点 | 说明 |
| --- | --- |
| 不能为负 | padding 永远 ≥ 0 |
| 撑大盒子 | `content-box` 下 padding 会让盒子变大；`border-box` 下不会 |
| 背景继承 | 父元素 background 会延伸到 padding 区（这是 padding 和 margin 的关键区别） |

### 4.2 border

```css
border: 1px solid red;                    /* 简写 */
border-top: 2px dashed #333;              /* 单边 */
border-radius: 8px;                       /* 圆角 */
border-radius: 50%;                       /* 圆（正方形时） */
border-radius: 8px 0 8px 0;               /* 顺时针 */
```

| 注意点 | 说明 |
| --- | --- |
| `border-color` 简写 | 必须先有 `border-style` 才生效 |
| `border-collapse: collapse` | 表格边框合并 |
| 三角形 | 常用 `border` 拼三角形（`width:0; border: 10px solid transparent; border-top-color: red`） |

---

## 5. 实战要点

### 5.1 水平居中（不靠 Flex 的传统写法）

```css
.box {
    width: 200px;       /* 必须有宽度 */
    margin: 0 auto;     /* 水平居中 */
}
```

> 只对**块级 + 有宽度**的元素生效。

### 5.2 垂直居中（传统 3 种）

| 场景 | 写法 |
| --- | --- |
| 单行文字 | `line-height = height` |
| 已知高度块 | `position: absolute; top: 50%; margin-top: -height/2;` |
| 通用（推荐） | Flex，见 [IV_CSS布局笔记](04-css-layout.md) |

### 5.3 margin: auto 的妙用

```css
/* Flex 子项主轴上吸收剩余空间 */
.item { margin-left: auto; }

/* 绝对定位水平垂直居中 */
.abs-center {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    margin: auto;
    width: 100px; height: 100px;
}
```

---

## 6. 常见坑

| 坑 | 后果 | 解决 |
| --- | --- | --- |
| 没设 `box-sizing: border-box` | 加 padding 后盒子变大 | 全局重置 |
| 想用 margin 撑开父容器 | margin 折叠 | 改用 padding |
| 给行内元素设 `width/height` | 无效 | 改 `display: inline-block` 或 `block` |
| 表格里设 margin | 无效 | 改用 padding 或 `border-spacing` |
| 负 margin 让元素溢出 | 出现横向滚动条 | 父容器 `overflow: hidden` |
| margin 折叠失效 | 间距没像预期那样 | 检查父容器是否有 border/padding/overflow |
