---
title: "Git Worktree 笔记"
sidebar_position: 4
---

# Git Worktree 笔记

> 一个 git 仓库同时跑多份工作目录。适合多分支并行、长跑任务期间继续工作、
> 多 AI agent 隔离实验。补充主线：[Hub/01_Git笔记] · [Hub/02_Git命令速查笔记]

---

## 1. 一句话理解

> `git worktree` 让**同一个仓库**有**多个工作目录**，每个目录可独立 checkout 不同分支。
> 所有 worktree 共享同一份 `.git` 存储（`.git/worktrees/<name>/` 下放各自的元数据）。

和 `git clone` 的区别：clone 是**复制整个 repo**（包括 `.git`）到新目录，独立维护；
worktree 是**复用 `.git` 存储**到新工作区，省空间、实时同步，不用 fetch。

---

## 2. 命令速查

| 命令                                                      | 用途                                                 |
| ------------------------------------------------------- | -------------------------------------------------- |
| `git worktree add <path> [<branch>]`                    | 新增 worktree，checkout 到指定分支（分支必须已存在）                |
| `git worktree add -b <new-branch> <path> <start-point>` | 在新 worktree 里建并 checkout 新分支                       |
| `git worktree add --detach <path> <commit>`             | 创建一个 detached HEAD 的临时 worktree（看老 commit 不污染分支）   |
| `git worktree list`                                     | 列出所有 worktree（包含主仓，标记 `bare` / `detached`）         |
| `git worktree remove <path>`                            | 移除 worktree（工作区要干净；可用 `--force` 强删）                |
| `git worktree move <old> <new>`                         | 移动 worktree 路径                                     |
| `git worktree lock [--reason <text>] <path>`            | 锁定 worktree，防止被 `git worktree remove` / `prune` 误删 |
| `git worktree unlock <path>`                            | 解锁                                                 |
| `git worktree prune`                                    | 清理元数据中指向已不存在路径的 stale 记录                           |
| `git worktree repair <path>`                            | 修复元数据（手动移动 worktree 目录后用）                          |

> **主仓也是一个 worktree**：`git worktree list` 第一行总是仓库根目录本身。
>
> **选项位置灵活**：`-b` / `--detach` 这类选项既可以放在 `path` 之前（man page 惯例），也可以放在 `path` 之后（实际敲命令时的常见习惯）。位置参数 `path` 与 `<start-point>` 的顺序不能颠倒。

---

## 3. 典型使用场景

### 3.1 多分支并行开发

不需要 `git stash` 反复切分支，每个分支一个 worktree：

```bash
git worktree add ../proj-feature-a feature/a
git worktree add ../proj-feature-b feature/b

# 在 ../proj-feature-a 改 a，在 ../proj-feature-b 改 b，互不干扰
```

### 3.2 长跑任务期间继续工作

```bash
# 主仓在跑大 rebase / 长测试 / 长构建，不想打断
git worktree add -b chore/side-task ../proj-side-task main
# 在 ../proj-side-task 继续提交小修小补
```

### 3.3 PR / 远程分支本地审阅

```bash
git fetch origin pull/123/head:pr-123
git worktree add ../proj-pr-123 pr-123
# 在 ../proj-pr-123 看代码、跑测试，不污染主仓工作区
```

### 3.4 多 AI agent 隔离实验（推荐场景）

不同 AI 助手（ClaudeCode / Codex / OpenCode）各自一个 worktree，互不踩：

```bash
git worktree add -b agent/claude-task ../proj-agent-claude main
git worktree add -b agent/codex-task  ../proj-agent-codex  main
```

每个 agent 在自己的 worktree 里 commit / push，主管线（主仓）继续正常开发。

### 3.5 隔离重构 / 实验性变更

```bash
git worktree add -b experiment/new-arch ../proj-refactor main
# 在 ../proj-refactor 改新架构，毁掉不心疼；主仓还在原分支工作
```

---

## 4. 使用约束

- **同一分支不能在多个 worktree 同时 checkout**。git 会拒绝：
  `fatal: 'feature/x' is already checked out at '.../proj-feature-x'`
  解决：另起一个分支，或者先 `git worktree remove` 旧的。
- **每个 worktree 独立 `.git/index`、独立 `HEAD`、独立未保存改动**。
- **`.git/worktrees/<name>/`** 是 worktree 元数据目录，不要手动改。
- **worktree 里的 `git` 操作**（commit / push / branch / log）正常进行；只是不能 checkout 已被别处占用的分支。
- **不能在 detached HEAD worktree 里直接 checkout 分支再 commit**（commit 会挂在 detached HEAD 上），要新建分支：`git switch -c <new-branch>`。

---

## 5. 常见坑

### 5.1 删了目录但忘了 prune

```bash
# 手动 rm -rf ../proj-side-task 后
git worktree list           # 还残留 ../proj-side-task 记录
git worktree prune          # 清理
```

### 5.2 移动 worktree 目录后 git 找不到

```bash
mv ../proj-feature-a ../proj-feature-a-renamed
git worktree list           # 路径对不上
git worktree repair ../proj-feature-a-renamed    # 修复
```

### 5.3 在某个 worktree 里 `git branch -D` 当前分支

```bash
# 当前 worktree 还在 checkout 这个分支，git 会拒绝：
git branch -D feature/x
# error: Cannot delete branch 'feature/x' checked out at '...'
# 解决：先切到别的分支，或 `git worktree remove` 这个 worktree
```

### 5.4 试图在 worktree 里再 `git worktree add` 同一分支

直接报错（同 5.3）。解决：新分支，或换目标路径。

### 5.5 IDE（VSCode 等）打开多个 worktree

每个 worktree 要单独打开成独立窗口，依赖、扩展、language server 都是独立识别。
大型 monorepo 打开多个 worktree 会比较吃内存，注意资源分配。

### 5.6 push 时不在任何分支上

detached HEAD 状态下 `git push` 会失败或推错地方，记得先 `git switch -c <branch>` 给出名字。

---

## 6. 与本知识库其他笔记的关系

- 在 `上下文工程异常问题总结.md` 中，worktree 被列为状态漂移的**诱因之一**——同一份代码在多个 worktree 漂移，
  agent 在 worktree A 改、用户跑 worktree B，看不到变更。
  反过来，worktree **也是状态漂移的缓解手段**——不同任务分到不同 worktree，状态天然隔离。
- 与 `Hub/01_Git笔记`、`Hub/02_Git命令速查笔记` 是补充关系：那两份覆盖基础概念和命令速查，
  本篇专门展开 worktree 一个主题。

---

## 7. 一句话口诀

> **多任务并行别反复切分支，多开 worktree 各干各的；删目录后记得 prune，移动目录后记得 repair。**

---

## 8. 最小复现（不在知识库留 demo，仅供本地验证）

```bash
cd /tmp
rm -rf wt-test && mkdir wt-test && cd wt-test
git init -b main
echo hello > a.txt && git add . && git commit -m init

git worktree add -b feat/x ../wt-test-feat main
cd ../wt-test-feat
echo world > b.txt && git add . && git commit -m "feat: add b"

cd /tmp/wt-test
git worktree list
# /tmp/wt-test        abc1234 [main]
# /tmp/wt-test-feat   def5678 [feat/x]

git worktree remove ../wt-test-feat
git worktree prune
```