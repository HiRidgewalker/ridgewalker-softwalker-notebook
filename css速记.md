# 📘 CSS 常用属性总结文档

---

# 一、CSS 属性分类总览

```text
CSS 属性主要分为三类：

1️⃣ 继承属性（会从父元素传递给子元素）
2️⃣ 非继承属性（只作用自身）
3️⃣ 布局属性（影响子元素布局行为）
```

---

# 二、常用“继承属性”（会向内扩散）

👉 特点：子元素默认继承父元素

---

## 🎨 文本与字体相关（最重要）

|属性|作用|
|---|---|
|color|文字颜色|
|font-size|字体大小|
|font-family|字体|
|font-weight|字重|
|line-height|行高|
|text-align|对齐方式|
|letter-spacing|字间距|
|word-spacing|单词间距|

---

## 📝 列表相关

|属性|作用|
|---|---|
|list-style|列表样式|

---

## 👁️ 可见性相关

|属性|作用|
|---|---|
|visibility|是否可见|

---

## 🧠 示例

```css
.parent {
  color: red;
  font-size: 20px;
}
```

```html
<div class="parent">
  <p>会继承颜色和字体</p>
</div>
```

---

# 三、常用“非继承属性”（默认不会扩散）

👉 特点：只作用当前元素

---

## 📦 盒模型

|属性|作用|
|---|---|
|width / height|宽高|
|margin|外边距|
|padding|内边距|
|border|边框|

---

## 🎨 背景

|属性|作用|
|---|---|
|background|背景|
|background-color|背景色|
|background-image|背景图|

---

## 🧱 布局基础

|属性|作用|
|---|---|
|display|布局方式|
|position|定位方式|
|top / left|定位偏移|
|z-index|层级|

---

## 🔄 示例

```css
.parent {
  background: red;
}
```

👉 子元素不会变红 ❌

---

# 四、布局类属性（影响子元素行为）

👉 不是继承，但会“改变子元素规则”

---

## 🔥 Flex 布局

|属性|作用|
|---|---|
|display: flex|开启 flex|
|flex-direction|主轴方向|
|justify-content|主轴对齐|
|align-items|交叉轴对齐|

👉 子元素变成 flex item

---

## 🔥 Grid 布局

|属性|作用|
|---|---|
|display: grid|开启网格|
|grid-template-columns|列定义|
|gap|间距|

---

## 🔥 定位

|属性|作用|
|---|---|
|position: relative|作为参考|
|position: absolute|相对父元素定位|

---

## 🔥 overflow

|属性|作用|
|---|---|
|overflow: hidden|裁剪内容|

---

# 五、特殊“看似扩散”的情况（重点）

---

## ⚠️ 1️⃣ margin 塌陷

```css
.parent {
  margin-top: 20px;
}
.child {
  margin-top: 30px;
}
```

👉 实际只取一个 margin

---

## ⚠️ 2️⃣ 盒模型影响布局

```css
div {
  width: 200px;
  padding: 20px;
}
```

👉 会影响整体占位

---

## ⚠️ 3️⃣ line-height 影响子元素

👉 继承但表现复杂

---

# 六、常用 CSS 属性功能总结（高频）

---

## 📦 布局

```css
display
position
float
flex
grid
```

---

## 📏 尺寸

```css
width
height
max-width
min-height
```

---

## 📐 间距

```css
margin
padding
gap
```

---

## 🎨 外观

```css
color
background
border
box-shadow
opacity
```

---

## 🔤 文本

```css
font-size
font-weight
text-align
line-height
```

---

## 🧭 定位

```css
position
top
left
z-index
```

---

## 🌀 动画

```css
transition
transform
animation
```

---

# 七、继承 vs 非继承（快速记忆）

---

## ✅ 记忆口诀

```text
文字相关 → 会继承
盒模型 → 不继承
布局 → 不继承但会影响子元素
```

---

# 八、终极总结（一句话）

```text
CSS 不会向外扩散，
部分属性会向内继承，
布局属性会改变子元素行为
```



---
---


`rem` 是 CSS 里的一个**长度单位（单位）**，全称是：

👉 **root em（基于根元素的 em）**

---

## 🧠 一句话理解

👉 `1rem = 根元素（html）的 font-size`

---

## 📦 举个例子

html {  
  font-size: 16px;  
}  
  
div {  
  width: 2rem;  
}

👉 结果：

2rem = 2 × 16px = 32px

---

## 🔍 rem vs em（容易混）

### 🔸 rem（推荐）

html { font-size: 16px; }  
  
div { font-size: 2rem; }  /* = 32px */

👉 永远基于 `html`

---

### 🔸 em

.parent { font-size: 20px; }  
.child { font-size: 2em; }

👉 `2em = 40px`（基于父元素）

⚠️ em 会**层层叠加（容易乱）**

---

## 📱 rem 的核心用途（重点）

👉 **做响应式布局**

例如：

html {  
  font-size: 62.5%;  /* 1rem = 10px */  
}  
  
div {  
  width: 10rem; /* = 100px */  
}

👉 好处：

- 计算简单（1rem = 10px）
- 统一缩放

---

## 🧠 实际开发中的套路

### 🔹 改根字体 = 整体缩放

html {  
  font-size: 14px;  
}

👉 整个页面会一起变小

---

## 📌 总结

👉 `rem` 本质：

> **相对于 html 字体大小的单位**

---

## ⚡ 对比总结

|单位|基准|
|---|---|
|rem|html|
|em|父元素|
|px|固定像素|

---

如果你做 React + Vite 项目，我可以告诉你一套**前端常用 rem + 适配方案（移动端 / PC）**，实战很有用 👍

---
---
`vh` 是 CSS 里的一个**视口单位（viewport unit）**

---

## 🧠 一句话理解

👉 `1vh = 浏览器可视区域高度的 1%`

---

## 📦 举个例子

假设当前浏览器窗口高度是 **1000px**

div {  
  height: 50vh;  
}

👉 结果：

50vh = 50% × 1000px = 500px

---

## 📱 常见用法（非常重要）

### 🔹 占满全屏

div {  
  height: 100vh;  
}

👉 元素高度 = 整个屏幕高度

---

### 🔹 做全屏页面（React 常用）

.container {  
  height: 100vh;  
}

👉 用于：

- 登录页
- 全屏背景
- Dashboard

---

## 🔍 和 rem / px 的区别

|单位|基准|
|---|---|
|vh|屏幕高度|
|rem|html 字体|
|px|固定像素|

---

## ⚠️ 常见坑（重点）

### ❗ 移动端问题（特别重要）

在手机浏览器中：

👉 `100vh` 可能 **大于实际可见高度**

原因：

- 浏览器地址栏（顶部/底部）会动态显示/隐藏

---

### ✅ 解决方案（了解即可）

height: 100dvh;

👉 `dvh = dynamic viewport height`（更准确）

---

## 📌 总结

👉 `vh` 本质：

> **相对于浏览器高度的百分比单位**

---

## ⚡ 常见组合

width: 100vw;   /* 宽度占满屏幕 */  
height: 100vh;  /* 高度占满屏幕 */

---

如果你愿意，我可以把 **vw / vh / rem / px 的使用场景 + 实战建议**一次性帮你理清（前端布局核心知识）。

---
---
`svh` 是 CSS 里的一种**新视口单位（viewport unit）**，专门解决移动端 `vh` 的问题。

---

## 🧠 一句话理解

👉 `1svh = 视口“最小高度”的 1%`

---

## 📱 为什么会有 svh？

在手机浏览器中：

- 地址栏（顶部/底部）会**出现 / 隐藏**
- 导致页面高度不断变化

👉 于是就有三种单位：

---

## 🔍 三种 vh 对比（重点）

|单位|含义|特点|
|---|---|---|
|`vh`|传统视口高度|不稳定（移动端有坑）|
|`svh`|**small viewport height**|👉 最小高度（最安全）|
|`lvh`|large viewport height|最大高度|
|`dvh`|dynamic viewport height|实时变化|

---

## 📦 举个例子

假设手机浏览器：

- 地址栏显示时：高度 = 700px
- 地址栏隐藏时：高度 = 800px

那么：

1svh = 700px / 100 = 7px  
1lvh = 800px / 100 = 8px

---

## ✅ 实际用法

### 🔹 防止内容被遮挡（推荐）

.container {  
  height: 100svh;  
}

👉 永远不会被浏览器 UI 挡住

---

### 🔹 想要“完全填满屏幕”（更现代）

.container {  
  height: 100dvh;  
}

👉 会随地址栏变化动态调整

---

## ⚠️ 怎么选？

👉 简单记：

- 要稳定 → 用 `svh`
- 要自适应 → 用 `dvh`
- 不推荐 → `vh`（移动端有坑）

---

## 📌 总结

👉 `svh` 本质：

> **取“最小可视高度”的视口单位，保证页面不会被遮挡**

---

如果你在做 React + Vite 的移动端页面，这几个单位（`vh / svh / dvh`）用错会直接导致 UI 出 bug，我可以给你一套**实际项目推荐写法（很实用）** 👍