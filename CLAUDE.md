## 项目背景
- 当前项目是 obsidian 结构的个人知识库
- 当前主要任务：帮助用户重新整理知识库
- 该导航页中所有引用的文件都位于 `文档/` 文件夹下
- 引用格式遵循 obsidian 官方格式（即 `[[文件名]]` 这种双中括号 wiki 链接形式）

## 语言偏好
- 后续所有描述性内容、非技术名词，全部使用中文描述

## 代码演示外置 workspace 模式
- 可运行代码示例从笔记中提炼到 `workspace/` 目录下作为可执行 demo
- 原文通过 git 远程链接引用 demo，不保留大段代码块
- 合并后的精炼总览文件放在 `Hub/` 下
- 详细规范见 [rules/03-workspace演示模式.md](./rules/03-workspace演示模式.md)

## Python 虚拟环境（uv）
- `workspace/` 下所有 Python demo 使用统一的 `workspace/.venv/`
- 运行 demo 必须用 `workspace/.venv/bin/python`，禁止系统全局 Python
- 安装依赖用 `uv pip install --python workspace/.venv/bin/python <pkg>`
- 详细规范见 [rules/04-python虚拟环境.md](./rules/04-python虚拟环境.md)

## 笔记重构默认模式
- 重构 / 重新整理 / 合并 / 提炼 / 完善笔记时：借鉴原笔记内容，提炼 + 完善 + 总结后写入 `Hub/`，原笔记保留在原位置不删不改
- 同步更新 `目录.md` 中的引用链接，让导航指向新的 Hub/ 笔记
- 详细规范见 [rules/05-笔记重构默认模式.md](./rules/05-笔记重构默认模式.md)

## 记忆系统（显式 vs 自动）
- **用户明确要求添加的记忆**（显式指令，如「把这个记下来」「写进 rules」「加到 CLAUDE.md」）→ 写入 `CLAUDE.md` 或 `rules/`，随项目仓库版本管理
- **AI 主动添加的记忆**（自动判断「该记这条」）→ 写入默认 memory 目录（`~/.claude/projects/.../memory/`），属于跨会话 / 跨项目的用户偏好
- 区分依据：当次对话中是否出现「记下来 / 加记忆 / 写规则」等用户显式关键词