---
title: EvalScope 评测框架笔记
description: 阿里魔搭出品的一站式大模型评测框架：四大后端、本地 / 远程模型测试、191 个内置 benchmark、CollectionSchema 权重采样、LLM-as-Judge、Arena 对战、推理压测、Web Dashboard。覆盖 v1.8.1。
type: hub
---

# EvalScope 评测框架笔记

> **本文目的**：补全 `目录.md` 中评测章节的 EvalScope 部分。覆盖框架定位、本地与远程模型评测流程、内置数据集清单、自定义数据集方式（含 CollectionSchema 权重采样）、评测指标、生产特性。
> 对比框架笔记：[OpenCompass笔记](./OpenCompass笔记.md)、[LLM评测框架对比笔记](/blog/LLM评测框架对比笔记)

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | EvalScope 概述 | 项目背景、版本、定位（一站式） |
| 2 | 架构核心组件 | TaskConfig / ModelAPI / DataAdapter / CollectionSchema + 四大后端 |
| 3 | 本地模型测试 | `evalscope eval` 完整 CLI + HF / vLLM / LMDeploy / ms-swift + 多 GPU |
| 4 | 远程 API 模型测试 | openai_api / anthropic_api / DashScope / ModelScope Inference 五种 eval-type |
| 5 | 内置数据集清单 | 191 个 benchmark 按 8 大类整理 |
| 6 | 自定义数据集 | 四种内置模板 + JSONL + CollectionSchema 五层聚合 |
| 7 | 评测指标 | acc / f1 / BLEU / ROUGE / pass@k / winrate / elo + 四种 judge 策略 |
| 8 | 生产环境特性 | vLLM / SGLang 集成 + Arena + perf 压测 + service 服务化 + CI/CD |
| 9 | 来源链接 | 全部参考链接按章节分组 |

---

## 1. EvalScope 概述

[EvalScope](https://github.com/modelscope/evalscope) 是阿里魔搭（ModelScope）出品的大模型评测框架，最初是 ms-swift 训练框架下的 eval 子模块，后独立为 [PyPI 包 `evalscope`](https://pypi.org/project/evalscope/)。定位是 **「一站式评测 + 压测 + Arena + 可视化」**，把能力评测与推理性能压测整合到同一工具链。

| 项目信息 | 数值 | 来源 |
|---|---|---|
| 当前主版本 | v1.8.1（2026-06-16 发布） | [GitHub Releases](https://github.com/modelscope/evalscope/releases) |
| GitHub Star | 3k+ | [GitHub 主页](https://github.com/modelscope/evalscope) |
| 许可证 | Apache-2.0 | 仓库 LICENSE |
| 维护者 | ModelScope 团队（@wangxingjun778 等） | 仓库 CONTRIBUTORS |
| Python | ≥ 3.10 | [installation.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/installation.md) |
| 里程碑 | v1.0.0（2025-08-25）重构 api 模块 | [Releases](https://github.com/modelscope/evalscope/releases) |

### 「一站式」四大能力

| 能力 | 对应命令 | 用途 |
|---|---|---|
| **能力评测** | `evalscope eval` | 跑标准 benchmark（MMLU / GSM8K / HumanEval 等） |
| **推理压测** | `evalscope perf` | TTFT / TPOT / ITL / 吞吐压测（与 vllm bench 一致） |
| **Arena 对战** | `general_arena` dataset | Pairwise Battle + WinRate + Elo |
| **可视化** | `evalscope service` | Web Dashboard (9000) + HTML / Wandb / SwanLab |

主流使用方：

- **Qwen 系列发版评测**：Qwen3 / Qwen3-Coder / Qwen3-VL / Qwen3-Omni / Qwen3-Next 均有官方 best_practice
- **阿里云百炼（DashScope）**：通过 OpenAI 兼容接口被 EvalScope 默认支持
- **DeepSeek R1 Distill 评测**：有官方 best_practice 文档
- **GPT OSS / Llama 全栈**：`llm_full_stack.md` 给出训练 → 部署 → 评测 → 上传闭环

---

## 2. 架构核心组件

### 2.1 整体架构

```
┌────────────────────────────────────────────────────┐
│                EvalScope 架构                       │
├────────────────────────────────────────────────────┤
│  Input Layer                                        │
│    ├─ Model Sources (OpenAI API / DashScope / HF / │
│    │                ModelScope Hub / 本地)          │
│    └─ Datasets (内置 benchmark / JSONL / HF)       │
├────────────────────────────────────────────────────┤
│  Core Functions                                     │
│    ├─ Native Evaluator (默认)                      │
│    ├─ OpenCompass Backend (ms-opencompass 封装)   │
│    ├─ VLMEvalKit Backend (多模态)                  │
│    ├─ RAGEval Backend (RAG / Embedding)           │
│    └─ Perf 压测引擎 (TTFT / TPOT / ITL)            │
├────────────────────────────────────────────────────┤
│  Output Layer                                       │
│    ├─ 报告: JSON / Tables / Logs / HTML            │
│    └─ 可视化: Web Dashboard(9000) / Wandb / SwanLab│
└────────────────────────────────────────────────────┘
```

来源：[introduction.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/introduction.md)

### 2.2 关键抽象

| 抽象 | 作用 |
|---|---|
| **`TaskConfig`** | 评测任务配置（模型 / 数据集 / batch / judge 等） |
| **`run_task`** | 统一执行入口（CLI / Python / YAML / JSON 四种调用方式一致） |
| **`ModelAPI`** | 自定义模型适配器基类（继承后实现 `generate()` 方法） |
| **`DataAdapter`** | 数据集适配器（`DefaultDataAdapter` / `FunctionCallAdapter`） |
| **`NativeAgentConfig`** | Agent 驱动评测入口 |
| **`CollectionSchema`** + **`DatasetInfo`** + **`WeightedSampler`** | 多数据集混合采样 |
| **`@register_model_api`** | 注册自定义模型后端 |

### 2.3 四大后端

EvalScope 把多个评测框架作为后端集成：

| 后端 | 命令 `--eval-backend` | 覆盖范围 | 文档 |
|---|---|---|---|
| **Native**（默认） | `Native` | LLM / VLM / Embedding / Reranker / CLIP / AIGC | [introduction.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/introduction.md) |
| **OpenCompass** | `OpenCompass` | 纯文本评测，复用 OpenCompass 全数据集 | [opencompass_backend.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/backend/opencompass_backend.md) |
| **VLMEvalKit** | `VLMEvalKit` | 多模态评测，40+ VLM benchmark | [vlmevalkit_backend.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/backend/vlmevalkit_backend.md) |
| **RAGEval** | `RAGEval` | RAG / Embedding 评测（MTEB / RAGAS） | README What's New |

---

## 3. 本地模型测试

### 3.1 `evalscope eval` 完整 CLI 参数

```bash
evalscope eval --model <model_id> --datasets <dataset1> <dataset2> [options]
```

#### 模型参数

| 参数 | 说明 |
|---|---|
| `--model` | ModelScope 模型 ID / 本地路径 / API 模型 ID |
| `--model-id` | 报告中的别名 |
| `--api-url` | OpenAI 兼容端点 |
| `--api-key` | 默认 `EMPTY` |
| `--model-args` | JSON 字符串：`{"revision":"master","precision":"torch.float16","device_map":"auto"}` |
| `--model-task` | `text_generation` / `image_generation` |
| `--chat-template` | Jinja 模板字符串 |

#### 数据集参数

| 参数 | 说明 |
|---|---|
| `--datasets` | 空格分隔多个 |
| `--dataset-dir` | 默认 `~/.cache/modelscope/datasets` |
| `--dataset-hub` | `modelscope` / `huggingface` |
| `--limit` | int（前 N）或 float（前 N%） |
| `--repeats` | 重复次数 |
| `--dataset-args` | JSON 字符串 |

#### 评测类型 / 后端

| 参数 | 说明 |
|---|---|
| `--eval-type` | `llm_ckpt` / `openai_api` / `openai_responses_api` / `anthropic_api` / `litellm` / `text2image` / `custom` |
| `--eval-batch-size` | 默认 1（service 模式 8） |
| `--eval-backend` | `Native`（默认）/ `OpenCompass` / `VLMEvalKit` / `RAGEVal` / `ThirdParty` |
| `--eval-config` | 非 Native 后端的配置文件路径 |

#### Judge 参数

| 参数 | 说明 |
|---|---|
| `--judge-strategy` | `auto` / `llm` / `rule` / `llm_recall` |
| `--judge-model-args` | JSON 字符串 |
| `--analysis-report` | 是否生成 judge 分析报告 |

#### 其他

| 参数 | 说明 |
|---|---|
| `--work-dir` | 默认 `./outputs` |
| `--use-cache` | 复用本地缓存（断点续跑） |
| `--rerun-review` | 与 `--use-cache` 配合，强制重跑评分 |
| `--seed` | 随机种子 |
| `--debug` | debug 模式 |
| `--ignore-errors` | 跳过 OOM / 超时样本 |
| `--dry-run` | 只生成配置不实际跑 |

> 注：CLI 中**没有**原生的 `--num-gpus` / `--device` / `--parallel` / `--rate-limit`，多 GPU 通过 `--model-args '{"device_map":"auto"}'`；并发限速在 `evalscope perf` 中通过 `--parallel` / `--rate` 控制。

来源：[parameters.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/parameters.md)

### 3.2 Python SDK

```python
from evalscope import TaskConfig, run_task

task_cfg = TaskConfig(
    model='Qwen/Qwen2.5-0.5B-Instruct',
    datasets=['gsm8k', 'arc'],
    limit=5,
)
run_task(task_cfg=task_cfg)
```

`run_task` 同时接受 `TaskConfig` 对象、Python 字典、YAML 文件路径、JSON 文件路径四种形式。

来源：[basic_usage.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/basic_usage.md)

### 3.3 模型加载方式

| 加载方式 | 关键参数 | 适用 |
|---|---|---|
| ModelScope Hub 直接加载 | `--model Qwen/Qwen2.5-7B-Instruct` 自动下载 | 国内首选 |
| 本地路径 | `--model ./model/qwen2.5` | 离线 |
| HuggingFace Transformers | `--model-args '{"revision":"main"}'` | 国际通用 |
| vLLM 服务（推荐生产） | `vllm serve` + `--api-url http://...` | 高吞吐 |
| LMDeploy 服务 | `lmdeploy serve api_server` + `--api-url` | InternLM 生态 |
| ms-swift 部署 | `swift deploy --model ...` + `--api-url` | 训练后直评 |
| Ollama（GGUF 量化） | `ollama run modelscope.cn/...` + `--api-url` | 轻量本地 |

### 3.4 多 GPU 分布式

EvalScope 自身**不实现**模型分片，依赖底层推理后端：

- **本地 ckpt**：`--model-args '{"device_map":"auto"}'` 触发 Transformers 自动分片
- **vLLM 服务**：`tensor_parallel_size` 在 `vllm serve` 侧设置
- **多机**：通过 Ray / vLLM distributed 启动服务，EvalScope 通过 OpenAI 兼容接口统一调用

### 3.5 完整可复制工作流

```bash
# 1) 安装（推荐 conda 环境）
conda create -n evalscope python=3.10 -y
conda activate evalscope
pip install evalscope                    # 基础
pip install 'evalscope[perf]'            # + 压测
pip install 'evalscope[service]'         # + WebUI
pip install 'evalscope[all]'             # 全功能

# 2) 本地 ckpt 评测（ModelScope 自动下载）
evalscope eval \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --datasets gsm8k arc \
  --limit 5

# 3) Python SDK 等价
python -c "
from evalscope import TaskConfig, run_task
run_task(task_cfg=TaskConfig(
    model='Qwen/Qwen2.5-0.5B-Instruct',
    datasets=['gsm8k', 'arc'], limit=5))
"

# 4) 输出报告
# 终端表格 + ./outputs/<timestamp>/{logs, predictions, reviews, reports, configs}/
```

---

## 4. 远程 API 模型测试（EvalScope 强项）

### 4.1 `--eval-type` 五种类型

| `--eval-type` | 适配服务 |
|---|---|
| `openai_api` | OpenAI / vLLM / LMDeploy / ms-swift / Ollama 等所有 OpenAI 兼容服务 |
| `openai_responses_api` | OpenAI 官方 Responses API（支持 stream） |
| `anthropic_api` | Anthropic Claude |
| `litellm` | 通过 LiteLLM 统一代理 100+ 模型 |
| `custom` | 用户自定义（继承 `ModelAPI` + `@register_model_api`） |

### 4.2 场景 1：OpenAI 兼容 vLLM 本地服务

```bash
# 1) 启动 vLLM 服务
export VLLM_USE_MODELSCOPE=True
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --served-model-name qwen2.5 --trust-remote-code --port 8801

# 2) 评测
evalscope eval \
  --model qwen2.5 \
  --api-url http://127.0.0.1:8801/v1 \
  --api-key EMPTY \
  --eval-type openai_api \
  --datasets gsm8k --limit 10
```

### 4.3 场景 2：DashScope（阿里云百炼）远程

```bash
evalscope eval \
  --model qwen2.5-7b-instruct \
  --api-url https://dashscope.aliyuncs.com/compatible-mode/v1 \
  --api-key $DASHSCOPE_API_KEY \
  --eval-type openai_api \
  --datasets chinese_simpleqa \
  --judge-strategy llm \
  --judge-model-args '{"model_id":"qwen2.5-72b-instruct","api_url":"https://dashscope.aliyuncs.com/compatible-mode/v1","api_key":"'$DASHSCOPE_API_KEY'"}'
```

### 4.4 场景 3：ModelScope Inference API

```bash
evalscope eval \
  --model Qwen/Qwen3-32B \
  --api-url https://api-inference.modelscope.cn/v1/chat/completions \
  --api-key $MODELSCOPE_SDK_TOKEN \
  --eval-type openai_api \
  --datasets mmlu_pro --limit 10
```

### 4.5 场景 4：OpenAI 官方 + 流式

```bash
evalscope eval \
  --model gpt-4.1-mini \
  --api-url https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --eval-type openai_responses_api \
  --datasets gsm8k --limit 10 \
  --generation-config '{"stream": true, "max_tokens": 512}'
```

### 4.6 并发 / 限速

`evalscope eval` 本身并发控制有限：

- `--eval-batch-size`（默认 1，service 模式 8）
- 服务端（vLLM）侧配置

`evalscope perf` 提供完整压测级并发控制：`--parallel 1 10 50 100 200` / `--number 10 20 100 200 400` / `--rate`（泊松到达）/ `--open-loop`（无背压）。

---

## 5. 内置数据集清单

EvalScope **benchmarks 目录共 191 个独立 benchmark 文档**，覆盖 LLM / VLM / Agent / AIGC / Embedding 等多个领域。

完整 191 个 benchmark 列表：[docs/en/benchmarks/](https://github.com/modelscope/evalscope/tree/main/docs/en/benchmarks)

### 5.1 学科知识 / 通用能力

| 数据集 | 任务类型 | 子集 | 默认 metric | URL |
|---|---|---|---|---|
| `mmlu` | Knowledge MCQ | 57 学科（STEM/Humanities/Social Sciences/Other） | `acc` | [mmlu.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mmlu.md) |
| `mmlu_pro` | Knowledge MCQ | 14 类别 | `acc` | [mmlu_pro.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mmlu_pro.md) |
| `mmlu_redux` | Knowledge MCQ | 57 学科 | `acc` | 同上 |
| `ceval` | Chinese MCQ | 52 学科 | `acc` | [ceval.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/ceval.md) |
| `cmmlu` | Chinese MCQ | 67 学科 | `acc` | [cmmlu.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/cmmlu.md) |
| `arc` | MCQ Reasoning | ARC-Easy / ARC-Challenge | `acc` | [arc.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/arc.md) |
| `hellaswag` | Commonsense MCQ | default | `acc` | [hellaswag.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/hellaswag.md) |
| `gpqa_diamond` | Knowledge MCQ | diamond | `acc` | [gpqa_diamond.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/gpqa_diamond.md) |
| `super_gpqa` | Knowledge MCQ | 多领域 | `acc` | 同上 |
| `commonsense_qa` | Commonsense MCQ | default | `acc` | [commonsense_qa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/commonsense_qa.md) |
| `trivia_qa` | QA ReadingComp | default | `acc` | [trivia_qa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/trivia_qa.md) |
| `truthful_qa` | Knowledge | default | `acc` | [truthful_qa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/truthful_qa.md) |

### 5.2 中文能力

| 数据集 | 任务类型 | 子集 | 默认 metric | URL |
|---|---|---|---|---|
| `ceval` | Chinese Knowledge | 52 学科 | `acc` | 见上 |
| `cmmlu` | Chinese Knowledge | 67 学科 | `acc` | 见上 |
| `iquiz` | Chinese Knowledge | 中学科目 | `acc` | [iquiz.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/iquiz.md) |
| `maritime_bench` | Chinese Knowledge | 船舶专业 | `acc` | [maritime_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/maritime_bench.md) |
| `chinese_simpleqa` | Chinese QA | default | judge（LLM） | [chinese_simpleqa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/chinese_simpleqa.md) |
| `gaokao` | Chinese Knowledge | 高考题目 | `acc` | 默认数据集列表 |
| `maritime_ocr_bench` | Chinese OCR | default | `acc` | [maritime_ocr_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/maritime_ocr_bench.md) |

### 5.3 推理 / 数学

| 数据集 | 任务类型 | 子集 | 默认 metric | 评测方式 | URL |
|---|---|---|---|---|---|
| `gsm8k` | Math Reasoning | main | `acc` | 4-shot CoT，`\boxed{}` | [gsm8k.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/gsm8k.md) |
| `gsm8k_v` | Math Reasoning | verified | `acc` | 4-shot CoT | [gsm8k_v.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/gsm8k_v.md) |
| `math_500` | Math | 500 题 | `acc` | 0-shot | [math_500.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/math_500.md) |
| `competition_math` | Math | default | `acc` | 0-shot | [competition_math.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/competition_math.md) |
| `aime24` / `aime25` / `aime26` | Math | 各年 | `acc` | 0-shot | [aime24.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/aime24.md) |
| `bbh` | Reasoning | 27 子任务 | `acc` | 0-shot CoT | [bbh.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/bbh.md) |
| `drop` | Reasoning | default | `acc` | 离散推理 | [drop.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/drop.md) |
| `musr` | MCQ Reasoning | default | `acc` | 0-shot | [musr.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/musr.md) |
| `logi_qa` | MCQ Reasoning | default | `acc` | 逻辑推理 | [logi_qa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/logi_qa.md) |
| `winogrande` | MCQ Reasoning | default | `acc` | 共指消解 | [winogrande.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/winogrande.md) |

### 5.4 代码

| 数据集 | 任务类型 | 子集 | 默认 metric | 评测方式 | URL |
|---|---|---|---|---|---|
| `humaneval` | Coding | 164 题 | `acc` | 0-shot，4 秒/题，**默认沙箱执行** | [humaneval.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/humaneval.md) |
| `humaneval_plus` | Coding | 164 题 | `acc` | 增强测试用例 | [humaneval_plus.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/humaneval_plus.md) |
| `mbpp` | Coding | default | `acc` | Python 函数补全 | [mbpp.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mbpp.md) |
| `mbpp_plus` | Coding | default | `acc` | 增强测试 | [mbpp_plus.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mbpp_plus.md) |
| `live_code_bench` | Coding | v5/v6 | `acc` / pass@1 | 时间窗口过滤，需沙箱 | [live_code_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/live_code_bench.md) |
| `bigcodebench` / `_hard` | Coding | default | `acc` | 工具调用式 | [bigcodebench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/bigcodebench.md) |
| `scicode` | Coding | scientific | `acc` | 科研代码 | [scicode.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/scicode.md) |
| `swe_bench_verified` / `_lite` / `_pro` | Coding | 多子集 | `acc` | Agent 风格 | [swe_bench_verified.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/swe_bench_verified.md) |

### 5.5 多模态（VLM Native 后端开箱支持）

| 数据集 | 任务类型 | 子集 | 默认 metric | URL |
|---|---|---|---|---|
| `mmmu` | MultiModal QA | 30 学科 | `acc` | [mmmu.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mmmu.md) |
| `mm_bench` | MultiModal QA | `cn` + `en` | `acc` | [mm_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mm_bench.md) |
| `math_vista` | MultiModal Math | default | `acc` | [math_vista.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/math_vista.md) |
| `ocr_bench` / `_v2` | MultiModal OCR | default | `acc` | [ocr_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/ocr_bench.md) |
| `ai2d` | MultiModal QA | default | `acc` | [ai2d.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/ai2d.md) |
| `hallusion_bench` | Hallucination | default | `acc` | [hallusion_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/hallusion_bench.md) |
| `mm_star` | MultiModal MCQ | default | `acc` | [mm_star.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mm_star.md) |
| `chartqa` / `docvqa` / `infovqa` | MultiModal QA | default | `acc` | [chartqa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/chartqa.md) |
| `real_world_qa` / `vqav2` | MultiModal QA | default | `acc` | [real_world_qa.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/real_world_qa.md) |
| `mvbench` / `videomme_v2` | Video MultiModal | default | `acc` | [mvbench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mvbench.md) |
| `refcoco` | Grounding | default | `acc` | [refcoco.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/refcoco.md) |

### 5.6 指令遵循 / Arena

| 数据集 | 任务类型 | 子集 | 默认 metric | URL |
|---|---|---|---|---|
| `ifeval` | InstructionFollowing | default | `prompt_level_strict/loose` | [ifeval.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/ifeval.md) |
| `ifbench` | InstructionFollowing | default | `acc` | [ifbench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/ifbench.md) |
| `multi_if` | InstructionFollowing MultiTurn | default | `acc` | [multi_if.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/multi_if.md) |
| `eq_bench` | InstructionFollowing | default | `acc` | [eq_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/eq_bench.md) |
| `cl_bench` | InstructionFollowing Reasoning | default | `acc` | [cl_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/cl_bench.md) |
| `alpaca_eval` | Arena InstructionFollowing | default | `winrate` | [alpaca_eval.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/alpaca_eval.md) |
| `arena_hard` | Arena InstructionFollowing | default | `winrate` / `elo` | [arena_hard.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/arena_hard.md) |
| `general_arena` | Arena Custom | 自定义 | `winrate` / `elo` | [general_arena.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/general_arena.md) |

> 注：`mt_bench` / `followbench` / `toxigen` 在 EvalScope 文档树中**未提供独立页面**，建议用 `arena_hard` / `alpaca_eval` / `halueval` / `bfcl_v4` 替代。

### 5.7 长文本

| 数据集 | 任务类型 | 子集 | 默认 metric | URL |
|---|---|---|---|---|
| `longbench_v2` | LongContext MCQ | `short` / `medium` / `long` | `acc` | [longbench_v2.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/longbench_v2.md) |
| `needle_haystack` | LongContext Retrieval | `english` / `chinese` | `acc` + 热力图 | [needle_haystack.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/needle_haystack.md) |
| `aa_lcr` | LongContext Reasoning | default | `acc` | [aa_lcr.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/aa_lcr.md) |
| `docmath` | LongContext Math | default | `acc` | [docmath.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/docmath.md) |
| `locomo` / `longmemeval` | LongContext MultiTurn | default | `acc` | [locomo.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/locomo.md) |

### 5.8 安全 / 工具调用 / Agent

| 数据集 | 任务类型 | 默认 metric | URL |
|---|---|---|---|
| `halueval` | Hallucination | `acc` | [halueval.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/halueval.md) |
| `bfcl_v3` / `bfcl_v4` | FunctionCalling | `acc` | [bfcl_v4.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/bfcl_v4.md) |
| `acebench` | Agent FunctionCalling MultiTurn | `acc` | [acebench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/acebench.md) |
| `tau_bench` / `tau2_bench` / `tau3_bench` | Agent MultiTurn | `acc` | [tau_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/tau_bench.md) |
| `tir_bench` | Agent MultiTurn | `acc` | [tir_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/tir_bench.md) |
| `gaia` | Agent | `acc` | [gaia.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/gaia.md) |
| `terminal_bench_v2` / `v2_1` | Agent Coding | `acc` | [terminal_bench_v2.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/terminal_bench_v2.md) |
| `mcp_atlas` | Agent MCP | `acc` | [mcp_atlas.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/mcp_atlas.md) |
| `general_fc` | FunctionCalling Custom | `acc` | [general_fc.md](https://github.com/modelscope/evalscope/blob/main/docs/en/benchmarks/general_fc.md) |

---

## 6. 自定义数据集

### 6.1 四种内置模板

| 模板 | 文件结构 | 字段 | 适用 |
|---|---|---|---|
| `general_mcq` | `{subset}_dev.csv`（可选 few-shot）+ `{subset}_val.csv` | `id,question,A,B,C,D,answer` | 单选 MCQ |
| `general_mcq`（多选） | `{subset}_multi_val.jsonl` | `question, A-D, answer: ["A","C"]` | 多选 MCQ（`multiple_correct=True`） |
| `general_qa` | `example.jsonl` | `system/query/response` 或 `messages/response` | 开放问答 |
| `general_fc` | `example.jsonl` | `messages, tools, should_call_tool` | Function Calling |
| `general_arena` | `arena.jsonl` | `query` | Arena 对战 |

### 6.2 JSONL 字段示例（QA）

```json
{"system": "你是助手", "query": "巴黎是哪个国家的首都？", "response": "法国"}
```
或
```json
{"query": "...", "response": "..."}
```
或
```json
{"messages": [{"role":"system","content":"..."},{"role":"user","content":"..."}], "response": "..."}
```

### 6.3 完整示例（自定义 MCQ JSONL）

```python
from evalscope import TaskConfig, run_task

task_cfg = TaskConfig(
    model='Qwen/Qwen2-0.5B-Instruct',
    datasets=['general_mcq'],
    dataset_args={
        'general_mcq': {
            'local_path': 'custom_eval/text/mcq',  # 指向本地目录
            'subset_list': ['example'],              # 选择子集
            # 'extra_params': {'multiple_correct': True, 'use_cot': True}
        }
    }
)
run_task(task_cfg=task_cfg)
```

### 6.4 HuggingFace Dataset 直接复用

把 `local_path` 替换为 `dataset_id`：

```python
'general_mcq': {'dataset_id': 'evalscope/GeneralFunctionCall-Test'}
```

### 6.5 自定义 prompt template / postprocessor

通过 `extra_params.prompt_template` 覆盖默认模板。中文 MCQ 默认模板：

```
text
Please answer the question and select the correct answer from the options. The last line of your answer should be in the following format: "答案是：LETTER"
{query}
```

设置 `use_cot=True` 自动切换到 `*_COT` 模板。

### 6.6 CollectionSchema 权重采样（核心创新）

来源：[collection/schema.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/schema.md) · [collection/sample.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/sample.md)

EvalScope 提供**权重采样机制**把多个数据集混合成一个 JSONL：

```python
from evalscope.collections import CollectionSchema, DatasetInfo, WeightedSampler
from evalscope.utils.io_utils import dump_jsonl_data

schema = CollectionSchema(name='Qwen3', datasets=[
    CollectionSchema(name='English', datasets=[
        DatasetInfo(name='mmlu_pro',   weight=1, task_type='exam', tags=['en']),
        DatasetInfo(name='ifeval',     weight=1, task_type='instruction', tags=['en']),
    ]),
    CollectionSchema(name='Code', datasets=[
        DatasetInfo(name='live_code_bench', weight=1, task_type='code', tags=['en'],
            args={'subset_list':['v5_v6'], 'extra_params':{'start_date':'2025-01-01','end_date':'2025-04-30'}}),
    ]),
])
mixed_data = WeightedSampler(schema).sample(100000)
dump_jsonl_data(mixed_data, 'outputs/qwen3_test.jsonl')
```

三种采样策略：

| 策略 | 行为 | 适用 |
|---|---|---|
| **Weighted** | 按业务权重分配 | 强化价值取向（如「推理题占 50%」） |
| **Stratified** | 按原始数据集大小等比 | 保留语料结构 |
| **Uniform** | 每数据集固定数量 | 能力对齐（每个能力维度等量） |

### 6.7 五层聚合视角（collection evaluate.md）

`data_collection` 报告支持五层聚合：

| 层级 | 含义 |
|---|---|
| `subset_level` | 原数据集内部子集 |
| `dataset_level` | 同一数据集聚合 |
| `task_level` | 同任务类型聚合 |
| `tag_level` | 按 tag（语言、模式等）聚合 |
| `category_level` | 自定义聚合 |

三种聚合 metric：`micro_avg`（样本加权）/ `macro_avg`（等权）/ `weighted_avg`（叶子权重加权）。

来源：[collection/evaluate.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/evaluate.md)

---

## 7. 评测指标

### 7.1 内置 metric 列表

| Metric | 适用 | 备注 |
|---|---|---|
| `acc` | MCQ / 数值答案 | 各 benchmarks 默认 |
| `f1` | NER / 分类 | benchmarks 列表 |
| `BLEU-{1..4}` | QA / 翻译 | `general_qa` 默认 |
| `ROUGE-{1,2,L}-{R,P,F}` | QA / 摘要 | `general_qa` 默认 |
| `pass@k` | 代码生成 | `humaneval` / `live_code_bench` |
| `vote@k` | 数学 | 聚合 `mean_and_vote_at_k` |
| `pass^k` | 数学 | 聚合 `mean_and_pass^k` |
| `winrate` / `elo` | Arena 对战 | `arena_hard` / `alpaca_eval` / `general_arena` |
| TTFT / TPOT / ITL | 压测 | `evalscope perf` |

### 7.2 LLM-as-Judge（核心能力）

四种 `--judge-strategy`：

| 策略 | 行为 |
|---|---|
| `auto` | 自动选择 |
| `llm` | 使用 LLM judge（典型配置：`qwen2.5-72b-instruct` / `gpt-4-1106-preview`） |
| `rule` | 规则匹配（精确匹配 / 正则） |
| `llm_recall` | LLM judge + 召回（如多答案选择题） |

Judge 模型在 `--judge-model-args` 中以 JSON 配置：

```python
judge_model_args={
    'model_id': 'qwen2.5-72b-instruct',
    'api_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'api_key': os.getenv('DASHSCOPE_API_KEY'),
    'generation_config': {'temperature': 0.0, 'max_tokens': 8000}
}
```

### 7.3 子指标细分示例

- **MMLU** 4 大类 57 学科：STEM / Humanities / Social Sciences / Other（可通过 `subset_list` 选学科）
- **MMMU** 30 学科 183 子领域
- **Arena Hard**：自动输出 win rate + Elo
- **needle_haystack**：context length × depth 二维热力图

### 7.4 报告输出格式

| 格式 | 路径 / 方式 |
|---|---|
| 终端表格 | 跑完立即打印 |
| JSON | `outputs/<timestamp>/reports/` |
| HTML 报告 | `outputs/<timestamp>/reports/`（WebUI 内 "View HTML Report" 按钮可打开） |
| Web Dashboard | `evalscope service`（端口 9000） |
| Wandb | `--visualizer wandb` |
| SwanLab | `--visualizer swanlab` |
| Clearml | `--visualizer clearml` |
| SQLite（压测） | `--enable-progress-tracker` 实时写入 `progress.json` |

来源：[visualization.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/visualization.md)

---

## 8. 生产环境特性

### 8.1 与 vLLM / SGLang 部署服务集成（生产链路）

EvalScope 评测 **必须**有推理服务，标准生产链路：

```bash
# 1) vLLM 部署（推荐生产）
VLLM_USE_MODELSCOPE=True CUDA_VISIBLE_DEVICES=0 \
  vllm serve Qwen/Qwen3-32B --gpu-memory-utilization 0.9 \
  --served-model-name Qwen3-32B --trust-remote-code --port 8801 --tensor-parallel-size 4

# 2) EvalScope 评测
evalscope eval --model Qwen3-32B --api-url http://127.0.0.1:8801/v1 \
  --api-key EMPTY --eval-type openai_api --datasets data_collection \
  --dataset-args '{"data_collection":{"dataset_id":"evalscope/Qwen3-Test-Collection"}}'
```

支持的后端服务：

| 后端 | 启动命令 |
|---|---|
| **vLLM** | `python -m vllm.entrypoints.openai.api_server` |
| **ms-swift** | `swift deploy --model ...` |
| **LMDeploy** | `lmdeploy serve api_server ...` |
| **Ollama** | `ollama run modelscope.cn/...` |

SGLang：文档中**未单独提及**，但因支持 OpenAI 兼容接口，理论可用，未提供官方 best practice。

### 8.2 与 ms-swift 训练链路集成

```bash
# ms-swift 训练
swift sft --model_type qwen2-7b-instruct --model_id_or_path qwen/Qwen2-7B-Instruct \
  --dataset data/train.jsonl --sft_type lora --lora_rank 8 ...

# ms-swift 部署
swift deploy --model output/qwen2-7b-instruct/v0 --port 8000

# EvalScope 评测
evalscope eval --model qwen2-7b-instruct --api-url http://127.0.0.1:8000/v1 \
  --eval-type openai_api --datasets mmlu ceval gsm8k
```

来源：[swift_integration.md](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/swift_integration.md) · [llm_full_stack.md](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/llm_full_stack.md)

### 8.3 Arena 对战模式（`general_arena`）

```python
task_cfg = TaskConfig(
    model_id='Arena',
    datasets=['general_arena'],
    dataset_args={'general_arena': {'extra_params': {
        'models': [
            {'name': 'qwen2.5-0.5b',  'report_path': 'outputs/.../reports/qwen2.5-0.5b-instruct'},
            {'name': 'qwen2.5-7b',   'report_path': 'outputs/.../reports/qwen2.5-7b-instruct'},
            {'name': 'qwen2.5-72b',  'report_path': 'outputs/.../reports/qwen2.5-72b-instruct'},
        ],
        'baseline': 'qwen2.5-7b'  # 必填，是 models 之一
    }}},
    judge_model_args={...},  # 配置 judge LLM
)
```

输出：**Win Rate + Elo 分数 + 置信区间**（自动交换输出位置两轮比较去偏差）。

来源：[arena.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/arena.md)

### 8.4 推理性能压测（`evalscope perf`）

```bash
evalscope perf \
  --parallel 1 10 50 100 200 \
  --number 10 20 100 200 400 \
  --url http://127.0.0.1:8801/v1/chat/completions \
  --model qwen2.5-0.5b \
  --api openai
```

输出指标：TTFT / TPOT / ITL / 请求吞吐 / token 吞吐 / 平均延迟 / P99 延迟。

**与 vllm bench 数值一致**（来源 [vs_vllm_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/stress_test/vs_vllm_bench.md)）：

| 指标 | vLLM bench | EvalScope |
|---|---|---|
| Duration | 9.25 s | 9.50 s |
| Request throughput | 108.08 req/s | 105.31 req/s |
| Output token throughput | 10808.22 tok/s | 10530.7 tok/s |

**`--sla-auto-tune`**：自动二分搜索 `parallel` 或 `rate` 满足 SLA 约束（TTFT/TPOT/吞吐 JSON 配置）。

### 8.5 评测服务化（EvalScope Server Mode）

```bash
pip install 'evalscope[service]'
evalscope service --host 0.0.0.0 --port 9000 --outputs ./outputs
```

提供 RESTful API（Flask）：

| 端点 | 用途 |
|---|---|
| `GET /health` | 健康检查 |
| `POST /api/v1/eval` | 发起评测（必填 `model`, `datasets`, `api_url`） |
| `POST /api/v1/perf` | 发起压测（必填 `model`, `url`） |

WebUI 默认地址：`http://127.0.0.1:9000`。

来源：[service.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/service.md)

### 8.6 CI/CD 集成思路

文档**未提供官方 CI/CD 模板**。基于 service 模式可实现的典型工作流：

1. GitHub Actions 触发模型发版 → 启动 vLLM 服务
2. POST `/api/v1/eval` 调用 EvalScope
3. 解析 JSON 报告 → 写入 PR comment
4. 失败阻断 merge

### 8.7 断点续跑 / 容错

| 参数 | 用途 |
|---|---|
| `--use-cache <outputs/xxx>` | 跳过已完成样本 |
| `--rerun-review` | 与 `--use-cache` 配合，强制重跑评分步骤 |
| `--ignore-errors` | 跳过 OOM / 超时 / 服务崩溃样本 |
| `--no-test-connection` | 跳过连接测试直接压测 |
| `--warmup-num` | 预热请求数 |

### 8.8 主要坑点

1. **CLI 没有 `--num-gpus` / `--device` / `--api-type`**：多 GPU 通过 `--model-args device_map=auto`；远程通过 `--eval-type`
2. **`--limit` 不等于全量**：默认是 int（前 N）或 float（前 N%），容易误用
3. **代码类评测必须用沙箱**：`humaneval` / `live_code_bench` 默认本地执行不安全，需配置 sandbox（[sandbox.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/sandbox.md)）
4. **`--use-cache` 路径带时间戳**：`outputs/20230101_123456` 格式容易记错
5. **`--judge-model-args` 是 JSON 字符串** 不是 YAML，逗号不能有空格
6. **Arena 必须指定 baseline**：`baseline` 必须是 `models` 列表中的某一个
7. **`mt_bench` / `followbench` / `toxigen` 等历史数据集未提供**：用 `arena_hard` / `alpaca_eval` / `halueval` / `bfcl_v4` 替代
8. **`eval-type='custom'` 必须注册模型**：否则报 ModelAPI 找不到

### 8.9 关键命令速查

```bash
# 安装
pip install evalscope          # 基础
pip install 'evalscope[all]'   # 全功能
pip install 'evalscope[perf]'  # 压测
pip install 'evalscope[service]' # WebUI

# 评测
evalscope eval --model M --datasets D1 D2 --limit 10

# 远程 API
evalscope eval --model M --api-url URL --api-key KEY --eval-type openai_api --datasets D

# 压测
evalscope perf --parallel 1 10 50 100 --number 10 100 1000 --url URL --model M --api openai

# 可视化
evalscope service --outputs ./outputs
```

---

## 9. 来源链接

### 9.1 官方仓库 / 文档

- [EvalScope GitHub](https://github.com/modelscope/evalscope)
- [EvalScope PyPI](https://pypi.org/project/evalscope/)
- [EvalScope Releases](https://github.com/modelscope/evalscope/releases)
- [README](https://github.com/modelscope/evalscope/blob/main/README.md)
- [introduction.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/introduction.md)
- [installation.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/installation.md)
- [basic_usage.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/basic_usage.md)
- [parameters.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/parameters.md)
- [visualization.md](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/visualization.md)

### 9.2 工作流 / 高级

- [custom_dataset/llm.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/custom_dataset/llm.md)
- [custom_model.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/custom_model.md)
- [collection/schema.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/schema.md)
- [collection/sample.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/sample.md)
- [collection/evaluate.md](https://github.com/modelscope/evalscope/blob/main/docs/en/advanced_guides/collection/evaluate.md)

### 9.3 后端 / 评测类型

- [opencompass_backend.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/backend/opencompass_backend.md)
- [vlmevalkit_backend.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/backend/vlmevalkit_backend.md)
- [arena.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/arena.md)
- [service.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/service.md)
- [sandbox.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/sandbox.md)

### 9.4 压测

- [quick_start.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/stress_test/quick_start.md)
- [parameters.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/stress_test/parameters.md)
- [vs_vllm_bench.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/stress_test/vs_vllm_bench.md)
- [speed_benchmark.md](https://github.com/modelscope/evalscope/blob/main/docs/en/user_guides/stress_test/speed_benchmark.md)

### 9.5 Benchmark 详情

- [benchmarks 目录（共 191 个）](https://github.com/modelscope/evalscope/tree/main/docs/en/benchmarks)

### 9.6 Best Practice

- [Qwen3](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/qwen3.md)
- [Qwen3-VL](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/qwen3_vl.md)
- [Qwen3-Coder](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/qwen3_coder.md)
- [Qwen3-Omni](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/qwen3_omni.md)
- [swift_integration](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/swift_integration.md)
- [llm_full_stack](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/llm_full_stack.md)
- [deepseek_r1_distill](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/deepseek_r1_distill.md)
- [gpt_oss](https://github.com/modelscope/evalscope/blob/main/docs/en/best_practice/gpt_oss.md)

### 9.7 配套 demo

- [example/llm-demo/03_eval_frameworks](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/llm-demo/03_eval_frameworks/README.md) — OpenCompass + EvalScope 双框架 mock 演示