---
title: "Git 回滚决策笔记"
sidebar_position: 3
---

# Git 回滚决策笔记

> 旧稿第四节 + 附录 1/2/3 的深度整理版本。聚焦"回滚"这一最容易混乱的主题：先讲清回滚对象（哪一层），再讲清每个回滚命令的机制，最后给出场景决策。
> 关联笔记：[I_Git笔记](./I_Git笔记.md)、[II_Git命令速查笔记](./II_Git命令速查笔记.md)
> 旧稿目录已清理，当前以本文为准。

---

## 1. Git 三层模型与回滚对象

回滚命令看起来多，本质是因为它们**回滚的对象不一样**。理解分层是看懂所有回滚命令的前提。

| 层级 | 名称 | 含义 |
| --- | --- | --- |
| 第一层 | **工作区**（Working Tree） | 你当前正在编辑的文件内容 |
| 第二层 | **暂存区**（Index / Staging Area） | 已经 `git add` 准备提交的内容 |
| 第三层 | **提交历史**（Commit History） | 已经 `git commit` 形成的历史快照 |

> **核心问题：在你回滚前，先想清楚"我到底想撤销哪一层？"**

回滚命令速记（按对象）：

- 想撤销**文件内容** → `git restore`
- 想撤销**提交指针 + 当前状态** → `git reset`
- 想撤销**某次提交带来的内容**（不改历史）→ `git revert`
- 想撤销**现场感**（临时搬走改动）→ `git stash`
- 想删除**未跟踪文件** → `git clean`
- 想撤销**工作区某个文件到旧版本**（旧写法）→ `git checkout -- <file>`

---

## 2. 六大回滚命令详解

### 2.1 `git restore`（撤销文件改动，推荐）

Git 2.23+ 引入，专门负责文件恢复（把 `checkout` 的一部分职责拆出来）。语义清晰，是现代推荐写法。

#### 2.1.1 撤销工作区修改（最常用）

```bash
git restore <file>          # 撤销指定文件
git restore .               # 撤销所有文件
```

**机制**：把工作区文件恢复到暂存区的版本。前提：文件已 add 过；如果没 add，会恢复到 HEAD。

**本质**：覆盖工作区文件内容，不动提交历史。

#### 2.1.2 撤销暂存区（保留工作区）

```bash
git restore --staged <file>
```

**机制**：把文件从"已暂存"状态撤下来，工作区修改保留。

**示例**：

```bash
git add a.py
git restore --staged a.py   # a.py 不再是 staged，但工作区里改的内容还在
```

**本质**：只改暂存区，不改工作区，不改历史。

#### 2.1.3 同时撤销工作区和暂存区

```bash
git restore --staged <file>
git restore <file>
```

或分两步。先撤暂存、再撤工作区。

> 官方文档：<https://git-scm.com/docs/git-restore>

---

### 2.2 `git reset`（移动 HEAD，必要时同步状态）

`git reset` 是一组命令，由 3 个模式控制同步程度。是 Git 中"最容易混乱但也最强"的命令。

#### 2.2.1 核心机制

`git reset` 做两件事：

1. **移动当前分支指针 / HEAD**（如 `git reset HEAD~1` 把 HEAD 移回上一个提交）
2. **根据模式决定是否同步暂存区 / 工作区**

#### 2.2.2 三种模式对比

| 模式 | 提交历史 | 暂存区 | 工作区 | 改历史 | 安全性 |
| --- | --- | --- | --- | --- | --- |
| `--soft`   | 回退 | ✅ 保留 | ✅ 保留 | 是 | 中 |
| `--mixed`  | 回退 | ❌ 清空 | ✅ 保留 | 是 | 中（默认） |
| `--hard`   | 回退 | ❌ 清空 | ❌ 清空 | 是 | 低 |

#### 2.2.3 `git reset --soft HEAD~1`

```bash
git reset --soft HEAD~1
```

**效果**：

- 提交没了
- 改动还在
- 仍然处于 staged 状态

**本质**：最温柔的回退，只动 HEAD。

**场景**：只是想修改 commit message，或者"重新提交一次但内容不变"。

```bash
git commit -m "写错了"
git reset --soft HEAD~1
git commit -m "正确描述"   # 不用重新 add
```

#### 2.2.4 `git reset --mixed HEAD~1`（默认）

```bash
git reset HEAD~1            # 等价于 git reset --mixed HEAD~1
```

**效果**：

- 提交没了
- staged 取消了
- 工作区改动还在

**本质**：默认回退。后悔提交 + 后悔 add，但代码还想保留继续改。

**场景**：刚 commit，但想重新组织代码 / 重新 `add` 一部分文件再提交。

> **口诀**：
> - `mixed` = 后悔提交 + 重新选择提交内容（最常用）
> - `soft`  = 后悔提交 + 保持原样直接再提交

**Codex 场景推荐**：在 AI 改完代码后，用 `mixed` 回退，重新 `add` 确认无问题的文件再提交。

#### 2.2.5 `git reset --hard HEAD~1`（⚠️ 危险）

```bash
git reset --hard HEAD~1
```

**效果**：

- 提交没了
- staged 没了
- 工作区修改也没了

**本质**：最彻底的回退，全部回到旧提交状态。**未提交的改动会丢失，无法恢复**。

> ⚠️ 危险警告：`git reset --hard` 会删除所有未提交改动，且**不可恢复**。生产环境慎用。

#### 2.2.6 `mixed` vs `soft` 决策

**问自己一句：**

> "我要不要重新挑文件 add？"

- **要** → `mixed`（默认）
- **不要** → `soft`

---

### 2.3 `git reset --keep <commit>`（安全回退）

`--keep` 是相对少用的模式，但提供了"既要回退版本，又不允许伤害当前改动"的能力。

#### 2.3.1 核心机制

`--keep` 做三件事：

1. 移动 HEAD 到目标 commit（和 reset 一样）
2. 尝试更新工作区
3. **如果发现本地改动会被覆盖 → 直接报错，不执行**

#### 2.3.2 与三种模式对比

| 模式 | 工作区改动 | 暂存区 | 特点 |
| --- | --- | --- | --- |
| `soft`     | 保留 | 保留 | 只动 HEAD |
| `mixed`    | 保留 | 清空 | 默认 |
| `hard`     | ❌ 删除 | ❌ 删除 | 强制回退 |
| **`keep`** | ✅ 保留（但不能冲突） | 根据情况 | 安全回退 |

#### 2.3.3 行为示例

当前状态：`A → B → C (HEAD)`，你在 C 上修改了 `a.py` 但还没 commit。

```bash
git reset --keep B
```

- **情况 1：B 和 C 对 `a.py` 没冲突** → 成功，HEAD 回到 B，本地修改还在
- **情况 2：B 和 C 对 `a.py` 有冲突** → ❌ 报错 `error: Your local changes would be overwritten`

#### 2.3.4 适用场景

- 写了一些代码，想回到旧版本看看，但**不想丢当前改动**
- Codex 改了一堆 + 你手动修了一部分，想回退历史但保留自己改的
- 不确定会不会冲突，想"安全试一下"

> **记忆口诀**：
> ```text
> soft   → 最温柔（只动 HEAD）
> mixed  → 默认（动 HEAD + index）
> hard   → 最狠（全删）
> keep   → 最谨慎（不安全就不动）
> ```

> 官方文档：<https://git-scm.com/docs/git-reset>

---

### 2.4 `git revert`（生成反向提交）

和 `reset` 完全不同：**不改历史**，而是新建一个提交，内容是把指定提交的改动反向抵消。

#### 2.4.1 基本用法

```bash
git revert <commit_id>
```

#### 2.4.2 机制图解

```text
原历史：A → B → C
执行：git revert C
新历史：A → B → C → D
其中 D 的内容是把 C 做的改动反着做一遍
```

#### 2.4.3 为什么安全

- 原历史保留
- 新增一个"撤销提交"
- **不会让别人本地历史乱掉**

#### 2.4.4 适合场景

- 已经 push 到远程了
- 团队协作
- 不想改写 Git 历史

> **一句话**：想撤销一次提交但**不改历史** → `revert`。

> 官方文档：<https://git-scm.com/docs/git-revert>

---

### 2.5 `git stash`（临时存储改动）

不是严格意义的"回滚提交"，但常被当成"回退现场"的方式。

#### 2.5.1 核心用法

```bash
git stash                   # 把当前工作区和暂存区改动打包
git stash list              # 查看 stash 列表
git stash pop               # 恢复最近一次 stash，并删除记录
git stash apply             # 恢复但不删除
```

#### 2.5.2 机制

- 把未提交改动（工作区 + 暂存区）打包到栈里
- 当前目录恢复干净
- 恢复时再应用回来

**本质**：不是删改动，是**临时搬走改动**。

#### 2.5.3 常用参数

```bash
git stash push -m "msg"     # 带说明的 stash
git stash -u                # 包含未跟踪文件
```

#### 2.5.4 适合场景

- 正在改代码，突然要切分支修紧急 bug
- 改到一半不想 commit，又想保存当前进度
- 想把当前改动收起来，切去干别的

> 官方文档：<https://git-scm.com/docs/git-stash>

---

### 2.6 `git clean`（删除未跟踪文件）

清理 **untracked files**（Git 没跟踪的文件），不是回滚提交历史。

#### 2.6.1 核心用法

```bash
git clean -fd
```

- `-f`：强制执行（默认是 dry-run）
- `-d`：删除目录

#### 2.6.2 机制

删除**未跟踪**的文件和目录：

- 临时文件
- 测试目录
- 生成文件（构建产物等）

> 注意：`git reset --hard` 删不掉这些文件，因为它们不在 Git 跟踪范围里。要靠 `git clean`。

#### 2.6.3 ⚠️ 危险警告

`git clean -fd` 会**直接删除未跟踪文件（包括你新建的代码）**。建议先用 `git clean -fdn` 干跑一遍确认要删哪些。

```bash
git clean -fdn              # -n: dry-run，只列出要删的，不真删
git clean -fd               # 确认后再真删
```

> 官方文档：<https://git-scm.com/docs/git-clean>

---

### 2.7 `git checkout`（旧式回滚，仅供理解）

以前很多撤销操作都用 `git checkout -- <file>`，但 `checkout` 还负责切分支、切提交，语义混杂。Git 2.23+ 才拆出 `switch`（切分支）和 `restore`（恢复文件）。

```bash
git checkout -- <file>      # 旧写法：恢复文件
git checkout <branch>       # 切分支
```

#### 推荐替代

- **文件恢复** → `git restore`
- **分支切换** → `git switch`

> 现在学习时建议直接用新写法，不用学 `checkout` 的复杂语义。

---

## 3. 核心对比表（一张记所有回滚命令）

| 命令 | 回滚对象 | 改历史 | 安全性 |
| --- | --- | ---: | ---: |
| `git restore`              | 工作区 / 暂存区 | 否 | 高 |
| `git reset --soft`         | 提交指针 | 是 | 中 |
| `git reset --mixed`        | 提交指针 + 暂存区 | 是 | 中（默认） |
| `git reset --hard`         | 提交指针 + 暂存区 + 工作区 | 是 | 低 |
| `git reset --keep`         | 提交指针（会校验工作区安全） | 是 | 中高 |
| `git revert`               | 某次提交的效果（生成反向提交） | 否（新增历史） | 高 |
| `git stash`                | 未提交改动（临时搬走） | 否 | 高 |
| `git clean -fd`            | 未跟踪文件 | 否 | 低 |

---

## 4. 决策场景 8 例

| 场景 | 推荐命令 | 说明 |
| --- | --- | --- |
| **1. 文件改坏了，但还没 add** | `git restore <file>` | 直接撤销工作区改动 |
| **2. 已经 add，但还没 commit** | `git restore --staged <file>`<br>再 `git restore <file>` | 先撤暂存，再撤工作区 |
| **3. 刚 commit，想撤销但保留代码** | `git reset --soft HEAD~1` | 改动还在 staged |
| **4. 刚 commit，想撤销并取消暂存，但保留代码** | `git reset --mixed HEAD~1` | 改动回到工作区，可重新 add |
| **5. 刚 commit，连代码都不想要了** | `git reset --hard HEAD~1` | ⚠️ 危险，慎用 |
| **6. 已经 push 到远程，想安全撤销一次提交** | `git revert <commit_id>` | 不改历史，团队协作友好 |
| **7. 想把当前改动收起来，切去干别的** | `git stash` → 切分支干活 → `git stash pop` | 临时保存 |
| **8. 项目里多了很多没跟踪的垃圾文件** | `git clean -fdn` 干跑 → `git clean -fd` 真删 | 清 untracked |

---

## 5. `soft` vs `mixed` 决策详解

这两个模式 99% 场景只需要二选一。

| 模式 | commit 回退 | 暂存区 | 工作区 |
| --- | --- | --- | --- |
| `soft`  | ✅ | ✅ 保留 | ✅ 保留 |
| `mixed` | ✅ | ❌ 清空 | ✅ 保留 |

**唯一差别：暂存区要不要清空。**

### 5.1 用 `mixed`（默认，大多数情况）

```bash
git reset HEAD~1
```

适合：

- 刚 commit，但想重新整理代码
- 想重新 `add` 一部分文件再提交
- 想把"已暂存"状态全部打散

**场景例子**：

```bash
git add .
git commit -m "乱提交"
# 后悔了，想拆分提交
git reset HEAD~1             # 撤销 commit + 清空 staged
# 重新挑选文件 add
git add file1.py file2.py
git commit -m "拆分后提交"
```

### 5.2 用 `soft`（少数场景）

```bash
git reset --soft HEAD~1
```

适合：

- 只是想修改 commit message
- "重新提交一次，但内容不变"

**场景例子**：

```bash
git commit -m "写错了"
# 想改成更准确的描述
git reset --soft HEAD~1
git commit -m "正确描述"      # 不用重新 add，改动还在 staged
```

### 5.3 决策口诀

> 问自己一句：
> > "我要不要重新挑文件 add？"
>
> - 要 → **`mixed`**
> - 不要 → **`soft`**

---

## 6. 关键规则速记

### 6.1 三句口诀

```text
不想改历史 → restore / revert / stash
想动指针   → reset
删垃圾     → clean
```

### 6.2 安全原则

- **本地未推送**的 commit 可以放心 `reset`
- **已 push 到远程**的 commit 优先用 `revert`，不要 `reset`（否则会改写历史，影响队友）
- **危险命令执行前先想清楚**：`reset --hard` / `clean -fd` 都会丢失数据，且 `clean` 默认就是直接删

### 6.3 决策树

```text
想撤销 → 在哪一层？
  ├── 文件内容（工作区/暂存区）→ restore
  ├── 提交历史（未 push）      → reset
  ├── 提交历史（已 push）      → revert
  ├── 临时收起来               → stash
  └── 删未跟踪文件             → clean
```

### 6.4 Codex / AI 改码场景

推荐习惯：

1. **改动前做快照**：`git add . && git commit -m "checkpoint"`
2. **改完看 diff**：`git diff` 或 `git diff --stat`
3. **改崩了先回退**：`git restore .` 或 `git checkout -- .`（不丢 staged）
4. **commit 拆错想重组**：`git reset --mixed HEAD~1`，重新挑选 add
5. **想保留 Codex 改动 + 自己的修改**：`git reset --keep <old_commit>`（安全试一下）
