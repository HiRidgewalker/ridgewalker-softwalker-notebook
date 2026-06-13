一个python的包管理器: [UV](https://docs.astral.sh/uv/getting-started/installation/)

## 升级uv
```shelle
uv self update
```
## uninstalltion
```shell
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
```
## 删除uv和uvx二进制文件
```shell
rm $HOME\.local\bin\uv.exe
rm $HOME\.local\bin\uvx.exe
```
## UV常用命令
[UV常用命令](https://docs.astral.sh/uv/getting-started/features/)
UV安装python
```shell
-- 安装特定版本
uv python install 3.12

-- 安装多个版本
uv python install 3.11, 3.12
```

**uv安装和管理python**
`uv python install` ：安装 Python 版本。
`uv python list` ：查看可用的 Python 版本。
`uv python find` ：查找已安装的 Python 版本。
`uv python pin` ：固定当前项目以使用特定的 Python 版本。
`uv python uninstall` ：卸载一个 Python 版本。

**Scripts脚本**
`uv run` ：运行脚本。
`uv add --script` ：向脚本添加依赖项。
`uv remove --script` ：从脚本中删除依赖项。
> 示例: https://docs.astral.sh/uv/guides/projects/#managing-dependencies


**Project项目**
`uv init` ：创建一个新的 Python 项目。
`uv add` ：向项目添加依赖项。
`uv remove` ：从项目中删除依赖项。
`uv sync` ：将项目的依赖项与环境同步。
`uv lock` ：为项目的依赖项创建一个锁文件。
`uv run` ：在项目环境中运行命令。
`uv tree` ：查看项目的依赖树。
`uv build` ：将项目构建到分发档案中。
`uv publish` ：将项目发布到包索引。

**Tools工具**
`uvx` / `uv tool run` ：在临时环境中运行工具。
`uv tool install` ：在用户范围内安装工具。
`uv tool uninstall` ：卸载工具。
`uv tool list` ：列出已安装的工具。
`uv tool update-shell` ：更新 shell 以包含工具可执行文件。

**pip接口**
`uv venv` ：创建一个新的虚拟环境。
`uv pip install` ：将包安装到当前环境中。
`uv pip show` ：显示有关已安装包的详细信息。
`uv pip freeze` ：列出已安装的软件包及其版本。
`uv pip check` ：检查当前环境是否有兼容的包。
`uv pip list` ：列出已安装的包。
`uv pip uninstall` ：卸载软件包。
`uv pip tree` ：查看环境的依赖树。

**在环境中锁定软件包**
`uv pip compile` ：将需求编译成锁文件。
`uv pip sync` ：使用锁文件同步环境。

**管理和检查 uv 的状态，例如缓存、存储目录或执行自我更新**
`uv cache clean` ：删除缓存条目。
`uv cache prune` ：删除过时的缓存条目。
`uv cache dir` ：显示 uv 缓存目录路径。
`uv tool dir` ：显示 uv 工具目录路径。
`uv python dir` ：显示 uv 安装的 Python 版本路径。
`uv self update` ：将 uv 更新到最新版本。

**获取说明**
`uv 命令 --help`
获取详细说明
`uv 命令 -v`
获取更详细说明
`uv 命令 -vv`

uv创建项目
`uv init 项目名称`

uv添加依赖
`uv add 第三方包名称`

uv从requirements.txt中添加包
`uv add -r requirements.txt`

uv删除依赖项
`uv remove 依赖性名称`

uv更改依赖项
`uv add "httpx>0.1.0"`

在特定平台安装依赖项
`uv add "jax; sys_platform == 'linux'"`

uv安装whl文件
`uv add /example/foo-0.1.0-py3-none-any.whl`

同步环境
`uv sync`

创建虚拟环境时候指定python版本
`uv venv --python 3.11.6`
> https://docs.astral.sh/uv/concepts/python-versions/#requesting-a-version

创建虚拟环境
uv 支持创建虚拟环境，例如在 `.venv` 创建虚拟环境：
`uv venv`

### `uv.lock`文件
`uv.lock` 是一个跨平台的锁文件，其中包含项目依赖项的精确信息。与用于指定项目总体需求的 `pyproject.toml` 不同，锁文件包含项目环境中已安装的确切解析版本。此文件应纳入版本控制，以便在不同机器上实现一致且可重复的安装。

`uv.lock` 是一个人类可读的 TOML 文件，但由 uv 管理，不应手动编辑。
明确创建锁文件
`uv lock`
虽然锁文件是自动创建的，但也可以使用 `uv lock` 明确创建或更新锁文件：


### uv激活虚拟环境

> uv sync
> .venv\Scripts\activate // win
> source .venv/bin/activate // ubuntu


## uv sync总结
### 1. uv sync使用场景
✅ 需要运行 `uv sync` 的典型场景
2. **第一次初始化环境时**
    - 新 clone 下来的项目，还没有虚拟环境。
    - 直接跑：        
        `uv sync`        
        会创建虚拟环境并安装 `pyproject.toml` / `uv.lock` 里声明的依赖。     
---
2. **你修改了 `pyproject.toml` 依赖配置**
    - 增加/删除依赖：
        `dependencies = ["fastapi", "pandas", "sqlalchemy"]  # 新增`
    - 修改 Python 要求版本：
        `requires-python = ">=3.10"`
    - 改完后运行：
        `uv sync`
        → 会重新解析依赖并更新虚拟环境。
---
3. **你切换了 Python 版本**
    - 比如：
        `uv python pin 3.10 uv sync`
    - 这时 `uv` 会重新安装所有包，换成适配 3.10 的 wheel。   
---
4. **锁文件（uv.lock）更新或不同步时**
    - 如果你拉取了别人的分支，里面 `uv.lock` 变了。
    - 运行：
        `uv sync`
        → 会让本地虚拟环境跟锁文件完全一致。  
---
5. **虚拟环境损坏或丢失时**
    
    - 比如你手动删了 `.venv` 或者依赖乱掉了。
    - 直接跑：
        `uv sync`
        → 会重新创建虚拟环境并安装依赖。
---
❌ 不需要运行 `uv sync` 的情况
- 只是运行代码，不改依赖、不切换 Python → 不需要。
- 已经 `uv add package` 或 `uv remove package`（这些命令会自动同步） → 不需要额外 `uv sync`。
---
📌 总结口诀
- **第一次建环境 → sync**
- **改了依赖 → sync**
- **换 Python 版本 → sync**
- **换了锁文件 → sync**
- **环境坏掉了 → sync**
其他时候就不用管。

### 2. `uv sync`执行后的行为
🔎 具体行为
1. **如果有新增依赖**
    - `pyproject.toml` 里加了包，`uv sync` 会下载并安装到虚拟环境。
2. **如果有删除依赖**
    - 从 `pyproject.toml` 或 `uv.lock` 里删了包，`uv sync` 会从虚拟环境里卸载掉它。
3. **如果依赖版本发生变化**
    - 例如从 `pandas = "^2.2"` 改成 `pandas = "^2.1"`，
    - `uv sync` 会卸载旧版本，下载并安装新版本。
4. **如果切换了 Python 版本**
    - 例如从 Python 3.12 切到 3.10，
    - 有些 wheel 版本不兼容，`uv sync` 会自动重新解析依赖树，下载 3.10 能用的包。
5. **如果虚拟环境里多了没声明的包**
    - `uv sync` 会把它们移除，保证虚拟环境和 `uv.lock` 一致。
---
📦 下载位置
- 包会被下载到 **全局缓存目录**（一般在 `~/.cache/uv`）。
- 然后再从缓存里安装到你的虚拟环境（比如 `.venv/` 或 `venv/`）。
- 所以多次 `uv sync` 不会重复从网络下载，而是直接用缓存。
👉 总结：  
是的，运行 `uv sync` 会让虚拟环境里的第三方包 **精确对齐配置/锁文件**，需要新增的会下载，需要替换的会换掉，不需要的会删掉。

## `uv python pin`总结
### 1. `uv python pin`使用场景
🎯 `uv python pin` 的核心作用
它的作用是把项目固定到某一个python版本上， 保证后续所有`uv`操作都使用这个版本
🔎 具体做了什么
当你执行：`uv python pin 3.10`
会有两个效果：
1. **写入 `.python-version` 文件**
    - 在项目根目录生成一个 `.python-version` 文件，内容类似：  `3.10`
    - `uv` 之后在这个目录里执行时，会自动选择 Python 3.10 解释器。
2. **更新 `pyproject.toml` 的 Python 要求**
    - 它会改写： `[project] requires-python = ">=3.12"`
        变成类似：`[project] requires-python = "==3.10.*"`
    - 这样锁文件（`uv.lock`）和依赖解析时，都只会用 3.10 的包。
---
✅ 使用场景
1. **你希望项目长期固定 Python 版本**
    - 比如团队协作时，大家都用 3.10，避免有人用 3.12 出现兼容性问题。
2. **在同一台机器上有多个 Python 版本**
    - `uv` 会优先使用 `.python-version` 指定的版本，不会乱跑。
3. **避免锁文件不一致**
    - 如果团队有人用 3.12，有人用 3.10，锁文件可能会不同步。
    - `uv python pin` 让大家一致用一个版本。
---
⚠️ 注意
- `uv python pin` 是 **项目级别** 的，不是全局的。
- 它不是一次性的（不是只对当前命令有效），而是写进配置，后续一直生效。
- 如果要改回别的版本，可以再执行一次，比如：
    `uv python pin 3.12`
---
📌 总结
- `uv python pin X.Y` = **固定项目 Python 版本为 X.Y**
- 它会写 `.python-version`，并更新 `pyproject.toml` 的 `requires-python`。
- 好处是团队协作和依赖解析更稳定，不会因为 Python 版本差异导致问题。

### 2. `uv python pin`执行后的行为
当你在项目里执行了：
`uv python pin 3.10`
之后在这个目录下: 
📌 所有 `uv` 命令都会用 Python 3.10 作为解释器
1. **`uv sync`**
    - 会用 Python 3.10 解析依赖，安装的包版本都是 3.10 能兼容的 wheel。
2. **`uv add`**
    - 比如：`uv add fastapi`
    - 安装的是适配 3.10 的 `fastapi` 及其依赖版本。
    - 然后更新 `pyproject.toml` 和 `uv.lock`。
3. **`uv pip`**
    - 本质上是 pip 的封装，但会强制用 3.10 的虚拟环境：
        `uv pip install requests`
    - 安装的目标环境是 3.10 的虚拟环境，不会误装到 3.12。
4. **运行代码时**
    - 如果你用 `uv run python script.py`，执行的解释器就是 3.10。  
---
🔎 为什么能做到？
- `uv python pin` 会在项目里生成一个 `.python-version` 文件（内容是 `3.10`）。
- `uv` 每次在当前目录运行时，都会优先读取这个文件，确定应该用哪个 Python 解释器。
- 同时会把 `pyproject.toml` 的
    `requires-python = "==3.10.*"`
    写死，确保锁文件解析和虚拟环境都是一致的。
---
⚠️ 注意点
- 只有在 **项目目录下** 才生效；如果你 cd 到别的地方再跑 `uv`，就不会强制用 3.10。
- 如果机器上没有 Python 3.10，`uv` 会报错，提示你安装：
    `uv python install 3.10`
---
👉 总结：  
`uv python pin 3.10` = 之后在该项目里所有的 `uv sync / uv add / uv pip / uv run` **都会用 Python 3.10 的虚拟环境**。

## 使用uv创建一个python项目并执行python版本的步骤
✅ 推荐顺序
1. **先 init**（初始化项目结构）
    `uv init myproj `
    `cd myproj`
2. **再 pin**（锁定 Python 版本）
    `uv python pin 3.10`
3. **最后 sync**（创建虚拟环境 + 装依赖）
    `uv sync`

---

🔎 为什么这样排顺序？
- `uv init` 必须先生成 `pyproject.toml`，否则没有配置文件可修改。
- `uv python pin` 会在已有 `pyproject.toml` 基础上更新 Python 版本要求。
- `uv sync` 根据最终配置创建虚拟环境并下载依赖。


## 好习惯: 调用uv里面的命令，比如pip之类的，永远是uv在前面
🔹 最安全、最推荐的习惯
- **安装依赖**：
`uv add fastapi `
`uv add pandas`
- **使用 pip**：
`uv pip install requests uv pip list uv pip uninstall xxx`
- **运行脚本**：
`uv run python main.py`
---
为什么这样安全
1. **始终使用 uv 管理的虚拟环境**
    - 不依赖系统 PATH，也不会误用 Conda 或系统 Python。
2. **自动匹配 Python 版本**
    - 如果项目里用 `uv python pin 3.10`，uv 会确保命令运行在 3.10 的环境里。 
3. **锁文件同步依赖**
    - `uv add` 会同时更新 `pyproject.toml` 和 `uv.lock`，保证团队协作时依赖一致。
---
口诀
> **“uv 开头的命令，就是安全的命令”**  
> 不用担心 PATH、pip 找不到或者跑到 Conda 环境的问题。


## uv add 和uv pip install的区别
总结一句话就是：
- **`uv add <package>`**
    - 会 **安装到虚拟环境**
    - 会 **更新 `pyproject.toml`**
    - 会 **更新 `uv.lock`**
- **`uv pip install <package>`**
    - 只会 **安装到虚拟环境**
    - **不会更新** `pyproject.toml` 或 `uv.lock`

## uv remove和uv pip unintall
1️⃣ uv remove
- 命令：
`uv remove fastapi`
- 作用：
1. **从虚拟环境卸载包** ✅
2. **更新 pyproject.toml** ✅
3. **更新 uv.lock** ✅
> 就像 `uv add` 的反向操作，保证依赖声明和锁文件同步。
---
2️⃣ uv pip uninstall
- 命令：
`uv pip uninstall fastapi`
- 作用：
1. **只卸载虚拟环境里的包** ✅
2. **不会修改 pyproject.toml** ❌
3. **不会修改 uv.lock** ❌

> 只在本地环境生效，不影响锁文件或团队其他人。

注意最好使用`uv venv .venv`使用默认的虚拟环境名称，或者uv add 之类的加上`--activate`，默认使用的就是激活的虚拟环境

---
3️⃣ 使用 `.python-version` + `--active`
- 如果不想改默认虚拟环境，也可以临时使用当前激活的虚拟环境：
`source venv/bin/activate `
`uv add fastapi --active`
- `--active` 会告诉 uv 使用当前 shell 激活的虚拟环境，无论名称是什么
- 适合临时操作或测试环境
---
4️⃣ 配置文件方式（可选）
- 可以在 `pyproject.toml` 里设置：
`[tool.uv] venv = "venv"    # 指定虚拟环境路径或名称`
- uv 启动时会读取这个配置，默认使用指定名称的虚拟环境


## `.venv`自动创建逻辑
### 🗂️ `.venv` 自动创建逻辑
1. `uv init`
- **不会创建 `.venv`**。
- 它只是初始化项目结构（生成 `pyproject.toml`、`src/` 等），不会动虚拟环境。
---
2. `uv python pin`
- **不会创建 `.venv`**。
- 它只会在项目目录下生成或修改 `.python-version` 文件（记录 Python 版本），并不会创建虚拟环境。
---
 3. `uv add`
- **会创建 `.venv`（如果还不存在的话）**。
- 因为要安装依赖，必须有一个虚拟环境，所以 uv 会在项目根目录下自动创建 `.venv/`。
- 同时会更新 `pyproject.toml` 和 `uv.lock`。
---
4. `uv sync`
- **也会创建 `.venv`（如果还不存在的话）**。
- `uv sync` 的作用是根据 `pyproject.toml` 和 `uv.lock` 把依赖同步到环境里，所以需要 `.venv`，如果没有就新建。
---
✅ 总结表格

|命令|是否创建 `.venv`|说明|
|---|---|---|
|`uv init`|❌ 否|只生成项目结构|
|`uv python pin`|❌ 否|只写 `.python-version`|
|`uv add`|✅ 会|安装依赖时需要虚拟环境|
|`uv sync`|✅ 会|同步依赖时需要虚拟环境|

👉 所以：**只有涉及依赖安装的命令（`uv add`、`uv sync`）才会触发 `.venv` 自动创建**。


