# LLM Demo

演示 [[Hub/01_大语言模型笔记]] 中可执行代码部分。

## Demo 列表

| 目录 | 内容 | 模型依赖 |
|---|---|---|
| [01_tokenization_and_generation](./01_tokenization_and_generation) | Tokenizer 切分、next token prediction、KV cache、Sampling 策略 | GPT-2 (~500MB) |

## 安装与运行

```bash
# 装依赖（统一 venv）
uv pip install --python workspace/.venv/bin/python -r workspace/llm-demo/01_tokenization_and_generation/requirements.txt

# 跑 demo（首次会下载 GPT-2）
workspace/.venv/bin/python workspace/llm-demo/01_tokenization_and_generation/main.py
```

## 对应笔记

- [[Hub/01_大语言模型笔记]] — LLM 架构、训练流程、推理部署
- [[Hub/02_PyTorch笔记]] — PyTorch 基础（demo 底层依赖）
- [[Hub/03_深度学习环境安装笔记]] — CUDA / PyTorch 环境配置