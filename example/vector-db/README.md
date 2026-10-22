# example/vector-db —— 向量数据库 Demo 总索引

对应笔记：

- [[01_Milvus笔记]]
- [[02_Qdrant笔记]]
- [[03_zvec笔记]]

## 文件

| 文件 | 内容 |
|---|---|
| `docker-compose.yml` | 一键起 Milvus standalone + Qdrant（含 etcd / minio） |
| `milvus_demo.py` | Milvus dense / sparse / hybrid（RRF + Weighted）检索 |
| `qdrant_demo.py` | Qdrant dense / sparse / BM25 / hybrid（Prefetch + RRF）+ payload 过滤 |
| `zvec_demo.py` | zvec in-process dense / multi-query（in-process，无 docker） |

## 启动服务（仅 Milvus / Qdrant 需要）

```bash
cd example/vector-db

# 起 Milvus（standalone）+ Qdrant
docker compose up -d milvus qdrant

# 检查状态
docker compose ps

# Milvus WebUI
open http://127.0.0.1:9091/webui/

# Qdrant Dashboard
open http://127.0.0.1:6333/dashboard

# 停掉
docker compose down
```

zvec 是 in-process 库，**不需要 docker**——直接 pip install 后即可运行。

## 安装依赖

按仓库规范，Python deps 装在 `example/.venv/`：

```bash
uv pip install --python .venv/bin/python pymilvus qdrant-client zvec
```

## 运行

```bash
# Milvus（需要 docker）
.venv/bin/python example/vector-db/milvus_demo.py

# Qdrant（需要 docker）
.venv/bin/python example/vector-db/qdrant_demo.py

# zvec（in-process，无需 docker）
.venv/bin/python example/vector-db/zvec_demo.py
```

每个 demo 都包含：

1. 建 collection（含 dense + sparse + 标量字段）
2. 插入若干示例文档
3. 单独 dense 搜 / 单独 sparse 搜 / BM25 文本搜
4. 混合检索（不同 rerank 策略）
5. 收尾（删除 collection / 清本地数据）

## 三库关键差异速查

| 维度 | Milvus | Qdrant | zvec |
|---|---|---|---|
| 类型 | C/S 服务 | C/S 服务 | **in-process 库** |
| Docker | ✅ standalone / cluster | ✅ 单镜像 | ❌ 不适用 |
| 索引（dense） | FLAT / IVF / HNSW / SCANN / DiskANN | HNSW（filter-aware） | Flat / HNSW / HNSW-RaBitQ / IVF / DiskANN |
| 索引（sparse） | SPARSE_INVERTED_INDEX | sparse HNSW + IDF modifier | FTS（BM25）+ sparse |
| 混合 API | `hybrid_search` + `AnnSearchRequest[]` | `query_points` + `Prefetch[]` + `FusionQuery` | `collection.query(queries=[...], reranker=...)` |
| Reranker | `RRFRanker` / `WeightedRanker` | `Fusion.RRF` / `Fusion.DBSF` | `WeightedReRanker` |
| 量化 | AUTOINDEX / IVF_PQ / HNSW_PQ | Scalar / Binary / PQ / TurboQuant | RaBitQ |
| 持久化 | WAL + MinIO/S3 | WAL + 本地卷 | WAL + 本地目录 |
| 适用规模 | 十亿级 + 集群 | 百万 ~ 亿级 | 数百万 ~ 千万级 |
| 内核语言 | C++ + Go | Rust | C++ + SWIG |

## 注意事项

- **Milvus** standalone 用 etcd + minio，所以 docker-compose.yml 把它们一起拉起；如果只想跑 Qdrant，单独 `docker compose up -d qdrant` 即可
- **Qdrant** 默认无鉴权；生产部署前开 API key + TLS
- **zvec** 仍在快速迭代（v0.5.x）；API 细节以 [zvec.org/en/docs/db](https://zvec.org/en/docs/db/) 当期为准
- **数据卷**：milvus_data / etcd_data / minio_data / qdrant_storage / zvec_demo_data 都是本地目录，删除即可清空对应库