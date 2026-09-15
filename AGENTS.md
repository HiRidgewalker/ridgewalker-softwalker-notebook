# attention: following the rules
- hiduck/general-rule/03-workspace演示模式
- hiduck/general-rule/04-python虚拟环境
- hiduck/general-rule/05-笔记重构默认模式
- hiduck/general-rule/06-mermaid可视化表达规范

# AGENTS.md

本文件是当前知识库的项目级记忆总入口，供支持 AGENTS.md 规范的 agent 使用。支持 CLAUDE.md 规范的 agent 读取根目录 `CLAUDE.md`；两个总文件应保持同等含义。

## 项目背景

- 当前项目是 obsidian 结构的个人知识库
- 当前主要任务：帮助用户重新整理知识库
- 目录导航使用裸文件名 wiki 链接；核心知识入口位于 `Hub/`，速记位于 `速记/`，个人成长位于 `个人成长/`
- 引用格式遵循 obsidian 官方格式（即 `[[文件名]]` 这种双中括号 wiki 链接形式）

## 语言偏好

- 后续所有描述性内容、非技术名词，全部使用中文描述

## 记忆组织方式

- 根目录 `AGENTS.md` 与 `CLAUDE.md` 是项目记忆总文件，面向不同 agent 规范保持同步
- `rules/` 中的文档是扩展记忆文件或详细规则文件
- 新增项目级总规则时，同步更新 `AGENTS.md` 与 `CLAUDE.md`
- 新增细化规则时，写入 `rules/`，并在两个总文件中添加引用

## 代码演示外置 workspace 模式

- 可运行代码示例从笔记中提炼到 `workspace/` 目录下作为可执行 demo
- 原文通过 git 远程链接引用 demo，不保留大段代码块
- 合并后的精炼总览文件放在 `Hub/` 下
- 详细规范见 [rules/03-workspace演示模式.md](03-workspace演示模式.md)

## Python 虚拟环境（uv）

- `workspace/` 下所有 Python demo 使用统一的 `workspace/.venv/`
- 运行 demo 必须用 `workspace/.venv/bin/python`，禁止系统全局 Python
- 安装依赖用 `uv pip install --python workspace/.venv/bin/python <pkg>`
- 详细规范见 [rules/04-python虚拟环境.md](04-python虚拟环境.md)

## 笔记重构默认模式

- 重构 / 重新整理 / 合并 / 提炼 / 完善笔记时：提炼 + 完善 + 总结后写入目标入口目录；技术与通用主题默认写入 `Hub/`
- 同步更新 `目录.md` 中的引用链接，让导航指向新的 Hub/ 笔记
- 详细规范见 [rules/05-笔记重构默认模式.md](05-笔记重构默认模式.md)

## Mermaid 可视化表达规范

- 需要流程图、架构图等可视化内容时，默认优先使用 Mermaid 语法表达
- 不用纯文本字符串、ASCII 字符画、手写箭头缩进等方式模拟图形
- 详细规范见 [rules/06-mermaid可视化表达规范.md](06-mermaid可视化表达规范.md)

## 记忆系统

- 项目级显式记忆：写入根目录 `AGENTS.md` / `CLAUDE.md` 或 `rules/`，随项目仓库版本管理
- 扩展规则：写入 `rules/`，并从 `AGENTS.md` / `CLAUDE.md` 引用
- 用户级 / 全局偏好：只有用户明确要求“全局记忆”“Codex 用户级记忆”等跨项目偏好时，才写入用户级位置
- 不把当前项目规则写到外部 memory 目录
