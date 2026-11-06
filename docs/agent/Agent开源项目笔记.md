---
title: "Agent 开源项目笔记"
---

# Agent 开源项目笔记

> 原 旧稿（后半开源项目列表与学习路径部分）的重新整理版本，提炼为项目分级、推荐深挖组合、读代码重点、底层设计模式、学习路径。旧稿目录已清理，当前以本文为准。

## 一、三梯队项目

### 第一梯队（必须精读）

| 项目 | GitHub | 能力覆盖 | 适合学习什么 |
| --- | --- | --- | --- |
| **Auto-GPT** | [repo](https://github.com/Significant-Gravitas/AutoGPT) | ✅记忆 ✅规划 ✅工具 ✅循环执行 | 单 Agent 全流程设计 |
| **BabyAGI** | [repo](https://github.com/yoheinakajima/babyagi) | ✅任务拆解 ✅任务队列 | 任务规划模型 |
| **AgentGPT** | [repo](https://github.com/reworkd/AgentGPT) | ✅目标驱动 ✅任务生成 | UI + Agent Loop |
| **MetaGPT** | [repo](https://github.com/FoundationAgents/MetaGPT) | ✅多Agent ✅SOP ✅复杂规划 | 多角色协作 |

### 第二梯队（进阶理解）

| 项目 | GitHub | 适合学习 |
| --- | --- | --- |
| **SuperAGI** | [repo](https://github.com/TransformerOptimus/SuperAGI) | 工程化 Agent 系统 |
| **CAMEL-AI** | [repo](https://github.com/camel-ai/camel) | Agent 协作机制 |
| **ChatDev** | [repo](https://github.com/OpenBMB/ChatDev) | 多角色开发 |
| **GPT-Engineer** | [repo](https://github.com/AntonOsika/gpt-engineer) | Agent 如何落地产出 |

### 第三梯队（资源合集）

| 项目 | 作用 |
| --- | --- |
| [Awesome AI Agents](https://github.com/e2b-dev/awesome-ai-agents) | 收录大量 Agent 项目 |
| [500+ AI Agent 项目合集](https://github.com/ashishpatel26/500-AI-Agents-Projects) | 各行业 Agent 实例 |

> 这些是"找灵感"的，不是重点学习对象。

---

## 二、推荐深挖的 3 个项目组合

### 1. Auto-GPT（核心骨架）

学什么：

- Agent Loop（最重要）
- Memory（短期 + 长期）
- Tool 调用
- Self-reflection（自我反馈）

核心思想：

```
Goal → 拆任务 → 执行 → 观察 → 写入 memory → 再循环
```

### 2. BabyAGI（任务规划精髓）

学什么：

- Task Queue（任务队列）
- Task Prioritization（任务排序）
- Task Creation（自动生成子任务）

解决的核心问题：**一个目标，如何拆成可执行任务？**

### 3. MetaGPT（复杂系统思维）

学什么：

- 多角色（PM / Architect / Engineer）
- SOP（标准流程）
- 多 Agent 协作

核心思想：**复杂 Agent = 不是一个脑子，而是一个团队。**

---

## 三、读代码重点

### Auto-GPT

- `agent.py` / 循环逻辑
- Memory 设计（vector store）
- Tool Registry（工具注册）
- Prompt 构造

核心逻辑其实就一句：

```
while not done:
    think
    act
    observe
```

### BabyAGI

- Task List（任务列表）
- Task Creation Agent
- Task Execution Agent
- Task Prioritization Agent

核心结构：

```
任务池（queue）
  ↓
取一个任务
  ↓
执行
  ↓
生成新任务
  ↓
重新排序
```

### MetaGPT

- Role 定义（PM / Architect）
- Message 传递
- Workflow（SOP）

本质是：

```
需求 → PM → 架构 → 任务 → 工程师 → 输出
```

---

## 四、四个底层设计模式

要学的不是代码，而是这些项目**共同的结构**。

### 1. Agent Loop（核心）

```
while True:
    思考（LLM）
    决策（下一步）
    调工具
    观察结果
    写入 memory
```

所有 Agent 本质都是这个循环。

### 2. Memory 模型（三层）

- **短期 memory**：当前任务上下文
- **长期 memory**：向量库
- **状态 memory**：任务进度

### 3. Planning 模型（两种主流）

- **任务队列**（BabyAGI 风格）：适合复杂目标
- **一步步规划**（AutoGPT 风格）：适合执行型 Agent

### 4. Tool 使用模式

核心不是"调用"，而是：

```
LLM 决定是否调用工具
  ↓
工具执行
  ↓
结果反馈给 LLM
```

---

## 五、最实用的学习路径（4 步）

### 第一步：理解 Agent 是什么

看 **Auto-GPT**。目标：

- 理解 Agent Loop
- 理解 Memory
- 理解 Tool

### 第二步：理解规划

看 **BabyAGI**。目标：

- 学会"任务拆解"
- 学会"任务队列"

### 第三步：理解复杂系统

看 **MetaGPT**。目标：

- 多 Agent
- SOP
- 复杂流程

### 第四步：自己写一个简化版

写一个 Mini Agent：

```
输入目标
  ↓
自动拆任务
  ↓
调用工具（比如 search / code）
  ↓
有 memory
  ↓
能循环执行
```

---

## 六、关键结论

> 这些优秀 Agent，本质上都在做同一件事：

```
Goal → Plan → Act → Observe → Memory → Loop
```

学习路径上**先看成品架构，再抽象能力**，比直接学框架更高效。