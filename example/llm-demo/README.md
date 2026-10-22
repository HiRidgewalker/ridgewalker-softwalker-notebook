# LLM Demo

演示 [[I_大语言模型笔记]] 中可执行代码部分。

## Demo 列表

| 目录 | 内容 | 模型依赖 |
|---|---|---|
| [01_tokenization_and_generation](./01_tokenization_and_generation) | Tokenizer 切分、next token prediction、KV cache、Sampling 策略 | GPT-2 (~500MB) |
| [02_inference_serving](./02_inference_serving) | OpenAI SDK 客户端 + Prometheus `/metrics` 解析 + `vllm bench serve` 风格 benchmark 模拟 | 不需要（mock 自动降级，可切到本地 vLLM/SGLang） |
| [03_eval_frameworks](./03_eval_frameworks) | OpenCompass + EvalScope 双框架 Mock 演示：自定义 JSONL + 本地 mock 模型 + 远程 mock API + 数据集选型 + 报告解读 | 不需要（纯 mock） |
| [04_rag_evaluation](./04_rag_evaluation) | Mock RAG pipeline + RAGAS 4 大核心指标（context_precision/recall/faithfulness/answer_relevancy）+ 阈值调优；可选 live 模式接真实 ragas + OpenAI | 不需要（mock 模式）；可选 live 模式 |

## 安装与运行

```bash
# 装依赖（统一 venv）
uv pip install --python .venv/bin/python -r example/llm-demo/01_tokenization_and_generation/requirements.txt
uv pip install --python .venv/bin/python -r example/llm-demo/02_inference_serving/requirements.txt

# 跑 demo（首次会下载 GPT-2）
.venv/bin/python example/llm-demo/01_tokenization_and_generation/main.py

# 跑 demo（无需服务，mock 模式即可；或加环境变量切到本地 vLLM/SGLang）
.venv/bin/python example/llm-demo/02_inference_serving/main.py

# 跑评测框架 demo（无需任何依赖，标准库即可）
python3 example/llm-demo/03_eval_frameworks/main.py
# 或指定单个 demo：
python3 example/llm-demo/03_eval_frameworks/main.py --demo custom_dataset

# 跑 RAG 评测 demo（mock 模式，无需任何依赖）
python3 example/llm-demo/04_rag_evaluation/main.py
# 或指定单个 demo：
python3 example/llm-demo/04_rag_evaluation/main.py --demo pipeline
# 切到 live 模式（需要装 ragas + datasets + openai + OPENAI_API_KEY）：
# uv pip install --python .venv/bin/python ragas datasets openai
# export EVAL_MODE=live OPENAI_API_KEY=sk-xxx
```

## 对应笔记

- [[I_大语言模型笔记]] — LLM 架构、训练流程、推理部署
- [[II_推理部署笔记]] — vLLM / SGLang 生产环境的显存/并发/指标/日志/选型对比
- [[OpenCompass笔记]] — OpenCompass v0.5.3 评测框架（架构 / 本地 / 远程 / 60+ 数据集 / 自定义 / 指标）
- [[EvalScope笔记]] — EvalScope v1.8.1 评测框架（四大后端 / 191 benchmark / CollectionSchema / Arena / 压测）
- [[LLM评测框架对比笔记]] — 选型决策树 + 10 维度差异表 + 7 步标准生产流程 + 8 项报告指标
- [[RAG工业方案笔记]] — RAG 范式、9 大框架、文档解析、Embedding、向量库、评测体系
- [[Rerank笔记]] — 4 种重排序范式、5 大模型系列、LLM-based 重排序、工业部署
- [[Prompt工程笔记]] — Anthropic 原则、DSPy 编译器范式、结构化输出、模板管理
- [[上下文工程与Agent笔记]] — Context Engineering 四大策略、Manus 经验、Agent 框架、Memory 系统、MCP
- [[02_PyTorch笔记]] — PyTorch 基础（demo 底层依赖）
- [[II_深度学习环境安装笔记]] — CUDA / PyTorch 环境配置