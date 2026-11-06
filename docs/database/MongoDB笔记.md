---
title: "MongoDB 笔记"
type: hub
topic: MongoDB
status: refactored
source: legacy-note
---

# MongoDB 笔记

> 由旧稿重新整理版本（原文件只有一行对比文字 + GUI 工具名，本笔记在其基础上**完善**）。
> 关系型数据库选型见 [关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)，Redis 见 [Redis笔记](./Redis笔记.md)。
> 旧稿目录已清理，当前以本文为准。

## 目录

1. 特性
2. 数据模型（文档 / 集合 / BSON）
3. 语法速查（CRUD / 查询 / 聚合 / 索引）
4. 使用场景
5. 事务（4.0+ 多文档 ACID）
6. 副本集与分片
7. Python `pymongo` 集成示例
8. 常见使用注意

---

## 1. 特性

| 维度 | MongoDB |
|---|---|
| 类型 | **文档型数据库**（Document Store） |
| 存储格式 | BSON（Binary JSON），最大 16 MB / 文档 |
| Schema | **动态 schema**（同一集合中文档字段可不同） |
| 主键 | 默认 `_id`（ObjectId，含时间戳 + 机器 + 进程 + 计数器） |
| 查询语言 | MQL（MongoDB Query Language），类 JSON |
| 索引 | B-tree / 文本 / 地理 / 哈希 / TTL |
| 扩展 | **副本集**（高可用）+ **分片**（水平扩展） |
| 事务 | 4.0+ 支持多文档 ACID 事务 |
| 一致性 | 默认多数读；可调 read concern / write concern |
| 适用规模 | 单节点 → 几十 TB（分片） |

MongoDB 与传统关系型数据库的核心差异（也是它取舍点）：

| 对比维度 | 关系型数据库 | MongoDB |
|---|---|---|
| 数据模型 | 表 + 行 + 列，强 schema | 集合 + 文档，弱 schema |
| 关联 | JOIN | 嵌入式文档 / `$lookup` 聚合 |
| 扩展方式 | 垂直扩展为主 | 水平扩展（分片）天然友好 |
| 事务 | 设计核心 | 4.0+ 才支持，事务粒度有约束 |
| 适用负载 | OLTP 通用 | 半结构化 / 大文档 / 写入密集 |

---

## 2. 数据模型（文档 / 集合 / BSON）

- **数据库 (database)** → 包含若干集合
- **集合 (collection)** → 类比「表」，但不强 schema
- **文档 (document)** → 类比「行」，BSON 格式，最外层是 `{}`，字段是键值对

```json
{
  "_id": ObjectId("..."),
  "name": "alice",
  "age": 30,
  "tags": ["admin", "beta"],
  "address": {
    "city": "Shanghai",
    "zip": "200000"
  },
  "createdAt": ISODate("2026-07-02T10:00:00Z")
}
```

> 关系型 → MongoDB 的映射概念：
> - 表 → collection
> - 行 → document
> - 列 → field
> - 主键 → `_id`
> - 联合索引 → compound index
> - 表关联 → 嵌入（embed）或 `$lookup`

---

## 3. 语法速查

### 3.1 库 / 集合操作

```javascript
use mydb                       // 切换/创建数据库（首次写入时才真正创建）
db.createCollection("user")    // 创建集合（也可省略，直接 insert 自动建）
db.user.drop()                 // 删除集合
show dbs                       // 列出所有库
show collections               // 列出当前库的所有集合
```

### 3.2 CRUD

```javascript
// Create
db.user.insertOne({ name: "alice", age: 30 })
db.user.insertMany([
  { name: "bob", age: 25 },
  { name: "carol", age: 28 }
])

// Read
db.user.find()                                    // 全部
db.user.find({ age: { $gte: 18 } })               // 条件
db.user.findOne({ name: "alice" })                // 单条
db.user.find({ name: /^a/ })                      // 正则

// Update
db.user.updateOne(
  { name: "alice" },
  { $set: { age: 31 } }
)
db.user.updateMany(
  { age: { $lt: 18 } },
  { $set: { minor: true } }
)

// Delete
db.user.deleteOne({ name: "alice" })
db.user.deleteMany({ age: { $lt: 0 } })
```

### 3.3 常用查询操作符

| 操作符 | 含义 | 示例 |
|---|---|---|
| `$eq` / `$ne` | 等于 / 不等于 | `{ age: { $eq: 30 } }` |
| `$gt` / `$gte` / `$lt` / `$lte` | 大于 / 大于等于 / 小于 / 小于等于 | `{ age: { $gte: 18, $lte: 60 } }` |
| `$in` / `$nin` | 在 / 不在数组内 | `{ status: { $in: ["active", "pending"] } }` |
| `$and` / `$or` / `$not` | 逻辑 | `{ $or: [{ age: { $lt: 18 } }, { vip: true }] }` |
| `$exists` | 字段是否存在 | `{ phone: { $exists: true } }` |
| `$regex` | 正则 | `{ name: { $regex: "^a", $options: "i" } }` |
| `$elemMatch` | 数组元素匹配 | `{ scores: { $elemMatch: { $gte: 80 } } }` |

### 3.4 投影 / 排序 / 分页 / 计数

```javascript
db.user.find({}, { name: 1, age: 1, _id: 0 })     // 投影
db.user.find().sort({ age: -1 })                  // 排序（1 升 / -1 降）
db.user.find().skip(20).limit(10)                 // 翻页
db.user.find({ age: { $gte: 18 } }).countDocuments()  // 计数
```

### 3.5 聚合管道（Aggregation Pipeline）

聚合是 MongoDB 做复杂分析 / 转换的核心，由多个 stage 组成：

```javascript
db.order.aggregate([
  { $match: { status: "paid" } },                  // 过滤
  { $group: { _id: "$userId", total: { $sum: "$amount" } } },  // 分组
  { $sort: { total: -1 } },                       // 排序
  { $limit: 10 },                                 // 取前 10
  { $lookup: {                                    // 关联（类似 JOIN）
      from: "user",
      localField: "_id",
      foreignField: "_id",
      as: "user"
  }}
])
```

常用 stage：`$match` / `$project` / `$group` / `$sort` / `$limit` / `$skip` / `$lookup` / `$unwind` / `$addFields` / `$bucket`。

### 3.6 索引

```javascript
db.user.createIndex({ name: 1 })                 // 单字段
db.user.createIndex({ name: 1, age: -1 })        // 复合索引
db.user.createIndex({ location: "2dsphere" })    // 地理空间
db.user.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })  // TTL
db.user.getIndexes()
db.user.createIndex({ name: 1 }, { unique: true })
```

---

## 4. 使用场景

✅ **适合**

- **半结构化数据**：每条记录的字段不完全一致（CMS、产品目录、用户画像）
- **大文档 / 嵌套数据**：评论树、配置中心、订单 + 明细放在同一文档（嵌入式）
- **写入密集**：日志、IoT 传感器数据、点击流
- **需要水平扩展**：单库即将超过单机容量 → 用分片
- **地理信息 / 时间序列**：内置地理索引 + TTL 索引
- **快速迭代**：schema 不固定，业务经常加字段

❌ **不适合**

- 强事务 / 多表 JOIN 多的 OLTP 业务（关系型更合适）
- 复杂报表 / OLAP（专用数仓 ClickHouse / Doris）
- 强一致性金融场景（可用，但要充分测试事务边界）

---

## 5. 事务（4.0+ 多文档 ACID）

MongoDB 4.0 起支持**副本集上的多文档 ACID 事务**，4.2 起支持**分片集群事务**。

```javascript
const session = db.getMongo().startSession()
session.startTransaction()
try {
  session.getDatabase("mydb").account.updateOne(
    { _id: "A" },
    { $inc: { balance: -100 } }
  )
  session.getDatabase("mydb").account.updateOne(
    { _id: "B" },
    { $inc: { balance:  100 } }
  )
  session.commitTransaction()
} catch (e) {
  session.abortTransaction()
  throw e
} finally {
  session.endSession()
}
```

**与关系型事务的关键差异**：

| 维度 | 关系型 | MongoDB |
|---|---|---|
| 默认隔离 | 由隔离级别决定 | snapshot isolation（默认） |
| 锁粒度 | 行 / 间隙 | 文档级 + 事务协调 |
| 性能影响 | 长期运行事务会阻塞 | **事务默认 60s 超时**，长事务代价更大 |
| 数据限制 | — | 事务期间不能修改文档使操作影响超过 16MB / 不允许写新集合（部分版本限制） |

> **最佳实践**：能用单文档原子操作解决的，不要上事务；事务要短小，能拆就拆。

---

## 6. 副本集与分片

- **副本集 (Replica Set)**：1 主 + 多从，自动故障转移（≈ 高可用）
- **分片 (Sharding)**：按 shard key 把数据分散到多个副本集（≈ 水平扩展）

常用组合：`mongos`（路由） + `config server`（集群元数据） + 多个 `shard`（每个 shard 是一个副本集）。

---

## 7. Python `pymongo` 集成示例

`pymongo` 是 MongoDB 官方同步驱动。

```python
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017/")
db = client["demo"]
users = db["user"]

# CRUD
users.insert_one({"name": "alice", "age": 30})
user = users.find_one({"name": "alice"})
print(user)

users.update_one({"name": "alice"}, {"$set": {"age": 31}})

users.delete_one({"name": "alice"})

# 批量
users.insert_many([
    {"name": "bob", "age": 25},
    {"name": "carol", "age": 28},
])

# 条件查询 + 投影
for u in users.find({"age": {"$gte": 18}}, {"_id": 0, "name": 1, "age": 1}):
    print(u)

# 唯一索引（防重复）
users.create_index("name", unique=True)

# 事务（需要副本集）
with client.start_session() as s:
    with s.start_transaction():
        users.update_one({"name": "alice"}, {"$inc": {"age": 1}}, session=s)
        users.update_one({"name": "bob"},   {"$inc": {"age": -1}}, session=s)
```

异步场景用 `motor`（已合并到 `pymongo` 的 `AsyncMongoClient`，pymongo ≥ 4.9 可用）。

---

## 8. 常见使用注意

- **16 MB 单文档上限**：嵌套数组 / 大字段不要无脑往一个文档塞。
- **避免大集合无索引排序**：`.sort()` 内存排序默认上限 32 MB，超过会报错。
- **正则查询性能**：避免 `^` 开头的正则（可以用前缀索引），开头是通配符的全表扫。
- **嵌入式 vs 引用式**：高频一起读 → 嵌入；独立查询 / 大量更新 → 引用 + `$lookup`。
- **副本集**才能用事务，单机 `mongod` 不行（开发测试时注意）。
- **不要把所有数据塞进一个大文档**：MongoDB 的强项不是"无限嵌套"，而是无 schema + 文档级原子写。
- **ObjectId 含时间戳**：可以用 `obj.generation_time` 取创建时间（粗略按秒）。

---

## 关联笔记

- Redis：[Redis笔记](./Redis笔记.md)
- 关系型对比与选型：[关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)
- 向量检索：[Qdrant笔记](../vector-db/Qdrant笔记.md)
- Demo：`example/db/mongodb_demo.py`