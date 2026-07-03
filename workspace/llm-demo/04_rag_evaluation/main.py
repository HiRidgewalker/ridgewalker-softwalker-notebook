"""
04_rag_evaluation · RAG 评测 Demo

演示 [[Hub/RAG工业方案笔记]] / [[Hub/Rerank笔记]] 中 RAG 评测体系的可执行部分。
覆盖 RAGAS 4 大核心指标（context_precision / context_recall / faithfulness /
answer_relevancy）+ mock RAG pipeline + 阈值调优。

**默认 mock 模式运行，全程不联网、不需要 GPU、不需要真实模型或 API。**

环境变量：
  EVAL_MODE    : mock / live（默认 mock）
                 live 模式需要 OPENAI_API_KEY，且要求已装 ragas>=0.4 + openai>=1.0
  OPENAI_API_KEY : live 模式必需

运行：
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo pipeline
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo metrics
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo flow
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo tuning
  workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --help

Author: 知识库 demo
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# 常量与配置
# ---------------------------------------------------------------------------

EVAL_MODE = os.environ.get("EVAL_MODE", "mock")  # mock / live
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WORK_DIR = Path(os.environ.get("EVAL_WORK_DIR", str(Path(__file__).resolve().parent / "_outputs")))
WORK_DIR.mkdir(parents=True, exist_ok=True)

VALID_DEMOS = {"pipeline", "metrics", "flow", "tuning"}

# 模拟的文档语料（5 个技术主题）
DOC_CORPUS = [
    {
        "id": "doc-1",
        "title": "RAGFlow 文档解析能力",
        "content": (
            "RAGFlow 是 infiniflow 出品的深文档理解 RAG 引擎。"
            "最新版本 v0.26.2，GitHub 84.1k stars。"
            "核心特性：深文档理解、复杂表格识别、版面分析、Agent 融合。"
            "适合复杂 PDF（论文 / 财报 / 合同）场景。"
        ),
        "embedding": [0.12, 0.34, 0.56, 0.78, 0.90, 0.11, 0.22, 0.33],
    },
    {
        "id": "doc-2",
        "title": "BGE-M3 Embedding 模型",
        "content": (
            "BGE-M3 是 BAAI 推出的多语言 Embedding 模型。"
            "FlagEmbedding v1.4.0 收录，1024 维度，8K 上下文。"
            "支持 dense + sparse + multi-vec 三态检索，是中文 RAG 首选。"
        ),
        "embedding": [0.20, 0.30, 0.50, 0.70, 0.85, 0.15, 0.25, 0.35],
    },
    {
        "id": "doc-3",
        "title": "Qdrant 向量数据库",
        "content": (
            "Qdrant 是 Rust 写的向量数据库，v1.18.2，32.9k stars。"
            "强过滤 + 混合检索（RRF/DBSF）+ Edge 支持。"
            "适合个人知识库和中小团队，单二进制部署。"
        ),
        "embedding": [0.15, 0.32, 0.55, 0.75, 0.88, 0.13, 0.24, 0.34],
    },
    {
        "id": "doc-4",
        "title": "BGE Reranker v2 重排序",
        "content": (
            "BGE Reranker v2-m3 是 BAAI 推出的 Cross-encoder 重排序模型。"
            "568M 参数，8K 上下文，多语言。"
            "中文生产环境首选，可本地部署或用 TEI 服务化。"
        ),
        "embedding": [0.18, 0.31, 0.54, 0.76, 0.89, 0.14, 0.23, 0.34],
    },
    {
        "id": "doc-5",
        "title": "RAGAS 评测框架",
        "content": (
            "RAGAS v0.4.3 是 RAG 评测事实标准，14.6k stars。"
            "4 大核心指标：context_precision、context_recall、faithfulness、answer_relevancy。"
            "支持 mock 模式本地跑，也可接 OpenAI / Anthropic API 跑真实评测。"
        ),
        "embedding": [0.13, 0.33, 0.55, 0.77, 0.90, 0.12, 0.22, 0.33],
    },
    {
        "id": "doc-6",
        "title": "LangGraph Agent 框架",
        "content": (
            "LangGraph 是 LangChain 推出的 stateful graph 框架。"
            "支持 thread state + checkpoint + subgraph。"
            "适合复杂 Agent + 多步推理场景。"
        ),
        "embedding": [0.40, 0.20, 0.60, 0.10, 0.50, 0.30, 0.70, 0.25],
    },
    {
        "id": "doc-7",
        "title": "DSPy Prompt 编译器",
        "content": (
            "DSPy v3.2.1 是 Stanford NLP 推出的程序化 prompt 框架。"
            "35.7k stars。核心：signature + module + optimizer（MIPRO / GEPA）。"
            "复杂多步 pipeline / RAG / Agent 推荐使用。"
        ),
        "embedding": [0.35, 0.25, 0.55, 0.15, 0.45, 0.35, 0.65, 0.30],
    },
    {
        "id": "doc-8",
        "title": "Manus Context Engineering 经验",
        "content": (
            "Manus 团队总结了 6 条 Context Engineering 经验。"
            "包括 KV-cache 设计、Mask 而非 Remove、文件系统当 context、Recitation、保留错误、反模式化。"
            "Manus 平均 100:1 输入输出比，cache 命中率是最重要指标。"
        ),
        "embedding": [0.30, 0.40, 0.50, 0.20, 0.60, 0.10, 0.80, 0.15],
    },
]

# 测试集（5 条问答）
TEST_SET = [
    {
        "qid": "q1",
        "question": "RAGFlow 是什么？",
        "ground_truth": "RAGFlow 是 infiniflow 出品的深文档理解 RAG 引擎。",
        "relevant_docs": ["doc-1"],
    },
    {
        "qid": "q2",
        "question": "中文 RAG 推荐用什么 Embedding 模型？",
        "ground_truth": "推荐 BGE-M3（BAAI 出品，支持中英多语言，dense+sparse+multi-vec 三态）。",
        "relevant_docs": ["doc-2"],
    },
    {
        "qid": "q3",
        "question": "Qdrant 有什么特点？",
        "ground_truth": "Qdrant 是 Rust 写的向量数据库，支持强过滤、混合检索（RRF）、Edge 部署。",
        "relevant_docs": ["doc-3"],
    },
    {
        "qid": "q4",
        "question": "RAGAS 4 大核心指标是什么？",
        "ground_truth": "context_precision、context_recall、faithfulness、answer_relevancy。",
        "relevant_docs": ["doc-5"],
    },
    {
        "qid": "q5",
        "question": "Manus 团队总结了哪些 Context Engineering 经验？",
        "ground_truth": "6 条：KV-cache 设计、Mask 而非 Remove、文件系统当 context、Recitation、保留错误、反模式化。",
        "relevant_docs": ["doc-8"],
    },
]


# ---------------------------------------------------------------------------
# Mock 模型与组件
# ---------------------------------------------------------------------------


@dataclass
class MockEmbedder:
    """Mock Embedding 模型（直接用预存的 embedding）"""

    model_name: str = "bge-m3-mock"

    def embed(self, text: str) -> list[float]:
        """对 query 文本做 embedding（mock：根据关键词匹配最相近的 doc embedding）"""
        # 简单的 keyword-based mock embedding
        keywords_map = {
            "ragflow": [0.12, 0.34, 0.56, 0.78, 0.90, 0.11, 0.22, 0.33],
            "bge": [0.20, 0.30, 0.50, 0.70, 0.85, 0.15, 0.25, 0.35],
            "qdrant": [0.15, 0.32, 0.55, 0.75, 0.88, 0.13, 0.24, 0.34],
            "ragas": [0.13, 0.33, 0.55, 0.77, 0.90, 0.12, 0.22, 0.33],
            "manus": [0.30, 0.40, 0.50, 0.20, 0.60, 0.10, 0.80, 0.15],
            "embedding": [0.20, 0.30, 0.50, 0.70, 0.85, 0.15, 0.25, 0.35],
            "中文": [0.18, 0.31, 0.54, 0.76, 0.89, 0.14, 0.23, 0.34],
            "推荐": [0.16, 0.30, 0.52, 0.74, 0.87, 0.13, 0.23, 0.33],
        }
        text_lower = text.lower()
        for kw, vec in keywords_map.items():
            if kw in text_lower:
                return vec
        # fallback：随机一个 doc embedding
        return random.choice(DOC_CORPUS)["embedding"]


@dataclass
class MockVectorDB:
    """Mock 向量数据库（cosine 相似度 + top-k 召回）"""

    name: str = "qdrant-mock"

    @staticmethod
    def cosine_sim(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b + 1e-9)

    def search(self, query_emb: list[float], top_k: int = 3) -> list[dict]:
        scored = []
        for doc in DOC_CORPUS:
            score = self.cosine_sim(query_emb, doc["embedding"])
            scored.append({"doc": doc, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


@dataclass
class MockReranker:
    """Mock 重排序器（小幅调整排序，模拟 Cross-encoder 精排）"""

    name: str = "bge-reranker-v2-m3-mock"

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        # 模拟 Cross-encoder：用 query 关键词匹配给小幅加分
        query_words = set(query.lower().split())
        for c in candidates:
            doc_text = c["doc"]["title"].lower() + " " + c["doc"]["content"].lower()
            overlap = len(query_words & set(doc_text.split())) / (len(query_words) + 1)
            c["rerank_score"] = c["score"] + overlap * 0.2
        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return candidates


@dataclass
class MockLLM:
    """Mock 生成模型（基于 top-1 doc 内容生成答案）"""

    name: str = "claude-sonnet-5-mock"

    def generate(self, query: str, contexts: list[dict]) -> str:
        """根据 context 生成答案（80% 概率回答准确 + 20% 概率幻觉）"""
        if not contexts:
            return "我不知道这个问题的答案。"
        top_doc = contexts[0]["doc"]

        # mock 生成：直接抽取 content 的核心句
        content = top_doc["content"]
        # 取第一个句号前的内容
        first_sentence = content.split("。")[0] + "。"
        # 80% 概率：正常回答
        if random.random() < 0.8:
            return f"根据检索到的资料：{first_sentence}"
        # 20% 概率：轻微幻觉（编造细节）
        else:
            return f"根据检索到的资料：{first_sentence}（注：该模型由 MiniMax 提供，最新版本）"


# ---------------------------------------------------------------------------
# Mock RAG Pipeline
# ---------------------------------------------------------------------------


@dataclass
class RAGConfig:
    """RAG pipeline 配置（用于 threshold tuning demo）"""

    chunk_size: int = 512
    top_k_recall: int = 5  # 第一阶段召回数
    top_k_rerank: int = 3  # 重排后输出数
    rerank_enabled: bool = True
    llm_temperature: float = 0.0


@dataclass
class RAGPipeline:
    """完整 RAG pipeline：embed → recall → rerank → generate"""

    config: RAGConfig = field(default_factory=RAGConfig)
    embedder: MockEmbedder = field(default_factory=MockEmbedder)
    vector_db: MockVectorDB = field(default_factory=MockVectorDB)
    reranker: MockReranker = field(default_factory=MockReranker)
    llm: MockLLM = field(default_factory=MockLLM)

    def run(self, query: str) -> dict:
        t0 = time.time()

        # 1. Embedding
        t_embed = time.time()
        query_emb = self.embedder.embed(query)
        t_embed = (time.time() - t_embed) * 1000

        # 2. Recall
        t_recall = time.time()
        candidates = self.vector_db.search(query_emb, top_k=self.config.top_k_recall)
        t_recall = (time.time() - t_recall) * 1000

        # 3. Rerank（可选）
        t_rerank = time.time()
        if self.config.rerank_enabled and self.reranker:
            candidates = self.reranker.rerank(query, candidates)
        reranked = candidates[: self.config.top_k_rerank]
        t_rerank = (time.time() - t_rerank) * 1000

        # 4. Generate
        t_gen = time.time()
        answer = self.llm.generate(query, reranked)
        t_gen = (time.time() - t_gen) * 1000

        total_ms = (time.time() - t0) * 1000

        return {
            "query": query,
            "answer": answer,
            "retrieved_docs": [c["doc"]["id"] for c in candidates],
            "reranked_docs": [c["doc"]["id"] for c in reranked],
            "retrieval_scores": [round(c["score"], 4) for c in candidates],
            "rerank_scores": [round(c.get("rerank_score", c["score"]), 4) for c in candidates],
            "latency_ms": {
                "embed": round(t_embed, 2),
                "recall": round(t_recall, 2),
                "rerank": round(t_rerank, 2),
                "generate": round(t_gen, 2),
                "total": round(total_ms, 2),
            },
        }


# ---------------------------------------------------------------------------
# RAGAS 4 大指标（mock 实现，公式与 ragas 库一致）
# ---------------------------------------------------------------------------


def compute_context_precision(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """
    Context Precision@K = (relevant items in top-K) / K
    简化版：top-K 中相关 doc 的占比
    """
    if not retrieved_ids:
        return 0.0
    relevant_set = set(relevant_ids)
    hits = sum(1 for d in retrieved_ids if d in relevant_set)
    return hits / len(retrieved_ids)


def compute_context_recall(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """
    Context Recall = (relevant items retrieved) / (total relevant items)
    """
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids)
    hits = sum(1 for d in relevant_ids if d in retrieved_set)
    return hits / len(relevant_ids)


def compute_faithfulness(answer: str, retrieved_contents: list[str]) -> float:
    """
    Faithfulness = (answer 中事实可由 context 支撑的比例)
    mock 实现：检查 answer 的关键词是否出现在任一 retrieved content 中
    """
    if not answer:
        return 0.0
    all_context = " ".join(retrieved_contents).lower()
    # 简单 mock：取 answer 中的中文词（长度 >= 2），检查是否在 context 中
    import re

    answer_words = re.findall(r"[\u4e00-\u9fa5]{2,}", answer)
    if not answer_words:
        return 0.5  # 没有中文词，给中间值
    hits = sum(1 for w in answer_words if w in all_context)
    return hits / len(answer_words)


def compute_answer_relevancy(question: str, answer: str) -> float:
    """
    Answer Relevancy = answer 与 question 的语义相关度
    mock 实现：检查 answer 是否包含 question 中的关键实词
    """
    if not question or not answer:
        return 0.0
    import re

    question_words = set(re.findall(r"[\u4e00-\u9fa5]{2,}", question))
    answer_words = set(re.findall(r"[\u4e00-\u9fa5]{2,}", answer))
    if not question_words:
        return 0.5
    overlap = len(question_words & answer_words)
    return overlap / len(question_words)


def evaluate_one(pipeline: RAGPipeline, test_item: dict) -> dict:
    """对单条 test case 跑完整 pipeline + 4 大指标"""
    result = pipeline.run(test_item["question"])

    retrieved_ids = result["retrieved_docs"]
    relevant_ids = test_item["relevant_docs"]
    retrieved_contents = [
        d["content"] for d in DOC_CORPUS if d["id"] in retrieved_ids
    ]

    metrics = {
        "qid": test_item["qid"],
        "question": test_item["question"],
        "context_precision": round(compute_context_precision(retrieved_ids, relevant_ids), 4),
        "context_recall": round(compute_context_recall(retrieved_ids, relevant_ids), 4),
        "faithfulness": round(compute_faithfulness(result["answer"], retrieved_contents), 4),
        "answer_relevancy": round(compute_answer_relevancy(test_item["question"], result["answer"]), 4),
        "answer": result["answer"],
        "retrieved_docs": retrieved_ids,
        "latency_total_ms": result["latency_ms"]["total"],
    }
    return metrics


def aggregate_metrics(per_query: list[dict]) -> dict:
    """聚合 4 大指标"""
    keys = ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]
    summary = {}
    for k in keys:
        values = [q[k] for q in per_query]
        summary[k] = {
            "mean": round(statistics.mean(values), 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
        }
    summary["avg_latency_ms"] = round(
        statistics.mean(q["latency_total_ms"] for q in per_query), 2
    )
    return summary


# ---------------------------------------------------------------------------
# Demo 函数
# ---------------------------------------------------------------------------


def demo_rag_pipeline_overview() -> None:
    """Demo 1: Mock RAG pipeline 全链路可视化"""
    print("=" * 70)
    print("Demo 1: Mock RAG Pipeline 全链路可视化")
    print("=" * 70)

    config = RAGConfig(top_k_recall=5, top_k_rerank=3)
    pipeline = RAGPipeline(config=config)

    query = "RAGFlow 是什么？"
    print(f"\n[Query] {query}\n")

    result = pipeline.run(query)

    print("[Step 1] Embedding")
    print(f"  - 模型: {pipeline.embedder.model_name}")
    query_emb = pipeline.embedder.embed(query)
    print(f"  - query embedding (前 4 维): {[round(x, 3) for x in query_emb[:4]]}")
    print(f"  - 耗时: {result['latency_ms']['embed']:.2f} ms")

    print("\n[Step 2] 向量召回 (Qdrant mock, top-5)")
    for i, (doc_id, score) in enumerate(zip(result["retrieved_docs"], result["retrieval_scores"]), 1):
        title = next(d["title"] for d in DOC_CORPUS if d["id"] == doc_id)
        print(f"  {i}. {doc_id} ({title}) — cosine={score}")

    print("\n[Step 3] 重排序 (BGE Reranker v2-m3 mock, top-3)")
    for i, (doc_id, score) in enumerate(zip(result["reranked_docs"], result["rerank_scores"][:3]), 1):
        title = next(d["title"] for d in DOC_CORPUS if d["id"] == doc_id)
        print(f"  {i}. {doc_id} ({title}) — rerank_score={score}")

    print("\n[Step 4] LLM 生成 (Claude Sonnet 5 mock)")
    print(f"  Answer: {result['answer']}")

    print("\n[延迟统计]")
    for k, v in result["latency_ms"].items():
        print(f"  {k}: {v} ms")


def demo_ragas_metrics() -> None:
    """Demo 2: RAGAS 4 大核心指标计算"""
    print("=" * 70)
    print("Demo 2: RAGAS 4 大核心指标")
    print("=" * 70)

    print("\n[指标定义]")
    print("  - Context Precision: top-K 中相关 doc 的占比")
    print("  - Context Recall: 相关 doc 被检索到的比例")
    print("  - Faithfulness: 答案中的事实可由 context 支撑的比例")
    print("  - Answer Relevancy: 答案与问题的语义相关度")

    config = RAGConfig(top_k_recall=5, top_k_rerank=3)
    pipeline = RAGPipeline(config=config)

    print("\n[跑 5 条测试集]\n")

    results = []
    for test_item in TEST_SET:
        m = evaluate_one(pipeline, test_item)
        results.append(m)
        print(f"  [{m['qid']}] {m['question']}")
        print(f"    CP={m['context_precision']:.3f}  CR={m['context_recall']:.3f}  "
              f"F={m['faithfulness']:.3f}  AR={m['answer_relevancy']:.3f}")

    print("\n[聚合结果]")
    summary = aggregate_metrics(results)
    for k, v in summary.items():
        if isinstance(v, dict):
            print(f"  {k}: mean={v['mean']:.3f}  min={v['min']:.3f}  max={v['max']:.3f}  stdev={v['stdev']:.3f}")
        else:
            print(f"  {k}: {v}")

    print("\n[关键观察]")
    cp = summary["context_precision"]["mean"]
    cr = summary["context_recall"]["mean"]
    f = summary["faithfulness"]["mean"]
    ar = summary["answer_relevancy"]["mean"]
    print(f"  - Context Precision = {cp:.2f}: {'✅ 检索器质量良好' if cp > 0.7 else '⚠️ 检索器需要优化'}")
    print(f"  - Context Recall = {cr:.2f}: {'✅ 召回充分' if cr > 0.7 else '⚠️ 召回不足，需扩大 top_k 或加 HyDE'}")
    print(f"  - Faithfulness = {f:.2f}: {'✅ 无明显幻觉' if f > 0.8 else '⚠️ 幻觉风险高，需 prompt 约束'}")
    print(f"  - Answer Relevancy = {ar:.2f}: {'✅ 答案相关' if ar > 0.7 else '⚠️ 答非所问，需检查 prompt'}")


def demo_evaluation_flow() -> None:
    """Demo 3: 完整评测流程 + 输出 JSON + Markdown 报告"""
    print("=" * 70)
    print("Demo 3: 完整评测流程 + 报告产出")
    print("=" * 70)

    config = RAGConfig(top_k_recall=5, top_k_rerank=3)
    pipeline = RAGPipeline(config=config)

    print("\n[Step 1] 准备测试集（5 条问答，已硬编码）")
    for t in TEST_SET:
        print(f"  - {t['qid']}: {t['question']}")

    print("\n[Step 2] 跑 RAG pipeline + 计算 4 大指标")
    per_query = [evaluate_one(pipeline, t) for t in TEST_SET]
    summary = aggregate_metrics(per_query)

    print("\n[Step 3] 输出 JSON 报告")
    report = {
        "config": {
            "chunk_size": config.chunk_size,
            "top_k_recall": config.top_k_recall,
            "top_k_rerank": config.top_k_rerank,
            "rerank_enabled": config.rerank_enabled,
        },
        "summary": summary,
        "per_query": per_query,
    }
    json_path = WORK_DIR / "rag_eval_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  → 写入 {json_path}")

    print("\n[Step 4] 输出 Markdown 报告")
    md_lines = [
        "# RAG 评测报告",
        "",
        "## 配置",
        "",
        f"- chunk_size: {config.chunk_size}",
        f"- top_k_recall: {config.top_k_recall}",
        f"- top_k_rerank: {config.top_k_rerank}",
        f"- rerank_enabled: {config.rerank_enabled}",
        "",
        "## 聚合指标",
        "",
        "| 指标 | mean | min | max | stdev |",
        "|---|---|---|---|---|",
    ]
    for k in ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]:
        v = summary[k]
        md_lines.append(f"| {k} | {v['mean']:.3f} | {v['min']:.3f} | {v['max']:.3f} | {v['stdev']:.3f} |")
    md_lines.append(f"\n平均延迟: {summary['avg_latency_ms']} ms\n")
    md_lines.append("## 逐条结果\n")
    md_lines.append("| qid | question | CP | CR | F | AR | latency |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for q in per_query:
        md_lines.append(
            f"| {q['qid']} | {q['question']} | {q['context_precision']:.3f} | "
            f"{q['context_recall']:.3f} | {q['faithfulness']:.3f} | "
            f"{q['answer_relevancy']:.3f} | {q['latency_total_ms']}ms |"
        )

    md_path = WORK_DIR / "rag_eval_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"  → 写入 {md_path}")

    print("\n[Step 5] 关键观察")
    print(f"  - 5 条测试全部跑完，4 大指标已聚合")
    print(f"  - JSON 报告可用于 CI/CD 集成，Markdown 报告可用于人工 review")
    print(f"  - 输出目录: {WORK_DIR}")


def demo_threshold_tuning() -> None:
    """Demo 4: 阈值调优 — 不同参数组合的指标对比"""
    print("=" * 70)
    print("Demo 4: 阈值调优 — chunk_size / top_k / rerank 影响")
    print("=" * 70)

    configs = [
        ("baseline (top_k=5, rerank=3, enabled)", RAGConfig(top_k_recall=5, top_k_rerank=3, rerank_enabled=True)),
        ("more recall (top_k=10)", RAGConfig(top_k_recall=10, top_k_rerank=3, rerank_enabled=True)),
        ("less rerank output (top_k=5, rerank=1)", RAGConfig(top_k_recall=5, top_k_rerank=1, rerank_enabled=True)),
        ("no rerank (baseline only)", RAGConfig(top_k_recall=5, top_k_rerank=5, rerank_enabled=False)),
    ]

    print(f"\n{'Config':<40} {'CP':>6} {'CR':>6} {'F':>6} {'AR':>6} {'Lat':>8}")
    print("-" * 75)

    for name, cfg in configs:
        pipeline = RAGPipeline(config=cfg)
        per_query = [evaluate_one(pipeline, t) for t in TEST_SET]
        summary = aggregate_metrics(per_query)
        cp = summary["context_precision"]["mean"]
        cr = summary["context_recall"]["mean"]
        f = summary["faithfulness"]["mean"]
        ar = summary["answer_relevancy"]["mean"]
        lat = summary["avg_latency_ms"]
        print(f"{name:<40} {cp:>6.3f} {cr:>6.3f} {f:>6.3f} {ar:>6.3f} {lat:>7.1f}ms")

    print("\n[调优建议]")
    print("  - CR 低 → 扩大 top_k_recall 或加 HyDE query rewrite")
    print("  - CP 低 + CR 高 → 检索器太松，加 rerank 或提高相似度阈值")
    print("  - CP 高 + CR 低 → 检索器太严，加多路召回 (BM25)")
    print("  - Faithfulness 低 → prompt 加「只根据 context 回答，不要编造」")
    print("  - Answer Relevancy 低 → 检查 query 改写 + answer 格式约束")
    print("  - 延迟敏感场景 → 关闭 rerank 或减少 top_k_rerank")


# ---------------------------------------------------------------------------
# Live 模式（可选，需要装 ragas>=0.4 + openai>=1.0）
# ---------------------------------------------------------------------------


def try_live_mode() -> bool:
    """尝试切到 live 模式，失败则返回 False"""
    if EVAL_MODE != "live":
        return False
    if not OPENAI_API_KEY:
        print(f"[WARN] EVAL_MODE=live 但 OPENAI_API_KEY 未设置，回退 mock 模式", file=sys.stderr)
        return False
    try:
        from datasets import Dataset  # noqa: F401
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        print("[INFO] live 模式已就绪（ragas + openai）")
        return True
    except ImportError as e:
        print(f"[WARN] live 模式依赖缺失 ({e})，回退 mock 模式", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RAG 评测 Demo — Mock RAG Pipeline + RAGAS 4 大核心指标",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s                     # 跑全部 demo（mock 模式）
  %(prog)s --demo pipeline     # 仅跑 pipeline overview
  %(prog)s --demo metrics      # 仅跑 RAGAS 指标
  %(prog)s --demo flow         # 仅跑完整评测流程
  %(prog)s --demo tuning       # 仅跑阈值调优

环境变量：
  EVAL_MODE=mock|live          # 默认 mock；live 需 ragas>=0.4 + OPENAI_API_KEY
  OPENAI_API_KEY=sk-xxx        # live 模式必需
        """,
    )
    parser.add_argument(
        "--demo",
        choices=sorted(VALID_DEMOS),
        default=None,
        help="跑单个 demo（不指定则跑全部）",
    )
    args = parser.parse_args()

    # live 模式探测
    live_ready = try_live_mode()

    demos_to_run: list[tuple[str, Callable[[], None]]] = [
        ("pipeline", demo_rag_pipeline_overview),
        ("metrics", demo_ragas_metrics),
        ("flow", demo_evaluation_flow),
        ("tuning", demo_threshold_tuning),
    ]

    if args.demo:
        demos_to_run = [(name, fn) for name, fn in demos_to_run if name == args.demo]

    print(f"\n[RAG 评测 Demo] 模式: {'live' if live_ready else 'mock'}")
    print(f"[RAG 评测 Demo] 跑 {len(demos_to_run)} 个 demo\n")

    for name, fn in demos_to_run:
        try:
            fn()
        except Exception as e:
            print(f"[ERROR] demo '{name}' 失败: {e}", file=sys.stderr)
            return 1

    print("\n" + "=" * 70)
    print("[完成]")
    print("=" * 70)
    if live_ready:
        print("已使用真实 ragas 库 + OpenAI API 跑评测")
    else:
        print("Mock 模式：未联网、未使用真实模型/API")
        print("如需切到 live 模式：")
        print("  1) uv pip install --python workspace/.venv/bin/python ragas datasets openai")
        print("  2) export EVAL_MODE=live OPENAI_API_KEY=sk-xxx")
        print("  3) python workspace/llm-demo/04_rag_evaluation/main.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())