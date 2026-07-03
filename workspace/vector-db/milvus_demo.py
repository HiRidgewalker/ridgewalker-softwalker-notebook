"""
Milvus demo —— 需要 docker-compose 起 standalone（端口 19530）。

演示：
- 建 collection（dense + sparse + 标量）
- 插入
- 单独 dense 搜 / 单独 sparse 搜
- 混合检索（RRFRanker / WeightedRanker）

对应笔记：[[01_Milvus笔记]]
"""
from pymilvus import (
    MilvusClient,
    DataType,
    AnnSearchRequest,
    RRFRanker,
    WeightedRanker,
)

URI = "http://localhost:19530"
COLLECTION = "demo"


def build_collection(client: MilvusClient) -> None:
    if COLLECTION in client.list_collections():
        client.drop_collection(COLLECTION)

    schema = client.create_schema(auto_id=True)
    schema.add_field("pk",            DataType.VARCHAR,        is_primary=True, max_length=64)
    schema.add_field("text",          DataType.VARCHAR,        max_length=512)
    schema.add_field("dense_vector",  DataType.FLOAT_VECTOR,   dim=4)
    schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)

    index_params = client.prepare_index_params()
    index_params.add_index("dense_vector",  index_type="AUTOINDEX", metric_type="IP")
    index_params.add_index("sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
    client.create_collection(
        collection_name=COLLECTION, schema=schema, index_params=index_params,
    )
    print(f"[milvus] collection '{COLLECTION}' created")


def insert_data(client: MilvusClient) -> None:
    client.insert(COLLECTION, [
        {"text": "hello world",       "dense_vector": [0.1, 0.2, 0.3, 0.4],
         "sparse_vector": {1: 0.5, 17: 0.3}},
        {"text": "milvus hybrid",     "dense_vector": [0.2, 0.1, 0.4, 0.3],
         "sparse_vector": {2: 0.6, 17: 0.2}},
        {"text": "vector database",   "dense_vector": [0.9, 0.8, 0.7, 0.6],
         "sparse_vector": {3: 0.4, 17: 0.5}},
        {"text": "hello milvus",      "dense_vector": [0.15, 0.25, 0.35, 0.45],
         "sparse_vector": {1: 0.4, 2: 0.3}},
    ])
    client.load_collection(COLLECTION)
    print("[milvus] inserted 4 rows + loaded")


def dense_search(client: MilvusClient) -> None:
    res = client.search(
        collection_name=COLLECTION,
        data=[[0.1, 0.2, 0.3, 0.4]],
        anns_field="dense_vector",
        limit=3,
        output_fields=["text"],
    )
    print("[milvus] dense search:")
    for hit in res[0]:
        print(f"  id={hit['id']} score={hit['distance']:.3f} text={hit.get('text')}")


def sparse_search(client: MilvusClient) -> None:
    res = client.search(
        collection_name=COLLECTION,
        data=[{1: 0.5, 17: 0.3}],
        anns_field="sparse_vector",
        limit=3,
        output_fields=["text"],
    )
    print("[milvus] sparse search:")
    for hit in res[0]:
        print(f"  id={hit['id']} score={hit['distance']:.3f} text={hit.get('text')}")


def hybrid_search(client: MilvusClient, rerank: str) -> None:
    q_dense = [0.1, 0.2, 0.3, 0.4]
    q_sparse = {1: 0.5, 17: 0.3}

    dense_req = AnnSearchRequest(
        data=[q_dense], anns_field="dense_vector",
        param={"metric_type": "IP"}, limit=10,
    )
    sparse_req = AnnSearchRequest(
        data=[q_sparse], anns_field="sparse_vector",
        param={"metric_type": "IP"}, limit=10,
    )
    if rerank == "rrf":
        rk = RRFRanker()                 # 默认 k=60
    else:
        rk = WeightedRanker(0.7, 1.0)    # sparse=0.7, dense=1.0

    res = client.hybrid_search(
        [sparse_req, dense_req],
        rerank=rk, limit=3, output_fields=["text"],
    )
    print(f"[milvus] hybrid search (rerank={rerank}):")
    for hit in res[0]:
        print(f"  id={hit['id']} score={hit['distance']:.3f} text={hit.get('text')}")


def main() -> None:
    client = MilvusClient(uri=URI)
    try:
        client.list_collections()  # 探活
    except Exception as e:
        print(f"[error] 连不上 Milvus：{e}")
        print("提示：在 workspace/vector-db/ 目录下运行 docker compose up -d milvus")
        return

    build_collection(client)
    insert_data(client)
    dense_search(client)
    sparse_search(client)
    hybrid_search(client, "rrf")
    hybrid_search(client, "weighted")
    client.drop_collection(COLLECTION)


if __name__ == "__main__":
    main()