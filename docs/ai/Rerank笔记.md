---
title: Rerank 重排序笔记
description: 2026 年工业级重排序：4 种范式对比（Cross-encoder / Bi-encoder / Late Interaction / LLM-based）、主流模型（BGE v2/v3 / Cohere v3.5 / Jina m0 / Qwen3-Reranker / gte-rerank）、LLM-based 重排序（RankGPT / RankZephyr / PRP / RankT5）、工业级部署（TEI / vLLM / SGLang / TensorRT-LLM）、场景化选型决策树。
type: hub
---

# Rerank 重排序笔记

> **本文目的**：替换 `Rerank` 原笔记（原 旧稿 仅 38 行 + 一段 Claude 回答，缺主流模型，已删除）。覆盖 2026 年工业级 Rerank：4 种范式对比、5 大模型系列对比、LLM-based 重排序、工业部署、选型决策树。
> 配套笔记：[RAG工业方案笔记](./RAG工业方案笔记.md)、[Prompt工程笔记](./Prompt工程笔记.md)、[上下文工程与Agent笔记](/blog/上下文工程与Agent笔记)
> 配套 demo：[example/llm-demo/04_rag_evaluation](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/llm-demo/04_rag_evaluation)

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | 为什么需要重排序 | Recall vs Precision；向量召回的"浅层相似"局限 |
| 2 | 重排序范式对比 | 4 种范式（Bi-encoder / Cross-encoder / Late Interaction / LLM-based）的性能/精度矩阵 |
| 3 | 主流 Rerank 模型 | 5 大系列对比（BGE / Cohere / Jina / Qwen3-Reranker / gte-rerank）|
| 4 | LLM-based 重排序 | RankGPT / RankZephyr / PRP / RankT5；listwise / pairwise / setwise |
| 5 | 工业级部署 | TEI / vLLM / SGLang / ONNX Runtime / TensorRT-LLM 推理对比 |
| 6 | 选型决策树 | 按场景给推荐（中文 / 多语言 / 多模态 / 成本敏感 / 精度极致）|
| 7 | 来源链接 | 全部 GitHub/HF 链接按章节分组 |

---

## 1. 为什么需要重排序

### 1.1 向量召回的局限性

向量数据库用 cosine / L2 / dot product 等数学距离做相似度，本质是**浅层相似**：
- 基于预计算的 embedding，query 和 doc 在向量空间中的几何距离
- 缺乏细粒度的 query-doc 交互建模
- 难以捕捉复杂的语义匹配（同义词、反义词、蕴含、否定、条件、因果）

### 1.2 两阶段检索范式

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 第一阶段       │    │ 第二阶段       │    │ 输出           │
│ 向量召回       │ →  │ Rerank 精排   │ →  │ Top-N（5~10）  │
│ Top-K（50~100）│    │ Cross-encoder │    │ 喂给 LLM       │
└──────────────┘    └──────────────┘    └──────────────┘
```

| 阶段 | 目标 | 候选数 | 精度 | 速度 | 模型 |
|---|---|---|---|---|---|
| **召回（Recall）** | 不漏，宁可多 | 50~100 | 中 | 极快（ms 级）| Bi-encoder（Embedding 模型）|
| **精排（Precision）** | 准，去噪音 | 5~10 | 高 | 慢（10ms~1s）| Cross-encoder / LLM-based |

**经验数据**：重排序通常能将搜索结果的相关性提升 **10%~30%**（参考 Claude 原始回答 + Cohere 官方 benchmark）。

### 1.3 何时需要 Rerank

| 信号 | 是否需要 Rerank |
|---|---|
| Context Precision < 0.7 | ✅ 强烈需要 |
| Context Precision 0.7~0.9 | ⚠️ 看延迟预算 |
| Context Precision > 0.9 | ❌ 可以暂时不上，省成本 |
| 检索召回 100+ 候选但只用 top 5 | ✅ 强烈需要 |
| 检索召回 10 候选直接用 | ❌ 不需要 |
| 用户对结果敏感（客服 / 医疗 / 法律）| ✅ 必上 |
| 用户对结果容忍度高（闲聊 / 创意）| ⚠️ 看场景 |

---

## 2. 重排序范式对比

### 2.1 4 种范式

| 范式 | 原理 | 精度 | 速度 | 成本 | 代表模型 |
|---|---|---|---|---|---|
| **Bi-encoder**（双塔）| query 和 doc 独立编码 → cosine 相似度 | 低-中 | 极快 | 低 | BGE-M3 / 所有 Embedding 模型 |
| **Cross-encoder**（交叉）| query 和 doc 拼接输入 BERT → 直接输出相关性分数 | 高 | 慢（10~50ms/对）| 中 | BGE Reranker / Cohere / Jina / gte-rerank |
| **Late Interaction**（ColBERT 风格）| query 和 doc 独立编码但保留所有 token → MaxSim 聚合 | 中-高 | 中 | 中 | ColBERT / BGE-M3（多向量）|
| **LLM-based** | 用 LLM 本身做精排（listwise / pairwise / setwise）| 最高 | 极慢（1~5s/查询）| 高 | RankGPT / RankZephyr / PRP / GPT-4 / Claude |

### 2.2 性能/精度矩阵

```
精度 ↑
       │
   LLM-based ●
       │
 Cross-encoder ●
       │
Late Interaction ●
       │
   Bi-encoder ●
       │
       └────────────────→ 速度
```

### 2.3 各范式适用场景

| 范式 | 适用场景 | 不适用场景 |
|---|---|---|
| **Bi-encoder** | 海量候选召回（百万级）；第一阶段 | 精排（精度不够）|
| **Cross-encoder** | 主流精排方案；top 100 → top 5 | 海量候选（计算成本爆炸）|
| **Late Interaction** | 召回 + 精排都可；中等规模 | 工业级超大规模（存储压力）|
| **LLM-based** | 高价值 / 低 QPS；评测 / 仲裁 | 高 QPS 生产环境（成本 + 延迟）|

---

## 3. 主流 Rerank 模型

### 3.1 5 大系列对比

| 模型 | 机构 | HF / 仓库 | 上下文 | 多语言 | 多模态 | 部署方式 | 何时用 |
|---|---|---|---|---|---|---|---|
| **BGE Reranker v2-m3** | BAAI | [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 8K | ✅ 多语言 | ❌ | 本地 / TEI / vLLM | 个人知识库 + 中文生产首选 |
| **BGE Reranker v2-gemma** | BAAI | [BAAI/bge-reranker-v2-gemma](https://huggingface.co/BAAI/bge-reranker-v2-gemma) | 8K | ✅ 多语言 | ❌ | 本地 | 高精度需求 |
| **BGE Reranker v2-minicpm-layerwise** | BAAI | [BAAI/bge-reranker-v2-minicpm-layerwise](https://huggingface.co/BAAI/bge-reranker-v2-minicpm-layerwise) | 8K | ✅ 多语言 | ❌ | 本地 | 可调节层数平衡精度/速度 |
| **Cohere Rerank v3.5** | Cohere | API | — | ✅ 100+ 语言 | ❌ | 商业 API | SaaS 场景，开箱即用 |
| **Jina Reranker m0** | Jina | [jinaai/jina-reranker-m0](https://huggingface.co/jinaai/jina-reranker-m0) | — | ✅ 多语言 | ✅ 图文 | 本地 / API | 多模态重排序 |
| **Qwen3-Reranker** | 阿里 | QwenLM 系列 | 32K | ✅ 多语言 | ❌ | 本地 / vLLM | 长文本 + 多语言 |
| **gte-rerank** | 阿里 | [Alibaba-NLP/gte-multilingual-reranker-base](https://huggingface.co/Alibaba-NLP/gte-multilingual-reranker-base) | 32K | ✅ 多语言 | ❌ | 本地 | MTEB 榜单前列 |
| **Pinecone Rerank** | Pinecone | API | — | ✅ 多语言 | ❌ | 商业 API | Pinecone 生态 |

### 3.2 BGE Reranker v2 全系对比

BAAI [FlagEmbedding v1.4.0](https://github.com/FlagOpen/FlagEmbedding)（2026-04-22）统一收录：

| 子模型 | Backbone | 参数量 | 速度 | 精度 | 适用场景 |
|---|---|---|---|---|---|
| **bge-reranker-v2-m3** | XLM-RoBERTa | 568M | 快 | 高 | 通用首选 |
| **bge-reranker-v2-gemma** | Gemma-2-9B | 9B | 慢 | 极高 | 精度极致 |
| **bge-reranker-v2-minicpm-layerwise** | MiniCPM | 2.4B | 可调（6/12/24/36 层）| 高 | 平衡精度/速度 |

### 3.3 选型速记

| 场景 | 推荐 | 理由 |
|---|---|---|
| **中文生产环境** | BGE Reranker v2-m3 | 中文 SOTA + 本地可跑 + 多语言 |
| **多语言 + 长文本** | gte-multilingual-reranker / Qwen3-Reranker | 32K 上下文 + 多语言 |
| **多模态（图文）** | Jina Reranker m0 | 原生多模态 |
| **SaaS 快速集成** | Cohere Rerank v3.5 | 开箱即用，按 query 计费 |
| **精度极致（不在乎成本）** | BGE Reranker v2-gemma | 9B 参数 |
| **平衡精度/速度** | BGE Reranker v2-minicpm-layerwise（调节层数）| 灵活 |
| **个人知识库 / Demo** | BGE Reranker v2-m3 | CPU 可跑 |

---

## 4. LLM-based 重排序

### 4.1 三种范式

| 范式 | Prompt 示例 | 复杂度 | 适用场景 |
|---|---|---|---|
| **Pointwise** | "Q: ... D: ... 相关吗？输出 0/1" | O(N) 次 LLM 调用 | 最简单但精度最低 |
| **Pairwise** | "Q: ... A: ... B: ... 哪个更相关？" | O(N²) 次 LLM 调用 | 精度高，常用于 Arena |
| **Listwise** | "Q: ... [A, B, C, D, E] 按相关性排序" | O(1) 次 LLM 调用 | 效率高，但 prompt 长 |

### 4.2 主流 LLM-based 重排序模型

| 模型 | 类型 | 代表论文 | 仓库 |
|---|---|---|---|
| **RankGPT** | listwise，用 GPT-4 sliding window | [Sun et al., 2023](https://arxiv.org/abs/2312.02713) | [RUCAIBox/RankGPT](https://github.com/RUCAIBox/RankGPT) |
| **RankZephyr** | listwise，用 Zephyr 微调 | [Pradeep et al., 2023](https://arxiv.org/abs/2312.02724) | [castorini/rank_llm](https://github.com/castorini/rank_llm) |
| **PRP**（Pairwise Ranking Prompting）| pairwise | [Qin et al., 2024](https://arxiv.org/abs/2402.13444) | [valohai/prp](https://github.com/valohai/prp) |
| **RankT5** | listwise，用 T5 微调 | [Zhuang et al., 2023](https://arxiv.org/abs/2310.08324) | [google-research/rank_llm](https://github.com/google-research/rank_llm) |
| **Setwise** | setwise（RankGPT 改进）| [Hwang et al., 2024](https://arxiv.org/abs/2404.03807) | 同 RankGPT |

### 4.3 何时用 LLM-based

| 场景 | 推荐 |
|---|---|
| **候选 ≤ 20 个** | ✅ listwise（RankGPT）|
| **候选 20~50 个** | ✅ setwise / sliding window |
| **候选 50~100 个** | ⚠️ 先 Cross-encoder 粗排到 20 再 LLM 精排 |
| **高价值（法律 / 医疗 / 金融）** | ✅ GPT-4 / Claude Opus 4.8 精排 |
| **实时高 QPS** | ❌ 用 Cross-encoder |
| **多模型对比评测** | ✅ LLM-based 更公平 |

### 4.4 成本分析

假设每条 query 20 候选、用 Claude Sonnet 5：

| 范式 | LLM 调用次数 | 输入 token | 输出 token | 成本估算 |
|---|---|---|---|---|
| Pointwise | 20 | 20 × 200 = 4K | 20 × 5 = 100 | ~$0.025 |
| Pairwise | 190（C(20,2)）| 190 × 400 = 76K | 190 × 5 = 950 | ~$0.45 |
| Listwise | 1 | 5K | 200 | ~$0.025 |

**结论**：listwise + sliding window 是性价比最高的 LLM-based 方案。

---

## 5. 工业级部署

### 5.1 推理引擎对比

| 引擎 | 仓库 | 适配模型 | 性能 | 何时用 |
|---|---|---|---|---|
| **TEI**（Text Embeddings Inference）| [huggingface/text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference) | BGE / gte-rerank / Jina 等 BERT 类 | 高吞吐、CPU/GPU 均可 | HuggingFace 生态首选 |
| **vLLM** | [vllm-project/vllm](https://github.com/vllm-project/vllm) | Cross-encoder / LLM-based | GPU 高吞吐 | 已有 vLLM 部署栈 |
| **SGLang** | [sgl-project/sglang](https://github.com/sgl-project/sglang) | Cross-encoder / LLM-based | GPU 高吞吐 + RadixAttention | 复杂调用 + LLM-based |
| **ONNX Runtime** | [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) | 任何 ONNX 模型 | 通用 | CPU / 边缘部署 |
| **TensorRT-LLM** | [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | NVIDIA 优化 | 极致 GPU 性能 | 生产级 NVIDIA GPU |
| **Infinity** | [microsoft/infinity](https://github.com/microsoft/infinity) | 任何 ONNX 模型 | 高吞吐 C++ | 微软 ONNX 生态 |

### 5.2 部署模式

**模式 1：独立 Rerank 服务**

```
Vector DB → recall top 100 → Rerank Service（TEI/vLLM） → top 5 → LLM
```

- 优点：解耦、可独立扩展
- 缺点：多一跳网络

**模式 2：与应用一起部署**

```
Application → 调用 rerank.py 函数 → 同进程 Rerank
```

- 优点：低延迟
- 缺点：绑死部署

**模式 3：Serverless API**

```
Application → Cohere / Jina / Pinecone API → 返回 rerank 结果
```

- 优点：零运维
- 缺点：数据出境 + 按量计费 + 延迟不稳定

### 5.3 性能优化

- **批量请求**：Cross-encoder 适合 batch（32~64 条/批），单条延迟高
- **异步并发**：用 asyncio + aiohttp 同时处理多个 query
- **预排序**：先按 embedding 距离粗排，去掉明显不相关的，再喂 rerank
- **缓存**：同一 query 的 rerank 结果可缓存（注意 doc 变化时失效）
- **量化**：INT8 量化对 Cross-encoder 影响 < 2%，生产环境推荐

---

## 6. 选型决策树

### 6.1 按场景推荐

| 场景 | 推荐组合 | 理由 |
|---|---|---|
| **个人知识库 / 中文为主** | BGE Reranker v2-m3（本地 TEI）| 中文 SOTA + CPU/GPU 均可跑 |
| **多语言（中英欧）** | gte-multilingual-reranker-base / BGE v2-m3 | 32K 上下文 + 多语言 |
| **多模态（图文混排）** | Jina Reranker m0 | 原生多模态 |
| **成本敏感 / 高 QPS** | BGE Reranker v2-m3 + TEI + INT8 量化 | 极致性价比 |
| **精度极致 / 低 QPS** | BGE Reranker v2-gemma + LLM-based 双精排 | 9B 模型 + GPT-4 仲裁 |
| **SaaS 快速集成（不想自建）** | Cohere Rerank v3.5 / Pinecone Rerank | 开箱即用，按 query 计费 |
| **长文本（10K+ context）** | gte-multilingual-reranker / Qwen3-Reranker | 32K 上下文 |
| **学术评测 / 高价值** | RankGPT（GPT-4 listwise sliding window）| LLM-as-judge 公平性 |

### 6.2 调参建议

| 参数 | 经验值 | 备注 |
|---|---|---|
| **Recall top_K** | 50~100 | 太小漏召回，太大 Rerank 慢 |
| **Rerank output top_N** | 5~10 | 喂给 LLM 的最终候选 |
| **batch_size** | 32~64 | 视 GPU 显存调整 |
| **max_length** | 512 | BGE 默认 512，可调到 8K |
| **Rerank 触发阈值** | Context Precision < 0.9 时启用 | 动态启用省成本 |

### 6.3 常见误区

- ❌ **Rerank 一定能提精度**：候选召回太差时，Rerank 也救不回来
- ❌ **Rerank 模型越大越好**：9B 模型延迟高、显存贵，多数场景 568M 的 BGE v2-m3 就够
- ❌ **必须用 LLM-based**：高 QPS 生产环境不现实，Cross-encoder 是事实标准
- ❌ **忽略延迟**：Rerank 是检索链路中的额外一跳，端到端延迟必须监控
- ❌ **Rerank 后直接用**：仍要 prompt LLM "只根据上下文回答，不要编造"

---

## 7. 来源链接（按章节分组）

### 7.1 Rerank 模型
- [FlagEmbedding (BAAI)](https://github.com/FlagOpen/FlagEmbedding)
- [BGE Reranker v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [BGE Reranker v2-gemma](https://huggingface.co/BAAI/bge-reranker-v2-gemma)
- [BGE Reranker v2-minicpm-layerwise](https://huggingface.co/BAAI/bge-reranker-v2-minicpm-layerwise)
- [gte-multilingual-reranker-base](https://huggingface.co/Alibaba-NLP/gte-multilingual-reranker-base)
- [Jina Reranker m0](https://huggingface.co/jinaai/jina-reranker-m0)
- [Cohere Rerank v3.5](https://cohere.com/rerank)
- [Pinecone Rerank](https://www.pinecone.io/rerank/)

### 7.2 LLM-based 重排序
- [RankGPT 论文](https://arxiv.org/abs/2312.02713)
- [RankGPT 仓库](https://github.com/RUCAIBox/RankGPT)
- [RankZephyr 论文](https://arxiv.org/abs/2312.02724)
- [PRP 论文](https://arxiv.org/abs/2402.13444)
- [RankT5 论文](https://arxiv.org/abs/2310.08324)
- [Setwise 论文](https://arxiv.org/abs/2404.03807)
- [rank_llm 仓库（Castorini）](https://github.com/castorini/rank_llm)

### 7.3 部署引擎
- [TEI (HuggingFace)](https://github.com/huggingface/text-embeddings-inference)
- [vLLM](https://github.com/vllm-project/vllm)
- [SGLang](https://github.com/sgl-project/sglang)
- [ONNX Runtime](https://github.com/microsoft/onnxruntime)
- [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- [Infinity (Microsoft)](https://github.com/microsoft/infinity)