"""
Qdrant demo —— 需要 docker-compose 起 Qdrant（端口 6333）。

演示：
- 建 collection（dense + sparse named vector + payload）
- 插入
- 单独 dense 搜 / 单独 sparse 搜 / BM25 文本搜
- 混合检索（Prefetch + Fusion.RRF）
- HNSW + Scalar Quantization 配置示例

对应笔记：[[Hub/02_Qdrant笔记]]
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models

URL = "http://localhost:6333"
COLLECTION = "demo"


def build_collection(client: QdrantClient) -> None:
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "dense": models.VectorParams(size=4, distance=models.Distance.COSINE),
        },
        sparse_vectors_config={
            "text": models.SparseVectorParams(modifier=models.Modifier.IDF),
        },
        hnsw_config=models.HnswConfigDiff(
            m=16,
            ef_construct=100,
            full_scan_threshold=10000,
        ),
        quantization_config=models.ScalarQuantization(
            scalar=models.ScalarQuantizationConfig(
                type=models.QuantizationType.INT8,
                quantile=0.99,
                always_ram=True,
            ),
        ),
    )
    print(f"[qdrant] collection '{COLLECTION}' created (HNSW + Scalar INT8)")


def insert_data(client: QdrantClient) -> None:
    client.upsert(
        collection_name=COLLECTION,
        points=[
            models.PointStruct(
                id=1, vector={"dense": [0.1, 0.2, 0.3, 0.4], "text": {1: 0.5, 17: 0.3}},
                payload={"text": "hello world",   "category": "news"},
            ),
            models.PointStruct(
                id=2, vector={"dense": [0.2, 0.1, 0.4, 0.3], "text": {2: 0.6, 17: 0.2}},
                payload={"text": "qdrant hybrid", "category": "tech"},
            ),
            models.PointStruct(
                id=3, vector={"dense": [0.9, 0.8, 0.7, 0.6], "text": {3: 0.4, 17: 0.5}},
                payload={"text": "vector db",     "category": "tech"},
            ),
            models.PointStruct(
                id=4, vector={"dense": [0.15, 0.25, 0.35, 0.45], "text": {1: 0.4, 2: 0.3}},
                payload={"text": "hello qdrant",  "category": "news"},
            ),
        ],
    )
    print("[qdrant] inserted 4 points")


def dense_search(client: QdrantClient) -> None:
    res = client.search(
        collection_name=COLLECTION,
        query_vector=("dense", [0.1, 0.2, 0.3, 0.4]),
        limit=3, with_payload=True,
    )
    print("[qdrant] dense search:")
    for p in res:
        print(f"  id={p.id} score={p.score:.3f} text={p.payload['text']}")


def sparse_search(client: QdrantClient) -> None:
    res = client.search(
        collection_name=COLLECTION,
        query_vector=("text", {1: 0.5, 17: 0.3}),
        limit=3, with_payload=True,
    )
    print("[qdrant] sparse search:")
    for p in res:
        print(f"  id={p.id} score={p.score:.3f} text={p.payload['text']}")


def bm25_search(client: QdrantClient) -> None:
    """用 qdrant/bm25 自动把文本转 sparse 向量"""
    res = client.query_points(
        collection_name=COLLECTION,
        query=models.Document(text="hello qdrant", model="qdrant/bm25"),
        using="text", limit=3, with_payload=True,
    )
    print("[qdrant] bm25 search:")
    for p in res.points:
        print(f"  id={p.id} score={p.score:.3f} text={p.payload['text']}")


def hybrid_search(client: QdrantClient) -> None:
    res = client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            models.Prefetch(
                query=models.Document(text="hello qdrant", model="qdrant/bm25"),
                using="text", limit=50,
            ),
            models.Prefetch(
                query=[0.1, 0.2, 0.3, 0.4],
                using="dense", limit=50,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=3, with_payload=True,
    )
    print("[qdrant] hybrid search (Prefetch + RRF):")
    for p in res.points:
        print(f"  id={p.id} score={p.score:.3f} text={p.payload['text']}")


def filter_search(client: QdrantClient) -> None:
    """向量搜索 + payload 过滤（过滤感知 HNSW）"""
    res = client.search(
        collection_name=COLLECTION,
        query_vector=("dense", [0.1, 0.2, 0.3, 0.4]),
        query_filter=models.Filter(must=[
            models.FieldCondition(key="category", match=models.MatchValue(value="tech")),
        ]),
        limit=3, with_payload=True,
    )
    print("[qdrant] dense + filter (category=tech):")
    for p in res:
        print(f"  id={p.id} score={p.score:.3f} text={p.payload['text']}")


def main() -> None:
    client = QdrantClient(url=URL)
    try:
        client.get_collections()  # 探活
    except Exception as e:
        print(f"[error] 连不上 Qdrant：{e}")
        print("提示：在 workspace/vector-db/ 目录下运行 docker compose up -d qdrant")
        return

    build_collection(client)
    insert_data(client)
    dense_search(client)
    sparse_search(client)
    bm25_search(client)
    hybrid_search(client)
    filter_search(client)
    client.delete_collection(COLLECTION)


if __name__ == "__main__":
    main()