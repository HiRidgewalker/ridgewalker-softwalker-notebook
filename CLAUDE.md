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