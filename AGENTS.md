# 基本能力

@hiduck/general-rule/直面需求编写笔记
@hiduck/general-rule/快速上手优先
@hiduck/general-rule/常用特性优先
@hiduck/general-rule/跳跃知识点简要解释
@hiduck/general-rule/mermaid可视化表达规范

## 仓库定位

本仓库是记录 software technology 的个人技术笔记本（Obsidian vault），用于沉淀各技术栈的学习笔记。核心知识入口位于 `hub/`，不参与技术分类的笔记位于 `未归类/`。

## 如何辅助记录技术

当用户想记录一个技术栈、学习一个技术组件或编写一篇技术文章时，直接基于该技术组件编写完整的学习文档笔记，不逐步追问大纲和素材。笔记以实用为主：快速上手优先、常用特性优先、原理简要说明并附在线详解链接、必要时用 Mermaid 图示辅助理解。

- 写作姿态：[直面需求编写笔记.md](hiduck/general-rule/直面需求编写笔记.md)
- 内容取舍：[快速上手优先.md](hiduck/general-rule/快速上手优先.md) · [常用特性优先.md](hiduck/general-rule/常用特性优先.md) · [跳跃知识点简要解释.md](hiduck/general-rule/跳跃知识点简要解释.md)
- 表达方式：[mermaid可视化表达规范.md](hiduck/general-rule/mermaid可视化表达规范.md)

## 语言偏好

- 后续所有描述性内容、非技术名词，全部使用中文描述

## 代码演示外置 example 模式

- 可运行代码示例从笔记中提炼到 `example/` 目录下作为可执行 demo
- 原文通过 git 远程链接引用 demo，不保留大段代码块
- 合并后的精炼总览文件放在 `hub/` 下
- 各子项目的目录结构与约定见 [example/README.md](example/README.md)

## Catalog 索引维护

- `Catalog.md` 采用平铺主题索引，章节标题统一英文
- 新增笔记按技术名追加到对应 `##` 章节，无对应主题时新增英文标题章节
