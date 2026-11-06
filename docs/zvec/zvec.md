---
title: "zvec 笔记"
---

# zvec 笔记

> 本笔记基于 zvec 官方仓库与文档整理。**zvec 是进程内（in-process）向量数据库**，设计目标与 Milvus / Qdrant 不同——它不是一个独立服务，而是像 SQLite 一样嵌入到应用进程里运行。
> 对比见 [Milvus笔记](../milvus/milvus.md) 和 [Qdrant笔记](../qdrant/qdrant.md)。
> 配套 demo：[example/vector-db/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/vector-db)

## 目录

1. 定位与适用场景
2. 安装与部署（in-process 模式）
3. 特性
4. 稠密向量与 HNSW 索引
5. 稀疏向量与 FTS
6. 混合检索（MultiQuery + WeightedReRanker）
7. 索引优化
8. 大数据量场景
9. Python SDK 集成示例
10. 常见使用注意

---

## 1. 定位与适用场景

zvec 是阿里开源的**进程内向量数据库**（Apache-2.0，C++ 核心 + 多语言绑定），"battle-tested within Alibaba Group"，定位 "blazing fast, in-process, embed directly into applications"。

适用：

- **嵌入式 / 端侧**：不需要起服务，应用启动时直接打开 collection
- **小到中等规模**（数百万级向量以下）低延迟检索
- **工具 / CLI / 笔记本 / Serverless**：环境受限、无法常驻服务
- 想要"一个 .db 文件"那样的便携性（持久化用本地路径）

不适用：

- 多客户端跨网络共享（它不是 C/S，没有网络协议）
- 极大规模（十亿级 + 分布式）—— Milvus / 专用集群更适合
- 需要与外部 BI / 监控工具直接对接（Milvus / Qdrant 生态更成熟）

---

## 2. 安装与部署（in-process 模式）

> ⚠️ **zvec 是嵌入式库，不支持 Docker 服务化部署**。它设计为一个进程内库，与 SQLite 同类。
> 想在容器中跑也是可以的，但容器内本质上是 `pip install zvec` 然后运行 Python 脚本——并非把 zvec 自身作为服务。

### 2.1 安装

```bash
# Python 3.10 – 3.14
pip install zvec
```

### 2.2 创建 collection（指定本地路径）

```python
import zvec

schema = zvec.CollectionSchema(
    name="example",
    vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, 4),
)

collection = zvec.create_and_open(path="./zvec_example", schema=schema)
```

`./zvec_example` 是本地持久化目录，WAL 保证崩溃后数据不丢。

### 2.3 支持的平台

| 平台 | 架构 |
|---|---|
| Linux | x86_64, ARM64 |
| macOS | ARM64 |
| Windows | x86_64 |

### 2.4 SDK 矩阵

| 语言 | 包名 / 安装 |
|---|---|
| Python | `pip install zvec` |
| Node.js | `npm install @zvec/zvec` |
| Go / Rust / Dart-Flutter | 见官方仓库 |

---

## 3. 特性

| 维度 | zvec |
|---|---|
| 类型 | **进程内向量数据库**（in-process） |
| 语言 / 内核 | C++ 核心（80.5%），通过 SWIG 输出多语言绑定 |
| 持久化 | WAL（write-ahead log）保证崩溃恢复 |
| 并发 | **多进程可同时读；写单进程独占** |
| 数据结构 | dense + sparse + FTS（BM25） |
| 混合检索 | `MultiQuery` 一条 query 融合 dense + sparse + 标量过滤 + FTS |
| 索引 | Flat / HNSW / HNSW-RaBitQ / IVF / DiskANN |
| 量化 | RaBitQ（标量量化方案） |
| 工具 | Zvec Studio 可视化 |
| 许可证 | Apache-2.0 |

> 关键能力（v0.5.0，2026-06-12）：原生 FTS、混合检索 `MultiQuery`、DiskANN on-disk 索引、新增 Go/Rust SDK。
> 最新 release：v0.5.1（2026-06-24）。

---

## 4. 稠密向量与 HNSW 索引

### 4.1 索引类型（来自 vector-index 章节）

| 索引 | 类型 | 说明 |
|---|---|---|
| Flat | Brute-Force | 100% 召回，无压缩（baseline） |
| HNSW | 图 | 主流选择 |
| HNSW-RaBitQ | 图 + 量化 | 内存紧 |
| IVF | 倒排 | 平衡 |
| DiskANN | on-disk 图 | 超大规模、内存紧 |

### 4.2 HNSW 参数（来自 HNSW 章节）

**索引时（构建）参数：**

| 参数 | 含义 | 调参方向 |
|---|---|---|
| `metric_type` | 相似度度量（IP / L2 / COSINE） | 按 embedding 训练方式 |
| `m` | 每节点最大双向边数 | 越大精度↑、内存↑ |
| `ef_construction` | 建图候选池 | 越大图质量↑、建索引慢（不影响查询） |
| `quantize_type` | 量化方法（默认 none） | RaBitQ 等 |

**查询时参数：**

| 参数 | 含义 | 调参方向 |
|---|---|---|
| `ef` | 查询候选池 | 越大召回↑、延迟↑ |
| `radius` | 距离阈值（range filter，配合 IP） | 例如 `radius=0.6` |
| `is_linear` | 强制暴力扫 | 仅调试 / 极小 collection 用 |
| `is_using_refiner` | 用原始向量对 top 候选精排 | 量化场景用，额外延迟 |

API 类：

- Python：`zvec.model.param.HnswIndexParam` / `HnswQueryParam`
- Node.js：`ZVecHnswIndexParams` / `ZVecHnswQueryParams`

---

## 5. 稀疏向量与 FTS

### 5.1 稀疏向量

稀疏向量用 `{dim: weight}` 字典表示，与 dense 共存于同一个 collection 的不同 vector 字段：

```python
zvec.VectorSchema("sparse_embedding", zvec.DataType.SPARSE, ???)
# 注意：精确 API 细节参考官方 docs/db/data-operations/query/multi-vector
```

### 5.2 Full-Text Search（FTS，v0.5.0+）

zvec 提供**原生关键字检索**，对 string 字段做 BM25 打分，与向量检索在同一条查询里融合。

### 5.3 BM25 倒排索引

zvec 内置 inverted-index 概念（见 docs/concepts/inverted-index），给字符串字段建索引以支持 BM25 评分。

> 详细的 sparse / FTS 字段类型常量以官方 [zvec.org/en/docs/db](https://zvec.org/en/docs/db/) 为准，API 可能随小版本调整。

---

## 6. 混合检索（MultiQuery + WeightedReRanker）

### 6.1 API 模式

`collection.query()` 接收一个 `queries=[...]` 列表，每个 query 对应一个向量字段；多条结果用 `reranker` 融合。

```python
result = collection.query(
    topk=5,
    queries=[
        zvec.Query(field_name="dense_embedding",   vector=[0.1] * 768),
        zvec.Query(field_name="sparse_embedding",  vector={1: 0.1, 37: 0.43}),
    ],
    filter="publish_year >= 2020",     # 标量过滤（可与 vector 一起生效）
    reranker=zvec.WeightedReRanker(
        topn=3,
        metric=zvec.MetricType.IP,
        weights={"dense_embedding": 1.2, "sparse_embedding": 1.0},
    ),
)
```

> 官方 multi-vector 文档里 `filter` 的精确传参方式以最新版为准，建议写代码前看 [multi-vector docs](https://zvec.org/en/docs/db/data-operations/query/multi-vector)。

### 6.2 Reranker 选型

| Reranker | 含义 | 场景 |
|---|---|---|
| `WeightedReRanker` | 按权重融合（已文档化） | 已知各字段重要性差异 |
| RRF | Reciprocal Rank Fusion | 等权融合（参考通用做法） |

---

## 7. 索引优化

### 7.1 索引选型

| 数据量 | 推荐 |
|---|---|
| < 10w，调试 / 基线 | `Flat` |
| 10w ~ 百万 | `HNSW`（默认） |
| 百万 ~ 千万 | `HNSW-RaBitQ`（量化省内存） |
| 千万以上 | `IVF` 或 `DiskANN`（on-disk） |

### 7.2 HNSW 调参 checklist

- **建索引阶段**：根据数据量调 `m`（默认 16）、`ef_construction`（默认 100）
- **查询阶段**：根据召回目标调 `ef`，观察 latency
- **量化**：`HNSW-RaBitQ` 减少内存；查询时开 `is_using_refiner=true` 拉回精度
- **极小集合**：用 `is_linear=true` 走暴力更直接
- **范围查询**：`radius` 配合 IP / L2 metric 直接限定距离

### 7.3 FTS / 倒排索引

- 给需要关键字检索的 string 字段建 inverted-index
- 在 `MultiQuery` 里和向量一起查询，reranker 统一融合

---

## 8. 大数据量场景

### 8.1 容量档位（in-process 库的合理上限）

| 数据量 | 推荐路径 |
|---|---|
| < 百万 | HNSW 全内存 |
| 百万 ~ 千万 | HNSW-RaBitQ（量化省内存） |
| **千万级以上** | **DiskANN on-disk 索引** + 充足 SSD |
| 极大规模 | 评估是否切到 Milvus 集群 |

### 8.2 并发模型（来自 README）

- **多进程可同时读**：多个 reader 进程安全
- **写单进程独占**：同一时刻只有一个 writer
- → 应用架构上需要**读写分离或多 reader + 单 writer**

### 8.3 提升检索**时间**的做法

1. **DiskANN on-disk**：索引落 SSD/NVMe，内存只放图必要部分
2. **RaBitQ 量化**：内存紧时优先
3. **`is_using_refiner=false`**：在量化场景关掉精排换速度
4. **`is_linear=true`**：极小集合直接暴力，省 HNSW 开销
5. **`radius` 范围裁剪**：提前剪掉距离太远的候选
6. **`topk` 与 `ef`**：按需设置，不要"越大越好"
7. **WAL 调优**：批量写、关 fsync（接受少量丢失）

### 8.4 提升检索**精度**的做法

1. **`m` 与 `ef_construction` 加大**：建图质量↑（不影响查询速度）
2. **查询时 `ef` 加大**：召回↑、延迟↑
3. **`is_using_refiner=true`**：量化场景用原始向量精排 top-k
4. **MultiQuery 混合 dense + sparse + FTS**：补回单一模态漏点
5. **reranker**：向量召回后用 cross-encoder 重排
6. **标量预过滤**：强约束先缩范围再 ANN
7. **向量归一化**：cosine 等价 dot 时记得 normalize

### 8.5 持久化与可靠性

- WAL 保证崩溃后可恢复
- 备份：`./zvec_example` 目录整体拷贝
- 写性能受限于单进程独占；高写吞吐场景需要外部分布式

---

## 9. Python SDK 集成示例

```python
import zvec

# 1) 定义 schema
schema = zvec.CollectionSchema(
    name="example",
    vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, 4),
)

# 2) 创建并打开（持久化到 ./zvec_example）
collection = zvec.create_and_open(path="./zvec_example", schema=schema)

# 3) 插入
collection.insert([
    zvec.Doc(id="doc_1", vectors={"embedding": [0.1, 0.2, 0.3, 0.4]}),
    zvec.Doc(id="doc_2", vectors={"embedding": [0.2, 0.3, 0.4, 0.1]}),
])

# 4) 单条向量查询
results = collection.query(
    zvec.VectorQuery("embedding", vector=[0.4, 0.3, 0.3, 0.1]),
    topk=10,
)
for r in results:
    print(r.id, r.score)
```

> 完整 dense + sparse + 混合 + reranker 代码见 `example/vector-db/zvec_demo.py`。
> 实际字段类型名（`VECTOR_FP32` / `SPARSE` 等）与 `MultiQuery` 写法以官方 [docs/db](https://zvec.org/en/docs/db/) 当期版本为准，API 可能在小版本中调整。

---

## 10. 常见使用注意

- **不是 C/S**：没有网络端口，所有调用都在应用进程里 → 单应用独享数据
- **写单进程独占**：高并发写需要应用层排队 / 分片到多个 collection
- **数据 = 本地目录**：迁移 / 备份 = 拷贝目录
- **API 在小版本可能微调**：写代码前对照官方当期文档
- **Docker 不适用**：本身就是库，"容器化"等价于把脚本放容器里跑
- **不能跨网络共享**：需要共享时换 Milvus / Qdrant / pgvector

---

## 关联笔记

- Milvus：[Milvus笔记](../milvus/milvus.md)
- Qdrant：[Qdrant笔记](../qdrant/qdrant.md)
- 关系型 + pgvector：[PostgreSQL笔记](../postgresql/postgresql.md)
- 检索 / RAG 概念：[RAG工业方案笔记](../rag/rag-industrial-solutions.md)、[Rerank笔记](../rag/rerank.md)
- Demo：`example/vector-db/zvec_demo.py`