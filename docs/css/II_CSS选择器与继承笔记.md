---
sidebar_position: 2
title: "CSS 选择器与继承笔记"
---


# CSS 选择器与继承笔记

> 本篇覆盖 4 类选择器、优先级（specificity）计算、继承性、层叠规则。
> 详细规范：[MDN 选择器](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_selectors)、[MDN 优先级](https://developer.mozilla.org/zh-CN/docs/Web/CSS/Specificity)、[MDN 继承](https://developer.mozilla.org/zh-CN/docs/Web/CSS/inheritance)

---

## 1. 4 类选择器

### 1.1 基础选择器

| 写法 | 名称 | 示例 | 说明 |
| --- | --- | --- | --- |
| `*` | 通配 | `* { margin: 0; }` | 选中所有元素 |
| `tag` | 元素 | `p { ... }` | 选中所有 `<p>` |
| `.class` | 类 | `.btn { ... }` | 选中所有 class 含 `btn` |
| `#id` | ID | `#header { ... }` | 选中 id 为 `header`（**唯一**） |

### 1.2 组合选择器

| 写法 | 名称 | 含义 |
| --- | --- | --- |
| `A, B` | 并集 | A 或 B |
| `A B` | 后代 | A 内任意层级的 B |
| `A > B` | 子代 | A 的**直接**子级 B |
| `A + B` | 相邻兄弟 | 紧跟在 A 后的 B |
| `A ~ B` | 通用兄弟 | A 后的所有 B |

### 1.3 属性选择器

```css
[disabled]                  /* 有 disabled 属性 */
[type="text"]               /* 属性等于某值 */
[class~="btn"]              /* 属性值含独立单词 btn */
[href^="https://"]          /* 属性值以...开头 */
[href$=".pdf"]              /* 属性值以...结尾 */
[href*="example"]           /* 属性值含...子串 */
```

### 1.4 伪类 / 伪元素

```css
/* 伪类 = 元素的特殊状态 */
a:hover        /* 鼠标悬停 */
li:nth-child(2)    /* 第 2 个子元素 */
input:focus    /* 聚焦 */
:not(.disabled)    /* 否定 */

/* 伪元素 = 元素的"虚拟子元素" */
p::before      /* 内容前插入 */
p::after       /* 内容后插入 */
::placeholder  /* 占位符 */
::selection    /* 选中文字 */
```

> 早期规范用 `:`，现在 CSS3 推荐 `::` 区分伪元素，但浏览器都接受单冒号。

---

## 2. 优先级（Specificity）

### 2.1 权重表

| 类型 | 权重 |
| --- | --- |
| `!important` | 最高（慎用） |
| 内联样式 `style="..."` | 1000 |
| ID 选择器 `#id` | 100 |
| 类/属性/伪类 `.class` / `[attr]` / `:hover` | 10 |
| 元素/伪元素 `div` / `::before` | 1 |
| 通配 `*` | 0 |
| 继承来的属性 | 0（最低） |

### 2.2 计算规则

把每条规则的"命中片段"按权重相加，**从左到右比较**：

```css
/* 0,1,0,1 → 0个ID + 1个class + 0个元素 + 1个伪元素 */
a:hover::after { ... }

/* 0,0,1,1 → 0+0+0+1=1 */
div { ... }

/* 0,1,1,0 → 0+0+1+1=11 */
ul li.active { ... }
```

**易错**：`#header .nav a` 是 `0,1,1,1`（110+1=111），不是 113。

### 2.3 优先级相同怎么办？

**后写的赢**（在样式表里出现的顺序）—— 这就是"**层叠**"。

```css
p { color: red; }
p { color: blue; }   /* 生效：blue */
```

### 2.4 `!important` 滥用后果

```css
.btn { color: blue !important; }
.btn { color: red !important; }   /* 也加 important 才覆盖 */
```

- 一旦开始用，后面要覆盖也只能加 `!important`，**形成军备竞赛**
- **原则**：尽量用选择器权重解决问题，只在改不动第三方样式时用 `!important`

---

## 3. 继承（Inheritance）

### 3.1 是什么

子元素默认**继承**父元素的部分属性（主要是文字相关）。盒模型、布局、定位**不继承**。

### 3.2 常见属性归属速记

#### 继承属性（"文字相关"）

| 分类 | 属性 |
| --- | --- |
| 文字 | `color`、`font`、`font-*`、`line-height`、`text-align`、`letter-spacing`、`word-spacing`、`white-space` |
| 列表 | `list-style`、`list-style-*` |
| 可见 | `visibility`、`cursor` |
| 表格 | `border-collapse`、`caption-side` |

#### 不继承属性（"盒模型 / 布局"）

| 分类 | 属性 |
| --- | --- |
| 盒模型 | `width`、`height`、`margin`、`padding`、`border` |
| 背景 | `background`、`background-color`（**默认不继承**） |
| 布局 | `display`、`position`、`top/left`、`float`、`z-index` |
| 其他 | `overflow`、`transform` |

### 3.3 强制属性继承

```css
.btn {
    /* 显式让不继承的属性继承 */
    background: inherit;
    color: inherit;
}
```

### 3.4 通用清零（重置样式）

```css
*, *::before, *::after {
    box-sizing: border-box;     /* 详见 03 */
    margin: 0;
    padding: 0;
}

body {
    font: 16px/1.5 system-ui, sans-serif;
    color: #333;
}
```

> 推荐用 [Normalize.css](https://github.com/necolas/normalize.css) 或 [modern-normalize](https://github.com/sindresorhus/modern-normalize) 替代手写清零。

---

## 4. 层叠（Cascade）规则

多条规则匹配同一个元素时，**按下面顺序**决定胜者：

1. **`!important`**（开发者的明确意图，最高）
2. **来源**（用户代理 < 用户 < 作者；带 `!important` 的反过来）
3. **优先级**（specificity，见 §2）
4. **书写顺序**（后写的赢）

> 速记：**先看是否加 important → 再看来源 → 再比权重 → 权重相同看顺序**。

---

## 5. 实战要点

### 5.1 调试优先级问题

打开浏览器 DevTools → Elements 面板 → 看右侧 Styles，能看到：

- 命中规则
- 被划掉的规则（被覆盖了）
- 来自哪个文件
- 选择器权重

### 5.2 BEM 命名（避免选择器过深）

```css
/* Block__Element--Modifier */
.card__title { ... }
.card__title--highlight { ... }
```

- 优点：选择器扁平，优先级好算，避免 `!important`
- 缺点：类名长

### 5.3 `:where()` / `:is()`（CSS 新特性，简化写法）

```css
/* 旧：写 3 个 */
:is(h1, h2, h3) { font-weight: bold; }

/* :where() 权重为 0（容易被覆盖） */
:where(h1, h2, h3) { color: gray; }
```

---

## 6. 常见坑

| 坑 | 说明 |
| --- | --- |
| ID 选择器权重太高 | 改不动 → 改用 class |
| 嵌套太深 | `.a .b .c .d` 权重 0,0,4,0，再覆盖要写更长选择器 |
| 忘记考虑伪类 | `a` 和 `a:hover` 是不同选择器，权重差 10 |
| `*` 通配选择 | 性能差，少用于大项目 |
| 内联样式和 `!important` 双重叠加 | 改不动只能重构 |
| 跨页面污染 | 全局选择器命中了不期望的元素 |
