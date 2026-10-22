# Python 虚拟环境（uv）

## 规则

`example/` 下的每个 Python 项目都是独立项目，各自维护依赖声明与虚拟环境。虚拟环境只属于该项目，不跨项目共用，也不纳入版本控制。

## 原因

- 各 demo 依赖的第三方库版本可能冲突（asyncio 行为差异、httpx vs aiohttp 等），独立环境避免互相干扰
- 共用环境会让项目之间隐式耦合，拆成独立项目后难以单独复现
- 系统 Python 缺包时容易污染全局依赖
- uv 安装速度快、依赖解析准确，比手动 pip + venv 更可靠

## 如何应用

### 1. 进入项目目录

```bash
cd example/<项目路径>
```

### 2. 初始化环境

```bash
uv venv .venv --python 3.12
```

### 3. 安装依赖

```bash
uv pip install --python .venv/bin/python <包名>
```

依赖确定后写入该项目的 `requirements.txt`。

### 4. 运行 demo

```bash
.venv/bin/python <demo>.py
```

不要使用 `python` / `python3`（指向系统全局），因为不同机器的系统 Python 版本不一致，全局包污染也会导致 demo 行为差异。

### 5. 不纳入版本控制

`.venv/`、`__pycache__/`、`*.pyc` 已在 `.gitignore` 中排除，不提交。

## 环境声明文件

- Python 项目保留 `requirements.txt`
- Go 项目保留 `go.mod`
- 前端项目保留 `package.json` 与 `tsconfig.json`

除上述声明文件外，安装产物与运行缓存不进入仓库。

## 引用本规则的入口

详见根目录 `AGENTS.md` / `CLAUDE.md` 中的 "Python 虚拟环境（uv）" 小节。
