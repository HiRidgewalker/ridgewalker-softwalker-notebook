---
title: LLM 评测框架对比笔记（OpenCompass vs EvalScope）
description: 场景化选型决策树 + 标准生产评测流程 + 自定义数据集流程 + 报告指标清单 + 常见踩坑。覆盖两框架差异、共同点、互操作，以及业界最佳实践。
date: 2026-11-06
---

# LLM 评测框架对比笔记（OpenCompass vs EvalScope）

> **本文目的**：作为 [OpenCompass笔记](/ai/OpenCompass笔记) 和 [EvalScope笔记](/ai/EvalScope笔记) 的对比与汇总文档，避免内容重复。本笔记专注于**横向对比 + 选型决策 + 生产流程模板**。
> 单框架细节请直接查阅两份单框架笔记。

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | 定位差异 | 学术权威 vs 一站式 |
| 2 | 共同点 | 5 项基础能力两框架均支持 |
| 3 | 差异表（核心） | 10 维度 × 2 框架对比 |
| 4 | 选型决策树 | 8 类场景 → 推荐框架 |
| 5 | 互操作与混合部署 | EvalScope 把 OpenCompass 封装为后端 |
| 6 | 标准生产评测流程 | 7 步流水线（通用模板） |
| 7 | 自定义数据集的标准化流程 | JSONL / prompt template / 后处理 |
| 8 | 报告关键指标清单 | 8 项必备字段 |
| 9 | 常见踩坑 | 6 类典型问题 |
| 10 | 业界生产实践 | HF Leaderboard / LMSYS Arena / HELM / Llama / Qwen |
| 11 | 来源链接 | 全部参考链接按章节分组 |

---

## 1. 定位差异

| 框架 | 厂商 | 定位 | 关键差异 |
|---|---|---|---|
| **OpenCompass** | 上海 AI Lab / 书生·浦语 | **学术权威纯文本评测** | CompassKit + CompassHub + CompassRank + CompassAcademic 四件套；学术榜单（C-Eval / SuperBench）官方维护 |
| **EvalScope** | 阿里魔搭（ModelScope） | **一站式：评测 + 压测 + Arena + 可视化** | 把能力评测与推理性能压测整合到同一工具链；与 ms-swift 训练链路深度整合 |

> 一句话：**学术榜单用 OpenCompass，生产一体化用 EvalScope**。

---

## 2. 共同点

两份框架都具备以下基础能力：

| 能力 | OpenCompass | EvalScope |
|---|---|---|
| 本地模型评测 | ✅ HF / LMDeploy / vLLM backend | ✅ `--eval-type llm_ckpt` |
| 远程 API 模型评测 | ✅ OpenAI 兼容 | ✅ openai_api / anthropic_api / litellm / custom |
| OpenAI 兼容协议 | ✅ | ✅（强项，5 种 eval-type） |
| LLM-as-Judge | ✅ | ✅（4 种 judge-strategy） |
| 自定义数据集 | ✅ BaseDataset + yaml | ✅ 4 种模板 + CollectionSchema |
| 分布式评测 | ✅ Slurm / DLC | ✅ 依赖底层推理后端（vLLM TP） |
| 与 vLLM / SGLang 集成 | ✅ 通过 backend / API | ✅ 通过 `--api-url` |
| 断点续跑 | ✅ `-r` | ✅ `--use-cache` |
| 报告格式 | CSV / Markdown / 雷达图 | JSON / HTML / Web Dashboard / Wandb |

---

## 3. 差异表（核心）

### 3.1 能力覆盖

| 维度 | OpenCompass | EvalScope |
|---|---|---|
| **内置 benchmark 数** | 60+ | **191** |
| **多模态支持** | ❌ 纯文本（需配合 VLMEvalKit） | ✅ **Native 后端开箱支持 40+ VLM** |
| **Function Calling / Agent** | ❌ 需自定义 | ✅ Native Agent + 沙箱 |
| **性能压测（TTFT/TPOT）** | ❌ | ✅ **`evalscope perf`**（与 vllm bench 一致） |
| **Arena 对战** | ❌ | ✅ **`general_arena`** + WinRate + Elo |
| **Web Dashboard** | ❌ 离线报告 | ✅ **`evalscope service` 端口 9000** |
| **权重采样多数据集混合** | ❌ 需手动配置 | ✅ **CollectionSchema**（Weighted / Stratified / Uniform） |
| **服务化（REST API）** | ❌ | ✅ **`evalscope service`** |
| **可视化后端集成** | ❌ | ✅ Wandb / SwanLab / Clearml |

### 3.2 工程能力

| 维度 | OpenCompass | EvalScope |
|---|---|---|
| **后端选择** | HF / LMDeploy / vLLM / OpenAI API | HF / vLLM / OpenAI API / Anthropic API / LiteLLM / Custom |
| **CLI 参数丰富度** | 中（run.py + 20 参数） | **高**（`evalscope eval` + 30+ 参数） |
| **Python SDK** | Config-driven（yaml/python） | `TaskConfig` 对象 + dict + YAML + JSON 四种 |
| **集成 OpenCompass 作为后端** | — | ✅ `ms-opencompass` |
| **集成 VLMEvalKit 作为后端** | ❌ | ✅ |
| **集成 RAGEval（MTEB/RAGAS）** | ❌ | ✅ |
| **集成 ms-swift 训练链路** | ❌ | ✅ 官方 best_practice |

### 3.3 生态与社区

| 维度 | OpenCompass | EvalScope |
|---|---|---|
| **GitHub Star** | **7.1k** | 3k+ |
| **主导厂商** | 上海 AI Lab（学术派） | 阿里魔搭（工业派） |
| **主流用户** | InternLM 系列、Llama 官方推荐 | Qwen 系列发版、阿里云百炼 |
| **学术榜单** | CompassRank、C-Eval、SuperBench | — |
| **国内可达性** | ✅（国内源友好） | ✅（默认走 ModelScope） |
| **国际学术引用** | 中等（HF Open LLM Leaderboard 引用少） | 中等 |
| **Meta Llama 官方背书** | ✅ 推荐 | — |

### 3.4 文档与上手

| 维度 | OpenCompass | EvalScope |
|---|---|---|
| **官方文档完整度** | 高（中文 doc.opencompass.org.cn + 英文 docs/en） | 高（docs/zh + docs/en 双语，README 详细） |
| **配置文件方式** | **YAML / Python Config**（Config-driven） | YAML / JSON / Python Dict / TaskConfig 对象 |
| **典型配置行数** | 30~60 行（model + dataset + 评测方式分开） | **10~20 行**（TaskConfig 一站式） |
| **debug 模式** | `--debug`（每个 dataset 取前 N） | `--debug` / `--dry-run` / `--limit` |
| **可视化报表** | `viz_multi_model.py` 雷达图 | HTML / Web Dashboard / Wandb |

---

## 4. 选型决策树

按场景给推荐（结合两份框架的实际能力）：

```
你测什么模型？测什么场景？
│
├─ 中文 Qwen 系列发版评测
│    → EvalScope（官方 best_practice，ms-swift 集成）
│
├─ 英文 / 多语 Llama 系列发版评测
│    → OpenCompass（Meta 官方推荐，学术权威）
│    或 EvalScope（如果需要 perf 压测 + Arena）
│
├─ 中文 InternLM / DeepSeek 系列
│    → OpenCompass（学术榜单）或 EvalScope（国内友好）
│
├─ 通用学术榜单对比（C-Eval / MMLU / SuperBench）
│    → OpenCompass（CompassRank 一键发布）
│
├─ 多模态（VLM）
│    → EvalScope Native 后端（40+ VLM benchmark 开箱）
│    或 EvalScope + VLMEvalKit 后端
│
├─ Function Calling / Agent 评测
│    → EvalScope（BFCL / ACEBench / τ-bench / GAIA）
│
├─ 推理性能压测（TTFT/TPOT）
│    → EvalScope perf（与 vllm bench 一致）
│    或 vllm bench serve（更直接）
│
├─ Arena 双盲对战
│    → EvalScope general_arena
│    或 LMSYS Chatbot Arena（公开数据）
│
├─ RAG / Embedding 评测
│    → EvalScope RAGEVal 后端（MTEB / RAGAS）
│
├─ 国内离线环境
│    → EvalScope（默认 ModelScope Hub，国内可达性最好）
│
└─ 纯文本 / 简单基座评测
     → OpenCompass（轻量、学术权威）
```

### 4.1 选择清单

| 场景 | 推荐框架 | 理由 |
|---|---|---|
| 阿里 Qwen 系列发版 | **EvalScope** | 官方 best_practice，ms-swift 闭环 |
| Meta Llama 系列发版 | **OpenCompass** | Meta 推荐，学术权威 |
| InternLM 系列 | OpenCompass / EvalScope | 都可，OpenCompass 学术榜单加分 |
| 中文 VLM 模型 | **EvalScope** | Native 后端开箱 40+ 多模态 benchmark |
| Function Calling 模型 | **EvalScope** | BFCL / ACEBench / τ-bench 完整覆盖 |
| Agent 类应用（GAIA / SWE-bench） | **EvalScope** | Docker 沙箱 + ReAct 全套 |
| 推理服务压测 | **EvalScope perf** | 与 vllm bench 一致，输出指标语义对齐 |
| 内部模型竞品对比 | **EvalScope general_arena** | WinRate + Elo + 双盲 |
| RAG 系统评估 | **EvalScope RAGEVal** | MTEB / RAGAS 内置 |
| C-Eval / SuperBench 上榜 | **OpenCompass** | CompassRank 一键发布 |
| 纯文本基座快筛 | OpenCompass（HF / LMDeploy backend） | 轻量、配置直观 |
| 纯英文开源模型对标 | OpenCompass（学术）或 EvalScope（生产） | 看使用场景 |

---

## 5. 互操作与混合部署

### 5.1 EvalScope 把 OpenCompass 封装为后端

EvalScope 通过 `--eval-backend OpenCompass` + `--eval-config <yaml>` 直接复用 OpenCompass 的所有配置：

```bash
# 用 OpenCompass 的 yaml 跑 EvalScope
evalscope eval \
  --model Qwen/Qwen2.5-7B-Instruct \
  --eval-backend OpenCompass \
  --eval-config configs/opencompass_eval.py \
  --datasets mmlu ceval gsm8k
```

来源：[opencompass_backend.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/backend/opencompass_backend.md)

### 5.2 OpenCompass 也能调 OpenAI 兼容远程服务

```python
# OpenCompass 用 OpenAI backend 接 vLLM 起的服务
models = [dict(type='openai', abbr='vllm-qwen', model='qwen2.5',
               key='EMPTY', api_base='http://127.0.0.1:8801/v1')]
```

### 5.3 指标口径差异

| 维度 | OpenCompass | EvalScope |
|---|---|---|
| 输出主表 | `summary_*.csv` | `reports/*.json` |
| 可视化 | `viz_multi_model.py` 雷达图 | HTML / Web Dashboard / Wandb |
| 子指标细分 | 自动按子集分桶 | `subset_list` 选 / 五层聚合视角 |
| Judge 模型配置 | `LLMJudgeEvaluator` | `--judge-model-args` JSON |
| Arena 模式 | ❌ | `general_arena` + WinRate + Elo |

> 实操建议：**两框架产出的指标可以并存**（同一份数据集跑两遍，分别看 OpenCompass 的学术报告 + EvalScope 的工程报告）。不要试图做"指标换算"，直接以报告为准。

---

## 6. 标准生产评测流程（通用模板）

适用于两个框架的 7 步流水线：

```
┌──────────────────────────────────────────────────────┐
│ 1. 模型准备                                           │
│    ├─ 本地：HF / vLLM / LMDeploy / ms-swift 部署     │
│    └─ 远程：OpenAI 兼容 API（vLLM / SGLang / DashScope）│
├──────────────────────────────────────────────────────┤
│ 2. 数据集准备                                         │
│    ├─ 内置 benchmark（OpenCompass 60+ / EvalScope 191）│
│    ├─ 自定义 JSONL                                    │
│    └─ HF / ModelScope Hub 直接复用                    │
├──────────────────────────────────────────────────────┤
│ 3. 评测执行                                           │
│    ├─ 并发：--max-num-workers / --eval-batch-size    │
│    ├─ 超时：框架默认 + 自定义 retry                   │
│    └─ 容错：--ignore-errors / --use-cache            │
├──────────────────────────────────────────────────────┤
│ 4. 结果汇总                                           │
│    ├─ 框架内置 metric                                 │
│    ├─ 子集分析：按学科 / 任务 / 语言切分             │
│    └─ 失败样本回写 raw JSONL（便于二次分析）         │
├──────────────────────────────────────────────────────┤
│ 5. 报告产出                                           │
│    ├─ CSV / JSON / Markdown                          │
│    ├─ HTML / Web Dashboard / Wandb                   │
│    └─ 可视化对比（雷达图 / 柱状图）                   │
├──────────────────────────────────────────────────────┤
│ 6. 对比分析                                           │
│    ├─ 与 baseline（同系列旧模型 / 竞品 / 闭源对照）  │
│    └─ 历史回归（防止新版本回退）                     │
├──────────────────────────────────────────────────────┤
│ 7. 归档与回溯                                         │
│    ├─ 评测快照：commit id + dataset hash + model rev │
│    ├─ temperature / max_tokens / prompt hash 锁定   │
│    └─ 可复现命令归档                                  │
└──────────────────────────────────────────────────────┘
```

### 6.1 推荐落地的最小可用模板

| 时间 | 数据集组合 | 框架 |
|---|---|---|
| **第一周（baseline）** | MMLU + GSM8K + IFEval + HumanEval pass@1（每个 ~500 条子样本） | OpenCompass 或 EvalScope |
| **第二周（扩展）** | 加 HellaSwag / ARC / C-Eval / LiveCodeBench / MT-Bench | EvalScope（数据齐全） |
| **第三周（生产化）** | Bad Case 抽样 / 评测快照（commit 锁定）/ CI 化回归 | EvalScope（service 模式）+ CI |
| **第四周（对比与文档）** | Arena 评测（多模型对比）/ Wandb 可视化 / 报告沉淀 | EvalScope general_arena |

---

## 7. 自定义数据集的标准化流程

### 7.1 格式选型

| 格式 | 优点 | 缺点 | 适用 |
|---|---|---|---|
| **JSONL** | 流式评测、错误隔离、字段灵活 | 文件大、需手工切分 | **绝大多数场景首选** |
| **CSV** | 表型结构清晰 | 仅扁平字段、嵌套困难 | MCQ 等扁平结构 |
| **HF Dataset** | 复用 HF 预处理流水线 | 依赖 datasets 库 | 已有 HF 流水线 |

### 7.2 Prompt Template 设计

| 类型 | 示例 | 适用 |
|---|---|---|
| **Zero-shot** | `请回答：{question}` | 模型默认能力测试 |
| **Few-shot** | 固定 n-shot 例子（C-Eval / MMLU 默认 5-shot） | 标准化榜单 |
| **CoT** | `让我们一步步思考：...` | 推理类（GSM8K / MATH 显著） |

### 7.3 Ground Truth 字段设计

必须显式定义：

| 字段 | 含义 | 示例 |
|---|---|---|
| `answer` / `label` | 唯一正确答案 | `"3"` / `"A"` |
| `reference` | 参考答案（开放式） | `"法国是欧洲国家"` |
| `response` | 标准回复（教学场景） | `"巴黎是法国的首都"` |

### 7.4 后处理（extract-then-compare）

```python
# EvalScope 内置 xFinder 提取器
# OpenCompass 通过 --reuse / 自定义 extract 函数

# 典型抽取：\boxed{...}
import re
def extract_boxed(text):
    m = re.search(r'\\boxed\{([^}]+)\}', text)
    return m.group(1) if m else None
```

### 7.5 完整示例：从原始数据到可评测数据集

```
原始 JSON / 数据库
  ↓
标准化 JSONL（统一字段：question / answer / category / meta）
  ↓
注册进框架（OpenCompass configs/datasets/ 或 EvalScope custom_eval/）
  ↓
写 TaskConfig / dataset_args（声明 prompt_template / evaluator）
  ↓
烟雾测试（5 条 --limit 5）→ 调通
  ↓
全量跑 + 结果回写
```

---

## 8. 报告关键指标清单

生产报告必备 8 项字段：

| 字段 | 说明 | 框架对应 |
|---|---|---|
| **总分（overall）** | 加权或简单平均，注明权重 | OpenCompass summary csv / EvalScope reports JSON |
| **子维度分数** | 按学科 / 任务 / 语言切分 | 两框架都支持 |
| **置信区间 / 标准差** | 多次跑的标准差，或 BT 拟合的 95% CI | EvalScope Arena 自带 |
| **失败 case 抽样** | 每数据集随机抽 5~10 条 bad case | 需手动抽样 |
| **评测耗时与成本** | 总 GPU 小时 / 总 token 数 / API 调用金额 | 框架不直接提供 |
| **评测元数据** | 模型 commit id / framework 版本 / dataset hash / temperature / max_tokens / prompt hash | 需手动记录 |
| **可复现命令 / 配置** | 开箱即可 `git checkout` + 重跑 | OpenCompass run.py / EvalScope TaskConfig |
| **可视化** | 雷达图 / 柱状图 / Dashboard | OpenCompass viz / EvalScope HTML+WebUI |

### 8.1 报告模板示例

```markdown
# 模型 X 评测报告 — YYYY-MM-DD

## 总分
- 综合：68.4（加权平均）
- 置信区间：[67.2, 69.6]（N=3 跑）

## 子维度
- 学科知识（MMLU / C-Eval）：72.1
- 推理（GSM8K / MATH）：58.3
- 代码（HumanEval pass@1）：65.0
- 中文（C-Eval / C-MMLU）：71.5
- 指令遵循（IFEval）：75.2

## Bad Case（每类 3 条）
- GSM8K: 模型在多步减法上犯粗心错误
- HumanEval: 边界条件 missing
- ...

## 评测元数据
- 模型：Qwen/Qwen2.5-7B-Instruct (commit: abc123)
- 框架：EvalScope v1.8.1
- 数据集 hash：mmlu@ef456、gsm8k@789abc
- temperature: 0.0
- max_tokens: 2048
- prompt template hash: a1b2c3

## 可复现命令
evalscope eval --model Qwen/Qwen2.5-7B-Instruct \
  --datasets mmlu gsm8k humaneval --temperature 0.0 \
  --judge-strategy rule --work-dir outputs/20260702_qwen25
```

---

## 9. 常见踩坑

### 9.1 数据集污染

- **HF Leaderboard 教训**：DROP 曾因污染下架（[HF 复盘](https://huggingface.co/blog/open-llm-leaderboard-drop)）
- **缓解**：
  - 用「近期题」或「动态题库」（LiveCodeBench 持续更新、IFEval 包含新型格式）
  - 公开 canary string（GPQA 含 BigBench canary）
  - 评测前做 decontamination：在训练数据上跑 n-gram 重叠检测

### 9.2 Prompt 不一致

- 同一份 MMLU + 同一份 5-shot，原始 / HELM / Harness 实现之间最大差 **30%**（[HF MMLU 复盘](https://huggingface.co/blog/open-llm-leaderboard-mmlu)）
- **缓解**：固定 prompt 版本 + commit hash + prompt template hash 归档到报告

### 9.3 评测随机性

- `temperature > 0` 时单次评测不稳
- **缓解**：
  - 能确定性评测的（选择题 / 抽取）用 `temperature=0` greedy
  - 开放式评测用 `temperature=0` + 多次重采平均，或采样一次 + 把方差记入报告
  - MT-Bench 的 multi-turn 也要确保 same seed

### 9.4 LLM-as-Judge 的偏差

MT-Bench 已识别 4 种偏差（[MT-Bench 论文](https://arxiv.org/abs/2306.05685)）：

| 偏差 | 表现 | 缓解 |
|---|---|---|
| **Position bias** | 偏好先出现的回答 | 交换顺序 |
| **Verbosity bias** | 偏好长回答 | AlpacaEval LC 剥离长度 |
| **Self-enhancement bias** | GPT-4 偏好 GPT-4 输出 | 用不同系列 judge |
| **推理能力受限** | judge 不擅长推理判断 | 用 Qwen2.5-72B / Claude-Opus 等强模型 |

### 9.5 长文本评测截断

- NIAH 经典失败模式是「中间遗忘」
- RULER 强化了对 mid-context 的检索与聚合
- **缓解**：强制满上下文扫描 + length × depth 二维热力图

### 9.6 多轮对话状态管理

- MT-Bench 用两轮问题检验模型记忆 / 修正能力
- **缓解**：评测框架需保证 chat template 一致（system prompt、history 注入）

---

## 10. 业界生产实践

### 10.1 HuggingFace Open LLM Leaderboard

| 版本 | 数据集 | 经验 |
|---|---|---|
| **v1** | ARC、HellaSwag、MMLU、TruthfulQA、Winogrande、GSM8K、DROP | 后两者曾因标准化问题被争议 |
| **v2** | IFEval、BBH、MATH Level 5、GPQA、MGSM、MuSR | 均为「持续动态 / 更难 / 更不易饱和」集合 |

评测基于 EleutherAI LM Evaluation Harness，强制固定 commit id + 5-shot example 顺序来保证可比性。

来源：[Leaderboard v2 启动 blog](https://huggingface.co/spaces/open-llm-leaderboard/blog) · [lm-evaluation-harness README](https://github.com/EleutherAI/lm-evaluation-harness)

### 10.2 LMSYS Chatbot Arena

匿名两两对战 → Bradley-Terry 模型 + style control + 95% CI。

数据沉淀：[LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)（1M 真实对话 / 25 LLM / 154 语种）。

来源：[Chatbot Arena 论文](https://arxiv.org/abs/2403.04132) · [Arena FAQ](https://arena.ai/faq)

### 10.3 Stanford HELM

- 7 类指标（accuracy / calibration / robustness / fairness / bias / toxicity / efficiency）× 16 个核心场景
- 覆盖率从原 17.9% 提升至 96.0%
- 评测规模：~4900 evaluations，12B tokens，17M 模型调用

来源：[HELM 论文](https://crfm.stanford.edu/2022/11/17/helm.html)

### 10.4 Meta Llama 系列发版评测

来源：[Llama 3.1 Model Card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md)

**Pretrain benchmark set**：MMLU、MMLU-Pro (CoT)、AGIEval、CommonSenseQA、Winogrande、BBH (CoT)、ARC-C、TriviaQA-Wiki、SQuAD、QuAC、BoolQ、DROP。

**Instruct benchmark set**：追加 IFEval、ARC-C、GPQA、HumanEval/MBPP++/Multipl-E、GSM8K (CoT)、MATH (CoT)、API-Bank/BFCL/Gorilla/Nexus、多语言 MGSM。

发版前必做红队 + 关键风险测试（CBRNE、儿童安全、cyber uplift），并通过 Llama Guard 3 / Prompt Guard / Code Shield 做输入输出过滤。

### 10.5 阿里 Qwen 系列发版评测

- **Qwen2 / Qwen2.5**：覆盖 MMLU、HumanEval、MATH，与 Llama / Mistral / Claude / GPT-4o 对比，分「base vs base」「instruct vs instruct」两轨
- **Qwen2.5-Max**：MMLU-Pro、LiveCodeBench、LiveBench、Arena-Hard、GPQA-Diamond，明显向「动态 / 更难 / Arena 偏好」倾斜
- **Qwen3**：开启 thinking / non-thinking 双模式评测，强调推理预算可控

「Friends of Qwen」标注外部评测方：LMSys、OpenCompass、Open LLM Leaderboard。

来源：[Qwen2.5-Max blog](https://qwenlm.github.io/blog/qwen2.5-max/) · [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/)

### 10.6 OpenAI / Anthropic 内部评测（公开资料）

- **OpenAI GPT-4 技术报告**：列出多类对抗性 / 准确性评测（[arXiv:2303.08774](https://arxiv.org/abs/2303.08774)）
- **Anthropic**：在 [Core Views on AI Safety](https://www.anthropic.com/news/core-views-on-ai-safety) 公开承诺 capability 跨越安全门槛前不发版，由外部独立组织评估能力 + 安全

---

## 11. 来源链接

### 11.1 框架官方

- [OpenCompass GitHub](https://github.com/open-compass/opencompass) / [EvalScope GitHub](https://github.com/modelscope/evalscope)
- [OpenCompass 官网](https://opencompass.org.cn/) / [CompassRank 排行榜](https://rank.opencompass.org.cn/)
- [EvalScope PyPI](https://pypi.org/project/evalscope/) / [EvalScope Releases](https://github.com/modelscope/evalscope/releases)

### 11.2 业界实践

- [HF Open LLM Leaderboard v2 启动 blog](https://huggingface.co/spaces/open-llm-leaderboard/blog)
- [HF Leaderboard DROP 复盘](https://huggingface.co/blog/open-llm-leaderboard-drop)
- [HF Leaderboard MMLU 复盘](https://huggingface.co/blog/open-llm-leaderboard-mmlu)
- [lm-evaluation-harness README](https://github.com/EleutherAI/lm-evaluation-harness)
- [Chatbot Arena 论文](https://arxiv.org/abs/2403.04132)
- [Arena FAQ](https://arena.ai/faq)
- [HELM 论文](https://crfm.stanford.edu/2022/11/17/helm.html)
- [LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)

### 11.3 原始 benchmark 论文

- [HellaSwag](https://arxiv.org/abs/1905.07830) · [MMLU](https://arxiv.org/abs/2009.03300) · [GSM8K](https://arxiv.org/abs/2110.14168)
- [MATH](https://arxiv.org/abs/2103.03874) · [HumanEval](https://github.com/openai/human-eval) · [BBH](https://arxiv.org/abs/2210.09261)
- [LongBench](https://arxiv.org/abs/2308.14508) · [MT-Bench](https://arxiv.org/abs/2306.05685) · [IFEval](https://arxiv.org/abs/2311.07911)
- [Needle-in-a-Haystack](https://github.com/gkamradt/LLMTest_NeedleInAHaystack)

### 11.4 厂商发版评测

- [Llama 3.1 Model Card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md)
- [Qwen2.5-Max blog](https://qwenlm.github.io/blog/qwen2.5-max/) · [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/)
- [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)
- [Anthropic Core Views on AI Safety](https://www.anthropic.com/news/core-views-on-ai-safety)

### 11.5 配套 demo

- [example/llm-demo/03_eval_frameworks](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/llm-demo/03_eval_frameworks/README.md) — OpenCompass + EvalScope 双框架 mock 演示

标签：#llm-eval
