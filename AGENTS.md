# 基本能力

@hiduck/general-rule/直面需求编写笔记
@hiduck/general-rule/快速上手优先
@hiduck/general-rule/常用特性优先
@hiduck/general-rule/跳跃知识点简要解释
@hiduck/general-rule/mermaid可视化表达规范

## 仓库定位

本仓库是 Software Tech Notebook，用于记录 software technology 的个人技术笔记。源文件为纯 markdown，不绑定任何笔记软件；同时通过 Docusaurus 提供本地可运行的静态站点。核心知识入口位于 `docs/`，按 `Catalog.md` 的 48 个主题分子目录。

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

## Catalog 索引维护

- `Catalog.md` 保留在仓库根目录，采用平铺主题索引，章节标题统一英文
- 新增笔记按技术名追加到对应 `##` 章节，无对应主题时新增英文标题章节
- 它是站点首页与 agent 导航的索引源，**不是**侧边栏来源

## Web 站点

- 浏览：`npm start`（开发服务器）或 `npm run build && npm run serve`（静态产物）
- 目录结构严格对应 `Catalog.md`：`## 主题` 直接作为 `docs/` 下的一级目录，主题下的 `[[链接]]` 为文章；`# Catalog` 只是文档标题，不生成目录
- 主题目录名为章节标题转 slug：`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`
- 单技术笔记放 `docs/<slug>/`；Tech Blog 文章（跨技术选型、方案总览、跨栈整合）放 `blog/`
- Tech Blog 文章 frontmatter 必须带 `tags`：技术栈标签，最多 5 个，取自 `Catalog.md` 该条目后的括号标注；新增或调整后在仓库根目录执行 `npm run gen:tags` 生成
- 标签渲染在文章标题下方，颜色由 `src/theme/Tag` 按标签名稳定取色，点标签进入 `/blog/tags/<slug>` 聚合页
- 侧边栏由目录结构与 `_category_.json` 决定，不手工维护
- `docs/index.md` 由 `Catalog.md` 生成，属于生成物，**不要手工编辑**
- 笔记间引用使用标准 markdown 链接：同主题 `[标题](./笔记名.md)`，跨主题 `[标题](../wsl/WSL笔记.md)`
- 新增主题时：在 `Catalog.md` 增加 `## 章节`，创建 `docs/<slug>/` 与 `_category_.json`
