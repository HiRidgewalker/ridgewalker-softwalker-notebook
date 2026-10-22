---
title: OpenCompass 评测框架笔记
description: 上海 AI Lab / 书生·浦语出品的大模型评测框架：架构、本地 / 远程模型测试、60+ 内置数据集、自定义数据集、评测指标、生产环境特性。覆盖 v0.5.3。
type: hub
---

# OpenCompass 评测框架笔记

> **本文目的**：补全 `目录.md` 中评测章节的 OpenCompass 部分。覆盖框架定位、本地与远程模型评测流程、内置数据集清单、自定义数据集方式、评测指标、生产特性。
> 对比框架笔记：[[EvalScope笔记]]、[[LLM评测框架对比笔记]]
> 原 旧稿 仅 27 行外部链接 + 两个 CLI 片段，重构后已迁移至此。

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | OpenCompass 概述 | 项目背景、版本、四件套生态 |
| 2 | 架构核心组件 | Config / Datasets / Models / Runner / Evaluator / Visualizer 六大模块 |
| 3 | 本地模型测试 | HF Transformers / LMDeploy / vLLM 三种加速后端 + 多机多卡 + 命令行 |
| 4 | 远程 API 模型测试 | OpenAI 兼容 API + 自定义 API + 限速 + 完整 yaml |
| 5 | 内置数据集清单 | 60+ 数据集按 11 大类整理 |
| 6 | 自定义数据集 | 数据集目录 + BaseDataset 继承 + 完整 JSONL 示例 |
| 7 | 评测指标 | 客观指标 vs LLM-as-Judge 边界 + 子指标细分 + 报告格式 |
| 8 | 生产环境特性 | Slurm / DLC 分布式、断点续跑、容器化、与 vLLM / SGLang 集成 |
| 9 | 来源链接 | 全部参考链接按章节分组 |

---

## 1. OpenCompass 概述

[OpenCompass](https://github.com/open-compass/opencompass) 是上海人工智能实验室 / 书生·浦语团队开源的大模型评测框架，目标是「**科学、开放、可复现**」的模型评测。

| 项目信息 | 数值 | 来源 |
|---|---|---|
| 当前主版本 | v0.5.3（2025-06-29） | [GitHub Releases](https://github.com/open-compass/opencompass/releases) |
| GitHub Star | 7.1k | [GitHub 主页](https://github.com/open-compass/opencompass) |
| 许可证 | Apache-2.0 | 仓库 LICENSE |
| 维护者 | 上海 AI Lab / 书生·浦语团队 | [OpenCompass 官网](https://opencompass.org.cn/) |
| 官方文档 | https://opencompass.readthedocs.io/ | readthedocs |

### 四件套生态

OpenCompass 不是一个孤立的 CLI，而是一整套评测基础设施：

| 组件 | 用途 | 链接 |
|---|---|---|
| **OpenCompass**（核心库） | 数据集 / 模型 / 评测 pipeline | https://github.com/open-compass/opencompass |
| **CompassKit** | 评测算法与子模块集合（数据集、Prompt、Metric） | 仓库内 `opencompass/` 子目录 |
| **CompassHub** | 数据集与评测任务协作发布平台 | https://hub.opencompass.org.cn/ |
| **CompassRank** | 模型排行榜 | https://rank.opencompass.org.cn/ |
| **CompassAcademic** | v0.5.0 新增学术评测套件 | [v0.5.0 Release Notes](https://github.com/open-compass/opencompass/releases) |

主流使用方：

- **InternLM 系列**发版评测均使用 OpenCompass
- **Meta Llama 系列**官方推荐 OpenCompass 作为第三方评测
- **国内学术榜单**（如 C-Eval 榜单、SuperBench）由 OpenCompass 团队维护

---

## 2. 架构核心组件

OpenCompass 采用 Config-driven 设计，所有行为由 yaml / python 配置文件驱动：

```
┌─────────────────────────────────────────────────┐
│                OpenCompass 架构                  │
├─────────────────────────────────────────────────┤
│  Config (YAML/Python)                           │
│    ├─ Models (HF / LMDeploy / vLLM / API)       │
│    ├─ Datasets (MMLU / C-Eval / GSM8K / ...)   │
│    └─ Evaluators                                │
├─────────────────────────────────────────────────┤
│  Runner (分布式 / Slurm / DLC)                  │
│    ├─ Inferencer (本地推理 / API 调用)         │
│    └─ Evaluator (指标计算)                      │
├─────────────────────────────────────────────────┤
│  输出：summary_*.csv / 报告 Markdown / 可视化    │
└─────────────────────────────────────────────────┘
```

六大核心模块：

| 模块 | 职责 |
|---|---|
| **Config 系统** | YAML / Python 配置文件，描述模型 + 数据集 + 评测方式的组合 |
| **Datasets** | 内置数据集注册表，每个数据集有 Reader + Inferencer + Evaluator 三件套 |
| **Models** | 模型配置，支持 HF / LMDeploy / vLLM / OpenAI API / 自定义 backend |
| **Runner** | 调度执行，支持单机多卡、Slurm 集群、DLC 分布式 |
| **Evaluator** | 指标计算（Acc / F1 / BLEU / ROUGE / PPL / LLM-as-Judge） |
| **Visualizer** | 结果可视化（雷达图、柱状图、对比表） |

支持的后端：

| Backend | 加速比（相对 HF） | 适用 |
|---|---|---|
| HF Transformers | 1×（基线） | 教学、小模型、需看 hidden state |
| LMDeploy | 2.2× | InternLM 生态、量化场景 |
| vLLM | 3.1× | 主流本地部署，吞吐高 |
| OpenAI API | 网络决定 | 远程闭源模型 |
| 自定义 | — | 自建推理服务 |

来源：[OpenCompass 仓库 README](https://github.com/open-compass/opencompass) · [官方文档 user_guides/evaluation.html](https://doc.opencompass.org.cn/zh_CN/user_guides/evaluation.html)

---

## 3. 本地模型测试

### 3.1 HF Transformers 后端（基线）

```python
# config_hf.py
from mmengine.config import read_base

with read_base():
    from .models.hf_internlm2_7b import models
    from .datasets.mmlu.mmlu_5shot_ppl import mmlu_datasets

# 完整工作目录结构
# configs/
# ├── models/hf_internlm2_7b.py    # 模型定义
# ├── datasets/mmlu/mmlu_5shot_ppl.py  # 数据集定义
# └── eval_internlm2.py             # 评测入口
```

```bash
# 命令行执行
python run.py configs/eval_internlm2.py -w outputs/internlm2_mmlu
```

### 3.2 LMDeploy 后端（加速）

```python
# model config 里加 run_mode='lmdeploy' 即可
models = [
    dict(
        type='lmdeploy'，
        abbr='internlm2-7b-lmdeploy'，
        model_path='internlm/internlm2-chat-7b'，
        engine_config=dict(max_batch_size=128, tp=1)，
        gen_config=dict(max_new_tokens=512, top_k=1)，
    )
]
```

来源：[OpenCompass LMDeploy Backend 文档](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/lmdeploy.md)

### 3.3 vLLM 后端（最高吞吐）

```python
# run_mode='vllm'
models = [
    dict(
        type='vllm'，
        abbr='qwen2-7b-vllm'，
        model_path='Qwen/Qwen2-7B-Instruct'，
        engine_config=dict(tensor_parallel_size=2, max_num_seqs=256)，
        gen_config=dict(max_new_tokens=1024, temperature=0.0)，
    )
]
```

来源：[OpenCompass vLLM Backend 文档](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/vllm.md)

### 3.4 命令行 `run.py` 完整参数

```bash
python run.py CONFIG [--work-dir OUT] [options]
```

| 参数 | 默认 | 说明 |
|---|---|---|
| `--models` / `-m` | 全部 | 模型名（逗号分隔） |
| `--datasets` / `-d` | 全部 | 数据集名（逗号分隔） |
| `--work-dir` / `-w` | `./outputs/default` | 输出目录 |
| `-r` / `--reuse` | False | 断点续跑 |
| `--max-num-workers` | 1 | 并发 worker 数（API 评测必调） |
| `--max-num-workers-per-gpu` | 1 | 每 GPU 并发 |
| `--hf-num-gpus` | 1 | HF 模型占用的 GPU 数 |
| `--slurm` | False | 启用 Slurm 集群调度 |
| `--dlc` | False | 启用阿里云 DLC 调度 |
| `--debug` | False | debug 模式（每个 dataset 只跑前 N 条） |
| `--dry-run` | False | 只生成配置文件，不实际跑 |
| `-p` / `--partition` | — | Slurm 分区名 |
| `--accuracy` | False | 仅看 accuracy 列 |
| `--map-fn` | — | 结果聚合函数 |

### 3.5 多机多卡分布式

```bash
# Slurm 集群
python run.py configs/eval_llama3_70b.py \
  --slurm --partition big -w outputs/llama3_slurm

# 阿里云 DLC（分布式云）
python run.py configs/eval_qwen2_72b.py \
  --dlc --dlc-config-path dlc.json -w outputs/qwen2_dlc
```

### 3.6 完整可复制的工作流

```bash
# 1) 安装
conda create -n opencompass python=3.10 -y
conda activate opencompass
git clone https://github.com/open-compass/opencompass.git
cd opencompass
pip install -e .

# 2) 准备模型（下载到本地）
mkdir -p ./model
huggingface-cli download Qwen/Qwen2-7B-Instruct --local-dir ./model/qwen2-7b

# 3) 写配置（见 §3.3）
# 4) 跑评测（debug 模式先试）
python run.py configs/eval_qwen2_7b.py -w outputs/qwen2_test --debug
# 5) 全量跑
python run.py configs/eval_qwen2_7b.py -w outputs/qwen2_full
```

---

## 4. 远程 API 模型测试

### 4.1 OpenAI 兼容 API

OpenCompass 提供现成的 OpenAI / GPT-4 / Claude 配置文件：

```python
# configs/models/gpt_4o.py
api_meta_template = dict(
    round=[
        dict(role='HUMAN', api_role='user'),
        dict(role='BOT', api_role='assistant', generate=True),
    ],
)

models = [
    dict(
        type='openai',
        abbr='gpt-4o',
        model='gpt-4o-2024-08-06',
        key=os.environ['OPENAI_API_KEY'],
        api_base='https://api.openai.com/v1',
        meta_template=api_meta_template,
        max_seq_len=8192,
    )
]
```

### 4.2 自定义 API 模型（HuggingFace Inference / 自建网关）

```python
models = [
    dict(
        type='openai',
        abbr='my-inference-endpoint',
        model='meta-llama/Meta-Llama-3-8B-Instruct',
        key=os.environ['HF_TOKEN'],
        api_base='https://xxxx.us-east-1.aws.endpoints.huggingface.cloud/v1',
        meta_template=api_meta_template,
    )
]
```

### 4.3 限速与并发

远程 API 必须调 `--max-num-workers`，否则会被服务端限流：

```bash
# 8 个并发 worker
python run.py configs/eval_gpt4.py -w outputs/gpt4 --max-num-workers 8

# 极保守：1 个 worker + 自定义 retry
python run.py configs/eval_claude.py -w outputs/claude --max-num-workers 1
```

### 4.4 流式 vs 非流式

OpenCompass 默认非流式（`stream=False`）。如需流式以统计 TTFT，需自定义 Inferencer 或改用 EvalScope（见 [[EvalScope笔记]] §5）。

---

## 5. 内置数据集清单

OpenCompass 内置 **60+ 数据集**，按 11 大类组织。完整列表见 [官方数据集索引](https://github.com/open-compass/opencompass/blob/main/docs/en/datasets.md)。

### 5.1 学科知识（通用）

| 数据集 | 任务类型 | 评测方式 | 默认 prompt 版本 |
|---|---|---|---|
| [MMLU](https://github.com/open-compass/opencompass/blob/main/configs/datasets/mmlu/mmlu_5shot_ppl.py) | 57 学科 MCQ | 5-shot PPL | 5-shot |
| [C-Eval](https://github.com/open-compass/opencompass/blob/main/configs/datasets/ceval/ceval_5shot_ppl.py) | 52 学科中文 MCQ | 5-shot PPL | 5-shot |
| [C-MMLU](https://github.com/open-compass/opencompass/blob/main/configs/datasets/cmmlu/cmmlu_5shot_ppl.py) | 67 学科中文 MCQ | 5-shot PPL | 5-shot |
| [AGIEval](https://github.com/open-compass/opencompass/blob/main/configs/datasets/agieval/agieval_gen.py) | 高考 / 律师资格等 | gen | 0-shot |
| [ARC](https://github.com/open-compass/opencompass/blob/main/configs/datasets/arc/arc.py) | 常识推理 MCQ | 0-shot PPL | 0-shot |
| [HellaSwag](https://github.com/open-compass/opencompass/blob/main/configs/datasets/hellaswag/hellaswag.py) | 常识续写 | 0-shot PPL | 0-shot |

### 5.2 中文能力

| 数据集 | 任务类型 | 评测方式 |
|---|---|---|
| CLUE_AFQMC | 文本相似度 | gen |
| CLUE_CMRC | 阅读理解 | gen |
| CLUE_C3 | 多项选择 | gen |
| CLUE_CHID | 完形填空 | gen |
| FewCLUE | 少样本文本分类 | gen |
| LCSTS | 摘要 | gen |
| XCOPA | 多语言常识 | gen |

### 5.3 推理 / 数学

| 数据集 | 任务类型 | 评测方式 |
|---|---|---|
| [GSM8K](https://github.com/open-compass/opencompass/blob/main/configs/datasets/gsm8k/gsm8k_gen.py) | 小学数学 | 4-shot CoT gen |
| MATH | 高中数学 12.5K | 4-shot CoT gen |
| BBH | 23 个推理任务 | 3-shot CoT gen |
| DROP | 离散推理 | gen |
| TheoremQA | 定理问答 | gen |
| [CMath](https://github.com/open-compass/opencompass/blob/main/configs/datasets/cmath/cmath_gen.py) | 中文数学 | gen |

### 5.4 代码

| 数据集 | 任务类型 | 评测方式 |
|---|---|---|
| HumanEval | 164 题 Python | 0-shot gen + 沙箱 |
| MBPP | Python 函数补全 | 3-shot gen |
| HumanEvalPlus | 增强测试用例 | gen + 沙箱 |

> 注：LiveCodeBench 等持续更新数据集需通过自定义数据集方式接入。

### 5.5 多模态（需配合 VLMEvalKit）

OpenCompass 本身**纯文本**，多模态需通过外部后端：

| 数据集 | 来源 |
|---|---|
| MMBench | 第三方 |
| MMMU | 第三方 |
| MathVista | 第三方 |
| OCRBench | 第三方 |

> 强烈建议多模态评测直接用 [[EvalScope笔记]]（Native 后端开箱支持 40+ VLM benchmark）。

### 5.6 指令遵循

| 数据集 | 评测方式 |
|---|---|
| IFEval | 25 类可验证指令，0-shot |
| MT-Bench | 80 题 × 2 轮，GPT-4 judge |
| AlpacaEval | 805 题，GPT-4 judge |
| FollowBench | 5 级难度，GPT-4 judge |

### 5.7 长文本

| 数据集 | 评测方式 |
|---|---|
| LongBench | 6 任务类别 |
| L-Eval | 多领域长文本 |
| LEval | 多领域长文本 |

### 5.8 知识 / 工具 / Agent

| 数据集 | 评测方式 |
|---|---|
| TriviaQA | 闭卷 QA |
| NaturalQuestions | 开放域 QA |
| ToolBench | 工具调用 |
| AgentBench | Agent 多任务 |

> 完整 60+ 数据集列表见 [configs/datasets/](https://github.com/open-compass/opencompass/tree/main/configs/datasets) 目录树。

---

## 6. 自定义数据集

### 6.1 数据集目录结构

OpenCompass 要求每个数据集都注册在 `configs/datasets/<dataset_name>/`，至少包含：

```
configs/datasets/my_custom/
├── __init__.py
├── my_custom.py           # 主配置
├── my_custom_gen_db509b.py  # 生成式评测 prompt 版本
└── my_custom_ppl_00b348.py  # 判别式评测 prompt 版本
```

### 6.2 完整示例：自定义 JSONL 数据集（5 条数学应用题）

**Step 1：准备 JSONL 文件** `data/my_custom.jsonl`

```jsonl
{"id": 1, "question": "小明有 5 个苹果，吃了 2 个，还剩几个？", "answer": "3"}
{"id": 2, "question": "一本书 200 页，第一天看了 25%，第二天看了 1/4，剩多少页？", "answer": "100"}
{"id": 3, "question": "一个长方形周长 36cm，长是宽的 2 倍，面积多少？", "answer": "72"}
{"id": 4, "question": "鸡兔同笼，共 35 头 94 脚，问鸡几只？", "answer": "23"}
{"id": 5, "question": "火车 3 小时行 240km，每小时行多少km？", "answer": "80"}
```

**Step 2：写数据集类** `configs/datasets/my_custom/my_custom.py`

```python
from opencompass.datasets import BaseDataset
from opencompass.registry import LOAD_DATASET
from typing import List, Dict

@LOAD_DATASET.register_module()
class MyCustomDataset(BaseDataset):

    @staticmethod
    def load(path: str) -> List[Dict]:
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                data.append({
                    'question': item['question'],
                    'answer': item['answer'],
                })
        return data
```

**Step 3：写 Reader + Inferencer + Evaluator** `configs/datasets/my_custom/my_custom_gen.py`

```python
from opencompass.datasets import build_dataset
from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.openicl.icl_evaluator import AccEvaluator
from mmengine.config import read_base

my_custom_reader_cfg = dict(
    input_columns=['question'],
    output_column='answer',
)

my_custom_infer_cfg = dict(
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(round=[
            dict(role='HUMAN', prompt='请解答下面的数学题：\n{question}'),
            dict(role='BOT', prompt='{answer}'),
        ]),
    ),
    retriever=dict(type=ZeroRetriever),
    inferencer=dict(type=GenInferencer, max_out_len=512),
)

my_custom_eval_cfg = dict(
    evaluator=dict(type=AccEvaluator),
)

my_custom_datasets = [
    dict(
        type='MyCustomDataset',
        path='data/my_custom.jsonl',
        reader_cfg=my_custom_reader_cfg,
        infer_cfg=my_custom_infer_cfg,
        eval_cfg=my_custom_eval_cfg,
    )
]
```

**Step 4：跑**

```bash
python run.py configs/eval_my_custom.py -d my_custom -w outputs/my_custom_test
```

来源：[OpenCompass 自定义数据集文档](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/customize_dataset.md)

### 6.3 评测方式：gen vs ppl

| 方式 | 含义 | 适用 |
|---|---|---|
| `gen` | 模型生成完整答案，提取后比对 | 问答 / 生成 / 数学 |
| `ppl`（perplexity） | 算每个选项的 PPL，取最低 | 选择题（MMLU 形式） |

---

## 7. 评测指标

### 7.1 客观指标 vs LLM-as-Judge 边界

| 维度 | 客观指标 | LLM-as-Judge |
|---|---|---|
| 适用 | 唯一正确答案 | 开放式对话 / 写作 |
| 优点 | 可复现、抗偏差 | 可拓展到开放任务 |
| 风险 | 拼写变体敏感 | Position / Verbosity / Self-enhancement bias |
| 推荐 | Acc / F1 / BLEU / ROUGE | 用 strong LLM (GPT-4 / Claude) 双盲 + 交换位置 |

### 7.2 内置 metric 列表

| Metric | 适用 | 评测器 |
|---|---|---|
| Accuracy | 选择题、抽取题 | `AccEvaluator` |
| Precision / Recall / F1 | 分类 | `F1Evaluator` |
| BLEU-{1..4} | QA / 翻译 / 生成 | `BLEUEvaluator` |
| ROUGE-{1,2,L} | 摘要 | `ROUGEEvaluator` |
| CIDEr | 图像描述 | `CIDErEvaluator` |
| chrF | 字符级 F | `ChrFEvaluator` |
| PPL | 选择题 loglikelihood | `PPLInferencer`（特殊） |
| LLM-as-Judge | 开放式 | `LLMJudgeEvaluator`（需配 judge LLM） |

来源：[OpenCompass Evaluator 列表](https://github.com/open-compass/opencompass/tree/main/opencompass/openicl/icl_evaluator)

### 7.3 子指标细分

MMLU 4 大类 57 学科、C-Eval 4 类 52 学科、C-MMLU 67 学科、GSM8K 按难易分桶——OpenCompass 自动按子集分桶输出。

### 7.4 报告格式

| 格式 | 路径 / 命令 |
|---|---|
| CSV | `outputs/<exp>/summary_*.csv` |
| Markdown | `outputs/<exp>/report.md` |
| 雷达图 / 柱状图 | `opencompass.visualize` 或 `tools/viz_multi_model.py` |
| CompassRank 排行 | 上传 JSON 到 [rank.opencompass.org.cn](https://rank.opencompass.org.cn/) |

来源：[OpenCompass 可视化文档](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/visualization.md)

---

## 8. 生产环境特性

### 8.1 分布式并行

| 模式 | 适用 |
|---|---|
| 单机多卡 `--hf-num-gpus` | 实验室 |
| Slurm `--slurm --partition` | 集群 |
| DLC `--dlc` | 阿里云分布式 |

### 8.2 断点续跑

```bash
# 中途中断后，加 -r 复用已有推理结果
python run.py configs/eval_llama3.py -w outputs/llama3 -r
```

### 8.3 结果对比

```bash
# review.py 把多个实验结果并排对比
python tools/review.py outputs/exp1 outputs/exp2 outputs/exp3
```

### 8.4 容器化

```dockerfile
FROM nvcr.io/nvidia/pytorch:23.10-py3
RUN pip install opencompass
COPY configs /example/configs
COPY data /example/data
WORKDIR /workspace
ENTRYPOINT ["python", "run.py", "configs/eval.py", "-w", "/outputs"]
```

### 8.5 与 vLLM / SGLang 部署服务集成

两种接入路径：

| 路径 | 步骤 |
|---|---|
| **本地 backend** | vLLM backend（`run_mode='vllm'`）直接跑，OpenCompass 启动 vLLM 实例 |
| **远程 API** | 先 `vllm serve <model>` 起服务，再用 `type='openai'` 接进来 |

> SGLang 同理，但需用 `type='openai'` + `api_base='http://localhost:30000/v1'` 远程接入。

### 8.6 缓存机制

- dataset 缓存：`~/.cache/opencompass/`
- inference 结果缓存：`-r` 触发复用
- `--use-cache <dir>`：手动指定缓存路径

---

## 9. 来源链接

### 9.1 官方仓库 / 文档

- [OpenCompass GitHub](https://github.com/open-compass/opencompass)
- [OpenCompass Releases](https://github.com/open-compass/opencompass/releases)
- [OpenCompass 官网](https://opencompass.org.cn/)
- [OpenCompass 中文文档](https://doc.opencompass.org.cn/)
- [OpenCompass 数据集索引](https://github.com/open-compass/opencompass/blob/main/docs/en/datasets.md)
- [OpenCompass 评测流程文档](https://doc.opencompass.org.cn/zh_CN/user_guides/evaluation.html)

### 9.2 Backend 文档

- [vLLM Backend](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/vllm.md)
- [LMDeploy Backend](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/lmdeploy.md)
- [OpenAI Backend](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/openai_api.md)

### 9.3 高级用法

- [自定义数据集](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/customize_dataset.md)
- [LLM-as-Judge 配置](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/judge.md)
- [可视化](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/visualization.md)
- [结果对比](https://github.com/open-compass/opencompass/blob/main/docs/en/user_guides/result_review.md)

### 9.4 数据集 Card（抽样）

- [MMLU](https://github.com/open-compass/opencompass/blob/main/configs/datasets/mmlu/mmlu_5shot_ppl.py)
- [C-Eval](https://github.com/open-compass/opencompass/blob/main/configs/datasets/ceval/ceval_5shot_ppl.py)
- [C-MMLU](https://github.com/open-compass/opencompass/blob/main/configs/datasets/cmmlu/cmmlu_5shot_ppl.py)
- [GSM8K](https://github.com/open-compass/opencompass/blob/main/configs/datasets/gsm8k/gsm8k_gen.py)
- [HumanEval](https://github.com/open-compass/opencompass/blob/main/configs/datasets/humaneval/humaneval_gen.py)
- [ARC](https://github.com/open-compass/opencompass/blob/main/configs/datasets/arc/arc.py)
- [HellaSwag](https://github.com/open-compass/opencompass/blob/main/configs/datasets/hellaswag/hellaswag.py)
- [AGIEval](https://github.com/open-compass/opencompass/blob/main/configs/datasets/agieval/agieval_gen.py)
- [CMath](https://github.com/open-compass/opencompass/blob/main/configs/datasets/cmath/cmath_gen.py)

### 9.5 配套 demo

- [[example/llm-demo/03_eval_frameworks]] — OpenCompass + EvalScope 双框架 mock 演示