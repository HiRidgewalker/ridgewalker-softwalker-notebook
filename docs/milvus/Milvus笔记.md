---
title: "Milvus 笔记"
---

# Milvus 笔记

> 本笔记基于 Milvus 官方文档（standalone docker、hybrid search、reranking、index 章节）整理。
> 对比见 [Qdrant笔记](../qdrant/Qdrant笔记.md) 和 [zvec笔记](../zvec/zvec笔记.md)。
> 配套 demo：[example/vector-db/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/vector-db)

## 目录

1. 定位与适用场景
2. 本地 Docker 部署
3. 特性
4. 稠密向量与索引
5. 稀疏向量与索引
6. 混合检索（RRFRanker / WeightedRanker）
7. 索引优化与查询调优
8. 大数据量场景
9. Python `pymilvus` 集成示例
10. 常见使用注意

---

## 1. 定位与适用场景

Milvus 是为大规模向量检索设计的开源向量数据库，C++ 内核、Go 编排，支持 CPU / GPU 多种索引。

适用：

- **十亿级向量**的语义检索 / RAG
- 多模态（文本 + 图片 + 视频 embedding）联合检索
- 强 filter + 向量混合过滤（标量过滤与向量搜索同时进行）

不适用：

- 单进程 in-process 库场景（用 zvec 更合适）
- 简单本地 demo（Qdrant 启动更轻）

---

## 2. 本地 Docker 部署

Milvus 提供 standalone 单节点脚本（推荐用于本地开发）：

```bash
# 下载脚本
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

# 启动（拉镜像 + 起容器 milvus，端口 19530）
bash standalone_embed.sh start

# 重启 / 升级 / 停止 / 删除
bash standalone_embed.sh restart
bash standalone_embed.sh upgrade
bash standalone_embed.sh stop
bash standalone_embed.sh delete
```

- gRPC 端口：**19530**
- WebUI：**http://127.0.0.1:9091/webui/**
- 数据卷：`volumes/milvus`
- 修改配置：`user.yaml`，再 `restart`

> **v3.0-beta 新架构**：Streaming Node + Woodpecker MQ（替代 Kafka/Pulsar）+ 合并架构。
> 项目实战推荐 docker-compose 一键起 Milvus + etcd，见 `example/vector-db/docker-compose.yml`。

---

## 3. 特性

| 维度 | Milvus |
|---|---|
| 语言 / 内核 | C++ 检索核心 + Go 编排 |
| 部署 | Standalone / Cluster（K8s）/ Distributed |
| 索引 | FLAT / IVF / HNSW / SCANN / DiskANN（GPU：GPU_CAGRA / GPU_IVF / GPU_BRUTE_FORCE） |
| 数据类型 | float / binary / sparse（SPARSE_FLOAT_VECTOR） |
| 混合检索 | `hybrid_search` + RRFRanker / WeightedRanker |
| 标量过滤 | 内嵌，支持复杂表达式 + 标量索引 |
| GPU 加速 | ✅ 一级特性（CAGRA 等 GPU 索引） |
| 多副本 / 分片 | ✅ 集群原生支持 |
| 隔离级别 | 支持多种 consistency level |

---

## 4. 稠密向量与索引

### 4.1 索引类型速查

| 索引 | 类型 | 适合 |
|---|---|---|
| `FLAT` | 无压缩 | 小数据集，需要 100% 召回（baseline） |
| `IVF_FLAT` | 倒排 | 高速查询、高召回 |
| `IVF_SQ8` | 量化 | 非常高速度、有限内存 |
| `IVF_PQ` | 量化 | 高速度、紧内存 |
| `HNSW` | 图 | 非常高速度、高召回、内存充裕 |
| `HNSW_SQ` / `HNSW_PQ` / `HNSW_PRQ` | 量化 + 图 | 内存受限下要 HNSW |
| `SCANN` | 量化 | 非常高速度，SIMD 加速 |
| `AUTOINDEX` | 自动 | 默认推荐，让 Milvus 选最优 |

> Milvus 默认推荐 `AUTOINDEX`，无需手工调参；上线前再针对数据 benchmark。

### 4.2 HNSW 参数

| 参数 | 范围 | 说明 |
|---|---|---|
| `M` | [2, 2048] | 每节点最大邻居数 |
| `efConstruction` | — | 建图候选池，越大图质量越好、建索引越慢 |
| `ef` | ≥ top_k | 搜索候选池，越大召回越好、查询越慢 |

### 4.3 IVF 参数

| 参数 | 默认 / 范围 | 说明 |
|---|---|---|
| `nlist` | 128（[1, 65536]） | 聚类数 |
| `nprobe` | 8 | 搜索时探测几个聚类 |
| `max_empty_result_buckets` | 2 | 允许连续空桶数 |

### 4.4 关键调优原则（来自官方 FAQ）

> "when the total number of vectors approximately equals `nlist`, IVF_FLAT and FLAT has little difference in the way of calculation required and search performance. But as the number of vectors grows to two times, three times, or n times of `nlist`, IVF_FLAT index begins to show increasingly greater advantages."

→ **经验值**：`nlist ≈ 4√N`（N 为向量数）是常见起点。

---

## 5. 稀疏向量与索引

### 5.1 字段类型

稀疏向量字段：`DataType.SPARSE_FLOAT_VECTOR`（无需指定 dim，自动从数据推断）。

### 5.2 索引：`SPARSE_INVERTED_INDEX`

| 参数 | 范围 | 说明 |
|---|---|---|
| `inverted_index_algo` | — | 倒排索引算法（Milvus 2.5.4+ 默认 `DAAT_WAND`，旧的 `SPARSE_WAND` 已弃用） |
| `bm25_k1` | [1.2, 2.0] | BM25 饱和度参数 |
| `bm25_b` | [0, 1]，默认 0.75 | BM25 长度归一化 |
| `drop_ratio_search` | [0, 1] | 搜索时丢弃低分维度，越小越快（召回略降） |

> 倒排索引按维度存"出现该维度的向量列表"，搜索时只在相关维度计算。

### 5.3 常用 sparse embedding 来源

- **BM25 / TF-IDF**：传统 IR 关键词向量
- **SPLADE**：基于 BERT 的可学习稀疏向量
- **BGE-M3**：单次推理同时产出 dense + sparse（见 §6.2）

---

## 6. 混合检索（RRFRanker / WeightedRanker）

### 6.1 API 流程

```python
from pymilvus import AnnSearchRequest, RRFRanker, WeightedRanker

# 1) 给每个向量字段构造一个 AnnSearchRequest
dense_req = AnnSearchRequest(
    data=[query_dense], anns_field="dense_vector",
    param={"metric_type": "IP"}, limit=10,
)
sparse_req = AnnSearchRequest(
    data=[query_sparse], anns_field="sparse_vector",
    param={"metric_type": "IP"}, limit=10,
)

# 2) 用 rerank 合并
rerank = RRFRanker()              # 等权融合
# rerank = WeightedRanker(0.7, 1.0)  # 自定义权重

# 3) hybrid_search
results = col.hybrid_search(
    [sparse_req, dense_req],
    rerank=rerank,
    limit=10,
    output_fields=["text"],
)
```

### 6.2 用 BGE-M3 一次产出 dense + sparse

```python
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

ef = BGEM3EmbeddingFunction(use_fp16=False, device="cpu")
dense_dim = ef.dim["dense"]
docs_emb = ef(docs)        # 返回 {"dense": [...], "sparse": [...]}
```

### 6.3 RRFRanker vs WeightedRanker 怎么选

| 用 RRFRanker | 用 WeightedRanker |
|---|---|
| 各字段重要性**未确定** | 各字段重要性**有明确偏好**（如文本 > 颜色） |
| 只想看"多个字段都同意的 top" | 需要把不同 metric 的分数融合到同一尺度 |
| 只想看**排名** | 分数**绝对值**也有意义 |

| Ranker | 参数 | 默认 |
|---|---|---|
| `RRFRanker(k=60)` | `k` 平滑项，值越小越偏 top rank | 60 |
| `WeightedRanker(w1, w2, ...)` | 各字段权重，范围 [0, 1]，权重个数 = AnnSearchRequest 个数 | — |

**WeightedRanker 内部**：

- 用 `arctan` 把不同 metric 的距离归一化到 [0, 1]（IP ∈ [-∞, +∞]，L2 ∈ [0, +∞]）
- 再按权重加权平均

---

## 7. 索引优化与查询调优

### 7.1 索引选型决策

| 场景 | 推荐 |
|---|---|
| 不确定 / 默认 | `AUTOINDEX` |
| 数据量小（< 10w），要 100% 召回 | `FLAT` |
| 中等规模，内存充裕，要最快查询 | `HNSW` |
| 中等规模，内存紧 | `HNSW_PQ` / `IVF_PQ` |
| 超大规模（亿级以上） | DiskANN（on-disk）+ GPU 加速（如有） |

### 7.2 通用调优 checklist

- **每个 vector field 单独指定 index**：当前 Milvus 一个 field 只支持一种索引类型，切换会自动删旧索引
- **建索引前先建好标量索引**：避免后续 rebuild
- **使用 AUTOINDEX 上线**：跑起来后用真实数据 benchmark，再决定要不要手动换 IVF/HNSW
- **搜索时指定合理的 `limit`**：`limit` 远大于实际需求会浪费资源
- **标量过滤加索引**：高频过滤字段必须建标量索引
- **预留 `output_fields`**：避免拉到整个 payload
- **合理选择 `consistency_level`**：`Strong` / `Bounded` / `Session` / `Eventually`，越强越慢

### 7.3 FAQ 中的官方建议

- IVF：`nlist` 取 `4√N` 量级（N = 向量总数）
- HNSW：增大 `efConstruction` 提高索引质量，但建索引变慢；查询时调 `ef` 平衡召回和延迟
- PQ：`m` 是子量化器数量，越大精度越高、压缩越弱

---

## 8. 大数据量场景

### 8.1 容量档位（来自官方 docs）

| 数据量 | 推荐路径 |
|---|---|
| < 百万级 | Standalone + HNSW |
| 百万 ~ 千万级 | Standalone + IVF_PQ / HNSW_PQ；考虑 quantization |
| 千万 ~ 亿级 | Distributed 集群 + 分片 + 量化 |
| **十亿级** | **DiskANN（on-disk）** + Distributed 集群 + 可选 GPU 索引 |
| > 十亿 | 多集群 + GPU 加速（CAGRA / IVF GPU 索引） |

### 8.2 提升检索**时间**的做法

1. **量化**：IVF_PQ / HNSW_PQ 减少内存带宽
2. **on-disk 索引**：DiskANN 把索引放 SSD/NVMe，内存只放 graph 必要部分
3. **GPU 索引**：CAGRA、GPU_IVF 在 GPU 上做 ANN，吞吐远超 CPU
4. **shard 并行**：把数据分到多 shard 并行查
5. **限制 `limit` 与 `offset`**：分页用 `offset + limit` 代替深分页
6. **合理 `nprobe` / `ef`**：不是越大越好，按业务召回要求调

### 8.3 提升检索**精度**的做法

1. **更高召回的索引**：HNSW > IVF_FLAT > IVF_PQ（同等数据下）
2. **混合检索**：dense + sparse RRF，能拉回纯 dense 漏掉的关键字匹配
3. **reranker**：向量召回后用 cross-encoder 重排（BGE-reranker 等），最终精度提升显著（但每条慢 1~2 个数量级，top_k 要小）
4. **向量归一化**：cosine 距离等价于 IP 时记得 normalize
5. **标量预过滤**：用强约束（category、时间窗）先缩范围，再向量 ANN
6. **扩 `nprobe` / `ef`**：搜索时增加候选数

### 8.4 容量规划 checklist

- 估算向量数 N 和维度 d，原始内存 ≈ N × d × 4 bytes
- 量化后压缩：SQ8 → ~4× 压缩；PQ → 16~64×；Binary → 32×
- 索引本身的开销：HNSW 约 N × M × 4 bytes（边数 × 字节）
- 留 30% 余量给 OS cache、查询缓冲、临时排序

---

## 9. Python `pymilvus` 集成示例

```python
from pymilvus import MilvusClient, DataType, AnnSearchRequest, RRFRanker

client = MilvusClient(uri="http://localhost:19530")
client.drop_collection("demo")

# 1) 建 schema：dense + sparse + 标量
schema = client.create_schema(auto_id=True)
schema.add_field("pk",            DataType.VARCHAR,    is_primary=True, max_length=64)
schema.add_field("text",          DataType.VARCHAR,    max_length=512)
schema.add_field("dense_vector",  DataType.FLOAT_VECTOR, dim=768)
schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)

# 2) 建索引
index_params = client.prepare_index_params()
index_params.add_index("dense_vector",  index_type="AUTOINDEX", metric_type="IP")
index_params.add_index("sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
client.create_collection("demo", schema=schema, index_params=index_params)

# 3) 插入（sparse 用 dict[int, float] 形式）
client.insert("demo", [
    {"text": "hello world", "dense_vector": [0.1]*768,
     "sparse_vector": {1: 0.5, 17: 0.3}},
])

# 4) 检索
client.load_collection("demo")
res = client.search(
    collection_name="demo",
    data=[[0.1]*768],
    anns_field="dense_vector",
    limit=5,
    output_fields=["text"],
)
print(res)
```

混合检索用 `client.hybrid_search(...)`，传 `AnnSearchRequest` 列表 + rerank。

---

## 10. 常见使用注意

- **Standalone 不等于生产高可用**：生产用 Distributed / K8s 部署
- **删除字段会触发重建**：schema 改动要谨慎；推荐上线前定型
- **标量过滤没索引会很慢**：高频过滤字段必须建标量索引
- **`AUTOINDEX` 不等于"无敌"**：上线后用真实数据 benchmark，再换特定索引
- **WebUI 是 Attu**（独立组件）或 Milvus 内置 WebUI（9091）：监控与数据浏览
- **多向量字段混合检索**时注意 `metric_type` 一致性；用 WeightedRanker 时 arctan 归一化会处理掉大部分差异
- **大数据量下必须**：`enable_partition_key` + shard 配置 + 监控

---

## 关联笔记

- Qdrant：[Qdrant笔记](../qdrant/Qdrant笔记.md)
- zvec：[zvec笔记](../zvec/zvec笔记.md)
- 关系型 + pgvector：[PostgreSQL笔记](../postgresql/PostgreSQL笔记.md)
- 检索 / RAG 概念：[RAG工业方案笔记](../rag/RAG工业方案笔记.md)、[Rerank笔记](../rag/Rerank笔记.md)
- Demo：`example/vector-db/milvus_demo.py`