---
title: 上下文工程与 Agent 笔记
description: 2026 年工业级 Context Engineering + Agent 系统：Prompt Engineering vs Context Engineering 边界、四大策略（Write/Select/Compress/Isolate）、Manus 六条工程经验、Anthropic Building Effective Agents 五种 Workflow、8 大 Agent 框架对比（LangGraph / CrewAI / AutoGen / Smolagents / Letta / Pydantic AI / Mastra / Agno）、Memory 系统（Mem0 / Letta / Zep）、MCP 生态、20 类上下文工程常见问题精炼。
type: hub
date: 2026-11-06
---

# 上下文工程与 Agent 笔记

> **本文目的**：替换 `上下文工程异常问题总结` 原笔记（原 557 行 20 类问题，内容质量尚可但缺 Prompt Engineering vs Context Engineering 边界、Manus 经验、Agent 框架对比、Memory 系统、MCP，已删除）。覆盖 2026 年工业级 Context Engineering + Agent 全栈。
> 配套笔记：[RAG工业方案笔记](/ai/RAG工业方案笔记)、[Prompt工程笔记](/ai/Prompt工程笔记)、[Rerank笔记](/ai/Rerank笔记)
> 配套 demo：[example/llm-demo/04_rag_evaluation](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/llm-demo/04_rag_evaluation)

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | Prompt Engineering vs Context Engineering | Karpathy 定义 + 4 维度对比 |
| 2 | Context Engineering 四大策略 | Write / Select / Compress / Isolate |
| 3 | Manus 六条工程经验 | KV-cache / Mask / 文件系统 / Recitation / 保留错误 / 反模式化 |
| 4 | Anthropic Building Effective Agents | 5 种 Workflow + Tool = ACI + 透明性 > 智能 |
| 5 | Agent 框架对比 | 8 大框架（LangGraph / CrewAI / AutoGen / Smolagents / Letta / Pydantic AI / Mastra / Agno）|
| 6 | 记忆系统 | Mem0 / Letta / Zep 对比 + 向量 vs 结构化 |
| 7 | 上下文工程常见问题（精炼原 20 类）| Context Rot / Pollution / Missing / Conflict / Overload / Lost-in-the-Middle 等 |
| 8 | MCP 与工具调用 | Model Context Protocol 生态 + 与 Function Calling 差异 |
| 9 | 来源链接 | 全部 GitHub 链接按章节分组 |

---

## 1. Prompt Engineering vs Context Engineering

### 1.1 Karpathy 的定义

> "Context engineering is the delicate art and science of filling the context window with just the right information for the next step." — Andrej Karpathy（2025）

Cognition（Devin 团队）补充："构建 AI agent 工程师的 #1 工作"。

### 1.2 4 维度对比

| 维度 | Prompt Engineering | Context Engineering |
|---|---|---|
| **关注对象** | system / user 指令本身 | 整个 context window：instructions + knowledge + tools + 历史 + 反馈 |
| **时间尺度** | 写一次 | 每次推理都在动态管理 |
| **典型动作** | 改写 prompt、加 few-shot | write / select / compress / isolate 四类策略 |
| **适用对象** | 单次 LLM 调用 | 长链路 Agent（Manus 平均 50 次工具调用）|

### 1.3 演进关系

```
Prompt Engineering（写指令）
       ↓
Context Engineering（管理整个 context window）
       ↓
Agent Engineering（编排多步推理 + 工具调用 + 记忆 + 多 agent 协作）
```

**结论**：Prompt Engineering 是基础；Context Engineering 是中间层；Agent Engineering 是工业级落地的全集。三者层层递进，不是替代关系。

---

## 2. Context Engineering 四大策略（LangChain 总结）

参考：[Context Engineering for Agents](https://www.langchain.com/blog/context-engineering-for-agents)

### 2.1 Write（写）

把信息写进 context window，让模型"看到"。

| 手段 | 作用 | 何时用 |
|---|---|---|
| **Scratchpad**（轮内笔记）| Agent 在每步写 notes，沉淀当前推理 | ReAct / Plan-and-Execute |
| **Memory**（跨会话笔记）| 长期记忆用户偏好 / 项目状态 | ChatGPT / Cursor / Windsurf 都用 |
| **todo.md recitation** | 每步重写 todo，把目标朗诵到 context 末端 | Manus 风格长任务 |
| **文件系统当 context** | 128K 不够用 → 文件系统 = 无限、持久、可操作 | Manus / Claude Code |

### 2.2 Select（选）

从大量候选中选出当前需要的，喂给模型。

| 手段 | 作用 | 数据 |
|---|---|---|
| **Tool-RAG** | 工具太多时，先 RAG 出当前需要的工具 | LangChain 实测：工具选择准确率提升 **3×** |
| **Memory retrieval** | 从长期记忆库 RAG 出相关记忆 | Mem0 / Letta |
| **Context RAG** | 从文档库 RAG 出相关 context | RAG 完整链路 |
| **Episodic / Procedural / Semantic memory** | 三类记忆分层检索 | Letta / Zep |

### 2.3 Compress（压）

当 context 接近上限时，压缩信息以腾出空间。

| 手段 | 作用 | 何时用 |
|---|---|---|
| **Summarization** | 长对话压缩成摘要 | Claude Code 在 95% 容量自动 compact |
| **Trimming** | 直接裁掉不重要的历史 token | 滑动窗口 |
| **LLM-based compression** | 用 LLM 重新组织 context | 关键信息提取 |
| **Token-level pruning** | 按 attention 权重剪枝 | 实验性 |

### 2.4 Isolate（隔）

把上下文隔离到不同 agent / sandbox，避免互相污染。

| 手段 | 作用 | 何时用 |
|---|---|---|
| **Multi-agent** | 主 agent + sub-agent，每个只看自己的 context | Anthropic research 用并行 sub-agent |
| **Sandbox** | Agent 工具调用隔离在 sandbox | HuggingFace CodeAgent 用 e2b |
| **Per-node selection** | LangGraph 每个 node 独立选择 context | 复杂 workflow |
| **Thread state** | 每个 thread 独立 state | LangGraph thread |

### 2.5 四大策略与 LangGraph / Claude Code 的对应

| 策略 | LangGraph 实现 | Claude Code 实现 |
|---|---|---|
| **Write** | thread state + 持久化 | scratchpad + memory |
| **Select** | per-node selection | tool-RAG |
| **Compress** | built-in 摘要 / trimming | 95% 自动 compact |
| **Isolate** | multi-agent / sandbox | sub-agent |

---

## 3. Manus 六条工程经验

参考：[Manus: Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)

### 3.1 KV-cache 设计（最重要的指标）

> **缓存命中率 = 生产 agent 最重要指标**

| 指标 | 数值 |
|---|---|
| Manus 平均输入输出比 | 100:1 |
| Cached input（Claude Sonnet）| $0.30 / MTok |
| Uncached input | $3 / MTok |
| 价格差 | **10×** |

**核心原则**：
- 稳定 prompt prefix → 提高 cache 命中率
- 避免在 prompt 中插入时间戳 / 随机 ID（破坏 cache）
- 把可变部分放在 prompt 末尾

### 3.2 Mask 而不是 Remove

动态增删 tool 会废掉 KV-cache。改用：
- **State machine**：固定 tool 列表，通过状态控制是否可用
- **Logit masking**：在生成阶段 mask 掉非法 token
- **Response prefill**：assistant 消息前缀引导生成方向

### 3.3 文件系统当 Context

- 128K 不够用 → 文件系统 = 无限、持久、可操作的外部记忆
- Agent 可以 read / write / search 文件，突破 context window 限制
- Claude Code / Manus / Devin 都重度依赖文件系统

### 3.4 Recitation 对抗注意力漂移

- 每步重写 `todo.md`，把目标朗诵到 context 末端
- 防止"lost in the middle"——长 context 末尾信息更容易被关注
- 与 Anthropic 的 extended thinking 同源

### 3.5 保留错误

> 删除失败记录 = 抹掉模型需要用来纠错的证据

- 错误日志、stacktrace、failed patches 都要保留
- Agent 需要"知道自己哪里错了"才能调整
- 完整 DECISIONS.md / FAILED_ATTEMPTS.md / KNOWN_ISSUES.md

### 3.6 不要 Few-shot 出模式化

- 注入结构化变化（不同序列化、不同措辞、轻微噪声）打破模仿
- 否则模型会机械模仿示例，失去泛化能力
- 与 Anthropic 原则"示例胜于描述"形成互补

---

## 4. Anthropic Building Effective Agents

参考：[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

### 4.1 Workflow > Agent

> 能用 workflow 解决的，就不要上 Agent。

5 种 Workflow（按复杂度递增）：

| Workflow | 模式 | 何时用 |
|---|---|---|
| **Prompt chaining** | 串行：步骤 1 → 步骤 2 → ... → 步骤 N | 流水线任务，每步确定性强 |
| **Routing** | 分类后分流到不同子流程 | 多类型 query 分类处理 |
| **Parallelization** | 多任务并行 → 聚合结果 | 多个独立子问题 |
| **Orchestrator-workers** | 主 agent 拆解 → 多 worker 并行 → 聚合 | 复杂任务并行处理 |
| **Evaluator-optimizer** | 生成 → 评分 → 反馈 → 重生成 | 答案质量优先场景 |

### 4.2 Tool = ACI（Agent-Computer Interface）

> Tool 描述要像产品 docstring，不是 API 签名。

| 维度 | 差的 tool 描述 | 好的 tool 描述 |
|---|---|---|
| **签名** | `get_user(id)` | `get_user(id: str) → User` |
| **示例** | 无 | `get_user("u_123") → User(name="李雷", age=30)` |
| **边界** | 无 | "id 必须是 string，若用户不存在抛 NotFoundError" |
| **错误处理** | 无 | "返回的 User 可能为 None，调用方需检查" |
| **Poka-yoke（防呆）**| 无 | "id 不能为空字符串，否则抛 ValueError" |

### 4.3 透明性 > 智能

- 让 agent 把计划显式写出来，用户能看见
- 不要让 agent 在暗处决策
- Claude Code 的 todo list / Manus 的 todo.md 都是这个原则的体现

### 4.4 Tool 投资回报率

> 投资 tool 描述和工具测试的回报率，比调 prompt 高。

- 调 prompt 提升 5~10%，调 tool 描述提升 20~50%
- 每个 tool 都要有单元测试 + 集成测试
- Anthropic 建议把 tool 视为产品来打磨

---

## 5. Agent 框架对比

### 5.1 8 大框架

| 框架 | 仓库 | Stars | 最新版本 | 定位 | 何时用 |
|---|---|---|---|---|---|
| **LangGraph** | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | — | 持续发布 | LangChain 主力 stateful graph；thread state + checkpoint | 复杂 Agent + 多步推理 |
| **CrewAI** | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | — | 持续发布 | Role-playing 多 agent 协作（Captain / Engineer / Researcher）| 多 agent 角色扮演场景 |
| **AutoGen** | [microsoft/autogen](https://github.com/microsoft/autogen) | — | v0.4+（重写后）| Microsoft 出品；群聊式 multi-agent | 研究 / 多 agent 群聊 |
| **Smolagents** | [huggingface/smolagents](https://github.com/huggingface/smolagents) | — | 持续发布 | HuggingFace 出品；极简 + code agent + sandbox (e2b) | 轻量 code agent |
| **Letta**（原 MemGPT）| [letta-ai/letta](https://github.com/letta-ai/letta) | — | 持续发布 | 带长期记忆的 agent；core memory + archival memory | 需要持久记忆的 agent |
| **Pydantic AI** | [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | — | 持续发布 | Pydantic 官方；FastAPI 风格；强类型 | Python 后端 + 强类型 |
| **Mastra** | [mastra-ai/mastra](https://github.com/mastra-ai/mastra) | — | 持续发布 | TypeScript Agent 框架；workflow + RAG + MCP | Node.js / TS 技术栈 |
| **Agno**（原 Fixpoint）| [agno-agi/agno](https://github.com/agno-agi/agno) | — | 持续发布 | 高性能多模态 agent；速度比 LangGraph 快 10× | 高性能 + 多模态场景 |

### 5.2 各框架核心差异

| 框架 | 核心抽象 | 多 agent | 记忆系统 | Tool 生态 | 学习曲线 |
|---|---|---|---|---|---|
| **LangGraph** | StateGraph + Node + Edge | ✅ subgraph | 外部（MemoryStore / Zep）| LangChain 全套 | 中（要理解 graph 概念）|
| **CrewAI** | Crew + Agent + Task | ✅ 内建（role-based）| 外部 | 自定义 + LangChain | 低（role 直观）|
| **AutoGen** | UserProxyAgent + AssistantAgent | ✅ 内建（群聊）| 外部 | 自定义 | 中（要理解群聊协议）|
| **Smolagents** | CodeAgent + Tool | ⚠️ 简单 | 无（自带 file system）| 自定义 | 低（极简）|
| **Letta** | Agent + Memory Blocks | ✅ 内建 | ✅ 内建（core + archival）| 自定义 | 中（记忆模型特殊）|
| **Pydantic AI** | Agent + Deps + Result | ⚠️ 简单 | 外部 | 自定义 + MCP | 低（Pydantic 风格）|
| **Mastra** | Agent + Workflow + Tool | ✅ 内建 | 外部 | MCP + 自定义 | 低（TS 友好）|
| **Agno** | Agent + Team + Workflow | ✅ 内建（Team）| 外部 | MCP + 自定义 | 中 |

### 5.3 选型决策

| 场景 | 推荐 |
|---|---|
| **Python + LangChain 生态** | LangGraph（首选）|
| **多 agent 角色扮演** | CrewAI（直观）|
| **群聊式 multi-agent** | AutoGen（学术 / 研究）|
| **轻量 code agent** | Smolagents（极简）|
| **需要长期记忆** | Letta（自带 memory）|
| **强类型 + FastAPI 后端** | Pydantic AI |
| **TypeScript / Node.js** | Mastra |
| **高性能 + 多模态** | Agno |

---

## 6. 记忆系统

### 6.1 三大记忆框架对比

| 框架 | 仓库 | 核心机制 | 何时用 |
|---|---|---|---|
| **Mem0** | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 向量 + 结构化双层记忆；自动 extract / update / delete | 通用 agent 记忆；生产稳定 |
| **Letta**（原 MemGPT）| [letta-ai/letta](https://github.com/letta-ai/letta) | Core memory（in-context）+ Archival memory（向量）；core memory 会自动压缩 + 滚动 | 长对话 + 角色一致性 |
| **Zep** | [getzep/zep](https://github.com/getzep/zep) | 生产级长期记忆服务；Graphiti 时序知识图谱 + 语义搜索 | 企业级 + 多用户记忆 |

### 6.2 向量记忆 vs 结构化记忆

| 维度 | 向量记忆 | 结构化记忆 |
|---|---|---|
| **存储** | Embedding + metadata | 表 / KV / 知识图谱 |
| **检索** | 相似度 | 精确查询 / 关系查询 |
| **可解释性** | 低（黑盒）| 高（可读）|
| **更新成本** | 中（重建索引）| 低（直接改）|
| **适用场景** | 模糊匹配 / 语义搜索 | 精确状态 / 关系推理 |

**2026 主流**：**向量 + 结构化双层**（Mem0 模式）。语义记忆走向量，状态 / 关系走结构化。

### 6.3 Memory 设计模式

- **Tier 1：Core / Working Memory**：放 context window 内；用户偏好、当前任务状态
- **Tier 2：Episodic Memory**：历史事件；按时间序列存储
- **Tier 3：Semantic Memory**：事实知识；走向量 RAG
- **Tier 4：Procedural Memory**：技能 / 工具调用模板

---

## 7. 上下文工程常见问题（精炼原 20 类）

### 7.1 核心问题清单（按影响排序）

| # | 问题 | 核心含义 | 解决方案 |
|---|---|---|---|
| 1 | **Context Rot** 上下文腐烂 | 上下文长期积累后变旧、变乱、变矛盾 | 定期 compact；维护 CURRENT_STATE.md |
| 2 | **Context Pollution** 上下文污染 | 错误、无关、过期信息进入上下文 | 输入过滤 + 来源标注 |
| 3 | **Context Missing** 上下文缺失 | 模型没拿到完成任务所需信息 | 提供 SPEC.md + DATABASE_SCHEMA.md 等结构化文档 |
| 4 | **Context Conflict** 上下文冲突 | 多个信息源互相矛盾 | 明确优先级：用户最新指令 > CURRENT_STATE.md > SPEC.md > README > 历史对话 |
| 5 | **Context Overload** 上下文过载 | 信息太多，模型有效利用能力下降 | 任务级裁剪 + 摘要 + 分层 |
| 6 | **Lost in the Middle** | 长上下文中间信息被忽略 | 关键信息放开头 / 末尾；用 XML tags 标记 |
| 7 | **State Drift** 状态漂移 | 模型理解和真实项目状态不一致 | Agent 重新扫描文件 + git worktree 隔离 |
| 8 | **Requirement Drift** 需求漂移 | 实现逐渐偏离最初目标 | 维护 requirements.md / out_of_scope.md / change_log.md |
| 9 | **RAG Pollution** 检索污染 | 检索到错误或过期资料 | 区分 docs/archived 与 docs/current + 过滤 |
| 10 | **Summary Distortion** 摘要失真 | 长上下文压缩后丢失关键约束 | 人工校验摘要 + 保留原始 + 元数据标记 |
| 11 | **Tool-State Desync** 工具状态不同步 | Agent 看到的文件/分支/环境和真实执行环境不一致 | patch 验证 + git worktree + 状态文件 |
| 12 | **Memory Pollution** 记忆污染 | 长期记忆保存了不再准确的信息 | 记忆加 TTL + 定期审计 + 来源标注 |
| 13 | **Prompt Bloat** Prompt 膨胀 | 不断往 prompt 加规则，最后臃肿 | 定期清理 + 分场景 prompt + 动态加载 |
| 14 | **Format Collapse** 格式崩坏 | 上下文复杂后开始破坏格式 | 结构化输出（Instructor）+ schema 校验 |
| 15 | **Task Boundary Leakage** 任务边界失控 | 模型把当前任务以外的事情也一起做 | 明确 Allowed Changes / Forbidden Changes |
| 16 | **Source of Truth Missing** 事实源不明确 | 没有告诉模型哪个文件是事实源 | 明确优先级：CURRENT_STATE.md > SPEC.md > ... |
| 17 | **Failed Attempt Residue** 历史失败残留 | 之前失败的实现路径留在上下文里，模型重复尝试 | 维护 DECISIONS.md / FAILED_ATTEMPTS.md |
| 18 | **Multi-Agent Context Inconsistency** 多 Agent 上下文不一致 | 多 agent 协作时各自拿到的上下文不一致 | 共享状态文件 + 主 agent 同步 |
| 19 | **Instruction Hierarchy Confusion** 指令层级混乱 | 模型不知道哪些指令优先级最高 | 明确规则：安全 > 用户最新 > spec > 任务 > 历史 |
| 20 | **Implicit Assumption Accumulation** 隐式假设累积 | 模型在没有确认的情况下做了假设，后续沿用 | 假设必须落到 spec 文件，不允许隐式 |

### 7.2 核心原则

> **不要依赖对话历史维持项目状态，要把项目状态沉淀到结构化文档里，并明确事实源、优先级、当前任务和变更记录。**

---

## 8. MCP 与工具调用

### 8.1 MCP 概述

[Model Context Protocol（MCP）](https://modelcontextprotocol.io/) 是 Anthropic 2024 年开源的开放标准，让 LLM 应用与外部工具 / 数据源标准化连接。

| 项目信息 | 数值 |
|---|---|
| 发布时间 | 2024-11 |
| 当前版本 | 持续演进（2026 已是事实标准）|
| 官方 server 数 | 100+ |
| 生态 server 数 | 1000+（社区贡献）|
| 支持客户端 | Claude Desktop / Claude Code / Cursor / Windsurf / Cline / Continue / ... |

### 8.2 MCP vs OpenAI Function Calling vs Anthropic Tool Use

| 维度 | OpenAI Function Calling | Anthropic Tool Use | MCP |
|---|---|---|---|
| **定位** | 模型能力 | 模型能力 | **协议标准** |
| **范围** | 单次调用 | 单次调用 | **跨工具、跨应用、跨模型** |
| **生态** | OpenAI 独占 | Anthropic 独占 | **开放，任何人都能实现 server/client** |
| **Tool 定义** | JSON Schema | JSON Schema | JSON Schema + MCP 协议 |
| **状态管理** | 无 | 无 | ✅ session / progress / cancellation |
| **多模态** | ⚠️ 部分 | ⚠️ 部分 | ✅ 完整支持 |

**结论**：MCP 是工业级 Tool Use 的标准协议，2026 年已成为事实标准。

### 8.3 MCP 生态（2026）

| 类别 | 代表 server |
|---|---|
| **文件 / 代码** | Filesystem / Git / GitHub / GitLab |
| **数据库** | PostgreSQL / SQLite / MySQL / MongoDB |
| **搜索** | Brave Search / Tavily / Google |
| **协作** | Slack / Notion / Linear / Jira / Confluence |
| **云** | AWS / GCP / Azure / Cloudflare |
| **浏览器** | Playwright / Puppeteer |
| **AI / ML** | HuggingFace / Replicate |
| **生产工具** | Sentry / Datadog / Grafana |

### 8.4 MCP 适用场景

| 场景 | 是否用 MCP |
|---|---|
| **Claude Desktop / Claude Code 集成第三方工具** | ✅ 强烈推荐 |
| **多模型统一接入一套工具** | ✅ 强烈推荐 |
| **企业内部工具标准化** | ✅ 强烈推荐 |
| **简单一次性工具调用** | ❌ 直接用 Function Calling |
| **OpenAI-only 场景** | ❌ 用 Function Calling |

---

## 9. 来源链接（按章节分组）

### 9.1 Context Engineering 概念
- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [LangChain: Context Engineering for Agents](https://www.langchain.com/blog/context-engineering-for-agents)
- [Manus: Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)

### 9.2 Agent 框架
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [AutoGen (Microsoft)](https://github.com/microsoft/autogen)
- [Smolagents (HuggingFace)](https://github.com/huggingface/smolagents)
- [Letta（原 MemGPT）](https://github.com/letta-ai/letta)
- [Pydantic AI](https://github.com/pydantic/pydantic-ai)
- [Mastra](https://github.com/mastra-ai/mastra)
- [Agno（原 Fixpoint）](https://github.com/agno-agi/agno)

### 9.3 记忆系统
- [Mem0](https://github.com/mem0ai/mem0)
- [Letta](https://github.com/letta-ai/letta)
- [Zep](https://github.com/getzep/zep)

### 9.4 MCP
- [Model Context Protocol 官网](https://modelcontextprotocol.io/)
- [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### 9.5 历史归档
- 原 `上下文工程异常问题总结.md`（项目根目录）已删除，核心 20 类问题提炼到本笔记 §7

标签：#agent #mcp #prompt-engineering
