# 基本能力

@hiduck/general-rule/直面需求编写笔记
@hiduck/general-rule/快速上手优先
@hiduck/general-rule/常用特性优先
@hiduck/general-rule/跳跃知识点简要解释
@hiduck/general-rule/mermaid可视化表达规范

## 仓库定位

本仓库是 Software Tech Notebook，用于记录 software technology 的个人技术笔记。源文件为纯 markdown，不绑定任何笔记软件；同时通过 Docusaurus 提供本地可运行的静态站点。核心知识入口位于 `docs/`，按 48 个主题分子目录。

## 如何辅助记录技术

当用户想记录一个技术栈、学习一个技术组件或编写一篇技术文章时，直接基于该技术组件编写完整的学习文档笔记，不逐步追问大纲和素材。笔记以实用为主：快速上手优先、常用特性优先、原理简要说明并附在线详解链接、必要时用 Mermaid 图示辅助理解。

- 写作姿态：[直面需求编写笔记.md](hiduck/general-rule/直面需求编写笔记.md)
- 内容取舍：[快速上手优先.md](hiduck/general-rule/快速上手优先.md) · [常用特性优先.md](hiduck/general-rule/常用特性优先.md) · [跳跃知识点简要解释.md](hiduck/general-rule/跳跃知识点简要解释.md)
- 表达方式：[mermaid可视化表达规范.md](hiduck/general-rule/mermaid可视化表达规范.md)

## 语言偏好

- 后续所有描述性内容、非技术名词，全部使用中文描述

## 代码演示外置 example 模式

- 可运行代码示例从笔记中提炼到 `example/` 目录下作为可执行 demo
- 笔记通过 GitHub 仓库链接引用 demo：`https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/...`（目录用 `tree`）
- 合并后的精炼总览文件放在 `docs/<对应主题 slug>/` 下
- 各子项目的目录结构与约定见 [example/README.md](example/README.md)

## 目录与索引维护

- 索引源就是 `docs/` 目录结构本身：主题即 `docs/` 下的一级目录，主题内笔记即目录下的 `.md` 文件
- 新增笔记直接放入对应 `docs/<slug>/`；无对应主题时新建目录与 `_category_.json`

## 笔记渲染约定

- Mermaid：用 ```` ```mermaid ```` 代码块，主题已配置，浏览器端渲染
- 数学公式：KaTeX 渲染，行内写 `$E=mc^2$`，块级写 `$$ ... $$`，支持 `\begin{align}`、`\begin{equation}` 等环境
- 非公式的美元符号必须转义为 `\$`，公式内也不要出现未转义的 `$`（KaTeX 会报错）
- 配置位置：`docusaurus.config.ts` 中 docs/blog 的 `remarkPlugins` / `rehypePlugins`；KaTeX 样式由 `src/clientModules/katex.ts` 本地引入

## Web 站点

- 浏览：`npm start`（开发服务器）或 `npm run build && npm run serve`（静态产物）
- 目录结构即站点目录：`docs/<slug>/` 一级目录为主题，目录下的 `.md` 文件为文章
- 主题目录名为章节标题转 slug：`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`
- 笔记文件名统一英文小写 kebab-case：`01-go-overview.md`、`markdown-latex-syntax.md`；系列文章用 `01-`、`02-` 前缀排序
- 目录树、首页与侧边栏条目统一显示英文文件名
- 侧边栏文档标签由 `docusaurus.config.ts` 的 `sidebarItemsGenerator` 取文件名（去掉 `.md`）生成，与源文件名自动同步；显式设置 `sidebar_label` 的文档（如首页）优先
- 单技术笔记放 `docs/<slug>/`；Tech Blog 文章（跨技术选型、方案总览、跨栈整合）放 `blog/`
- Tech Blog 文章 frontmatter 必须带 `tags`：技术栈标签，最多 5 个，直接在文章 frontmatter 维护
- 标签渲染在文章标题下方，颜色由 `src/theme/Tag` 按标签名稳定取色，点标签进入 `/blog/tags/<slug>` 聚合页
- 侧边栏由目录结构与 `_category_.json` 决定，不手工维护
- 主题目录始终显示为分组：目录内只有一篇与目录同名的笔记时（如 `docs/wsl/wsl.md`），在该目录 `_category_.json` 写 `"link": null`，否则 Docusaurus 会把它当作分类索引，侧边栏退化成一个链接
- `docs/intro.md`（站点首页）由 `scripts/gen-index.mjs` 扫描 `docs/` 生成，属于生成物，**不要手工编辑**
- 笔记间引用使用标准 markdown 链接：同主题 `[标题](./note-name.md)`，跨主题 `[标题](../wsl/wsl.md)`
- 新增主题时：创建 `docs/<slug>/` 与 `_category_.json`，首页与侧边栏自动收录
