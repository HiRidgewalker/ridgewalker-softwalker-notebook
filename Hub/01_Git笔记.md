# Git 笔记

> 原 `文档/Git常用命令.md` + `文档/git, github, gitee.md` 的重新整理版本。结构上分 3 个 Hub 文件：本文是**总览**，[[Hub/02_Git命令速查笔记]] 是**全参数速查**（命令多时翻这里），[[Hub/03_Git回滚决策笔记]] 是**回滚专题**（restore / reset / revert / stash / clean 的决策树）。原笔记保留在 `文档/Git常用命令.md` 和 `文档/git, github, gitee.md` 供回溯。

---

## 1. 概述与基础概念

### 1.1 Git 是什么

分布式版本控制系统。每个开发者本地都有完整的历史快照，不依赖中央服务器也能提交、查看历史、回滚。

### 1.2 Git 三层模型

理解 Git 最重要的心智模型：

| 层级 | 名称 | 含义 |
| --- | --- | --- |
| 第一层 | **工作区**（Working Tree） | 你当前正在编辑的文件 |
| 第二层 | **暂存区**（Index / Staging Area） | 已经 `git add` 准备提交的内容 |
| 第三层 | **提交历史**（Commit History） | 已经 `git commit` 形成的快照链 |

> 几乎所有 Git 命令都是在操作这三层之间的"流动"。

### 1.3 核心工作流

```text
add → commit → push
```

- `git add`：工作区 → 暂存区
- `git commit`：暂存区 → 提交历史
- `git push`：本地历史 → 远程仓库

> **一句话总结 Git 核心**：add → commit → push。**出问题就三招**：restore → reset → revert（详细决策见 [[Hub/03_Git回滚决策笔记]]）。

### 1.4 安装与配置

Git 官网下载：<https://git-scm.com/downloads>

> 详细代理配置、用户名邮箱、提交规范见本文 4.8「配置与平台」。

---

## 2. 命令速查表

> 完整参数与坑点见 [[Hub/02_Git命令速查笔记]]。

```bash
# ===== 信息查看 =====
git status                              # 当前状态：分支 / 改动 / 未跟踪
git log                                 # 提交历史
git log --oneline                       # 一行展示
git log --graph                         # 图形化分支
git log -n 5                            # 最近 5 条
git diff                                # 工作区 vs 暂存区
git diff --staged                       # 暂存区 vs 上次提交
git blame <file>                        # 看每一行是谁改的

# ===== 提交 =====
git add <file>                          # 添加到暂存区
git add .                               # 当前目录所有改动
git add -A                              # 所有改动（含删除）
git add -u                              # 只添加已跟踪文件变化
git commit -m "msg"                     # 提交
git commit -am "msg"                    # add + commit（不含新文件）
git commit --amend                      # 修改最后一次提交

# ===== 分支 =====
git branch                              # 查看本地分支
git branch -a                           # 含远程
git branch -v                           # 显示最后提交
git branch <name>                       # 创建分支
git checkout -b <name>                  # 创建并切换（旧写法）
git switch -c <name>                    # 创建并切换（新写法，推荐）
git switch <name>                       # 切换分支
git branch -d <name>                    # 安全删除
git branch -D <name>                    # 强制删除
git merge <branch>                      # 合并分支到当前

# ===== 远程 =====
git remote -v                           # 查看远程仓库
git fetch                               # 只获取不合并
git pull                                # 获取 + 合并（= fetch + merge）
git push                                # 推送到远程
git push -u origin main                 # 首次推送并设置上游

# ===== 回滚（重点）=====
git restore <file>                      # 撤销工作区
git restore --staged <file>             # 撤销暂存
git reset --soft HEAD~1                 # 回退 commit，保留暂存
git reset HEAD~1                        # 回退 commit，清空暂存（默认）
git reset --hard HEAD~1                 # 回退 commit + 暂存 + 工作区（⚠️ 危险）
git revert <commit_id>                  # 生成反向提交（已 push 用）
git clean -fd                           # 删除未跟踪文件
# 详细决策见 [[Hub/03_Git回滚决策笔记]]

# ===== Stash =====
git stash                               # 暂存当前改动
git stash push -m "msg"                 # 带说明
git stash -u                            # 包含未跟踪
git stash list                          # 查看 stash
git stash pop                           # 恢复并删除
git stash apply                         # 恢复但不删除

# ===== 标签 =====
git tag v1.0                            # 创建本地标签
git push origin v1.0                    # 推送标签到远程

# ===== 撤销 .gitignore 重新追踪 =====
git rm -r --cached .
git add .
git commit -m "retrack files based on .gitignore"
```

---

## 3. 实战高频组合（Codex / AI 改码场景）

> 这些组合是日常用 AI 辅助开发时的高频工作流，建议背下来。

### 🟢 1. 改代码前做快照

```bash
git add .
git commit -m "checkpoint"
```

万一 AI 改崩了，一键回到这个状态。

### 🔴 2. 改崩了回退（保留 staged）

```bash
git restore .
```

只撤销工作区改动，staged 的内容还在。

### 🔴 2b. 改崩了 + 想清掉一切

```bash
git restore .
git clean -fd
```

> ⚠️ `git clean -fd` 会**直接删除未跟踪文件**。建议先 `git clean -fdn` 干跑确认。

### 🟡 3. 回到上一个版本

```bash
git reset --hard HEAD~1
```

> ⚠️ 会丢所有未提交改动，慎用。详细见 [[Hub/03_Git回滚决策笔记#2-2-git-reset-移动-head必要时同步状态]]。

### 🔵 4. 开安全分支试验

```bash
git checkout -b codex-test    # 旧写法
# 或
git switch -c codex-test      # 新写法，推荐
```

在新分支试 AI 改动，OK 了再 merge / cherry-pick 回主分支。

### 🧠 5. 查看改了啥

```bash
git diff                # 工作区 vs 暂存
git diff --staged       # 暂存 vs HEAD
git diff --stat         # 统计形式
```

### 🟣 6. Commit 拆错想重组

```bash
git reset --mixed HEAD~1
git add <想提交的文件>
git commit -m "重组后提交"
```

详细见 [[Hub/03_Git回滚决策笔记#5-soft-vs-mixed-决策详解]]。

### ⚪ 7. 完全不想改了，回到干净状态

```bash
git restore .
git clean -fd
```

---

## 4. 命令详解

> 每条命令格式：**行为 → 关键参数 → 坑点 → 官方文档链接**。完整参数见 [[Hub/02_Git命令速查笔记]]。

### 4.1 信息查看

#### `git status`

- 显示：当前分支、是否有修改、是否有未跟踪文件。
- 日常最常用。

#### `git log`

常用参数：

```bash
git log --oneline       # 一行展示
git log --graph         # 图形化分支结构
git log --decorate      # 显示分支/标签
git log -n 5            # 最近 5 条
```

> 官方文档：<https://git-scm.com/docs/git-log>

#### `git diff`

```bash
git diff                # 工作区 vs 暂存区
git diff --staged       # 暂存区 vs 上一次提交
git diff <file>         # 指定文件
```

> 官方文档：<https://git-scm.com/docs/git-diff>

#### `git blame <file>`

- 查看每一行是谁、什么时候改的。
- 排错时定位"这段代码谁写的"很方便。

> 官方文档：<https://git-scm.com/docs/git-blame>

### 4.2 提交流程

#### `git add` 三种写法对比

| 写法 | 新文件 | 修改 | 删除 | 场景 |
| --- | --- | --- | --- | --- |
| `git add .`     | ✅ | ✅ | ❌ | 当前目录所有改动 |
| `git add -A`    | ✅ | ✅ | ✅ | 所有改动（含删除），最稳 |
| `git add -u`    | ❌ | ✅ | ✅ | 只添加已跟踪文件的变化 |

> **推荐**：不确定时用 `git add -A`，最安全。

#### `git commit`

```bash
git commit -m "msg"         # 提交
git commit -am "msg"        # add + commit，**不包含新文件**
git commit --amend          # 修改最后一次提交（可改 message 或补文件）
```

> ⚠️ **坑点**：`git commit -am` 不会提交新文件，因为 `-a` 只对已跟踪文件生效。新文件必须先 `git add`。

> 官方文档：<https://git-scm.com/docs/git-commit>

### 4.3 分支管理

#### `git branch` / `git switch` / `git checkout`

| 任务 | 新写法（推荐） | 旧写法 |
| --- | --- | --- |
| 创建并切换 | `git switch -c <name>` | `git checkout -b <name>` |
| 切换分支 | `git switch <name>` | `git checkout <name>` |

> Git 2.23+ 推荐用 `switch` 做分支操作，`restore` 做文件恢复，语义更清晰。

#### `git merge <branch>`

- 把 `<branch>` 合并到当前分支。
- 多人协作时常见。

#### 删除分支

```bash
git branch -d <branch>      # 安全删除（合并过才能删）
git branch -D <branch>      # 强制删除（不管有没有合并）
```

> 官方文档：<https://git-scm.com/docs/git-branch>

### 4.4 远程操作

#### `git remote -v`

- 查看远程仓库地址。

#### `git fetch` vs `git pull`

```text
git pull = git fetch + git merge
```

- `fetch`：只下载远程最新历史到本地，**不自动合并**
- `pull`：fetch 后自动 merge 到当前分支

> **坑点**：直接 `git pull` 可能引入合并冲突。如果不确定远程改了什么，先 `git fetch` + `git log HEAD..origin/main` 看一眼。

#### `git push`

```bash
git push                    # 推送到已配置的上游
git push origin main        # 推送到指定远程 + 分支
git push -u origin main     # 首次推送并设置上游（-u = --set-upstream）
```

> 官方文档：<https://git-scm.com/docs/git-push>

### 4.5 Stash（临时存储）

```bash
git stash                               # 暂存当前改动
git stash push -m "msg"                 # 带说明
git stash -u                            # 包含未跟踪文件
git stash list                          # 查看所有 stash
git stash pop                           # 恢复最近一次并删除记录
git stash apply                         # 恢复但不删除记录
```

> 适用场景：正在改代码要切分支修 bug；改到一半想临时保存进度。详见 [[Hub/03_Git回滚决策笔记#2-5-git-stash-临时存储改动]]。

> 官方文档：<https://git-scm.com/docs/git-stash>

### 4.6 标签（版本发布）

```bash
git tag v1.0                # 创建本地标签（轻量标签）
git tag -a v1.0 -m "msg"    # 创建附注标签（推荐）
git push origin v1.0        # 推送单个标签
git push origin --tags      # 推送所有标签
```

> 官方文档：<https://git-scm.com/docs/git-tag>

### 4.7 Blame（行级溯源）

```bash
git blame <file>            # 每一行前显示作者 + commit
git blame -L 10,20 <file>   # 只看第 10~20 行
```

> 官方文档：<https://git-scm.com/docs/git-blame>

### 4.8 配置与平台

> 原 `文档/git, github, gitee.md` 内容整合到本节。

#### 代理配置（提交到 GitHub）

如果用了代理工具（如 Clash、V2Ray），Git 走代理推送到 GitHub：

```bash
# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 设置代理（端口改成自己的）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

> 参考：<https://blog.csdn.net/m0_56699208/article/details/139141778>

#### 用户名和邮箱（`--local` / `--global` / `--system` 三级区别）

```bash
# system 级：所有用户生效（要 sudo / 管理员权限）
git config --system user.name "Your Name"
git config --system user.email "your@email.com"

# global 级：当前用户所有仓库生效（最常用）
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# local 级：只在当前仓库生效（覆盖 global）
git config --local user.name "Your Name"
git config --local user.email "your@email.com"
```

**优先级**：`local > global > system`

> **项目级配置推荐**：用 `--local` 区分工作账号和个人账号（不同项目不同身份）。

> 参考：<https://blog.csdn.net/bandaoyu/article/details/112968504>

#### 提交规范

推荐使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```text
<type>(<scope>): <subject>

<body>

<footer>
```

常见 type：

- `feat`：新功能
- `fix`：修 bug
- `docs`：文档变更
- `style`：代码格式（不影响逻辑）
- `refactor`：重构
- `test`：测试相关
- `chore`：杂项（构建、依赖等）

示例：

```text
feat(login): add OAuth2 support
fix(api): handle null response from upstream
docs(readme): update install instructions
```

---

## 5. 关键规则速记

### 5.1 一句话总结

```text
Git 核心：add → commit → push
回滚三招：restore → reset → revert
```

### 5.2 常见坑

| 命令 | 坑点 |
| --- | --- |
| `git reset --hard` | 会删除所有未提交改动，**不可恢复**，生产环境慎用 |
| `git clean -fd` | 直接删除未跟踪文件，**不可恢复**（先用 `-fdn` 干跑） |
| `git commit -am` | 不会提交新文件（`-a` 只对已跟踪文件生效） |
| `git pull` | 直接 pull 可能引入合并冲突，建议先 `git fetch` 看一眼 |
| `git push --force` | 强制推送会改写远程历史，团队协作禁用 |

### 5.3 何时用哪个回滚命令

> 详细决策表见 [[Hub/03_Git回滚决策笔记#3-核心对比表一张记所有回滚命令]]。

```text
撤销文件内容    → git restore
撤销 commit     → git reset (未 push) / git revert (已 push)
临时收起来      → git stash
删未跟踪文件    → git clean
```

### 5.4 推荐工作习惯

1. **改代码前先 commit 一次**（"checkpoint"），留个干净起点
2. **不确定用 fetch 别用 pull**（先看一眼再决定合不合并）
3. **危险命令前先想清楚**（`reset --hard` / `clean -fd` / `push -f`）
4. **已 push 的 commit 用 revert 撤销**，别 reset
5. **写好 commit message**，未来你会感谢现在的自己
