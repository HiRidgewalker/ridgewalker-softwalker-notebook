# 04_rag_evaluation · RAG 评测 Demo

演示 [[RAG工业方案笔记]] / [[Rerank笔记]] 中 RAG 评测体系的可执行部分。覆盖 **Mock RAG pipeline 全链路 + RAGAS 4 大核心指标 + 阈值调优**。

**默认 mock 模式运行，全程不联网、不需要 GPU、不需要真实模型或 API。**

## Demo 列表

| Demo | 内容 | 是否需要真实服务 |
|---|---|---|
| 1. `pipeline` | Mock RAG pipeline 全链路可视化：query → BGE-M3 embedding → Qdrant 召回 → BGE Reranker v2-m3 重排 → Claude Sonnet 5 mock 生成 | 不需要 |
| 2. `metrics` | RAGAS 4 大核心指标（context_precision / context_recall / faithfulness / answer_relevancy）公式 + 5 条测试集跑分 + 聚合统计 + 关键观察 | 不需要 |
| 3. `flow` | 完整评测流程：跑 pipeline → 计算指标 → 输出 JSON 报告 + Markdown 报告（可入 CI/CD） | 不需要 |
| 4. `tuning` | 阈值调优：4 组配置对比（baseline / more recall / less rerank / no rerank），演示 chunk_size / top_k / rerank 开关对 4 大指标的影响 | 不需要 |

## 涵盖知识点

- **RAG pipeline 全链路**：Embedding（bi-encoder）→ 向量召回（cosine）→ 重排序（cross-encoder）→ 生成（LLM）
- **RAGAS 4 大核心指标**：
  - Context Precision（top-K 中相关 doc 的占比）
  - Context Recall（相关 doc 被检索到的比例）
  - Faithfulness（答案中的事实可由 context 支撑的比例）
  - Answer Relevancy（答案与问题的语义相关度）
- **生产评测流程**：测试集 → pipeline → 指标聚合 → 报告产出（JSON + Markdown）
- **阈值调优经验**：
  - CR 低 → 扩大 top_k_recall 或加 HyDE
  - CP 低 + CR 高 → 加 rerank 或提高相似度阈值
  - CP 高 + CR 低 → 加多路召回 (BM25)
  - Faithfulness 低 → prompt 约束
- **报告模板**：JSON 报告 + Markdown 报告（可入 CI/CD）

## 安装与运行

```bash
# 装依赖（mock 模式无需任何包；live 模式需要 ragas + datasets + openai）
# uv pip install --python workspace/.venv/bin/python -r workspace/llm-demo/04_rag_evaluation/requirements.txt

# 跑全部 demo（mock 模式）
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py

# 跑单个 demo
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo pipeline
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo metrics
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo flow
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py --demo tuning
```

### 切到 live 模式（可选）

```bash
# 1. 装依赖
uv pip install --python workspace/.venv/bin/python ragas datasets openai

# 2. 设置环境变量
export EVAL_MODE=live
export OPENAI_API_KEY=sk-xxx

# 3. 跑（注意：live 模式需要联网 + OpenAI API）
workspace/.venv/bin/python workspace/llm-demo/04_rag_evaluation/main.py
```

环境变量：

| 变量 | 默认 | 说明 |
|---|---|---|
| `EVAL_MODE` | `mock` | 取值 `mock` / `live`，控制是否使用真实 ragas + OpenAI |
| `OPENAI_API_KEY` | 空 | live 模式必需；mock 模式忽略 |
| `EVAL_WORK_DIR` | `<demo_dir>/_outputs` | 报告输出目录 |

## Mock 数据集

- **语料库**：8 个文档片段，覆盖 RAGFlow / BGE-M3 / Qdrant / BGE Reranker / RAGAS / LangGraph / DSPy / Manus 等主题
- **测试集**：5 条问答对，每条标注 ground_truth + relevant_docs

## 关键观察

1. **RAGAS 是事实标准**：4 大指标各自捕获不同维度的问题，单看任何一个都会失真
2. **指标相互制约**：CP 与 CR 经常此消彼长，需要平衡；F 与 AR 更看 LLM 本身
3. **top_k 越大越好是误区**：扩大到一定阈值后边际收益递减，反而增加延迟和 LLM 成本
4. **Rerank 不是万能**：如果召回太差，rerank 也救不回来；先保 CR，再优化 CP
5. **报告双格式**：JSON 给 CI/CD 用，Markdown 给人工 review 用

## 对应笔记

- [[RAG工业方案笔记]] — RAG 范式、9 大框架、文档解析、Embedding、向量库、评测体系
- [[Rerank笔记]] — 4 种重排序范式、5 大模型系列、LLM-based 重排序、工业部署
- [[Prompt工程笔记]] — Prompt 工程原则、DSPy 编译器范式、结构化输出
- [[上下文工程与Agent笔记]] — Context Engineering、Agent 框架、记忆系统、MCP