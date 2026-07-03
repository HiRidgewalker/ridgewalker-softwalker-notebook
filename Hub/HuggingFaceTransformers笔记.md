# HuggingFace Transformers 笔记

> 原 `文档/HuggingFace Transformers.md`（仅 2 行一个链接）的重新整理版本，从零补充了 Transformers 库的核心概念、快速开始、常用模式、Hub 生态。原笔记保留在原位置供回溯。

## 一、定位

**HuggingFace Transformers** 是目前最主流的预训练模型 Python 库，由 HuggingFace 公司维护，GitHub 30k+ 星。提供了：

- 加载/使用/微调数千种预训练 Transformer 模型（BERT、GPT、T5、LLaMA、Qwen 等）
- 统一的 API 抽象（pipeline / AutoModel / AutoTokenizer）
- 与 PyTorch / TensorFlow / JAX 无缝集成
- 与 [[Ollama笔记]] 等本地运行时互补（Transformers 偏开发 / 微调，Ollama 偏本地推理服务）

## 二、核心能力

| 模块 | 作用 |
| --- | --- |
| **pipeline** | 一行代码做推理（文本生成、分类、问答、翻译、图像分类等几十种任务） |
| **AutoModel / AutoTokenizer** | 根据模型名自动加载对应架构的模型和分词器 |
| **Trainer** | 高级训练循环封装，省去手写训练代码 |
| **Datasets** | 数据集加载与处理库 |
| **Accelerate** | 分布式训练 / 混合精度 |
| **Hub** | 模型 / 数据集 / Demo 的托管与版本管理（hub.huggingface.co） |
| **PEFT** | LoRA 等参数高效微调 |
| **trl** | SFT / DPO / RLHF 训练 |

## 三、快速开始

### 3.1 最简推理：`pipeline`

```python
from transformers import pipeline

# 情感分析（默认下载 distilbert-base-uncased-finetuned-sst-2-english）
classifier = pipeline("sentiment-analysis")
result = classifier("I love using HuggingFace Transformers!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

### 3.2 显式加载模型

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

inputs = tokenizer("Hello, my name is", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0]))
```

### 3.3 常用任务对应 pipeline

| 任务 | pipeline 任务名 | 默认模型举例 |
| --- | --- | --- |
| 文本分类 | `"sentiment-analysis"` / `"text-classification"` | distilbert-sst2 |
| 文本生成 | `"text-generation"` | gpt2 |
| 问答（抽取式） | `"question-answering"` | distilbert-base-uncased-distilled-squad |
| 翻译 | `"translation_en_to_zh"` | Helsinki-NLP/opus-mt-en-zh |
| 摘要 | `"summarization"` | sshleifer/distilbart-cnn-12-6 |
| 命名实体识别 | `"ner"` | dslim/bert-base-NER |
| 图像分类 | `"image-classification"` | google/vit-base-patch16-224 |
| 语音识别 | `"automatic-speech-recognition"` | openai/whisper-base |
| 文本嵌入 | `"feature-extraction"` | sentence-transformers/all-MiniLM-L6-v2 |

## 四、与周边工具的关系

| 工具 | 定位 |
| --- | --- |
| **Transformers** | 训练 + 推理全流程，主打开发 |
| **Ollama**（[[Ollama笔记]]） | 本地一键跑开源模型，主打推理 |
| **VLLM** | 高吞吐推理服务 |
| **PEFT / LoRA** | 参数高效微调 |
| **trl** | SFT / DPO / RLHF 训练 |
| **sentence-transformers** | 专门做文本嵌入 |
| **datasets** | 数据集加载与处理 |

> 经验法则：**研究 / 微调选 Transformers，生产部署选 VLLM，本地快速体验选 Ollama。**

## 五、资源

- [Transformers 快速入门（中文）](https://transformers.run/)
- 官方文档：<https://huggingface.co/docs/transformers>
- 模型 Hub：<https://huggingface.co/models>
- 数据集 Hub：<https://huggingface.co/datasets>
- GitHub：<https://github.com/huggingface/transformers>

## 六、相关笔记

- 本地模型运行：[[Ollama笔记]]
- 高吞吐推理：[[VLLM]]
- LLM 基础：[[LLM]]
- AI 编程助手：[[ClaudeCode笔记]]

## 七、配套 demo

[workspace/ai-assistant/huggingface-pipeline-demo/pipeline_demo.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/ai-assistant/huggingface-pipeline-demo/pipeline_demo.py) —— pipeline 最小推理示例（情感分析 + 文本生成）。