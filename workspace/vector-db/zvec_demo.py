"""
zvec demo —— 进程内（in-process）向量库，不需要 docker 服务。

演示：
- 建 collection（持久化到本地目录）
- 插入 dense / sparse / 标量字段
- 单向量查询
- 多向量查询（MultiQuery）+ WeightedReRanker

对应笔记：[[Hub/03_zvec笔记]]

注意：zvec 仍在快速迭代（v0.5.x），API 细节以官方 https://zvec.org/en/docs/db/ 当期为准。
本 demo 演示 API 的整体形态；如遇小版本 API 调整请参考官方文档修正。
"""
import shutil
import zvec


DATA_DIR = "./zvec_demo_data"


def cleanup() -> None:
    shutil.rmtree(DATA_DIR, ignore_errors=True)


def main() -> None:
    cleanup()

    # 1) 定义 schema：dense 向量字段
    schema = zvec.CollectionSchema(
        name="demo",
        vectors=zvec.VectorSchema("dense_emb", zvec.DataType.VECTOR_FP32, 4),
    )

    # 2) 创建并打开（持久化到 DATA_DIR）
    col = zvec.create_and_open(path=DATA_DIR, schema=schema)

    # 3) 插入
    col.insert([
        zvec.Doc(id="d1", vectors={"dense_emb": [0.1, 0.2, 0.3, 0.4]},
                 fields={"text": "hello world"}),
        zvec.Doc(id="d2", vectors={"dense_emb": [0.2, 0.1, 0.4, 0.3]},
                 fields={"text": "zvec hybrid"}),
        zvec.Doc(id="d3", vectors={"dense_emb": [0.9, 0.8, 0.7, 0.6]},
                 fields={"text": "in-process db"}),
        zvec.Doc(id="d4", vectors={"dense_emb": [0.15, 0.25, 0.35, 0.45]},
                 fields={"text": "hello zvec"}),
    ])
    print("[zvec] inserted 4 docs")

    # 4) 单条向量查询
    res = col.query(
        zvec.VectorQuery("dense_emb", vector=[0.1, 0.2, 0.3, 0.4]),
        topk=3,
    )
    print("[zvec] single-vector query:")
    for r in res:
        print(f"  id={r.id} score={r.score:.3f}")

    # 5) 多向量查询（MultiQuery）+ WeightedReRanker
    #    注意：以下写法参考官方 multi-vector 文档的 API 形态；具体参数以当期文档为准
    try:
        multi_res = col.query(
            topk=3,
            queries=[
                zvec.Query(field_name="dense_emb", vector=[0.1, 0.2, 0.3, 0.4]),
                # 若 schema 含 sparse 字段，第二个 query 可加 sparse 向量
            ],
            reranker=zvec.WeightedReRanker(
                topn=3,
                metric=zvec.MetricType.IP,
                weights={"dense_emb": 1.0},
            ),
        )
        print("[zvec] multi-vector query (WeightedReRanker):")
        for r in multi_res:
            print(f"  id={r.id} score={r.score:.3f}")
    except Exception as e:
        print(f"[zvec] multi-query skipped (API may differ in current version): {e}")

    cleanup()


if __name__ == "__main__":
    main()