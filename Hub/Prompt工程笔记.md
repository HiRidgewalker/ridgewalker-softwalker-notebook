---
title: Prompt 工程笔记
description: 2026 年工业级 Prompt 工程：Anthropic 官方 7 大原则、DSPy 编译器范式（35.7k stars）、结构化输出四件套（Instructor / Outlines / TypeChat / Prompty）、Prompt 优化工具、模板管理三件套（LangSmith / Helicone / PromptLayer）、注入防护（NeMo Guardrails）、Few-shot/CoT/ReAct 现状、完整工业流程。
type: hub
---

# Prompt 工程笔记

> **本文目的**：替换 `Prompt` 原笔记（原 `文档/Prompt.md` 仅 13 行，严重过简，已删除）。覆盖 2026 年工业级 Prompt 工程：Anthropic 官方原则、DSPy 编译器范式、结构化输出、优化工具、模板管理、注入防护、技术现状、工业流程。
> 配套笔记：[[Hub/RAG工业方案笔记]]、[[Hub/Rerank笔记]]、[[Hub/上下文工程与Agent笔记]]
> 配套 demo：[workspace/llm-demo/04_rag_evaluation](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/llm-demo/04_rag_evaluation)

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | Anthropic 官方原则（2026）| 7 大原则 + XML tags + Tool = ACI |
| 2 | DSPy 编译器范式 | 不写 string prompt，写 signature + module，编译器自动优化 |
| 3 | 结构化输出四件套 | Instructor / Outlines / TypeChat / Prompty 对比 |
| 4 | Prompt 优化工具 | 开源 / 商业 / 控制台三类工具 |
| 5 | Prompt 模板管理 | LangSmith / Helicone / PromptLayer + A/B + 注入防护 |
| 6 | Few-shot / CoT / ReAct 现状 | 2026 年哪些技术仍主流、哪些退潮 |
| 7 | 完整工业流程 | 设计 → 测试 → 部署 → 监控 → 回归 → 防护 |
| 8 | 来源链接 | 全部 GitHub 链接按章节分组 |

---

## 1. Anthropic 官方 Prompt 工程原则（2026）

主参考：
- [Prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Prompting best practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

### 1.1 7 大核心原则（覆盖 Claude Sonnet 5 / Opus 4.8 / Fable 5 / Mythos 5）

| # | 原则 | 解释 | 错误示范 | 正确示范 |
|---|---|---|---|---|
| 1 | **明确胜于含蓄** | 指令要直接、具体、可验证 | "写一段关于猫的文章" | "写 300 字关于家猫的科学介绍，分 3 段，每段开头用 emoji 标记主题" |
| 2 | **示例胜于描述** | few-shot 是最稳的指令对齐方式 | "请按 JSON 格式输出" | 附 1~3 个完整 JSON 示例 |
| 3 | **XML tags > Markdown** | `<instructions>` / `<example>` / `<context>` 比 `## ` 标题更稳 | `## 上下文\nxxx` | `<context>\nxxx\n</context>` |
| 4 | **System = 角色 + 行为守则** | persona、tone、constraints、output format 全塞 system；user 只放任务 | system 写任务描述 | system 写"你是 X 助手，遵守 Y 规则，输出 Z 格式"；user 写"任务：..." |
| 5 | **CoT 不是"让它解释"，而是"让它先思考"** | 用 `<thinking>` 标签显式让模型先推理再输出，或者开 extended thinking | "请一步步思考" | `<thinking>\n先列出关键假设\n</thinking>\n<answer>\n最终答案\n</answer>` |
| 6 | **Tool use 设计为 ACI**（Agent-Computer Interface）| tool 描述要像 docstring：含示例、边界、poka-yoke（防呆）| `tool: get_user(id)` | `tool: get_user(id: str) → User\n返回用户信息。id 必须是 string；若用户不存在抛 NotFoundError。示例：get_user("u_123")` |
| 7 | **Prefill（响应前缀）** | assistant 消息的起手式作为额外控制信号 | （空） | prefill `{\n` 强制 JSON 输出；prefill `Sure, let me ...` 强制礼貌语调 |

### 1.2 Claude Code 等产品里的最佳实践（来自 Building Effective Agents）

- **Workflow > Agent**：能用 5 种 workflow（prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer）解决的，不要上 Agent
- **透明性 > 智能**：让 agent 把计划显式写出来，用户能看见
- **Tool 设计 = 产品**：投资 tool 描述和工具测试的回报率，比调 prompt 高
- **Claude Code 的 context 管理**：95% 容量自动 compact；todo 列表持续维护（与 Manus 的 recitation 同源）

---

## 2. DSPy（编译器范式）

### 2.1 定位与核心思想

[DSPy](https://github.com/stanfordnlp/dspy) 是 Stanford NLP 2024 年开源的程序化 LLM pipeline 框架，2026 年已是事实上的 prompt 编译器标准。

| 项目信息 | 数值 | 来源 |
|---|---|---|
| 最新版本 | 3.2.1 | [GitHub Releases](https://github.com/stanfordnlp/dspy/releases) |
| 发布时间 | 2026-05-05 | 同上 |
| Stars | 35.7k | GitHub 主页 |
| 维护者 | Stanford NLP + Omar Khattab 等 | 仓库 |
| 许可证 | Apache-2.0 | 仓库 LICENSE |
| Python | ≥ 3.10 | pyproject.toml |

**核心思想**：不写 string prompt，写 **signature**（输入输出 schema）+ **module**（计算单元）+ **optimizer**（编译器自动找最优 prompt / few-shot / 微调）。

### 2.2 三件套

| 组件 | 作用 | 示例 |
|---|---|---|
| **Signature** | 输入输出 schema | `class QA(dspy.Signature): question: str -> answer: str` |
| **Module** | 计算单元，类似 PyTorch layer | `class CoT(dspy.Module): def __init__(self): self.gen = dspy.ChainOfThought(QA)` |
| **Optimizer** | 自动找最优 prompt + few-shot | `BootstrapFewShot / MIPRO / GEPA / BootstrapFinetune` |

### 2.3 主流 Optimizer 对比

| Optimizer | 算法 | 何时用 | 备注 |
|---|---|---|---|
| **BootstrapFewShot** | 用 teacher 模型生成 few-shot 示例 + 过滤 | 入门默认 | 便宜、快 |
| **MIPRO**（Multiprompt Instruction Proposal Optimizer）| 同时优化 instruction + few-shot + 演示选择 | 中等复杂度 pipeline | DSPy 2.5+ 默认推荐 |
| **GEPA**（Genetic-Pareto Prompt Evolution）| 遗传算法 + Pareto 前沿 | 复杂多目标（准确率 + 成本 + 速度）| DSPy 3.x 主推 |
| **BootstrapFinetune** | 用 BootstrapFewShot 数据微调 LM 权重 | 极致成本 / 极致延迟 | 需要 GPU |

### 2.4 何时用 DSPy

| 场景 | 是否用 DSPy | 理由 |
|---|---|---|
| **单次 prompt 调用** | ❌ | 太重，直接写 string prompt |
| **RAG pipeline（多步）** | ✅ | module 化封装 + 自动化优化 |
| **Agent（多工具）** | ✅ | signature 天然映射 tool schema |
| **多模型对比 / 迁移** | ✅ | 改 LM 一行代码，optimizer 自动重新找 prompt |
| **Prompt A/B 测试 + 回归** | ✅ | optimizer 自动选最优版本 |
| **快速原型** | ⚠️ | 学习曲线较陡，先 string prompt 跑通再用 DSPy 重构 |

### 2.5 与传统 prompt 的对比

| 维度 | 传统 prompt | DSPy |
|---|---|---|
| 写什么 | string | signature + module |
| few-shot 怎么来 | 手工挑选 | optimizer 自动 |
| prompt 优化 | 人工试错 | 自动 + 可复现 |
| 多模型迁移 | 手动改 prompt | 改 LM 一行代码 |
| 评测 | 人工跑 | 内建 metric + optimizer 反馈 |
| 学习曲线 | 平缓 | 较陡（要理解 signature/module/optimizer）|

---

## 3. 结构化输出四件套

### 3.1 全景对比

| 框架 | 仓库 | 最新版本 | 发布时间 | Stars | 核心机制 | 何时用 |
|---|---|---|---|---|---|---|
| **Instructor** | [567-labs/instructor](https://github.com/567-labs/instructor) | 1.15.4 | 2026-06-28 | 13.4k | 装饰器 + Pydantic 模型，自动校验 / 重试 / 流式 partial 输出 | API 后端、需要强类型 JSON |
| **Outlines** | [dottxt-ai/outlines](https://github.com/dottxt-ai/outlines) | 活跃 | 持续 | 14.3k | 在 token 生成阶段约束（logit mask / regex / grammar / JSON Schema / CFG）| 本地模型 + 复杂结构 |
| **TypeChat** | [microsoft/typechat](https://github.com/microsoft/typechat) | 活跃 | 持续 | 8.7k | "Schema engineering"：先定义类型，库自动构建 prompt + 校验 + 修复 | 已有强类型后端 |
| **Microsoft Prompty** | [microsoft/prompty](https://github.com/microsoft/prompty) | 0.2.3-beta | 2025-07-24 | 1.2k | 标准化 `.prompty` 文件（YAML frontmatter + Markdown body）| 团队 prompt 资产标准化 |

### 3.2 三种实现路径

```
┌─────────────────────────────────────────────────────┐
│ 路径 1: Post-hoc parsing（应用层解析）              │
│ - LLM 输出 string → 应用层用正则/JSON 解析          │
│ - 优点：模型无关                                    │
│ - 缺点：容易格式崩坏，需要大量重试逻辑              │
├─────────────────────────────────────────────────────┤
│ 路径 2: Structured output via API（OpenAI JSON Mode）│
│ - 模型自身支持结构化输出（JSON mode / tool use）    │
│ - 优点：稳                                          │
│ - 缺点：仅特定模型支持                              │
├─────────────────────────────────────────────────────┤
│ 路径 3: Logit mask / constraint decoding（Outlines） │
│ - 在 token 生成阶段 mask 掉非法 token              │
│ - 优点：100% 符合 schema                            │
│ - 缺点：仅本地模型 / 慢 30%~50%                     │
└─────────────────────────────────────────────────────┘
```

### 3.3 选型决策

| 场景 | 推荐 |
|---|---|
| **API 后端 + Python + Pydantic** | Instructor |
| **本地模型 + 复杂结构** | Outlines（logit mask）|
| **TypeScript / .NET 后端** | TypeChat |
| **团队跨语言共享 prompt** | Prompty |
| **OpenAI 生态** | API JSON Mode + Instructor |
| **Claude 生态** | Tool use + Pydantic + Instructor |

### 3.4 Instructor 实战示例（最常用）

```python
import instructor
from pydantic import BaseModel
from openai import OpenAI

client = instructor.from_openai(OpenAI())

class User(BaseModel):
    name: str
    age: int
    role: str

user = client.chat.completions.create(
    model="gpt-4o",
    response_model=User,
    messages=[{"role": "user", "content": "李雷，30 岁，是工程师"}]
)
# 自动校验、重试、流式 partial 输出
```

---

## 4. Prompt 优化工具

### 4.1 工具对比

| 工具 | 类型 | 提供方 | 定位 | 何时用 |
|---|---|---|---|---|
| **prompt-optimizer** | 开源客户端 | [linshenkx/prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) | 31.7k stars；多模型（OpenAI / Gemini / DeepSeek / Grok / 智谱 / 硅基流动 / Anthropic）；纯客户端；已支持 MCP Server | 本地 / 离线 / 注重隐私的 prompt 调优工作台 |
| **PromptPilot** | 商业 SaaS | 字节火山引擎 | 火山方舟「Prompt 驾驶舱」，含 prompt 调优 / 评测 / 效果对比 | 国内豆包 / 火山方舟用户的全托管 prompt 工作台 |
| **PromptPerfect** | 商业 SaaS | Jina AI | 黑盒自动迭代 prompt | SaaS 一键优化，不想自建 |
| **Anthropic Console Prompt Generator** | 控制台内置 | Anthropic | 用一句话描述任务自动生成结构化 prompt；附 "Prompt Improver" 改写已有 prompt | 写 Claude prompt 的快速冷启动 |
| **OpenAI Playground** | 控制台内置 | OpenAI | 手动 + 变量化 prompt，无自动优化器（OpenAI 官方主打 Eval / Evals）| OpenAI 用户的轻量级 playground |

### 4.2 简短判断

- **开源首选**：prompt-optimizer（31.7k，已支持 MCP）
- **Claude 用户冷启动**：Anthropic Console Prompt Generator
- **OpenAI 用户**：OpenAI Playground + Evals 框架
- **企业内统一管控**：PromptPilot（火山）或 PromptPerfect
- **离线 / 隐私场景**：prompt-optimizer

---

## 5. Prompt 模板管理（生产级）

### 5.1 三件套对比

| 维度 | PromptLayer | LangSmith | Helicone |
|---|---|---|---|
| **GitHub** | [promptlayer/promptlayer](https://github.com/promptlayer/promptlayer) | [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk) | [Helicone/helicone](https://github.com/Helicone/helicone) |
| **最新版本** | 持续发布 | v0.9.5（2026-07-01）| v2025.08.21-1（2025-08-21）|
| **Stars** | — | 951 | 5.9k |
| **核心能力** | prompt 版本化、请求回放、AB | trace、eval、prompt 注册、agent 调试 | LLM observability、AI Gateway、prompt 部署 |
| **特色** | 与 OpenAI 客户端无缝集成 | LangChain 生态首选 | 100+ 模型统一网关，prompt 通过网关无代码部署 |
| **自托管** | ❌ SaaS only | ✅ 自托管可选 | ✅ 自托管可选 |

### 5.2 A/B 测试与回归

- **PromptLayer / LangSmith / Helicone** 三家都支持 prompt 版本 + 实验对比 + 回归用例
- **推荐组合**：
  - LangChain 生态 → **LangSmith**
  - 多模型 + 网关需求 → **Helicone**
  - OpenAI-only 场景 → **PromptLayer**

### 5.3 Prompt 注入防护

**通用模式（来自 OWASP / 红队实践）**：

| 层 | 防护手段 | 工具 |
|---|---|---|
| **输入侧** | 双 LLM 模式（privileged + quarantined）| 自研 |
| **工具侧** | allowlist + 参数 schema 校验 | 自研 + Instructor |
| **输出侧** | 结构化校验 + 二次审查 | Instructor / Outlines |
| **监控** | 异常工具调用 / 偏离主题检测 | LangSmith / Helicone |
| **通用护栏** | jailbreak 检测 / 内容安全 / 主题护栏 | [NVIDIA NeMo Guardrails 0.23.0](https://github.com/NVIDIA/NeMo-Guardrails) |

**推荐组合**：**NeMo Guardrails + 结构化输出（Instructor/Outlines）+ 监控（LangSmith/Helicone）** 三层。

---

## 6. Few-shot / CoT / ReAct 现状（2026）

### 6.1 技术现状判断

| 技术 | 2026 年是否主流 | 说明 |
|---|---|---|
| **Few-shot** | ✅ 仍然主流 | Anthropic 官方「示例胜于描述」；Instructor / DSPy 都内建 few-shot 优化 |
| **Chain-of-Thought (CoT)** | ⚠️ 主流但被内化 | 让模型「先思考」仍然有效，但 reasoning 模型（Claude extended thinking / o 系列）已经把 CoT 嵌入推理阶段 |
| **ReAct** | ❌ 退潮 | Agent 框架（LangGraph / Claude Code / Manus）用更结构化的 tool loop 替代了 ReAct 的 string-based 「Thought/Action/Observation」|
| **Self-consistency / ToT** | ⚠️ 仍可用但贵 | reasoning 模型时代，多数场景用单次 extended thinking 即可 |
| **Program-Aided Language Models (PAL)** | ✅ 主流 | 把代码当推理步骤，2026 年是 reasoning model 的默认伴侣 |

### 6.2 Reasoning 模型对传统 CoT 的影响

- Claude Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5 全部内置 **extended thinking**，外部显式 CoT prompt 的边际收益下降
- OpenAI o-series 同理：模型自己决定思考多深
- 但「让模型先列大纲 / 先思考再输出」仍然是 zero-shot 提升质量的有效手段
- **推荐**：`<thinking>` XML 标签 + extended thinking 双重保障

### 6.3 DSPy 自动优化的优势

- **MIPRO / GEPA / BootstrapFewShot** 在 2026 年已能自动发现最优 instruction + few-shot 组合
- 比手调 CoT 更系统、可复现、可对比
- **推荐**：复杂 pipeline 优先用 DSPy 自动化，简单的单次 prompt 仍可手调

---

## 7. 完整工业流程

### 7.1 6 步流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1. 设计   │ → │ 2. 测试   │ → │ 3. 部署   │
└──────────┘    └──────────┘    └──────────┘
                                     ↓
┌──────────┐    ┌──────────┐    ┌──────────┐
│ 6. 防护   │ ← │ 5. 回归   │ ← │ 4. 监控   │
└──────────┘    └──────────┘    └──────────┘
```

### 7.2 各步骤推荐工具

| 步骤 | 工具 | 产出物 |
|---|---|---|
| **1. 设计** | Anthropic Console / prompt-optimizer / DSPy signature | `.prompty` 文件 / Python signature |
| **2. 测试** | DSPy optimizer / Instructor 校验 / RAGAS 评测 | 优化后的 prompt + few-shot + metric |
| **3. 部署** | Prompty / LangSmith Hub / Helicone Gateway | 版本化 prompt + 灰度发布 |
| **4. 监控** | LangSmith / Helicone / Phoenix | trace + token 成本 + 延迟 + 异常 |
| **5. 回归** | RAGAS / DeepEval / TruLens + 黄金集 | 回归报告 + A/B 对比 |
| **6. 防护** | NeMo Guardrails + Instructor + allowlist | jailbreak 检测 + 内容安全 |

### 7.3 关键工程原则

- **每步可追溯**：每个 prompt 版本都要能回溯到具体 trace 和评测结果
- **每步可降级**：prompt 出错要能 fallback 到上一个稳定版本
- **每步可灰度**：新 prompt 先 5% 流量，metric OK 再 100%
- **每步可回归**：黄金集必须每次发版都跑，防止性能回退
- **每步可防护**：用户输入 + 工具调用 + 模型输出三层都要校验

---

## 8. 来源链接（按章节分组）

### 8.1 Anthropic 官方
- [Prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Prompting best practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

### 8.2 Prompt 框架
- [DSPy](https://github.com/stanfordnlp/dspy)
- [Instructor](https://github.com/567-labs/instructor)
- [Outlines](https://github.com/dottxt-ai/outlines)
- [TypeChat](https://github.com/microsoft/typechat)
- [Microsoft Prompty](https://github.com/microsoft/prompty)
- [Guidance](https://github.com/guidance-ai/guidance)
- [LMQL（已停止维护）](https://github.com/eth-sri/lmql)

### 8.3 优化工具
- [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer)
- [PromptPilot（火山）](https://promptpilot.volcengine.com/home)

### 8.4 模板管理
- [PromptLayer](https://github.com/promptlayer/promptlayer)
- [LangSmith SDK](https://github.com/langchain-ai/langsmith-sdk)
- [Helicone](https://github.com/Helicone/helicone)

### 8.5 注入防护
- [NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)