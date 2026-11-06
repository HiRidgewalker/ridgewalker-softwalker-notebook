---
title: "Qdrant 笔记"
---

# Qdrant 笔记

> 由旧稿重新整理版本（原文件只有一行 dashboard URL，本笔记**大幅完善**）。
> 本笔记基于 Qdrant 官方文档（quickstart、hybrid-queries、indexing、quantization 章节）整理。
> 对比见 [Milvus笔记](../milvus/Milvus笔记.md) 和 [zvec笔记](../zvec/zvec笔记.md)。
> 配套 demo：[example/vector-db/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/vector-db)
> 旧稿目录已清理，当前以本文为准。

## 目录

1. 定位与适用场景
2. 本地 Docker 部署
3. 特性
4. 稠密向量与 HNSW 索引
5. 稀疏向量与 BM25
6. 混合检索（Prefetch + RRF Fusion）
7. 量化与索引优化
8. 大数据量场景
9. Python `qdrant-client` 集成示例
10. 常见使用注意

---

## 1. 定位与适用场景

Qdrant（读 "quadrant"）是 Rust 实现的向量搜索引擎，强调**过滤感知 HNSW** 和**生产级稳定性**。

适用：

- 需要**强 payload 过滤 + 向量搜索**结合的场景（电商搜索、推荐）
- 中等规模到大规模（百万 ~ 亿级）向量检索
- 想要**REST / gRPC 双接口**，易于集成

不适用：

- 十亿级 + 极低延迟（Milvus / 专用 GPU 服务更合适）
- 嵌入式 in-process（用 zvec 更合适）

---

## 2. 本地 Docker 部署

```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant
```

| 端口 | 用途 |
|---|---|
| 6333 | REST API |
| 6334 | gRPC API |

Web Dashboard：**http://localhost:6333/dashboard**

> Windows 下挂载路径可能需要用 named volume（不要直接挂载 Windows 目录）。

> 默认**无加密、无鉴权**——生产部署前必须开 auth + TLS，参考官方 Production Checklist。

`example/vector-db/docker-compose.yml` 里已经准备好与 Milvus 共存的编排。

---

## 3. 特性

| 维度 | Qdrant |
|---|---|
| 语言 | Rust |
| 部署 | Single node / Cluster（自管 Raft） |
| 索引 | HNSW（dense + sparse 共用，sparse 需要自定义距离） |
| 量化 | Scalar int8 / Binary / Product / **TurboQuant**（v1.18+） |
| 标量过滤 | payload 索引（keyword / integer / float / geo / datetime / text） |
| 过滤感知 | ✅ HNSW 在建图时就感知 filter（filter-aware HNSW） |
| 混合检索 | Prefetch + RRF Fusion |
| 距离 | Cosine / Dot / Euclid / Manhattan |
| 接口 | REST + gRPC |
| 鉴权 | API Key + TLS |

> **过滤感知 HNSW** 是 Qdrant 核心差异化能力：HNSW 建图时把 payload 条件编进图的边，搜索时不会跨不满足条件的邻居，**减少无效搜索**。

---

## 4. 稠密向量与 HNSW 索引

### 4.1 HNSW 参数

| 参数 | 默认 | 范围 | 含义 |
|---|---|---|---|
| `m` | 16 | — | 每节点最大邻居数；越大精度高、内存多 |
| `ef_construct` | 100 | — | 建图候选池；越大索引质量好、建索引慢 |
| `ef` | = `ef_construct` | — | 查询候选池；越大召回好、查询慢 |
| `full_scan_threshold` | 10000 | KB | 低于该 KB 自动走全扫；过滤命中结果集小时降低它 |
| `max_indexing_threads` | — | — | 建索引并行度 |
| `on_disk` | false | — | 索引存盘（节省内存，搜索变慢） |
| `payload_m` | — | — | payload-aware 边数量 |

> 1KB ≈ 1 个 256 维向量。

### 4.2 调优建议（来自官方 docs）

1. **`m` 越大**：精度↑、内存↑
2. **`ef_construct` 越大**：建索引慢但索引质量好（不影响查询）
3. **查询时调 `ef`**：在召回 vs 延迟间权衡
4. **过滤命中结果集小** → 降 `full_scan_threshold`，让 planner 切到全扫避免 HNSW 开销
5. **payload 索引必须在数据写入**前建好 —— 否则要 `ef_construct + 1` 触发 optimizer 重建（**资源密集，慢**）
6. **严格过滤 + HNSW 连通性差** → 启用 **ACORN** 算法（v1.16+），探索二跳邻居提升精度（牺牲一点速度）

### 4.3 dense 集合配置示例

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="docs",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    hnsw_config=models.HnswConfigDiff(
        m=16,
        ef_construct=100,
        full_scan_threshold=10000,
    ),
)
```

---

## 5. 稀疏向量与 BM25

### 5.1 配置方式

稀疏向量是**命名向量**（per-collection 配置），不是默认字段：

```python
client.create_collection(
    collection_name="docs",
    vectors_config={
        "dense": models.VectorParams(size=768, distance=models.Distance.COSINE),
    },
    sparse_vectors_config={
        "text": models.SparseVectorParams(
            modifier=models.Modifier.IDF,    # IDF 加权（推荐 for BM25）
            # modifier=models.Modifier.NONE    # 不做 IDF
        ),
    },
)
```

> 稀疏向量**复用 HNSW 索引**，但需要自定义距离函数。

### 5.2 写入 sparse 向量

```python
from qdrant_client.http import models

client.upsert(
    collection_name="docs",
    points=[
        models.PointStruct(
            id=1,
            vector={
                "dense": [0.1, 0.2, ...],          # dense 部分
                "text":  {1: 0.5, 17: 0.3},        # sparse: {dim: weight}
            },
            payload={"title": "hello"},
        ),
    ],
)
```

### 5.3 用 BM25 自动产出稀疏向量

Qdrant 提供内置 BM25 嵌入模型，直接传文本：

```python
from qdrant_client import models

client.query_points(
    collection_name="docs",
    prefetch=models.Prefetch(
        query=models.Document(text="hello world", model="qdrant/bm25"),
        using="text",
        limit=100,
    ),
    query=[0.1, 0.2, ...],   # dense 查询向量
    using="dense",
    limit=10,
)
```

---

## 6. 混合检索（Prefetch + RRF Fusion）

Qdrant 的混合检索模型：**先并行 prefetch，再用 Fusion 融合**。

### 6.1 API 流程

```python
from qdrant_client import models

client.query_points(
    collection_name="docs",
    prefetch=[
        # 稀疏召回（BM25）
        models.Prefetch(
            query=models.Document(text="...", model="qdrant/bm25"),
            using="text",
            limit=100,
        ),
        # 稠密召回
        models.Prefetch(
            query=[0.1, 0.2, ...],
            using="dense",
            limit=100,
        ),
    ],
    # 融合两路结果
    query=models.FusionQuery(fusion=models.Fusion.RRF),
    limit=10,
)
```

### 6.2 融合策略

| Fusion | 说明 |
|---|---|
| `Fusion.RRF` | Reciprocal Rank Fusion，**默认推荐**，无参数等权融合 |
| `Fusion.DBSF` | Distribution-Based Score Fusion（按分数分布归一化） |

> RRF 公式：`score(d) = Σ 1 / (k + rank_i(d))`，k 默认为 60。

---

## 7. 量化与索引优化

### 7.1 量化类型对比（来自官方量化章节）

| 量化 | 压缩 | 编码选项 | 典型场景 |
|---|---|---|---|
| **Scalar Quantization** | 4×（float32 → uint8） | `quantile`, `always_ram` | 通用，**最常用** |
| **Binary Quantization** | up to 32× | `one_and_half_bits` / `two_bits` / 1-bit | 极快、精度损失大 |
| **Product Quantization (PQ)** | up to 64× | `compression`（如 `x16`） | 内存极紧 |
| **TurboQuant**（v1.18+） | 8×（bits4）/ 16× / 24× / 32× | `bits` | 16/24/32× 比 Binary 召回好 |

### 7.2 量化 + HNSW 配合

```python
from qdrant_client.http import models

client.update_collection(
    collection_name="docs",
    vectors_config={
        "dense": models.VectorParamsDiff(
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),
            quantization_config=models.ScalarQuantization(
                type=models.QuantizationType.INT8,
                quantile=0.99,
                always_ram=True,
            ),
        ),
    },
)
```

### 7.3 量化选型建议（按压缩率）

| 目标压缩 | 推荐 |
|---|---|
| 4× | Scalar Quantization（或 4-bit TurboQuant，除非用 Manhattan/L1） |
| 8× | 4-bit TurboQuant |
| 16× / 24× / 32× | TurboQuant 召回好；Binary 速度更快 |
| up to 64× | Product Quantization |

### 7.4 量化对搜索时间与召回的影响

**Binary Quantization 经验值（官方原文）**：

> "0.98 recall@100 with 4× oversampling" for OpenAI ada-002 (1536d)

→ Binary 量化时**必须配合 oversampling + rescoring** 才能拉回召回。

### 7.5 搜索时间调优参数

| 参数 | 作用 |
|---|---|
| `rescore` | 用原始向量重评 top-k（量化时拉回召回） |
| `oversampling` | 预选倍数（如 2.4 表示 limit=100 时先取 240） |
| `ignore` | 跳过量化向量走原始 |
| `always_ram` | true=量化向量常驻内存（速度快）；false=可 spill 到磁盘 |

---

## 8. 大数据量场景

### 8.1 存储模式三档（来自官方 docs）

| 模式 | 说明 |
|---|---|
| **All in RAM** | 最快，内存要求高（默认） |
| **量化常驻内存 + 原始向量在磁盘** | 速度与内存平衡（`always_ram=True` + memmap 存储） |
| **全在磁盘** | 最小内存，速度最慢，适合 SSD/NVMe |

### 8.2 提升检索**时间**的做法

1. **量化压缩**：Scalar 4× 起步，内存紧用 PQ 64×
2. **`always_ram=True`**：把量化向量常驻内存（前提：内存够）
3. **`on_disk=True` 给索引**：HNSW graph 落盘，节省内存（搜索慢一些）
4. **memmap 存储**：让 OS page cache 接管原始向量
5. **payload 索引**：高频过滤字段必须建索引
6. **ACORN 算法**：严格过滤场景，二跳邻居补全（精度↑速度↓，权衡）
7. **shard + replica**：集群部署水平扩展
8. **Binary Quantization + oversampling**：当磁盘 I/O 是瓶颈时效果显著
9. **rescore = false on disk**：原文建议——磁盘上 original 向量很慢，关掉 rescore

### 8.3 提升检索**精度**的做法

1. **HNSW 参数升级**：`m=32`、`ef_construct=200`、查询时 `ef=128+`
2. **混合检索**：dense + sparse + RRF，关键字召回补 dense 漏点
3. **rerank 上**：向量召回后再 cross-encoder 重排（top_k 小，效果显著）
4. **Scalar 量化 + rescoring**：用原始向量重评 top-k
5. **Binary 量化 + oversampling 4×**（或更高）+ rescoring
6. **payload 预过滤**：用强约束先缩范围再 ANN
7. **向量归一化**：cosine 等价于 dot 时记得 normalize
8. **扩搜索候选数**（`ef`、`limit`、`oversampling`）

### 8.4 容量估算

- 原始向量：N × d × 4 bytes
- HNSW 索引：约 N × M × 4 bytes（边数 × 字节）
- 量化压缩：4× ~ 64×
- 留 30% 余量给 OS cache + 临时排序 + payload

---

## 9. Python `qdrant-client` 集成示例

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url="http://localhost:6333")

# 1) 建 collection（dense + sparse 同存）
client.create_collection(
    collection_name="demo",
    vectors_config={
        "dense": models.VectorParams(size=768, distance=models.Distance.COSINE),
    },
    sparse_vectors_config={
        "text": models.SparseVectorParams(modifier=models.Modifier.IDF),
    },
)

# 2) 写入
client.upsert(
    collection_name="demo",
    points=[
        models.PointStruct(
            id=1,
            vector={
                "dense": [0.1] * 768,
                "text":  {1: 0.5, 17: 0.3},
            },
            payload={"title": "hello", "category": "news"},
        ),
    ],
)

# 3) 单独 dense 搜
client.search(collection_name="demo", query_vector=("dense", [0.1]*768), limit=5)

# 4) 单独 sparse 搜
client.search(collection_name="demo", query_vector=("text", {1: 0.4, 17: 0.3}), limit=5)

# 5) 混合 + RRF
client.query_points(
    collection_name="demo",
    prefetch=[
        models.Prefetch(query=models.Document(text="hello", model="qdrant/bm25"),
                        using="text", limit=50),
        models.Prefetch(query=[0.1]*768, using="dense", limit=50),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),
    limit=10,
)
```

---

## 10. 常见使用注意

- **生产前必看 Production Checklist**：默认无加密、无鉴权
- **payload 索引在建 collection 后也能加**，但 HNSW 已建好则需 `ef_construct+1` 触发 optimizer rebuild（**慢**）
- **ACORN**：严格过滤导致 HNSW 子图不连通时启用（v1.16+）
- **HNSW 参数**支持 collection 级别和 named vector 级别（v1.1.1+）
- **`using=`** 必须指定命名向量名（多向量场景必填）
- **大文本搜索**用 BM25 + sparse + IDF，比纯 dense HNSW 效果好
- **gRPC 比 REST 快**：批量操作走 gRPC

---

## 关联笔记

- Milvus：[Milvus笔记](../milvus/Milvus笔记.md)
- zvec：[zvec笔记](../zvec/zvec笔记.md)
- 检索 / RAG 概念：[RAG工业方案笔记](../rag/RAG工业方案笔记.md)、[Rerank笔记](../rag/Rerank笔记.md)
- Demo：`example/vector-db/qdrant_demo.py`