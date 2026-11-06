# 基本能力

@hiduck/general-rule/直面需求编写笔记
@hiduck/general-rule/快速上手优先
@hiduck/general-rule/常用特性优先
@hiduck/general-rule/跳跃知识点简要解释
@hiduck/general-rule/mermaid可视化表达规范

## 仓库定位

本仓库是记录 software technology 的个人技术知识库，源文件为纯 markdown，不绑定任何笔记软件；同时通过 Docusaurus 提供本地可运行的静态站点。核心知识入口位于 `docs/`，按 15 个技术域分子目录。

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
- 合并后的精炼总览文件放在 `docs/<对应技术域>/` 下
- 各子项目的目录结构与约定见 [example/README.md](example/README.md)

## Catalog 索引维护

- `Catalog.md` 保留在仓库根目录，采用平铺主题索引，章节标题统一英文
- 新增笔记按技术名追加到对应 `##` 章节，无对应主题时新增英文标题章节
- 它是站点首页与 agent 导航的索引源，**不是**侧边栏来源

## Web 站点

- 浏览：`npm start`（开发服务器）或 `npm run build && npm run serve`（静态产物）
- 单技术笔记放 `docs/<group>/`；跨技术主题文章（选型对比、方案总览、跨栈整合）放 `blog/`，以博客形式呈现
- 侧边栏由 `docs/` 目录结构与 `docs/<group>/_category_.json` 决定，不手工维护
- `docs/index.md` 由 `Catalog.md` 生成，属于生成物，**不要手工编辑**
- 笔记间引用使用标准 markdown 链接：同目录 `[标题](./笔记名.md)`，跨目录 `[标题](../devops/I_Docker笔记.md)`
- 新增技术域时创建目录与 `_category_.json`，并同步更新 `scripts/lib/catalog-map.mjs` 中的映射
