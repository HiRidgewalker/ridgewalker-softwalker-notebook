"""
pymongo demo —— 需要本地 MongoDB 服务（默认 localhost:27017）。

对应笔记：[[MongoDB笔记]]
"""
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

URI = "mongodb://localhost:27017/"


def main() -> None:
    client = MongoClient(URI)
    db = client["demo"]
    users = db["user"]

    # 清干净便于反复跑
    users.delete_many({})

    # Create
    res = users.insert_one({"name": "alice", "age": 30})
    print(f"[insert_one] inserted_id = {res.inserted_id}")

    users.insert_many([
        {"name": "bob",   "age": 25, "tags": ["vip"]},
        {"name": "carol", "age": 28, "tags": ["beta"]},
        {"name": "dave",  "age": 17, "tags": []},
    ])

    # 唯一索引（先建后插，否则已有重复会报错）
    try:
        users.create_index("name", unique=True)
    except Exception as e:
        print(f"[create_index] {e}")

    # Read
    alice = users.find_one({"name": "alice"})
    print(f"[find_one] {alice}")

    print("[find age>=18]")
    for u in users.find({"age": {"$gte": 18}}, {"_id": 0, "name": 1, "age": 1}):
        print(" ", u)

    # Update
    upd = users.update_one({"name": "alice"}, {"$set": {"age": 31}})
    print(f"[update_one] matched={upd.matched_count} modified={upd.modified_count}")

    # Delete
    dele = users.delete_one({"name": "dave"})
    print(f"[delete_one] deleted_count={dele.deleted_count}")

    # 聚合：按 tags 拆分后统计人数
    pipeline = [
        {"$match": {"tags": {"$ne": []}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]
    print("[aggregate tags count]")
    for row in users.aggregate(pipeline):
        print(" ", row)

    # 事务（需要副本集，单机 mongod 跑会失败）
    try:
        with client.start_session() as s:
            with s.start_transaction():
                users.update_one({"name": "alice"}, {"$inc": {"age": 1}}, session=s)
                users.update_one({"name": "bob"},   {"$inc": {"age": -1}}, session=s)
        print("[transaction] ok")
    except Exception as e:
        print(f"[transaction] skipped (needs replica set): {type(e).__name__}")

    # 收尾
    users.delete_many({})
    try:
        users.drop_index("name_1")
    except Exception:
        pass
    client.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}")
        print("提示：检查本地 MongoDB 是否启动，或参考 example/db/README.md 用 docker 起一个：")
        print("  docker run -d -p 27017:27017 --name demo-mongo mongo:7")