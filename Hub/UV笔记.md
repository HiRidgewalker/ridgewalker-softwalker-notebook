# UV 笔记

> 由旧稿重新整理版本，精炼为 4 章节结构：概述与安装 / 命令速查表 / Ubuntu+FastAPI 实战 / 命令详解。旧稿目录已清理，当前以本文为准。

## 1. 概述与安装

### 1.1 uv 是什么

uv 是 [Astral](https://astral.sh) 出品的 Python 包与项目管理器，用 Rust 实现，单一二进制。把 pip / venv / pyenv / pip-tools / poetry 等工具的能力整合到一套命令里，速度比传统工具快一个数量级。

> 官方文档：<https://docs.astral.sh/uv/>

### 1.2 安装

**macOS / Linux（官方安装器，推荐）**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows（PowerShell，推荐）**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**包管理器（备选）**

```bash
# macOS（Homebrew）
brew install uv

# Windows（winget）
winget install --id=astral-sh.uv

# 任何已有 Python 的环境（兜底，不推荐）
pip install uv
```

安装完成后：

```bash
uv --version    # 验证安装
```

### 1.3 升级与卸载

```bash
# 升级
uv self update
```

卸载（macOS / Linux）：

```bash
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
rm $HOME/.local/bin/uv
rm $HOME/.local/bin/uvx
```

卸载（Windows）：

```powershell
uv cache clean
Remove-Item -Recurse (uv python dir)
Remove-Item -Recurse (uv tool dir)
Remove-Item $HOME\.local\bin\uv.exe
Remove-Item $HOME\.local\bin\uvx.exe
```

---

## 2. 命令速查表

```text
# ===== 项目管理（pyproject.toml 驱动）=====
uv init <name>                       # 初始化项目骨架（生成 pyproject.toml + src/）
uv init .                            # 在当前目录初始化
uv add <pkg>                         # 添加依赖（同步：pyproject.toml + uv.lock + .venv）
uv add -r requirements.txt           # 从 requirements.txt 批量导入
uv add "pkg>=1.0"                    # 带版本约束
uv add "pkg; sys_platform == 'linux'"# 平台标记
uv add /path/to/foo.whl              # 安装本地 whl
uv remove <pkg>                      # 移除依赖（同步三处）
uv sync                              # 按 uv.lock 同步 .venv
uv lock                              # 显式创建/更新 uv.lock
uv run <cmd>                         # 在项目 .venv 中执行命令
uv tree                              # 打印依赖树
uv build                             # 构建 sdist / wheel
uv publish                           # 发布到 PyPI

# ===== Python 版本管理 =====
uv python install 3.12               # 安装指定版本（可逗号分隔多个）
uv python list                       # 列出可用/已安装 Python
uv python find [ver]                 # 查找已安装 Python 路径
uv python pin 3.12                   # 固定当前项目 Python 版本（写 .python-version）
uv python uninstall 3.12             # 卸载指定版本

# ===== 单文件脚本 =====
uv run script.py                     # 运行脚本（自动管理 # /// script 块中的依赖）
uv add --script <pkg>                # 向脚本头部添加内联依赖
uv remove --script <pkg>             # 从脚本中删除依赖

# ===== 全局工具 =====
uvx <cli>                            # 临时环境运行工具（uv tool run 的别名）
uvx ruff@0.5.0                       # 指定版本
uv tool install <cli>                # 用户级安装工具
uv tool list                         # 列出已安装工具
uv tool uninstall <cli>              # 卸载工具
uv tool update-shell                 # 把工具 bin 目录加入 PATH

# ===== pip 兼容接口（只动当前 venv，不动 pyproject.toml/lock）=====
uv venv                              # 在当前目录创建 .venv
uv venv --python 3.12                # 指定 Python 版本
uv pip install <pkg>                 # 装包
uv pip uninstall <pkg>               # 卸包
uv pip list                          # 列出已装包
uv pip freeze                        # 导出 requirements
uv pip show <pkg>                    # 查看包详情
uv pip check                         # 检查依赖兼容性
uv pip tree                          # 依赖树
uv pip compile                       # requirements.in -> 锁定的 requirements.txt
uv pip sync                          # 按锁定文件同步环境

# ===== 缓存与状态 =====
uv cache dir                         # 显示缓存目录
uv cache clean                       # 清空缓存
uv cache prune                       # 删除过期缓存
uv tool dir                          # 工具安装目录
uv python dir                        # Python 安装目录
uv self update                       # 升级 uv
uv <cmd> --help                      # 命令帮助
uv <cmd> -v                          # 详细输出
uv <cmd> -vv                         # 更详细输出
```

---

## 3. Ubuntu + FastAPI 实战

完整最小可运行流程：

```bash
# 1. 安装 uv（一次性，仅首次需要）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建并进入项目目录
mkdir my-fastapi-app && cd my-fastapi-app

# 3. 初始化项目骨架（生成 pyproject.toml 等，不会建 .venv）
uv init .

# 4. 锁定 Python 版本（写 .python-version + 更新 requires-python）
uv python pin 3.12

# 5. 添加 FastAPI 依赖（首次 add 会自动建 .venv 并装包）
uv add fastapi
uv add "uvicorn[standard]"

# 6. 显式同步一次（可选，add 已经触发过）
uv sync

# 7. 写一个最小 main.py
cat > main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}
EOF

# 8. 启动开发服务（热重载）
uv run uvicorn main:app --reload
```

启动后访问：

- 接口：<http://127.0.0.1:8000/>
- Swagger UI：<http://127.0.0.1:8000/docs>

### 3.1 常用后续动作

```bash
# 加包
uv add sqlalchemy pydantic
uv add "httpx>0.1.0"                  # 带版本约束

# 卸包
uv remove httpx

# 跑测试
uv add --dev pytest httpx
uv run pytest

# 导出 requirements（给非 uv 协作者）
uv pip freeze > requirements.txt

# 激活 venv（可选，uv run 已自动处理）
source .venv/bin/activate             # Ubuntu / macOS
.venv\Scripts\activate                # Windows
deactivate
```

### 3.2 协作时的最小提交集合

把以下文件纳入版本控制，队友 clone 后 `uv sync` 即可还原环境：

- `pyproject.toml`
- `uv.lock`
- `.python-version`

`.venv/` 加入 `.gitignore`。

---

## 4. 命令详解

> 章节结构：命令 → 行为说明 → 关键细节 → 官方文档链接。
> 重要的对比与坑点内嵌在对应命令下。

### 4.1 项目管理

#### `uv init`

- 在当前目录（或 `<name>` 指定目录）生成项目骨架：`pyproject.toml`、`.python-version`、`README.md`、`src/<pkg>/`、`hello.py`、`.gitignore`。
- 不会创建 `.venv`，不会装包。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/#project-structure>

#### `uv add`

- 一条命令同时做三件事：
  1. 写入 `pyproject.toml` 的 `[project].dependencies`（或开发依赖用 `--dev`）。
  2. 解析并更新 `uv.lock`。
  3. 装到 `.venv`（若 `.venv` 不存在则自动创建）。
- 支持版本约束、extras、平台标记、本地 whl、从 `requirements.txt` 批量导入。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/sync/#adding-dependencies>

> **对比：`uv add` vs `uv pip install`**
>
> | 命令 | 装到 `.venv` | 写 `pyproject.toml` | 写 `uv.lock` |
> | --- | --- | --- | --- |
> | `uv add` | ✅ | ✅ | ✅ |
> | `uv pip install` | ✅ | ❌ | ❌ |
>
> 口诀：涉及依赖声明用 `uv add`；只想临时装一个调试包用 `uv pip install`。

#### `uv remove`

- `uv add` 的反向：从 `.venv` 卸包 + 从 `pyproject.toml` 移除 + 更新 `uv.lock`。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/sync/#removing-dependencies>

> **对比：`uv remove` vs `uv pip uninstall`**
>
> | 命令 | 卸 `.venv` | 改 `pyproject.toml` | 改 `uv.lock` |
> | --- | --- | --- | --- |
> | `uv remove` | ✅ | ✅ | ✅ |
> | `uv pip uninstall` | ✅ | ❌ | ❌ |

#### `uv sync`

- 按 `uv.lock` 把 `.venv` 同步到完全一致：缺包则装、多了则卸、版本变了则换、`.venv` 不存在则建。
- **需要 sync 的典型场景**：
  1. 第一次克隆项目，还没有 `.venv`。
  2. 手动改了 `pyproject.toml` 依赖或 `requires-python`。
  3. 切换了 Python 版本（如 `uv python pin 3.10`）。
  4. 拉取了别人分支，`uv.lock` 变了。
  5. `.venv` 损坏或被误删。
- **不需要 sync 的情况**：
  - 只是跑代码，不改依赖、不切 Python。
  - 已经 `uv add` / `uv remove`（这两条命令会自动同步）。
- 包下载到全局缓存（`~/.cache/uv`），再从缓存装到 `.venv`；多次 sync 不重复拉网。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/sync/>

#### `uv lock`

- 显式创建/更新 `uv.lock`（`uv add` / `uv sync` 会自动调用，平时不用手敲）。
- `uv.lock` 是跨平台锁文件，TOML 格式，人类可读但不要手编。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/sync/#locking-environments>

#### `uv run`

- 在项目 `.venv` 中执行任意命令或脚本：`uv run uvicorn main:app --reload`、`uv run python main.py`、`uv run pytest`。
- 若 `.venv` 缺失或过期，会先隐式 sync。
- 官方文档：<https://docs.astral.sh/uv/concepts/projects/run/>

#### `uv tree`

- 打印项目依赖树，方便排查版本冲突。
- 官方文档：<https://docs.astral.sh/uv/reference/cli/#uv-tree>

#### `uv build` / `uv publish`

- `uv build`：把项目构建为 sdist + wheel。
- `uv publish`：上传到 PyPI 或私有索引（需 `UV_PUBLISH_TOKEN` 等环境变量）。
- 官方文档：
  - <https://docs.astral.sh/uv/concepts/projects/build/>
  - <https://docs.astral.sh/uv/guides/publish/>

### 4.2 Python 版本管理

#### `uv python install` / `list` / `find` / `uninstall`

- uv 自带 Python 管理：装任意版本（含 PyPy、freethreaded、musl 变体），按需下载、共享给所有项目。
- `uv python list` 同时展示「可下载版本」和「已安装版本」；加 `--only-installed` 只看本地。
- 官方文档：<https://docs.astral.sh/uv/concepts/python-versions/>

#### `uv python pin`

- 把项目固定到某个 Python 版本。会写两处：
  1. 项目根生成 `.python-version`（内容如 `3.12`）。
  2. `pyproject.toml` 的 `requires-python` 改为 `==3.12.*`。
- 之后在该目录下所有 `uv sync` / `uv add` / `uv pip` / `uv run` 都用这个版本。
- 是项目级，cd 出去就不生效；要换版本就再 `uv python pin <ver>`。
- 官方文档：<https://docs.astral.sh/uv/concepts/python-versions/#pinning-a-python-version>

### 4.3 单文件脚本

#### `uv run script.py`

- 自动读取脚本头部的 `# /// script` 块，按声明的依赖创建临时环境运行。
- 适合分享一次性脚本：依赖声明内嵌在文件里，无需 `requirements.txt`。
- 官方文档：<https://docs.astral.sh/uv/guides/scripts/>

#### `uv add --script` / `uv remove --script`

- 把依赖写入脚本头部的内联块（修改 `# /// script`），而不是 `pyproject.toml`。
- 官方文档：<https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies>

### 4.4 全局工具

#### `uvx`（`uv tool run` 的别名）

- 在临时环境运行 CLI，相当于 pipx 的 `pipx run`。
- 例：`uvx ruff`、`uvx black@24.1.0`、`uvx pycowsay "hello"`。
- 官方文档：<https://docs.astral.sh/uv/guides/tools/>

#### `uv tool install` / `list` / `uninstall`

- 永久装到用户 bin（默认 `~/.local/bin`）；首次装完跑 `uv tool update-shell` 把路径加入 PATH。
- 官方文档：<https://docs.astral.sh/uv/concepts/tools/>

### 4.5 pip 兼容接口

#### `uv venv`

- 在当前目录创建虚拟环境，默认名 `.venv`（可指定其他名字）。
- `--python 3.12` 指定解释器版本；不指定则读 `.python-version`。
- 官方文档：<https://docs.astral.sh/uv/reference/cli/#uv-venv>

#### `uv pip install` / `uninstall` / `list` / `freeze` / `show` / `check` / `tree`

- 与同名 pip 命令对应，但更快；只动当前 venv，不动 `pyproject.toml` / `uv.lock`。
- `uv pip freeze > requirements.txt` 给非 uv 协作者用。
- 官方文档：<https://docs.astral.sh/uv/pip/packages/>

#### `uv pip compile` / `uv pip sync`

- `uv pip compile requirements.in -o requirements.txt`：把松散需求编译成锁定版本（pip-tools 替代）。
- `uv pip sync requirements.txt`：按锁定文件同步环境（先卸后装，更严格）。
- 官方文档：<https://docs.astral.sh/uv/pip/compile/>

### 4.6 缓存与状态

#### `uv self update`

- 升级 uv 自身到最新版本。

#### `uv cache dir` / `clean` / `prune`

- 缓存位置：默认 `~/.cache/uv`（Linux/macOS）或 `%LOCALAPPDATA%\uv\cache`（Windows）。
- `clean` 清空全部；`prune` 只清过期的，保留还在被引用的。
- 官方文档：<https://docs.astral.sh/uv/concepts/cache/>

#### `uv tool dir` / `uv python dir`

- 显示工具安装目录 / Python 安装目录（卸载时需要）。
- 官方文档：<https://docs.astral.sh/uv/concepts/tools/#discovery>

### 4.7 关键规则速记

#### `.venv` 自动创建规则

| 命令 | 是否自动创建 `.venv` | 说明 |
| --- | --- | --- |
| `uv init` | ❌ | 只生成项目结构 |
| `uv python pin` | ❌ | 只写 `.python-version` |
| `uv add` | ✅ | 装包需要 venv |
| `uv sync` | ✅ | 同步依赖需要 venv |

#### 创建项目的推荐顺序

```bash
uv init myproj        # 1. 先有 pyproject.toml
cd myproj
uv python pin 3.12    # 2. 再锁 Python 版本
uv sync               # 3. 最后建 venv + 装依赖
```

`uv init` 必须先生成 `pyproject.toml`，否则 `uv python pin` 没有可改的配置文件；`uv sync` 根据最终配置建环境。

#### 好习惯

- 永远用 `uv` 前缀：`uv pip install`、`uv run python ...`，避免误用系统 Python / Conda 环境。
- 自动匹配项目 pin 的 Python 版本。
- 提交 `pyproject.toml` + `uv.lock`，协作时一致。
- 口诀：**「uv 开头的命令，就是安全的命令」**。
