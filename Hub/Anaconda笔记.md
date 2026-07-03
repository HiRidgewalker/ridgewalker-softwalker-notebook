# Anaconda 笔记

> 由旧稿重新整理版本，精炼为 4 章节结构：概述与定位 / 命令速查表 / Ubuntu 实战 / 命令详解。旧稿目录已清理，当前以本文为准。

## 1. 概述与定位

### 1.1 三个相关概念的关系

| 名称 | 本质 | 体积 | 适用场景 |
| --- | --- | --- | --- |
| **Anaconda Distribution** | 预装 300+ 科学计算包的发行版 | 2~4 GB | 教学、需要一键拥有全套工具 |
| **Miniconda** | 只含 conda + Python + 依赖 | < 100 MB | 生产环境 / 按需装包（推荐） |
| **conda-forge** | 社区驱动的包仓库（channel） | — | 第三方包、版本更新更快 |

> 关键区分：**conda** 是包管理工具本身（类似 pip），**Anaconda/Miniconda** 是发行版（类似 Python 的官方安装包），**conda-forge** 是包仓库（类似 PyPI）。

### 1.2 怎么选

- **推荐 Miniconda**：轻量、按需装、磁盘友好、生产环境无冗余
- **选 Anaconda Distribution**：教学 / 培训 / 不想自己装 numpy、pandas、scipy 等全套
- **不要**把 Anaconda Distribution 的 `base` 环境当开发环境用（容易污染 base、依赖混乱）

### 1.3 什么时候用 conda（vs venv vs uv）

| 工具 | 优势场景 |
| --- | --- |
| **conda** | 跨语言包（R / C / CUDA）、需要预编译二进制、系统库依赖复杂的科学计算栈 |
| **uv** | 纯 Python 项目、追求速度、现代 Python 工程实践 |
| **venv** | 标准库、零依赖、临时隔离 |

> 2026 年默认建议：纯 Python 项目用 **uv** 即可；只有真正需要 conda 生态（如 PyTorch + CUDA、复杂科学计算栈）时才用 conda。

### 1.4 三平台安装（Miniconda）

**Ubuntu / Linux**

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# 按提示回车 / yes / 选择安装路径（默认 ~/miniconda3）
```

**macOS**

```bash
# Intel x86_64
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# Apple Silicon (M1/M2/M3)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

或者直接下 pkg 双击安装：<https://docs.anaconda.com/miniconda/install/#quick-command-line-install>

**Windows**

下 exe 双击安装：<https://docs.anaconda.com/miniconda/install/#quick-command-line-install>

**安装后初始化**（关键，否则 `conda activate` 会报 `CommandNotFoundError`）

```bash
conda init bash     # bash
conda init zsh      # zsh
conda init fish     # fish
# 装完重启 shell 或 source ~/.bashrc 让 PATH 生效
```

**验证**

```bash
conda --version
```

### 1.5 卸载

**Linux / macOS**

```bash
# 1. 删除安装目录
rm -rf ~/miniconda3
# 或者 rm -rf ~/anaconda3（如果是 Anaconda Distribution）

# 2. 删除用户级配置和缓存
rm -rf ~/.conda
rm -rf ~/.continuum

# 3. 清理 ~/.bashrc / ~/.zshrc 里的 conda init 段
# 一般是这几行：
#   >>> conda initialize >>>
#   !! Contents within this block are managed by 'conda init' !!
#   ...
#   <<< conda init <<<
```

**Windows**

通过「控制面板 → 程序与功能」卸载 Anaconda / Miniconda，然后删 `C:\Users\<user>\.conda` 和 `C:\Users\<user>\.continuum`。

---

## 2. 命令速查表

```text
# ===== 环境管理 =====
conda create -n <env>                          # 创建空环境
conda create -n <env> python=3.12             # 创建时指定 Python 版本
conda create -n <env> python=3.12 numpy pandas # 创建时直接装包
conda activate <env>                           # 激活环境
conda deactivate                               # 退出当前环境（回到 base）
conda env list                                 # 列出所有环境
conda info --envs                              # 同上
conda env remove -n <env>                      # 删除指定环境
conda env rename -n <old> <new>                # 重命名环境
conda env export > environment.yml             # 导出环境配置
conda env export --from-history > environment.yml  # 只导出显式装的包（推荐）
conda env create -f environment.yml            # 从文件创建环境
conda env update -f environment.yml            # 按文件更新已有环境
conda env update --prune -f environment.yml    # 更新并移除 yml 中不存在的包

# ===== 包管理 =====
conda install <pkg>                            # 装包到当前环境
conda install <pkg>=2.3.4                      # 装指定版本
conda install <pkg>=2                          # 仅指定主版本
conda install -n <env> <pkg>                   # 装到指定环境
conda install -c conda-forge <pkg>             # 指定 channel 装包
conda install --channel conda-forge --name <env> <pkg>
conda update <pkg>                             # 升级包
conda update --all                             # 升级当前环境所有包
conda update -n base conda                     # 升级 conda 自身
conda remove <pkg>                             # 卸包
conda remove -n <env> --all                    # 删除环境中所有包（保留空环境）
conda list                                     # 列出当前环境的包
conda list -n <env>                            # 列出指定环境的包
conda search <pkg>                             # 搜索包
conda clean --all                              # 清理缓存（tarballs + 索引 + lock）

# ===== 信息查询 =====
conda --version                                # conda 版本
conda info                                     # 系统信息（Python 路径、envs 目录、channels 等）
conda list                                     # 当前环境已装包

# ===== 配置 =====
conda config --show                            # 查看所有配置
conda config --get channels                    # 查看 channel 列表与优先级
conda config --add channels conda-forge        # 添加 channel（追加到末尾）
conda config --prepend channels conda-forge    # 添加 channel（插到首位，优先级最高）
conda config --remove channels conda-forge     # 移除 channel
conda config --set show_channel_urls yes       # 装包时显示来源 URL
conda config --set auto_activate_base false    # 新 shell 不自动激活 base（推荐）
conda config --set env_prompt '({name}) '      # shell prompt 显示当前环境名

# ===== 导出与共享 =====
conda env export > environment.yml
conda env export --from-history > environment.yml
conda env create -f environment.yml
```

---

## 3. Ubuntu 实战（数据分析场景）

完整最小可运行流程：

```bash
# 1. 装 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
# -b 静默模式；-p 指定安装路径；装完手动 source 一次
source ~/miniconda3/etc/profile.d/conda.sh

# 2. 初始化 shell（之后重启 shell 自动生效）
conda init bash
source ~/.bashrc

# 3. 关掉 base 自动激活（推荐，避免污染）
conda config --set auto_activate_base false

# 4. 创建数据分析环境
conda create -n data python=3.12 numpy pandas jupyter matplotlib

# 5. 激活 + 验证
conda activate data
python --version          # 应为 3.12
python -c "import numpy, pandas, matplotlib; print('OK')"

# 6. 写个最小 demo.py
cat > demo.py <<'EOF'
import numpy as np
import pandas as pd

arr = np.array([1, 2, 3, 4, 5])
print("mean:", arr.mean())

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
print(df)
EOF

python demo.py

# 7. 导出环境配置（推荐 --from-history，只导出显式装的包）
conda env export --from-history > environment.yml
cat environment.yml
# 输出类似：
#   name: data
#   channels:
#     - defaults
#   dependencies:
#     - python=3.12
#     - numpy
#     - pandas
#     - jupyter
#     - matplotlib

# 8. 共享给队友 / 另一台机器
# 把 environment.yml 传过去，然后：
conda env create -f environment.yml -n data
```

### 3.1 常用后续动作

```bash
# 加包
conda install scikit-learn
# 或指定 channel
conda install -c conda-forge geopandas

# 卸包
conda remove pandas

# 升级当前环境所有包（谨慎，可能破坏依赖）
conda update --all

# 看当前环境装了什么
conda list

# 退出当前环境
conda deactivate

# 彻底删除环境
conda env remove -n data

# 清理缓存（释放磁盘）
conda clean --all
```

### 3.2 environment.yml 协作时的最小提交集合

- `environment.yml`（导出文件）
- 协作方 clone 后 `conda env create -f environment.yml` 即可还原

> 注意：原笔记提到的 `environment.yml` 默认导出方式会包含所有间接依赖（几百行），不方便跨平台协作；`--from-history` 只导出显式装的包，更精简可读。

---

## 4. 命令详解

### 4.1 环境管理

#### `conda create`

- 创建环境：`conda create -n <name>` 空环境；`conda create -n <name> python=3.12` 指定版本；`conda create -n <name> python=3.12 pkg1 pkg2` 创建时直接装包
- 不会激活，需要再 `conda activate`
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>

#### `conda activate` / `conda deactivate`

- 激活：当前 shell 切换到指定环境的 PATH（python / pip 都指向该环境）
- 停用：回到 `base`（如果 base 未自动激活，则退到系统 Python）
- **必须先 `conda init`**，否则 `conda activate` 报 `CommandNotFoundError`
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment>

#### `conda env list` / `conda info --envs`

- 列出所有环境（`*` 标当前激活）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#viewing-a-list-of-your-environments>

#### `conda env remove -n <env>`

- 彻底删除环境（连同其下所有包）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#removing-an-environment>

#### `conda env rename`

- 重命名环境。`conda rename` 行为在某些版本上有坑（跨位置移动可能改写 PATH），优先用 `export` → `create` 重建
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#rename-an-existing-environment>

### 4.2 包管理

#### `conda install`

- 默认从 `defaults` channel 装；`-c conda-forge` 指定 conda-forge
- 装到当前环境；`-n <env>` 指定环境
- 冲突解决：conda 会尝试找兼容的版本组合，无法满足时直接报错（不像 pip 有冲突但能装上）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#installing-packages>

#### `conda update` / `conda update --all`

- `conda update <pkg>`：升级指定包
- `conda update --all`：升级当前环境所有包到各自最新版本（**风险操作**，可能破坏依赖一致性）
- 升级 conda 自身：`conda update -n base conda`
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#updating-packages>

#### `conda remove`

- `conda remove <pkg>`：卸包
- `conda remove -n <env> --all`：删环境内所有包（保留空环境壳）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#removing-packages>

#### `conda list` / `conda search`

- `list`：当前环境已装包（带 channel 和版本号）
- `search`：在所有已知 channel 搜索可用包
- 官方文档：
  - <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#viewing-a-list-of-installed-packages>
  - <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#searching-for-packages>

#### `conda clean --all`

- 清理 tarballs（下载缓存）、索引缓存、lock 文件
- 长期使用后释放几 GB 不奇怪
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#clearing-the-index-and-package-cache>

### 4.3 共享环境

#### `conda env export`

- 默认导出当前环境所有包（含间接依赖），生成完整 yml
- `--from-history`：只导出显式 `conda install` 装过的包（推荐，跨平台兼容性好）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment>

#### `conda env create -f` / `conda env update -f`

- `create -f`：从 yml 新建环境（可加 `-n <name>` 改名）
- `update -f`：把当前环境更新到 yml 描述
- `update --prune -f`：更新并移除 yml 中不再声明的包（保持环境干净）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file>

#### `environment.yml` 结构详解

```yaml
name: data                # 环境名
channels:                 # 包仓库优先级（从上到下）
  - conda-forge           # 优先 conda-forge
  - defaults              # 找不到再走 defaults
dependencies:             # conda 装的包
  - python=3.12
  - numpy
  - pandas
  - pip                   # 想在环境内用 pip 时显式声明
  - pip:                  # pip 子段：在 conda 环境内用 pip 装的包
      - Flask-Testing
      - some-private-pkg
```

- `channels` 顺序即优先级
- `pip:` 子段用于装 conda 仓库没有的纯 Python 包
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#create-env-file-manually>

### 4.4 Channel 机制

| Channel | 说明 | 优先级策略 |
| --- | --- | --- |
| `defaults` | Anaconda 官方维护，包较少、更新慢 | 默认 |
| `conda-forge` | 社区驱动，包多、更新快、跨平台好 | 显式 `-c` 或 prepend |
| 自建 channel | 企业内部 / 私有包 | 自建索引 |

**关键概念**：装包时按 channels 列表顺序检索；找不到就报 `PackagesNotFoundError`

- 建议：现代项目以 **conda-forge** 为主、defaults 兜底

```bash
# 把 conda-forge 设为最高优先级
conda config --prepend channels conda-forge
```

- 官方文档：<https://docs.conda.org/projects/conda-build/en/latest/concepts/channels.html>

### 4.5 配置（`.condarc`）

- 用户级配置文件：`~/.condarc`（Linux/macOS）或 `C:\Users\<user>\.condarc`（Windows）
- 常用配置：

```yaml
# ~/.condarc
channels:
  - conda-forge
  - defaults

show_channel_urls: true         # 装包时打印来源 URL
auto_activate_base: false      # 新 shell 不自动激活 base
env_prompt: '({name}) '        # shell 提示符显示当前环境名
ssl_verify: true
```

- `conda config --show` 查看所有生效配置
- `conda config --set KEY VALUE` 设置单个配置项（自动写 `.condarc`）
- 官方文档：<https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/use-condarc.html>

### 4.6 conda vs uv 协作模式

两种主流用法：

**1. 完全替代**：现代 Python 项目直接用 uv，跳过 conda

```bash
# 等价的 uv 流程
uv init myproj
uv python pin 3.12
uv add numpy pandas
uv run python demo.py
```

**2. 混用**：conda 管 Python + 系统依赖（Cuda、MKL、GDAL），uv 加速装纯 Python 包

```bash
# conda 创建基础环境
conda create -n geo python=3.11 gdal
conda activate geo

# uv 在该环境内加速装纯 Python 依赖
uv pip install --python $CONDA_PREFIX/bin/python geopandas shapely
```

> 经验法则：能 uv 就 uv；只有真正需要系统级二进制包（Cuda、FFmpeg、GDAL、R 包）才上 conda。

### 4.7 常见踩坑

#### `conda activate` 报 `CommandNotFoundError`

原因：没执行 `conda init`，shell 不知道 conda 函数定义。

解决：

```bash
conda init bash   # 或 zsh / fish
source ~/.bashrc  # 或重启 shell
```

#### 装包时一直转圈或超时

原因：默认源下载慢。

解决：换 conda-forge + 国内镜像

```bash
conda config --prepend channels conda-forge
# 清华源（仅作示例，按需启用）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

#### `Solving environment: failed` 依赖冲突

- 优先看错误里的冲突包，指定版本范围
- 加 `--strict-channel-priority` 让 channel 优先级更严格，避免混装
- 实在不行就新建干净环境，逐一装包定位冲突源

#### base 环境被污染怎么办

```bash
# 1. 看 base 里装了什么
conda list -n base

# 2. 把不需要的包全卸了
conda remove -n base <pkg>

# 3. 实在乱就重装
rm -rf ~/miniconda3
# 重装 Miniconda
```

#### 共享包缓存（shared package cache）

- 多用户共用一份包缓存可省磁盘：原笔记有相关链接
- 配置：<https://docs.anaconda.com/working-with-conda/packages/shared-pkg-cache/>

#### 离线安装 conda 包

- 先在有网机器上 `conda download <pkg>` 或直接拷贝 `pkgs/` 目录
- 离线机器设置 `conda install --offline <pkg>`
- 官方文档：<https://docs.anaconda.com/working-with-conda/packages/install-packages/>
