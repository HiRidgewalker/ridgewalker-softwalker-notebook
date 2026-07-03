# Python 虚拟环境（uv）

## 规则

`workspace/` 下所有 Python 演示代码统一使用 `workspace/.venv/` 这个虚拟环境，禁止使用系统全局 Python 或其他虚拟环境。

## 原因

- 知识库内 demo 可能依赖不同版本的第三方库（asyncio 行为差异、httpx vs aiohttp 等），统一环境便于复现
- 系统 Python 缺包时容易污染全局依赖，污染系统
- uv 安装速度快、依赖解析准确，比手动 pip + venv 更可靠
- 集中在一个 venv，后续 `uv pip freeze` 一次性导出即可

## 如何应用

### 1. 初始化环境

```bash
uv venv workspace/.venv --python 3.12
```

> 仅在仓库首次克隆后执行一次即可，venv 已存在时跳过。

### 2. 安装依赖

```bash
uv pip install --python workspace/.venv/bin/python <包名>
```

或临时一次性运行：

```bash
uv run --python workspace/.venv/bin/python demo.py
```

### 3. 运行 demo

统一使用 venv 内的 Python 解释器：

```bash
workspace/.venv/bin/python workspace/python/<模块>/<demo>.py
```

不要使用 `python` / `python3`（指向系统全局），因为：
- 不同机器系统 Python 版本不一致
- 全局包污染会导致 demo 行为差异

### 4. 环境信息

- **目录**：`workspace/.venv/`
- **Python 版本**：3.12
- **工具**：uv（`~/.local/bin/uv`）
- **包管理器**：`uv pip`（兼容标准 pip，但解析更快）

### 5. .gitignore

`workspace/.venv/`、`__pycache__/`、`*.pyc` 已加入 `.gitignore`，venv 不入库。

## 当前 git 仓库信息

- 仓库名：`personal-knowledge-base`
- venv 路径：`workspace/.venv/`
- Python 解释器：`workspace/.venv/bin/python`

## 引用本规则的入口

详见根目录 `AGENTS.md` / `CLAUDE.md` 中的 "Python 虚拟环境（uv）" 小节。
