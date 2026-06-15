# CSS 笔记（总览）

> 原 `文档/CSS.md` + `文档/css margin折叠情况.md` + `文档/css速记.md` 的整合重构版本，按知识体系拆成 6 个文件，**本文件是总览入口**。
> 原稿保留：`文档/CSS.md`、`文档/css margin折叠情况.md`、`文档/css速记.md`。
> 可运行的 HTML+CSS 演示放 `workspace/css/`，本笔记通过 git 远程链接引用。
> 概念长篇解释优先引 [MDN 中文文档](https://developer.mozilla.org/zh-CN/docs/Web/CSS)。

## 1. 速查总览

### 1.1 是什么

CSS（Cascading Style Sheets，**层叠样式表**）是给 HTML 页面"穿衣服"的标准：定义**布局、颜色、字体、间距、动效**等视觉表现。和 HTML（结构）、JavaScript（行为）构成前端三件套。

### 1.2 什么时候用

| 场景 | 适不适合 CSS |
| --- | --- |
| 任何 Web 页面 / Web App | ✅ 必备 |
| 桌面应用 UI（Electron / Tauri） | ✅ |
| 移动 App（React Native） | ❌ 大部分用 JS 样式（flex 思想仍通用） |
| 邮件模板 | ⚠️ 只支持老的 CSS 子集（table 布局） |
| 打印 / PDF | ✅ @media print |

### 1.3 4 个核心概念

| 概念 | 一句话 | 详见 |
| --- | --- | --- |
| **层叠（Cascade）** | 多个规则冲突时怎么算赢 | [[Hub/02_CSS选择器与继承笔记]] |
| **继承（Inheritance）** | 父元素的样式默认传给子元素 | [[Hub/02_CSS选择器与继承笔记]] |
| **盒模型（Box Model）** | 每个元素是"盒子"，决定占多大空间 | [[Hub/03_CSS盒模型笔记]] |
| **视觉格式化模型** | 元素怎么排成页面（文档流 / 浮动 / 定位 / Flex / Grid） | [[Hub/04_CSS布局笔记]] |

### 1.4 三个引入方式

```html
<!-- 1. 内联（style 属性）—— 优先级最高，最不推荐 -->
<div style="color: red;">

<!-- 2. 内部（<style>）—— 单页面用 -->
<head><style>p { color: red; }</style></head>

<!-- 3. 外部（<link>）—— 推荐，多页面共享 -->
<head><link rel="stylesheet" href="style.css"></head>
```

> 优先级：**内联 > ID > class/属性/伪类 > 元素/伪元素**，可用 `!important` 强制提升（**慎用**）。

### 1.5 demo 总览

| Demo | 涵盖 | 链接 |
| --- | --- | --- |
| `01_box_model.html` | 盒模型结构 / margin 折叠（同级/父子/阻止折叠）/ `box-sizing` | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/css/01_box_model.html) |
| `02_flex.html` | Flex 速查：`flex-direction` / `flex-wrap` / `justify-content` / `align-items` 各种值对比 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/css/02_flex.html) |
| `03_units.html` | px / em / rem / vh / vw / svh / dvh / lvh 视觉对比 + 移动端地址栏场景 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/css/03_units.html) |

打开方式：浏览器（Chrome / Firefox / Safari）双击 .html 文件即可，**不需要任何环境**。

---

## 2. 主题笔记拆分

| 主题 | 笔记 | 关键内容 |
| --- | --- | --- |
| 选择器 / 优先级 / 继承 / 层叠 | [[Hub/02_CSS选择器与继承笔记]] | 4 类选择器、权重计算、`!important` |
| 盒模型 / margin 折叠 | [[Hub/03_CSS盒模型笔记]] | 盒模型结构、`box-sizing`、margin 折叠规则 |
| 布局：文档流 / 浮动 / 定位 / Flex / Grid | [[Hub/04_CSS布局笔记]] | 5 种布局方式 + 实战要点 |
| 单位与值 | [[Hub/05_CSS单位与值笔记]] | 长度 / 颜色 / 关键字 / 响应式 |
| 常见问题 | [[Hub/06_CSS常见问题笔记]] | 垂直居中 / BFC / sticky 失效 等（Q&A 模板） |

---

## 3. 学习路径建议

1. **第 1 步**：看 [MDN CSS 入门](https://developer.mozilla.org/zh-CN/docs/Learn/CSS) 前 4 章（"什么是 CSS"/"开始学习 CSS"/"文本样式"/"CSS 布局基础"）
2. **第 2 步**：跑 [[Hub/02_CSS选择器与继承笔记]] + 跑 `workspace/css/02_flex.html`（把 90% 布局用熟）
3. **第 3 步**：[[Hub/03_CSS盒模型笔记]] + 跑 `workspace/css/01_box_model.html`（margin 折叠是面试必问）
4. **第 4 步**：[[Hub/04_CSS布局笔记]]（定位 + Grid）
5. **第 5 步**：[[Hub/05_CSS单位与值笔记]] + 跑 `workspace/css/03_units.html`（响应式适配）
6. **第 6 步**：遇到坑就 append 到 [[Hub/06_CSS常见问题笔记]]

---

## 4. 速记口诀

```text
文字相关属性会继承（color / font-* / line-height / text-align）
盒模型四件套不继承（width / height / margin / padding）
布局属性不继承但会改变子元素行为（display / position / float）
脱离文档流就不参与普通排版（margin 折叠失效）
```

---

## 5. 官方文档链接

- MDN CSS 中文总览：<https://developer.mozilla.org/zh-CN/docs/Web/CSS>
- MDN CSS 入门（推荐从这开始）：<https://developer.mozilla.org/zh-CN/docs/Learn/CSS>
- W3C CSS 规范：<https://www.w3.org/Style/CSS/>
- CSS 验证器（看代码是否合规）：<https://jigsaw.w3.org/css-validator/>
- Can I Use（看浏览器兼容性）：<https://caniuse.com/>
