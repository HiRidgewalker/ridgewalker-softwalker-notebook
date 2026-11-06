---
title: "Git 命令速查笔记"
sidebar_position: 2
---

# Git 命令速查笔记

> 从 [I_Git笔记](01-git-overview.md) 第 2 章速查表展开，补全所有常用参数与坑点。按"主题 + 命令"分组，每条格式：**语法 → 行为 → 关键参数 → 坑点 → 官方文档链接**。
> 关联笔记：[I_Git笔记](01-git-overview.md)、[III_Git回滚决策笔记](03-git-rollback-decision.md)
> 旧稿目录已清理，当前以本文为准。

---

## 1. 查看类

### `git status`

**行为**：显示当前分支、工作区与暂存区状态、未跟踪文件。

```bash
git status                # 默认详细
git status -s             # 简短输出（机器友好）
```

**输出解读**：

- 红色 `M`：工作区有改动，未 add
- 绿色 `M`：已 add 但未 commit
- `??`：未跟踪文件（新文件）

> 官方文档：<https://git-scm.com/docs/git-status>

---

### `git log`

**行为**：显示提交历史。

| 参数 | 效果 |
| --- | --- |
| `--oneline` | 每个 commit 一行（hash + subject） |
| `--graph` | 图形化分支结构 |
| `--decorate` | 显示分支 / 标签指针 |
| `-n <N>` | 只看最近 N 条 |
| `--all` | 显示所有分支的 commit |
| `--author="<name>"` | 按作者过滤 |
| `--since="2 weeks ago"` | 按时间过滤 |
| `-p` | 显示每个 commit 的 diff |
| `--stat` | 显示文件改动统计 |

**常用组合**：

```bash
git log --oneline --graph --decorate -n 20    # 看最近 20 条 + 分支图
git log --author="limber" --since="1 month"   # 查自己最近一个月的提交
```

> 官方文档：<https://git-scm.com/docs/git-log>

---

### `git diff`

**行为**：显示差异。

| 命令 | 对比范围 |
| --- | --- |
| `git diff`              | 工作区 vs 暂存区 |
| `git diff --staged`     | 暂存区 vs HEAD（上一次提交） |
| `git diff HEAD`         | 工作区 vs HEAD |
| `git diff <commit1> <commit2>` | 两个 commit 之间 |
| `git diff <branch1>..<branch2>` | 两个分支之间 |

**常用参数**：

```bash
git diff --stat               # 只显示统计（哪些文件改了多少行）
git diff --color              # 彩色高亮
git diff <file>               # 只看某个文件
```

> 官方文档：<https://git-scm.com/docs/git-diff>

---

### `git blame`

**行为**：显示文件每一行最后是谁、什么时候改的。

```bash
git blame <file>                       # 整个文件
git blame -L 10,20 <file>              # 只看 10~20 行
git blame -L "/func_start/,/func_end/" <file>   # 按函数范围
```

> 官方文档：<https://git-scm.com/docs/git-blame>

---

## 2. 提交类

### `git add` 三种写法

| 写法 | 新文件 | 修改 | 删除 | 范围 |
| --- | --- | --- | --- | --- |
| `git add <file>`     | ✅ | ✅ | ✅ | 单个文件 |
| `git add .`          | ✅ | ✅ | ❌ | 当前目录及子目录 |
| `git add -A`         | ✅ | ✅ | ✅ | 整个仓库 |
| `git add -u`         | ❌ | ✅ | ✅ | 只对已跟踪文件 |

> **推荐**：不确定时用 `git add -A`，覆盖所有场景。

> ⚠️ 坑点：`git add -u` 不会添加新文件。如果你新建了文件但只用了 `-u`，会漏提交。

> 官方文档：<https://git-scm.com/docs/git-add>

---

### `git commit`

**行为**：把暂存区内容提交到本地历史。

| 参数 | 效果 |
| --- | --- |
| `-m "msg"` | 提交信息 |
| `-a` | 自动 add 已跟踪文件（**不包含新文件**） |
| `--amend` | 修改最后一次提交（改 message 或补文件） |
| `--no-edit` | amend 时保留原 message |
| `--allow-empty` | 允许空提交（没改动也能 commit） |

**常用写法**：

```bash
git commit -m "feat: add login feature"     # 正常提交
git commit -am "fix: bug"                    # 修 bug（已跟踪文件）
git commit --amend -m "new message"         # 改最后一次的 message
git commit --amend --no-edit                # 补文件到上次提交，message 不变
```

> ⚠️ 坑点：`git commit -am` 不会提交新文件。新文件必须先 `git add`。

> 官方文档：<https://git-scm.com/docs/git-commit>

---

## 3. 分支类

### `git branch`

```bash
git branch                  # 列出本地分支
git branch -a               # 含远程
git branch -v               # 显示最后提交
git branch <name>           # 创建分支（不切换）
git branch -d <name>        # 安全删除（合并过才能删）
git branch -D <name>        # 强制删除
git branch -m <new_name>    # 重命名当前分支
```

> 官方文档：<https://git-scm.com/docs/git-branch>

---

### `git switch`（推荐的新写法）

```bash
git switch <name>           # 切换到已有分支
git switch -c <name>        # 创建并切换（-c = --create）
git switch -                # 切换到上一个分支（来回切很方便）
```

> 官方文档：<https://git-scm.com/docs/git-switch>

---

### `git checkout`（旧写法，仍兼容）

```bash
git checkout <name>         # 切换分支
git checkout -b <name>      # 创建并切换
git checkout -- <file>      # 恢复文件（旧式，现在用 restore）
```

> 新写法 vs 旧写法：分支切换用 `switch`，文件恢复用 `restore`。`checkout` 兼有多种语义，不推荐新项目用。

---

### `git merge`

```bash
git merge <branch>          # 把 <branch> 合并到当前分支
git merge --no-ff <branch>  # 禁用 fast-forward，保留分支历史
git merge --abort           # 中止合并（冲突时回退）
```

**场景**：

- 团队成员把 feature 分支合并到 main
- 修完 bug 把 hotfix 分支合并回 main

> 官方文档：<https://git-scm.com/docs/git-merge>

---

## 4. 远程类

### `git remote`

```bash
git remote -v                           # 查看远程仓库地址
git remote add <name> <url>             # 添加远程仓库
git remote remove <name>                # 删除远程
git remote rename <old> <new>           # 重命名远程
git remote set-url <name> <new_url>     # 修改远程地址
```

> 官方文档：<https://git-scm.com/docs/git-remote>

---

### `git fetch`

**行为**：从远程下载最新历史，**不自动合并**。

```bash
git fetch                        # 获取所有远程的更新
git fetch origin                 # 只获取 origin
git fetch origin main            # 只获取 origin 的 main 分支
```

**典型用法**：

```bash
git fetch origin
git log HEAD..origin/main         # 看本地和远程的差异（还没 merge）
git diff HEAD..origin/main        # 看具体改动
```

> 官方文档：<https://git-scm.com/docs/git-fetch>

---

### `git pull`

**行为**：`git fetch` + `git merge` 的组合。

```bash
git pull                          # 当前分支对应的上游
git pull origin main              # 指定远程 + 分支
git pull --rebase                 # 用 rebase 代替 merge（更干净的历史）
```

> ⚠️ 坑点：直接 `git pull` 可能引入合并冲突。建议先 `git fetch` + `git log` 看一下差异再决定。

> 官方文档：<https://git-scm.com/docs/git-pull>

---

### `git push`

```bash
git push                         # 推送到已配置的上游
git push origin main             # 推送到指定远程 + 分支
git push -u origin main          # 首次推送并设置上游（-u = --set-upstream）
git push --all                   # 推送所有分支
git push --tags                  # 推送所有标签
git push --force                 # ⚠️ 强制推送（会改写远程历史，团队禁用）
git push --force-with-lease      # 安全版强制推送（远程有更新会拒绝）
```

> ⚠️ 坑点：默认拒绝 force push 推送到 main / master。要用 `--force-with-lease` 代替 `--force`，更安全。

> 官方文档：<https://git-scm.com/docs/git-push>

---

## 5. Stash / Tag / 杂项

### `git stash`

```bash
git stash                        # 暂存工作区 + 暂存区改动
git stash push -m "msg"          # 带说明
git stash push <file>            # 暂存指定文件
git stash -u                     # 包含未跟踪文件
git stash list                   # 列出所有 stash
git stash show -p                # 看某个 stash 的内容
git stash pop                    # 恢复最近一次并删除记录
git stash pop stash@{1}          # 恢复指定 stash
git stash apply                  # 恢复但不删除
git stash drop stash@{0}         # 删除某个 stash
git stash clear                  # 清空所有 stash
```

> 详细使用场景见 [III_Git回滚决策笔记 > 2-5-git-stash-临时存储改动](03-git-rollback-decision.md#25-git-stash临时存储改动)。

> 官方文档：<https://git-scm.com/docs/git-stash>

---

### `git tag`

```bash
git tag                          # 列出所有标签
git tag v1.0                     # 创建轻量标签
git tag -a v1.0 -m "release v1.0"  # 创建附注标签（推荐）
git tag -d v1.0                  # 删除本地标签
git push origin v1.0             # 推送单个标签
git push origin --tags           # 推送所有标签
git push origin :refs/tags/v1.0  # 删除远程标签

# 补充
# 查看所有本地 Tag
git tag

# 给当前 commit 创建带说明的 Tag
git tag -a v1.0.0 -m "Release v1.0.0"

# 给当前 commit 创建轻量 Tag
git tag v1.0.0

# 给指定历史 commit 创建 Tag
git tag -a v1.0.0 <commit-id> -m "Release v1.0.0"

# 查看 Tag 详细信息
git show v1.0.0

# 推送指定 Tag 到远程
git push origin v1.0.0

# 推送所有本地 Tag 到远程
git push origin --tags

# 拉取远程所有 Tag
git fetch --tags

# 切换到指定 Tag
git switch --detach v1.0.0

# 基于指定 Tag 创建新分支
git switch -c dev-v1.0.0 v1.0.0

# 删除本地 Tag
git tag -d v1.0.0

# 删除远程 Tag
git push origin --delete v1.0.0

# 直接克隆指定 Tag，只下载最少 Git 历史
git clone --branch v1.0.0 --depth 1 <repository-url>
```

> 官方文档：<https://git-scm.com/docs/git-tag>

---

### `git rm`（从仓库删除文件）

```bash
git rm <file>                    # 删除文件并 add 这次删除
git rm --cached <file>           # 不删文件，只从 Git 跟踪中移除
git rm -r --cached .             # 配合新 .gitignore 重新追踪（常用）
```

> 经典场景：项目早期提交了不该追踪的文件（如 `.env`），加了 `.gitignore` 后用 `--cached` 从跟踪移除。

---

## 6. 撤销 `.gitignore` 重新追踪

如果项目早期追踪了很多不该追踪的文件，加了新 `.gitignore` 后需要重新追踪：

```bash
git rm -r --cached .
git add .
git commit -m "retrack files based on .gitignore"
```

**机制**：

- `git rm -r --cached .`：从 Git 跟踪中移除所有文件（**不删实际文件**）
- `git add .`：按新的 `.gitignore` 规则重新 add
- `git commit`：提交这次"重新追踪"的快照

---

## 7. 速记对照表

| 任务 | 命令 |
| --- | --- |
| 看当前状态 | `git status` |
| 看提交历史 | `git log --oneline --graph` |
| 看工作区改动 | `git diff` |
| 看已 add 的改动 | `git diff --staged` |
| 添加所有改动 | `git add -A` |
| 提交 | `git commit -m "msg"` |
| 创建并切分支 | `git switch -c <name>` |
| 切分支 | `git switch <name>` |
| 合并分支 | `git merge <name>` |
| 拉取远程 | `git pull`（或先 `git fetch`） |
| 推送远程 | `git push` |
| 撤销工作区 | `git restore <file>` |
| 撤销暂存 | `git restore --staged <file>` |
| 回退 commit | `git reset --mixed HEAD~1` |
| 撤销已 push 的 commit | `git revert <commit_id>` |
| 临时收起来 | `git stash` |
| 删未跟踪 | `git clean -fd` |
| 打标签 | `git tag v1.0 && git push origin v1.0` |

> 详细回滚决策见 [III_Git回滚决策笔记](03-git-rollback-decision.md)。

> 多分支并行 / 多 agent 隔离：见 [Git Worktree 笔记](04-git-worktree.md)。
