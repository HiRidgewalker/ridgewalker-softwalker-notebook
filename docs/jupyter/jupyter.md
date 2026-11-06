---
title: "Jupyter 笔记"
---

# Jupyter 笔记

> 原 `jupyter笔记` 的提炼版本。原文以官方文档链接为主，本文件保留这些链接，并补充结构化经验与小工具 demo。

## 安装

两种方式：

- **anaconda**：conda 一键安装 Jupyter Notebook + 常用科学计算包
- **pip**：直接 `pip install notebook`，适合已有 Python 环境的场景

> [Install Jupyter Notebook Classic](https://docs.jupyter.org/en/latest/install/notebook-classic.html)

## 更新

> [Upgrade Jupyter Notebook](https://docs.jupyter.org/en/latest/use/upgrade-notebook.html)

升级命令（pip 安装方式）：

```bash
pip install -U notebook
```

## 安装内核（kernels）

Jupyter 本身只是一个前端壳子，真正执行代码的是 **kernel**。默认只装了 IPython kernel，其他语言的 kernel 需要单独装。

> [Install Jupyter Kernels](https://docs.jupyter.org/en/latest/install/kernels.html)

常见 kernel：

| Kernel | 安装方式 |
|---|---|
| Python（默认） | `pip install ipykernel` |
| R | `conda install -c r r-irkernel` |
| Julia | 在 Julia 内 `using IJulia` |
| JavaScript | `npm install -g ijavascript` |

注册当前 Python 环境为 kernel：

```bash
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"
```

## 运行

> [Running Jupyter Notebook](https://docs.jupyter.org/en/latest/running.html)

常用启动命令：

```bash
# 默认启动，自动打开浏览器
jupyter notebook

# 不打开浏览器（适合远程服务器开发）
jupyter notebook --no-browser

# 指定端口
jupyter notebook --port 8888

# 启动 Lab（推荐的新版前端）
jupyter lab
```

远程服务器场景：启动后复制控制台输出的 URL（含 token）到本地浏览器。

## 使用

> [Using Jupyter Notebook](https://docs.jupyter.org/en/latest/use/using.html)

### 两种 cell 类型

- **Code cell**：执行代码，结果（stdout、图、表格）直接渲染在 cell 下
- **Markdown cell**：写 Markdown 文本，支持 LaTeX、HTML、表格

### 常用快捷键

| 操作 | 快捷键 |
|---|---|
| 运行当前 cell 并选中下一格 | `Shift + Enter` |
| 运行当前 cell（不移动） | `Ctrl + Enter` |
| 上一格 / 下一格 | `Esc + K` / `Esc + J` 或 `↑` / `↓` |
| 切换 cell 类型为 Code / Markdown | `Esc + Y` / `Esc + M` |
| 插入 cell 上下方 | `Esc + A` / `Esc + B` |
| 删除 cell | `Esc + D D` |
| 命令面板 | `Ctrl + Shift + P` |

### 常用魔法命令（Magic Commands）

行魔法（`%` 前缀）和 cell 魔法（`%%` 前缀）：

| 命令 | 作用 |
|---|---|
| `%timeit` | 测试单行执行时间 |
| `%%time` | 测试整 cell 执行时间 |
| `%run xxx.py` | 在 cell 中运行外部脚本 |
| `%load xxx.py` | 把外部脚本内容加载到当前 cell |
| `%pwd` / `%cd` | 当前目录 / 切换目录 |
| `%matplotlib inline` | 图表内嵌显示 |
| `!shell_cmd` | 执行 shell 命令 |
| `%%writefile file` | 把 cell 内容写入文件 |
| `?obj` / `obj?` | 查询对象帮助 |

## 以编程方式读写 .ipynb

`nbformat` 是操作 notebook 文件的标准库，方便做模板化生成、批量处理、CI 中的 notebook 校验。

完整可运行示例：[example/python/jupyter/nbformat_demo.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/jupyter/nbformat_demo.py)

## 生态对比：Notebook vs Lab vs Hub

| 工具 | 角色 | 何时使用 |
|---|---|---|
| **Jupyter Notebook** | 经典单文档前端 | 教学、个人分析 |
| **JupyterLab** | 新一代多文档 IDE 风格前端 | 复杂项目、多文件协作 |
| **JupyterHub** | 多用户部署平台 | 团队 / 教学环境 |
| **VS Code / PyCharm** | 编辑器内 notebook 支持 | 已用 IDE 的开发场景 |

VS Code 内置的 notebook 支持现在体验已经很好，多数情况下可以替代浏览器版 Jupyter。

## 个人经验总结

- **远程服务器开发**：默认用 `jupyter lab --no-browser --port=8888` + SSH 端口转发或直接用 VS Code Remote 插件
- **环境隔离**：每个虚拟环境装好 `ipykernel` 后注册一次，避免污染 base kernel
- **避免 notebook 过于臃肿**：单个 notebook 只做一件事，便于 diff 和回滚
- **结合 uv 一起用**：在 venv 内启动 notebook，保证 kernel 指向正确的环境

## 运行约定

所有 demo 使用 `example/.venv/` 下的 Python 3.12，虚拟环境位于 `example/.venv/`。