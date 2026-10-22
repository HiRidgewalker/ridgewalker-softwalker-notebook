# CSS 布局笔记

> 本篇覆盖 5 种布局方式：文档流（normal flow）、浮动（float）、定位（position）、Flex、Grid。
> 详细规范：[MDN 文档流](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Normal_Flow)、[MDN Flex](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Flexbox)、[MDN Grid](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Grids)、[MDN 定位](https://developer.mozilla.org/zh-CN/docs/Web/CSS/position)
> 配套 demo：[02_flex.html](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/css/02_flex.html)

---

## 1. 文档流（Normal Flow）

### 1.1 是什么

**默认布局方式**。元素按 HTML 顺序自上而下排成两列：
- 块级（`display: block`）—— **垂直堆叠**，占满父容器宽度
- 行内（`display: inline`）—— **水平排列**，宽高由内容决定

### 1.2 元素类型速查

| `display` | 行为 | 典型标签 |
| --- | --- | --- |
| `block` | 垂直堆叠，可设宽高 | `div`、`p`、`h1`~`h6`、`ul`、`li` |
| `inline` | 水平排列，**不能**设宽高 | `span`、`a`、`em`、`strong` |
| `inline-block` | 水平排列，**可**设宽高 | `img`、`input`、`button` |
| `none` | 完全消失，不占空间 | （隐藏元素） |
| `contents` | 元素自身不渲染，子元素按"被提到上一层"渲染 | （少用） |

> `display: none` 不同于 `visibility: hidden`——前者**完全消失**（不占位），后者**不可见但占位**。

### 1.3 改变布局 = 离开文档流

`float`、`position: absolute/fixed` 会让元素**脱离文档流**（详见 §3、§4）。

---

## 2. 浮动（Float）—— 历史方案

### 2.1 是什么

让元素"飘"到左边或右边，文字围绕它。**曾是实现多列布局的唯一方案**（CSS 2.1 时代）。

```css
img { float: left; margin-right: 10px; }
```

### 2.2 浮动 4 个性质

| 性质 | 说明 |
| --- | --- |
| **脱离文档流** | 浮动元素不参与普通排版（不影响前后元素的垂直位置） |
| **互相贴靠** | 多个浮动元素会并排，到边缘换行 |
| **字围效果** | 文字会绕开浮动元素（典型应用：图文混排） |
| **收缩宽度** | 没设 width 的浮动元素，自动收缩为内容宽度 |

> ⚠️ **现代布局不要再用 float 做多列**——用 Flex / Grid 更清晰。

### 2.3 清除浮动

父容器**不会**被浮动子元素撑高（因为子元素脱离了文档流），需要"清除"：

```css
/* 1. 给父容器加 overflow（最简单） */
.parent { overflow: hidden; }

/* 2. 经典 clearfix（最稳） */
.clearfix::after {
    content: "";
    display: block;
    clear: both;
}
```

---

## 3. 定位（Position）⭐

### 3.1 5 个值

| 值 | 是否脱离文档流 | 参考点 | 用途 |
| --- | --- | --- | --- |
| `static`（默认） | ❌ | 文档流 | 普通排版 |
| `relative` | ❌（**占位**） | 自身原位置 | 微调 / 作 absolute 容器 |
| `absolute` | ✅ | 最近的"定位祖先" | 弹窗 / 下拉 / Tooltip |
| `fixed` | ✅ | 浏览器视口 | 吸顶导航 / 悬浮按钮 |
| `sticky` | ❌（在临界点前）/ ✅（之后） | 视口 | 吸顶 / 表格表头 |

### 3.2 定位三件套

定位元素（`relative` / `absolute` / `fixed` / `sticky`）可用 `top/right/bottom/left` 控制偏移：

```css
.box {
    position: absolute;
    top: 10px;
    right: 20px;
}
```

### 3.3 关键场景

#### 弹窗居中

```css
.modal {
    position: fixed;
    inset: 0;             /* top/right/bottom/left: 0 */
    margin: auto;
    width: 400px;
    height: 200px;
}
```

#### 吸顶导航

```css
.nav {
    position: sticky;
    top: 0;
    background: white;
    z-index: 100;
}
```

#### 父子定位关系

```css
.parent { position: relative; }   /* 作参考 */
.child  { position: absolute; top: 0; right: 0; }   /* 参考 parent */
```

### 3.4 z-index 与层叠上下文

`z-index` 只对**定位元素**（非 `static`）生效。

```css
.modal { z-index: 1000; }   /* 越大越靠上 */
```

> 同一个层叠上下文内比较 `z-index`；不同上下文看"祖先的 z-index"。**flex/grid 子项也参与层叠**。

---

## 4. Flex 布局 ⭐⭐⭐ 主力方案

### 4.1 启动

```css
.parent {
    display: flex;          /* 或 inline-flex */
}
```

### 4.2 父容器属性速查

| 属性 | 作用 | 常用值 |
| --- | --- | --- |
| `flex-direction` | 主轴方向 | `row`（默认）、`column`、`row-reverse`、`column-reverse` |
| `flex-wrap` | 溢出换行 | `nowrap`（默认）、`wrap`、`wrap-reverse` |
| `flex-flow` | 上两个简写 | `<direction> <wrap>` |
| `justify-content` | 主轴对齐 | `flex-start`、`flex-end`、`center`、`space-between`、`space-around`、`space-evenly` |
| `align-items` | 交叉轴对齐（**单行**） | `stretch`、`flex-start`、`flex-end`、`center`、`baseline` |
| `align-content` | 交叉轴对齐（**多行**） | 同 justify-content |
| `gap` | 子项间距 | `10px` 或 `10px 20px` |

### 4.3 子项属性速查

| 属性 | 作用 | 常用值 |
| --- | --- | --- |
| `flex-grow` | 剩余空间分配比例 | `0`（默认不放大）、`1`、`2` |
| `flex-shrink` | 空间不足时压缩比例 | `1`（默认）、`0`（不压缩） |
| `flex-basis` | 初始主轴尺寸 | `auto`（默认）、`0`、`200px` |
| `flex` | 上面三个的简写 | `none`、`1`、`1 1 0`、`auto` |
| `align-self` | 单独覆盖 align-items | 同 align-items |
| `order` | 视觉顺序 | `0`（默认）、`1`、`2` |

### 4.4 简写口诀

```text
flex: 1     →  flex: 1 1 0%   →  完美平均分配
flex: auto  →  flex: 1 1 auto →  按内容比例分配
flex: none  →  flex: 0 0 auto →  不放大不缩小，固定大小
```

### 4.5 居中三件套

```css
/* 水平 + 垂直居中（Flex 一行搞定） */
.parent {
    display: flex;
    justify-content: center;   /* 水平 */
    align-items: center;       /* 垂直 */
}
```

### 4.6 flex vs inline-flex

| | `display: flex` | `display: inline-flex` |
| --- | --- | --- |
| 容器自身 | 块级，占满父容器宽度 | 行内，宽度由内容决定 |
| 子项 | 弹性盒 | 弹性盒 |

---

## 5. Grid 布局

### 5.1 启动

```css
.parent {
    display: grid;
    grid-template-columns: 200px 1fr 200px;   /* 三列：固定-弹性-固定 */
    grid-template-rows: auto 1fr auto;        /* 三行：自动-弹性-自动 */
    gap: 10px;
}
```

### 5.2 核心概念

| 概念 | 含义 |
| --- | --- |
| **网格线** | 行/列的分隔线（编号从 1 开始） |
| **网格轨道** | 两条相邻网格线之间的区域 |
| **网格单元格** | 4 条网格线围成的最小区域 |
| **`fr` 单位** | 弹性比例（`1fr` = 占剩余空间 1 份） |

### 5.3 常用模板

```css
/* 经典两栏布局 */
grid-template-columns: 200px 1fr;

/* 12 列网格 */
grid-template-columns: repeat(12, 1fr);

/* 响应式自适应列（auto-fit + minmax） */
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
```

### 5.4 子项定位

```css
.item {
    grid-column: 1 / 3;        /* 跨 1~3 线（占 2 列） */
    grid-row: 1 / 2;
    /* 简写：grid-area: row-start / col-start / row-end / col-end */
}
```

### 5.5 Flex vs Grid 怎么选

| 场景 | 用 |
| --- | --- |
| 一维布局（行 或 列） | **Flex** |
| 二维布局（行 **和** 列） | **Grid** |
| 内容驱动（子项决定大小） | Flex |
| 布局驱动（容器决定大小） | Grid |
| 导航条 / 工具栏 | Flex |
| 整体页面骨架 | Grid |
| 居中单个元素 | 两者都行，Flex 写法更短 |

---

## 6. 实战模板

### 6.1 圣杯布局（顶 / 底 / 左中右）

```css
body {
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 200px 1fr 200px;
    grid-template-areas:
        "header header header"
        "left   main   right"
        "footer footer footer";
    min-height: 100vh;
}
header { grid-area: header; }
aside.left { grid-area: left; }
main { grid-area: main; }
aside.right { grid-area: right; }
footer { grid-area: footer; }
```

### 6.2 卡片列表（响应式）

```css
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
}
```

> 窗口窄时自动换行，宽时自动多列——**纯 CSS 响应式**。

### 6.3 移动端底部 Tab 栏

```css
.tab-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-around;
    background: white;
    border-top: 1px solid #eee;
    /* 适配刘海屏 */
    padding-bottom: env(safe-area-inset-bottom);
}
```

---

## 7. 常见坑

| 坑 | 原因 | 解决 |
| --- | --- | --- |
| 子项 width 不生效（flex 下） | `flex-basis` 优先 | 改用 `flex: 0 0 200px` |
| 子项溢出挤压 | `min-width: auto` 默认 = 内容宽 | 显式 `min-width: 0` |
| 垂直居中失效 | 父容器没高度 | 给父容器高度 / 用 grid `place-items: center` |
| 浮动父容器塌陷 | 子元素脱离文档流 | 清除浮动（见 §2.3） |
| `position: sticky` 不生效 | 父容器有 `overflow: hidden` | 改父容器 overflow |
| `z-index: 999` 还是被盖 | 父元素创建了新层叠上下文 | 把 z-index 加到父元素 |
| `display: flex` 后行内元素被挤开 | flex 子项默认 `min-width: auto` | 加 `min-width: 0` |
