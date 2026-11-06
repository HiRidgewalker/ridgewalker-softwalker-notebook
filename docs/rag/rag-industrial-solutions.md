---
title: RAG 工业方案笔记
description: 2026 年最新 RAG 工业级方案选型：范式演进（Naive → Advanced → Modular + Agentic RAG）、9 大开源框架（RAGFlow / LightRAG / GraphRAG / Dify / FastGPT / MaxKB / LangChain / LlamaIndex / Haystack）、文档解析、Embedding、向量库、评测体系（RAGAS）、完整工业链路、场景化选型决策树。
sidebar_position: 1
---

# RAG 工业方案笔记

> **本文目的**：替换 `RAG` 原笔记（原 旧稿 只有 64 行文章链接，严重过时，已删除）。覆盖 2026 年工业级 RAG 全栈：范式演进、开源框架对比、文档解析、Embedding、向量数据库、评测体系、完整工业链路、场景化选型决策树。
> 配套笔记：[Prompt工程笔记](../prompt-engineering/prompt-engineering.md)、[Rerank笔记](rerank.md)、[上下文工程与Agent笔记](/blog/上下文工程与Agent笔记)
> 配套 demo：[example/llm-demo/04_rag_evaluation](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/llm-demo/04_rag_evaluation)

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | RAG 范式演进 | Naive → Advanced → Modular 三阶段；Agentic RAG 四子流派 |
| 2 | 工业级 RAG 引擎 | 9 大开源框架对比（GitHub / 版本 / star / 定位 / 何时用）|
| 3 | 文档解析 | PDF/EPUB/Office → 结构化的工业级工具链 |
| 4 | Embedding 模型 | BGE / Qwen3-Embedding / bce / OpenAI / Cohere / Voyage / Jina 对比 |
| 5 | 向量数据库 | Qdrant / Milvus / Weaviate / pgvector / ES / Chroma 选型 |
| 6 | RAG 评测体系 | RAGAS 4 大核心指标 + 5 大观测/评测工具 |
| 7 | 完整工业链路 | 数据 → 解析 → 切片 → Embedding → 索引 → 检索 → 重排 → 生成 → 评测 |
| 8 | 选型决策树 | 按场景给推荐（个人 / 企业 / 多模态 / Agent / 国内合规 / 学术）|
| 9 | 来源链接 | 全部 GitHub 链接按章节分组 |

---

## 1. RAG 范式演进

### 1.1 三阶段演进（Gao et al. Survey）

| 阶段 | 时间 | 特征 | 局限 |
|---|---|---|---|
| **Naive RAG** | 2023 前 | 索引 → 检索 → 生成三步走 | 召回不准、生成幻觉、无后处理 |
| **Advanced RAG** | 2023-2024 | Pre-retrieval（query rewrite / HyDE）+ Post-retrieval（rerank / compression） | 模块割裂、缺乏全局视角 |
| **Modular RAG** | 2024-2026 | 模块化重组 + Agent 编排 + 自适应路由 | 复杂度高、需要更强的工程能力 |

参考：[Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)（Gao et al., 2023，最新版本持续更新至 2025）。

### 1.2 Agentic RAG 四子流派（2024 论文）

| 流派 | 核心思路 | 代表论文 | 落地成本 |
|---|---|---|---|
| **Self-RAG** | token 级 reflection + critique tokens，按需触发检索 | [Asai et al., ICLR 2024](https://arxiv.org/abs/2310.11511) | 高（要 fine-tune critic token）|
| **CRAG / Corrective-RAG** | retrieval evaluator + web search fallback；低置信度时触发重检索 | [Yan et al., 2024](https://arxiv.org/abs/2401.15884) | 中 |
| **Adaptive-RAG** | 根据 query complexity 选择：单跳检索 / 多步检索 / 直接生成 | [Jeong et al., 2024](https://arxiv.org/abs/2403.14403) | 中 |
| **Agentic Tool-Use RAG** | Agent 自主决定调用 RAG / SQL / Web / API / 计算器 | LangGraph / LlamaIndex / Manus | 低-中（2026 主流）|

**2026 落地建议**：CRAG + Adaptive-RAG 思路 + Agent 工具调用是工业级默认；Self-RAG 因 fine-tune 成本高，多数场景下不必上。

---

## 2. 工业级 RAG 引擎对比（9 大框架）

### 2.1 全景对比表

| 框架 | 仓库 | 最新版本 | 发布时间 | Stars | Fork | 核心定位 |
|---|---|---|---|---|---|---|
| **RAGFlow** | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | v0.26.2 | 2026 活跃 | 84.1k | 9.8k | 深文档理解的 RAG 引擎 + Agent 融合 |
| **LightRAG** | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | lightrag-hku (PyPI) | 活跃 | 37.2k | 5.2k | 轻量级 KG-RAG，五种查询模式，多模态 |
| **GraphRAG** | [microsoft/graphrag](https://github.com/microsoft/graphrag) | v3.1.0 | 2026-05-28 | 34.1k | 3.6k | 模块化图基 RAG 数据管线 |
| **Dify** | [langgenius/dify](https://github.com/langgenius/dify) | v1.10.0 | 2025-05-20（持续小版本） | 147k | 23.2k | LLM 应用生产平台（含 RAG + Agent + Workflow）|
| **FastGPT** | [labring/FastGPT](https://github.com/labring/FastGPT) | v4.15.0 | 2026-06-30 | 28.8k | 7.2k | 知识库 + 可视化 AI 工作流（国内活跃）|
| **MaxKB** | [1Panel-dev/MaxKB](https://github.com/1Panel-dev/MaxKB) | v2.10.2-lts | 2026-06-18 | 21.6k | 2.9k | 企业级 Agent + RAG + MCP |
| **LangChain** | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | core 1.4.8 | 2026-06-18 | 141k | 23.4k | Agent 工程平台（已演化为通用框架）|
| **LlamaIndex** | [run-llama/llama_index](https://github.com/run-llama/llama_index) | v0.14.23 | 2026-06-24 | 50.6k | 7.7k | 文档 Agent + OCR 平台（含 LlamaParse 商业版）|
| **Haystack** | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | v2.30.2 | 2026-06-18 | 25.8k | 2.9k | 生产级 LLM 编排框架（pipeline + agent）|

### 2.2 各框架"何时用"短评

| 框架 | 适用场景 | 不适用场景 | 一句话推荐 |
|---|---|---|---|
| **RAGFlow** | 复杂 PDF（论文 / 财报 / 合同）+ 需要深文档理解（表格 / 公式） | 轻量场景、纯文本 | "深文档 RAG 引擎 + Agent 融合"国内最稳的选项 |
| **LightRAG** | 需要 Graph + 向量混合检索；EMNLP 2025 论文加持 | 不需要图检索的传统 RAG | "5 种查询模式 + 图基 RAG"的轻量首选 |
| **GraphRAG** | 全局摘要类问题（"这批文档讲了哪些主题？"）；社区/警务/研究 | 单点查找类问题（"第 3 章第 2 节讲什么"）| 全局型 / 关系型问答的图基方案 |
| **Dify** | 需要可视化编排 Workflow + 多模型切换 + 企业内快速落地 | 强定制、高性能 | "全功能 LLM 应用平台"，国内企业私有化首选 |
| **FastGPT** | 国内中小团队，需要开箱即用的知识库 | 强定制 | "可视化 AI 工作流"国内中小团队首选 |
| **MaxKB** | 企业内 IM 集成（飞书 / 钉钉 / 企微）+ MCP | 终端用户产品 | "1Panel 生态 + Agent + RAG"的开箱即用方案 |
| **LangChain** | 复杂 Agent / 多工具调用 / 需要 LangSmith 配套 | 纯检索任务（链式调用太重）| "Agent 编排首选"，但要小心 1.x 后的 API 变化 |
| **LlamaIndex** | 文档 Agent / 数据连接器丰富 / LlamaParse OCR | 不需要 OCR 的纯文本场景 | "文档 Agent + OCR"最强，但商业 LlamaParse 已迁移 llama-cloud |
| **Haystack** | 生产级 pipeline 编排 / 需要 REST 服务化部署 | 快速原型 | "Pipeline-first"的稳健生产选择 |

### 2.3 选型速记

- **国内中小团队 / 开箱即用**：Dify > FastGPT > MaxKB
- **深文档 / PDF 论文 / 财报**：RAGFlow > LightRAG
- **全局型 / 关系型问答**：GraphRAG > LightRAG
- **复杂 Agent / 多工具**：LangChain + LangGraph > LlamaIndex
- **生产级 Pipeline / 服务化**：Haystack > 自研
- **学术研究 / 复现论文**：LightRAG（EMNLP 2025）/ GraphRAG（微软）

---

## 3. 文档解析（PDF / Office → 结构化）

### 3.1 工具对比

| 工具 | 仓库 | 最新版本 | 发布时间 | Stars | 适用场景 |
|---|---|---|---|---|---|
| **Docling** | [docling-project/docling](https://github.com/docling-project/docling) | v2.108.0 | 2026-07-01 | 62.5k | 多格式 + VLM + MCP server（IBM DS4SD，LF AI 托管）|
| **Marker** | [datalab-to/marker](https://github.com/datalab-to/marker) | 3.4 | 2026-06-18 | 37k | 中英文 PDF/EPUB/PPT；Hybrid Mode + LLM 增强 |
| **MinerU** | [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | 持续发布 | 2026 活跃 | >10k | 学术论文 / 复杂版面（已被 LightRAG 集成）|
| **MarkitDown** | [microsoft/markitdown](https://github.com/microsoft/markitdown) | 活跃 | 持续 | — | Office/PDF → MD（轻量、微软出品）|
| **olmOCR** | [allenai/olmocr](https://github.com/allenai/olmocr) | v0.4.0 | 2025-10-21 | — | RL 微调的 OLMo-based OCR（学术派）|
| **LlamaParse** | [run-llama/llama_cloud_services](https://github.com/run-llama/llama_cloud_services) | 已迁移 llama-cloud | 维护至 2026-05-01 | — | ⚠️ 商业云 OCR，新版走 `llama-cloud` 包 |
| **unstructured.io** | [Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured) | 持续发布 | 持续 | 15.1k | 通用 ingest + chunk + embed 流水线 |

### 3.2 推荐组合

| 场景 | 推荐组合 |
|---|---|
| **英文论文 / 学术** | Marker（PDF→MD）+ MinerU（复杂版面）|
| **国内企业文档（合同/财报）** | Docling（IBM，LF AI 托管）+ VLM 增强 |
| **Office 全家桶** | MarkitDown（微软，开箱即用）|
| **多模态 PDF（图文混排）** | Docling（VLM 集成）+ olmOCR（RL 增强）|
| **快速原型** | MarkitDown / Unstructured |
| **商业云 OCR** | LlamaParse（注意已迁移 llama-cloud）|

### 3.3 关键工程点

- **版面分析**：表格 / 公式 / 图片需要单独处理，不要当纯文本
- **OCR 后处理**：扫描件必须先 OCR 再切片，否则 chunk 质量极差
- **格式保留**：Markdown / JSON / HTML 三选一，Markdown 是事实标准
- **chunk 边界**：跨页/跨章节的段落要在解析阶段就合并，不要在切片阶段再处理

---

## 4. Embedding 模型（2026 SOTA）

### 4.1 主流模型对比

| 模型 | 机构 | HF / 仓库 | 维度 | 上下文 | 多语言 | 何时用 |
|---|---|---|---|---|---|---|
| **BGE-M3** | BAAI | [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | 1024 | 8K | ✅ 中英 + 100 语言 | 个人知识库首选；dense+sparse+multi-vec 三态 |
| **BGE-large-zh-v1.5** | BAAI | [BAAI/bge-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh-v1.5) | 1024 | 512 | ❌ 中文专用 | 纯中文场景、轻量 |
| **Qwen3-Embedding-8B** | 阿里 | [QwenLM/Qwen3-Embedding](https://huggingface.co/QwenLM/Qwen3-Embedding-8B) | 可配置 | 32K | ✅ 多语言 SOTA | MTEB multilingual #1（2025-06），高精度需求 |
| **bce-embedding-base_v1** | 网易 | FlagEmbedding v1.3.4 收录 | 768 | 512 | ✅ 中英 | 国内生产环境，已被多家大厂采用 |
| **text-embedding-3-large** | OpenAI | API | 3072 | 8K | ✅ 多语言 | 商业 API 基线；按 token 计费 |
| **embed-multilingual-v3** | Cohere | API | 1024 | 512 | ✅ 100+ 语言 | 商业 SaaS 场景 |
| **voyage-3-large** | Voyage | API | 1024 | 32K | ✅ 多语言 | 长文本检索 SOTA |
| **jina-embeddings-v4** | Jina | [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 可配置 | 8K | ✅ 多语言 | 多模态（图文）检索 |
| **text-embedding-v5** | Jina | API | — | 8K | ✅ 多语言 | Jina 最新 API 版 |
| **gte-Qwen2-7B-instruct** | 阿里 | [Alibaba-NLP/gte-Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct) | 3576 | 32K | ✅ 多语言 | MTEB 榜单常年前列 |

⚠️ **Conan-embedding（商汤）** 仓库链接 404，可能已被取代。

### 4.2 FlagEmbedding 生态

BAAI 的 [FlagEmbedding v1.4.0](https://github.com/FlagOpen/FlagEmbedding)（2026-04-22 发布）是中文 Embedding 的事实标准仓库，统一了：
- BGE 系列（embedding + reranker）
- bce-embedding（网易）
- LLM Embedder（多任务）
- BGE-Reasoner-preview（新增）

### 4.3 选型速记

| 场景 | 推荐 |
|---|---|
| **个人知识库** | BGE-M3（中文 + 8K 上下文 + 三态检索）|
| **生产 RAG 服务** | bce-embedding-base_v1（国内稳定） / Qwen3-Embedding-8B（精度极致）|
| **多语言 SOTA** | Qwen3-Embedding-8B（MTEB #1）|
| **长文本（32K+）** | voyage-3-large / gte-Qwen2-7B-instruct |
| **多模态（图文）** | jina-embeddings-v4 |
| **API 快速集成** | OpenAI text-embedding-3-large（基线）/ Cohere / Voyage |
| **极低成本（CPU 推理）** | bge-small-zh-v1.5 / bge-small-en-v1.5 |

### 4.4 工程要点

- **归一化**：cosine 相似度需要向量归一化；dot product 不需要
- **batch 编码**：大文档集必须 batch（32~128 条/批），单条编码效率极低
- **量化**：INT8 量化对召回率影响 < 1%，生产环境推荐
- **混合检索**：dense + sparse（BM25）+ multi-vec 三路召回 + RRF 融合是 2026 主流

---

## 5. 向量数据库

### 5.1 全景对比

| 数据库 | 仓库 | 最新版本 | 发布时间 | Stars | 核心场景 |
|---|---|---|---|---|---|
| **Qdrant** | [qdrant/qdrant](https://github.com/qdrant/qdrant) | v1.18.2 | 2026-06-04 | 32.9k | Rust + 强过滤 + 混合检索（RRF/DBSF）+ Edge |
| **Milvus** | [milvus-io/milvus](https://github.com/milvus-io/milvus) | 2.6+（2.5.x LTS） | 持续 | 45k+ | 分布式万亿级，Woodpecker WAL，Lite/Standalone/Distributed |
| **Weaviate** | [weaviate/weaviate](https://github.com/weaviate/weaviate) | v1.38.2 | 2026-06-25 | — | 模块化向量 + 知识图谱混合 |
| **pgvector** | [pgvector/pgvector](https://github.com/pgvector/pgvector) | 无 tag | 持续 | — | Postgres 扩展，省运维；已有 PG 团队首选 |
| **Elasticsearch** | [elastic/elasticsearch](https://github.com/elastic/elasticsearch) | v9.4.3 | 2026-06-30 | — | 已有 ES 栈时复用 dense_vector |
| **Chroma** | [chroma-core/chroma](https://github.com/chroma-core/chroma) | 1.5.9 | 2026-05-05 | — | Demo / 轻量本地 |
| **Vearch** | [vearch/vearch](https://github.com/vearch/vearch) | v3.5.9 | 2025-02-04 | — | ⚠️ **更新停滞**（一年半无新版），不推荐新项目 |

### 5.2 选型速记

| 场景 | 推荐 | 理由 |
|---|---|---|
| **个人知识库 / 中小团队** | Qdrant | Rust 性能强，单二进制部署，过滤能力一流 |
| **已有 PG 团队** | pgvector | 零运维成本，复用 PG 备份 / 主从 |
| **已有 ES 团队** | Elasticsearch dense_vector | 复用现有集群 |
| **企业级万亿规模** | Milvus | 分布式 + Woodpecker WAL + 多语言 SDK |
| **需要混合（图+向量）** | Weaviate | 模块化设计，原生支持 hybrid search |
| **Demo / 原型** | Chroma | 轻量、API 简单 |
| **边缘 / 端侧** | Qdrant Edge | Rust 嵌入式，< 50MB 二进制 |

### 5.3 工程要点

- **混合检索**：dense + BM25 + RRF 融合是 2026 标配（Qdrant / Milvus / Weaviate 都原生支持）
- **过滤**：metadata 过滤（如时间范围 / 文档类型）必须在向量检索前完成
- **分片**：亿级以上需要分片；Qdrant 推荐按 tenant 分片；Milvus 用 partition key
- **备份**：向量数据库的备份与关系数据库不同，需要单独设计（snapshot + 重建索引）
- **量化**：SQ（Scalar Quantization）/ PQ（Product Quantization）/ Binary 各有取舍

---

## 6. RAG 评测体系

### 6.1 评测工具对比

| 工具 | 仓库 | 最新版本 | 发布时间 | Stars | 定位 |
|---|---|---|---|---|---|
| **RAGAS** | [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | v0.4.3 | 2026-01-13 | 14.6k | **RAG 评测事实标准**；4 大核心指标 |
| **DeepEval** | [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | v4.0.5 | 2026-05-28 | 16.6k | Agent-native 评测，本地 TUI trace 检查 |
| **TruLens** | [truera/trulens](https://github.com/truera/trulens) | 2.8.1 | 2026-05-14 | 3.4k | 评测 + GEPA 遗传 prompt 优化 |
| **Phoenix** | [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) | v17.15.0 | 2026-07-01 | — | 可观测性 + LLM-as-judge |
| **LangSmith SDK** | [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk) | v0.9.5 | 2026-07-01 | 951 | LangChain 生态 tracing/eval |

### 6.2 RAGAS 4 大核心指标

| 指标 | 含义 | 范围 | 何时关注 |
|---|---|---|---|
| **Context Precision** | 检索到的 context 中相关条目的占比 | 0-1 | 检索器质量差（噪音多）时 |
| **Context Recall** | ground-truth 答案能被检索 context 覆盖的比例 | 0-1 | 召回不足、漏检时 |
| **Faithfulness** | 答案中的事实是否都能在 context 中找到依据 | 0-1 | 幻觉严重、编造内容时 |
| **Answer Relevancy** | 答案与问题的相关程度（不看正确性） | 0-1 | 答非所问、跑题时 |

**2026 实战经验**：
- 4 个指标都要看，单独看任何一个都会失真
- Faithfulness < 0.8 必须修（幻觉风险高）
- Context Recall < 0.7 要先扩检索（top_k / 加 HyDE / 换 embedding）
- Context Precision 低 + Recall 高 = 检索器太松，加 rerank
- Context Precision 高 + Recall 低 = 检索器太严，加多路召回

### 6.3 评测体系选择

| 场景 | 推荐 |
|---|---|
| **RAG 系统评测（事实标准）** | RAGAS |
| **Agent / 多步推理评测** | DeepEval（Agent-native）|
| **Prompt + RAG 联合优化** | TruLens（GEPA 算法）|
| **生产可观测 + 评测** | Phoenix（自托管）或 LangSmith（云托管）|
| **LangChain 生态全套** | LangSmith（trace + eval + prompt 注册）|
| **多模型 + 多场景对比** | RAGAS + Phoenix 双跑 |

### 6.4 测试集设计

- **领域内**：从业务真实日志采样 100~500 条问答对
- **领域外**：用 LLM 生成对抗样本（无关问题 / 陷阱问题 / 越狱 prompt）
- **黄金集**：人工标注 50~100 条高质量答案作 ground truth
- **回归集**：每次发版必须跑同一份测试集，防止性能回退

---

## 7. 完整工业链路

### 7.1 9 步全链路

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1. 数据源 │ → │ 2. 文档解析│ → │ 3. 切片   │ → │ 4. Embedding │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                       ↓
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 9. 评测   │ ← │ 8. 生成   │ ← │ 7. 重排序 │ ← │ 6. 检索   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                       ↑                              ↑
                       │              ┌──────────┐    │
                       └──────────────│ 5. 索引  │────┘
                                      └──────────┘
```

### 7.2 各步骤推荐工具与关键参数

| 步骤 | 推荐工具 | 关键参数 |
|---|---|---|
| **1. 数据源** | 文件 / S3 / OSS / Notion / 飞书 / Confluence | 增量同步、版本控制、去重 |
| **2. 文档解析** | Docling / Marker / MinerU | 表格识别、公式 OCR、版面分析 |
| **3. 切片** | LangChain / LlamaIndex / 自研（Recursive / Semantic / LLM-based）| chunk_size 512~1024、overlap 10%~20% |
| **4. Embedding** | BGE-M3 / Qwen3-Embedding / bce | batch_size 32~128、归一化 |
| **5. 索引** | Qdrant / Milvus / pgvector | HNSW ef_construction 200、M 16 |
| **6. 检索** | dense + BM25 + RRF | top_k 20~100、加 metadata 过滤 |
| **7. 重排序** | BGE-reranker-v2-m3 / Cohere v3.5 | 取 top 5~10，详见 [Rerank笔记](rerank.md) |
| **8. 生成** | Claude Sonnet 5 / GPT / Qwen3 | 温度 0、引用标注、拒绝回答机制 |
| **9. 评测** | RAGAS / DeepEval | 4 大指标 + 回归集 + A/B |

### 7.3 关键工程原则

- **每步可观测**：每一步的输入输出都要 trace（LangSmith / Phoenix）
- **每步可降级**：Embedding 服务挂了要能 fallback 到 BM25；LLM 服务挂了要能切备用模型
- **每步可缓存**：Embedding 结果按 (model, text_hash) 缓存；Rerank 结果按 (model, query, doc_id) 缓存
- **每步可回滚**：向量索引要支持快照回滚；prompt 版本要可回退

---

## 8. 选型决策树

### 8.1 按场景推荐

| 场景 | 推荐组合 | 理由 |
|---|---|---|
| **个人知识库（Obsidian / Notion）** | BGE-M3 + Qdrant + BGE-reranker-v2-m3 + RAGFlow 或 LightRAG | 轻量、本地可跑、不依赖云 |
| **企业文档库（合同/财报/手册）** | Docling + bce-embedding + Milvus + BGE-reranker + RAGFlow | 深文档理解、企业级分布式 |
| **多模态（图文混排）** | Docling（VLM）+ jina-embeddings-v4 + Qdrant + jina-reranker-m0 | 原生多模态支持 |
| **Agent 融合 RAG** | LangChain + LangGraph + Qdrant + RAGAS | Agent 编排 + 多工具调用 |
| **国内合规（数据不出境）** | bce-embedding + MaxKB + 达梦 / OceanBase + 本地 BGE-reranker | 全栈国内合规 |
| **学术研究（复现论文）** | LightRAG（EMNLP 2025）/ GraphRAG + LlamaIndex + RAGAS | 论文复现、生态完整 |
| **快速原型 / Demo** | Dify / FastGPT + Chroma + OpenAI Embedding | 5 分钟搭起来 |
| **企业 IM 集成（飞书/钉钉）** | MaxKB + Dify + pgvector | 开箱即用 IM 集成 |

### 8.2 常见误区

- ❌ **Embedding 越新越好**：Qwen3-Embedding-8B 不一定比 BGE-M3 在你的场景好，必须 A/B 测试
- ❌ **向量库越大越好**：个人知识库用 Chroma / Qdrant 就够，Milvus 是给万亿级准备的
- ❌ **Rerank 一定要上**：如果 Context Precision 已经 > 0.9，可以暂时不 rerank 省成本
- ❌ **Embedding 一定要 GPU 推理**：BGE-M3 / bce 都能 CPU 跑，吞吐量要求不高时不必上 GPU
- ❌ **Chunk 越小越好**：512 token 是经验值；要看下游 LLM 的 context window 和检索粒度

---

## 9. 来源链接（按章节分组）

### 9.1 RAG 范式
- [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997)
- [Self-RAG (ICLR 2024)](https://arxiv.org/abs/2310.11511)
- [Corrective RAG (CRAG)](https://arxiv.org/abs/2401.15884)
- [Adaptive-RAG](https://arxiv.org/abs/2403.14403)

### 9.2 RAG 框架
- [RAGFlow](https://github.com/infiniflow/ragflow)
- [LightRAG](https://github.com/HKUDS/LightRAG)
- [GraphRAG](https://github.com/microsoft/graphrag)
- [Dify](https://github.com/langgenius/dify)
- [FastGPT](https://github.com/labring/FastGPT)
- [MaxKB](https://github.com/1Panel-dev/MaxKB)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LlamaIndex](https://github.com/run-llama/llama_index)
- [Haystack](https://github.com/deepset-ai/haystack)

### 9.3 文档解析
- [Docling](https://github.com/docling-project/docling)
- [Marker](https://github.com/datalab-to/marker)
- [MinerU](https://github.com/opendatalab/MinerU)
- [MarkitDown](https://github.com/microsoft/markitdown)
- [olmOCR](https://github.com/allenai/olmocr)
- [LlamaParse（已迁移 llama-cloud）](https://github.com/run-llama/llama_cloud_services)
- [Unstructured](https://github.com/Unstructured-IO/unstructured)

### 9.4 Embedding
- [FlagEmbedding (BAAI)](https://github.com/FlagOpen/FlagEmbedding)
- [BGE-M3](https://huggingface.co/BAAI/bge-m3)
- [BGE-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh-v1.5)
- [Qwen3-Embedding-8B](https://huggingface.co/QwenLM/Qwen3-Embedding-8B)
- [gte-Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct)
- [jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4)

### 9.5 向量数据库
- [Qdrant](https://github.com/qdrant/qdrant)
- [Milvus](https://github.com/milvus-io/milvus)
- [Weaviate](https://github.com/weaviate/weaviate)
- [pgvector](https://github.com/pgvector/pgvector)
- [Elasticsearch](https://github.com/elastic/elasticsearch)
- [Chroma](https://github.com/chroma-core/chroma)

### 9.6 评测
- [RAGAS](https://github.com/vibrantlabsai/ragas)
- [DeepEval](https://github.com/confident-ai/deepeval)
- [TruLens](https://github.com/truera/trulens)
- [Phoenix](https://github.com/Arize-ai/phoenix)
- [LangSmith SDK](https://github.com/langchain-ai/langsmith-sdk)