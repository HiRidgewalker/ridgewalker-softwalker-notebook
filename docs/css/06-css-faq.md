---
title: "CSS 常见问题笔记"
sidebar_position: 6
---

# CSS 常见问题笔记

> 本篇按 **「问题 / 现象 / 解决 / 原理」** 四段模板收集 CSS 实战中踩过的坑。后续遇到同类问题直接 append 到这里。
> 工具：[MDN 中文](https://developer.mozilla.org/zh-CN/docs/Web/CSS)、[Can I Use](https://caniuse.com/)（查浏览器兼容）

---

## Q1. 垂直居中一个元素

### 问题

让一个元素在父容器中**水平 + 垂直**居中。

### 现象

- 文字居中能用 `text-align: center` + `line-height`，但**块级元素**不行
- `margin: 0 auto` 只解决水平方向
- `position: absolute` + `transform` 写法太繁琐

### 解决

#### 方法 1：Flex 一行搞定（**推荐**）

```css
.parent {
    display: flex;
    justify-content: center;   /* 水平 */
    align-items: center;       /* 垂直 */
}
```

#### 方法 2：Grid 更短

```css
.parent {
    display: grid;
    place-items: center;       /* = justify-items + align-items */
}
```

#### 方法 3：absolute + margin: auto

```css
.parent { position: relative; }
.child {
    position: absolute;
    inset: 0;                  /* top/right/bottom/left: 0 */
    width: 200px;
    height: 100px;
    margin: auto;
}
```

#### 方法 4：absolute + transform（不知道宽高时）

```css
.child {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
```

### 原理

- Flex/Grid 让子项自动按容器规则对齐
- `margin: auto` 在绝对定位里会吸收所有剩余空间
- `transform: translate(-50%)` 相对自身尺寸回退一半

---

## Q2. `position: sticky` 不生效

### 问题

想做一个"滚动到顶就吸住"的导航条，用 `position: sticky; top: 0;` 却不生效。

### 现象

- 元素不"吸"，直接滚出视口
- 或者吸住后又乱跳

### 解决

**4 个排查点**：

| 排查 | 原因 | 解决 |
| --- | --- | --- |
| 1. 父容器有 `overflow: hidden` / `auto` / `scroll` | sticky 的"吸附范围"被限制在父容器内 | 改用 `overflow: visible` |
| 2. 父容器高度 ≤ sticky 元素高度 | 没空间可"吸" | 父容器加高度 |
| 3. 元素兄弟有更高 `z-index` | 被盖住 | 显式设 `z-index` |
| 4. 想吸在**某个父容器的边**而不是视口 | sticky 只能相对最近的可滚动祖先 | 改父容器的滚动 |

### 原理

`position: sticky` 是 **`relative` + `fixed` 的混合**：
- 滚动未到临界点前 → 表现像 `relative`（在文档流里）
- 到达临界点后 → 表现像 `fixed`（吸在视口 / 父容器边）

它的"吸附参考"是**最近的滚动祖先**（默认视口）。如果祖先设了 `overflow: hidden`，该祖先就成了参考，sticky 只在它内部有效。

---

## Q3. flex 子项溢出 / 文字不换行

### 问题

Flex 容器里某个子项的文字太长，撑爆整个布局，旁边的兄弟被挤成 0 宽。

### 现象

```css
.parent { display: flex; }
/* 子项里有很长的一段英文/数字，撑出滚动条 */
```

### 解决

**关键属性：`min-width: 0`**

```css
.flex-item {
    min-width: 0;        /* 默认是 auto = 内容最小宽度 */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 文本溢出显示省略号三件套 */
```

或者：

```css
.flex-item {
    word-break: break-all;     /* 中文/长英文都能换 */
    overflow-wrap: break-word; /* 单词太长也能换 */
}
```

### 原理

Flex 子项默认 `min-width: auto`，意味着**最小宽度 = 内容宽度**——长字符串会让它撑爆容器。设为 `0` 后才能正常被压缩。

---

## Q4. margin 折叠 / 间距没像预期那样

详见 [III_CSS盒模型笔记 > 3-margin-折叠](03-css-box-model.md#3-margin-折叠margin-collapsing-面试必问)，这里只列排查清单：

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 父子 margin 合并 | 父元素没 border / padding / overflow | 父元素加 `overflow: hidden` 或改用 padding |
| 兄弟 margin 取大值 | 普通文档流垂直 margin 折叠 | 给其中一个加 `display: inline-block` / `float` |
| 想用 margin 推开父容器 | 折叠了 | 改用 padding |

---

## Q5. 元素被 `transform` / `opacity` 影响导致 `z-index` 失效

### 问题

设了 `z-index: 9999` 还是被兄弟元素盖住。

### 现象

DevTools 看层叠顺序，`z-index` 高的反而在下。

### 解决

排查这 3 个创建"**新层叠上下文**"的属性：

| 属性 | 会创建层叠上下文 |
| --- | --- |
| `position: relative/absolute/fixed` + `z-index` 有效 | ✅ |
| `opacity < 1` | ✅ |
| `transform` 不为 `none` | ✅ |
| `filter` 不为 `none` | ✅ |
| `will-change: opacity/transform` | ✅ |
| `mix-blend-mode` 不为 `normal` | ✅ |
| `isolation: isolate` | ✅ |

**调试方法**：在 DevTools → Layers 面板看实际的渲染层。

### 原理

`z-index` 只在**同一个层叠上下文**内比较。一旦父元素创建了新上下文，子元素的 z-index 只能和"父元素"这个整体的 z-index 比。

---

## Q6. 移动端 `100vh` 被地址栏遮挡

### 问题

移动端用 `height: 100vh` 做全屏容器，底部内容被浏览器地址栏挡住。

### 现象

- 滚动到底还有"看不见的下方"
- 设备旋转时布局抖动

### 解决

```css
/* ❌ 老写法（移动端有坑） */
.full-page { height: 100vh; }

/* ✅ 新写法（按场景选） */
.full-page { height: 100dvh; }    /* 动态填满，随地址栏变化 */
.full-page { height: 100svh; }    /* 取最小，永远不被遮挡 */
```

详见 [V_CSS单位与值笔记 > 2-2-视口单位](05-css-units-and-values.md#22-视口单位-vh--vw--svh--dvh--lvh)。

---

## Q7. flex/grid 子项被压缩成 0

### 问题

`flex: 1` 想要平均分配空间，结果某些子项变成 0 宽。

### 现象

```css
.parent { display: flex; }
.item   { flex: 1; }
/* 但长文本子项把别人挤没了 */
```

### 解决

```css
/* 关键：让 flex 子项可以缩小到 0 */
.parent { display: flex; }
.item   { flex: 1; min-width: 0; }   /* min-width: 0 是关键 */

/* 或者：把内容用 div 包裹 */
.item > .content { min-width: 0; }
```

### 原理

Flex 子项默认 `min-width: auto` = 内容宽度，长内容会"撑开自己"挤压别人。改 `0` 才允许被压缩。

---

## Q8. `position: absolute` 没找到参考元素

### 问题

绝对定位元素跑到视口左上角而不是父容器的角落。

### 现象

期望在 `.parent` 内部定位，结果飘到 body / viewport。

### 解决

**给祖先链上最近的元素加 `position: relative`**（或 `absolute/fixed`）：

```css
.parent {
    position: relative;   /* ← 这行是关键 */
}
.child {
    position: absolute;
    top: 10px;
    right: 10px;
}
```

### 原理

`absolute` 找"最近的**定位祖先**"（`position` 不是 `static` 的祖先）作参考。都没找到就用初始包含块（视口）。

---

## Q9.（占位）新问题追加示例

```markdown
## Q{N}. {问题标题}

### 问题
{一句话描述}

### 现象
- {关键表现 1}
- {关键表现 2}

### 解决
{命令 / 配置 / 代码改动}

### 原理
{为什么会这样}
```

> **使用说明**：
> - 遇到新问题 → 复制 Q9 模板 → 填四段 → 增到本文件末尾
> - 编号 Q10 / Q11 ... 顺延
> - 不需要的小节可以省略（如纯环境问题可省「原理」）
> - DevTools 截图可以用 `<img src="..." />` 引用
