---
type: hub
topic: Redis
status: refactored
source: 文档/Redis.md
---

# Redis 笔记

> 原 `文档/Redis.md` 的重新整理版本（原文件以骨架标题为主，本笔记在其基础上**完善**）。
> MongoDB 见 [[Hub/01_MongoDB笔记]]，关系型对比与选型见 [[Hub/04_关系型数据库对比与选型笔记]]。
> 原笔记保留在 `文档/Redis.md` 供回溯。

## 目录

1. 特性
2. 数据类型（10 种）速查
3. 命令速查
4. 使用场景
5. 事务与原子性（`MULTI/EXEC` / Lua）
6. 持久化（RDB / AOF）
7. 高可用（主从复制 / 哨兵 / Cluster）
8. Python `redis-py` 集成示例
9. 常见使用注意

---

## 1. 特性

| 维度 | Redis |
|---|---|
| 类型 | **内存数据结构存储**（in-memory data structure store） |
| 协议 | 自有 RESP 协议，单端口（默认 6379） |
| 线程模型 | **单线程执行命令**（6.0+ I/O 多线程），避免锁 |
| 数据结构 | string / list / hash / set / zset / bitmap / hyperloglog / geo / stream / pub-sub |
| 持久化 | RDB 快照 / AOF 日志 |
| 主从 | 原生主从复制 + 哨兵 + Cluster（16384 槽） |
| 事务 | `MULTI/EXEC`（非关系库语义） + Lua 脚本（真原子） |
| 性能 | 单节点 10w+ QPS（视命令与负载） |

一句话：**Redis 不是单纯的 KV，而是"带数据结构的内存服务器"**。

---

## 2. 数据类型（10 种）速查

| 类型 | 用途 | 典型命令 |
|---|---|---|
| **string** | 字符串、计数器、分布式锁 | `SET` / `GET` / `INCR` / `SETNX` |
| **hash** | 字段-值集合（一个 key 内多个 field） | `HSET` / `HGET` / `HGETALL` |
| **list** | 双向链表，队列 / 最新列表 | `LPUSH` / `RPUSH` / `LPOP` / `LRANGE` |
| **set** | 无序去重集合，标签、共同好友 | `SADD` / `SISMEMBER` / `SUNION` |
| **zset** (sorted set) | 带分数的有序集合，排行榜 | `ZADD` / `ZRANGE` / `ZRANGEBYSCORE` |
| **bitmap** | 位操作，签到 / 布隆过滤器 | `SETBIT` / `GETBIT` / `BITCOUNT` |
| **hyperloglog** | 基数估算（UV 统计），误差 ~0.81% | `PFADD` / `PFCOUNT` |
| **geo** | 地理坐标（经纬度），距离 / 附近 | `GEOADD` / `GEOSEARCH` |
| **stream** | 5.0+ 消息流，类轻量 Kafka | `XADD` / `XREAD` / `XGROUP` |
| **pub/sub** | 实时消息广播（无持久化） | `PUBLISH` / `SUBSCRIBE` |

---

## 3. 命令速查

### 3.1 通用

```bash
SET key value                       # 设置
GET key                             # 获取
DEL key                             # 删除
EXISTS key                          # 是否存在
EXPIRE key 60                        # 设置过期时间（秒）
TTL key                             # 查看剩余过期时间
TYPE key                            # 查看类型
KEYS pattern                        # ⚠️ 生产禁用（O(N) 阻塞）
SCAN 0 MATCH user:* COUNT 100       # ✅ 增量遍历（推荐）
```

### 3.2 各类型核心命令

```bash
# string
SET counter 0
INCR counter                        # 自增 1（原子）
DECR counter
INCRBY counter 10
SETNX lock:foo 1                    # 仅当不存在时设置（分布式锁基础）

# hash（一个 key 内多字段）
HSET user:1 name "alice" age 30
HGET user:1 name
HGETALL user:1
HMSET user:2 name "bob" age 25     # 批量设置

# list（队列 / 最新列表）
LPUSH msg:list "hello"
RPUSH msg:list "world"
LRANGE msg:list 0 -1               # 全量
LPOP msg:list
LLEN msg:list                      # 长度

# set
SADD tags:1 "python" "redis"
SISMEMBER tags:1 "python"          # 是否在集合中
SUNION tags:1 tags:2               # 并集

# zset（排行榜）
ZADD rank 100 "alice" 200 "bob" 150 "carol"
ZREVRANGE rank 0 9 WITHSCORES      # 前 10 名
ZRANGEBYSCORE rank 100 200         # 分数区间

# geo
GEOADD city 121.47 31.23 "shanghai" 116.40 39.90 "beijing"
GEODIST city shanghai beijing km
GEOSEARCH city FROMLONLAT 121.47 31.23 BYRADIUS 50 km

# stream
XADD orders * product "book" price 50
XREAD COUNT 10 BLOCK 0 STREAMS orders $
```

---

## 4. 使用场景

| 场景 | 用法 | 数据类型 |
|---|---|---|
| **缓存** | 读穿透 / 写穿透 / 延迟双删 | string / hash |
| **分布式锁** | `SET key val NX PX 30000` + Lua 释放 | string |
| **计数器** | 文章阅读量、点赞数 | string（`INCR` 原子） |
| **排行榜** | 游戏积分、热搜 | zset |
| **限流** | 滑动窗口 / 令牌桶 | string + Lua |
| **延迟队列** | 任务到时间出队（用 zset 存 score=执行时间戳） | zset |
| **最新 N 条** | 朋友圈最新评论 | list（`LPUSH` + `LTRIM`） |
| **共同好友 / 推荐** | 交集 / 并集 / 差集 | set |
| **签到 / 日活** | 每天一个 bitmap 位 | bitmap |
| **UV 统计** | 百万级不重复用户 | hyperloglog |
| **附近的人 / 门店** | 经纬度 + 半径 | geo |
| **轻量消息队列** | 持久化 + 消费组 | stream（5.0+） |
| **实时通知** | 聊天广播、分布式事件总线 | pub/sub |

> pub/sub **不持久化**——订阅者离线时消息丢失；需要持久化用 stream。

---

## 5. 事务与原子性

### 5.1 `MULTI / EXEC`（关系库用户最容易误解的部分）

```bash
MULTI
SET a 1
SET b 2
EXEC
```

- 命令入队，`EXEC` 时**依次执行**整个队列
- 队列中的命令**不会在 EXEC 之前执行**，不能读中间结果
- **不是**关系库的 BEGIN / COMMIT 语义，**没有回滚**——失败时已执行的不会撤销
- 没有隔离级别概念

> 所以 Redis 官方说 `MULTI/EXEC` 是 "transactional"，但**不是 ACID 事务**。要做复杂原子逻辑用 Lua。

### 5.2 Lua 脚本（真原子）

Lua 脚本在 Redis 内**单线程顺序执行**，执行期间不会有其他命令插入 → **真原子**。

```bash
EVAL "
  local cur = tonumber(redis.call('GET', KEYS[1]) or '0')
  if cur < tonumber(ARGV[1]) then
    redis.call('SET', KEYS[1], ARGV[1])
    return 1
  end
  return 0
" 1 max_value 100
```

常见用途：

- 分布式锁的安全释放（"只删自己的锁"，CAS）
- 限流（滑动窗口）
- "读 → 判断 → 写" 的原子操作（避免 race condition）

### 5.3 与关系库事务对比

| 维度 | 关系库事务 | Redis MULTI/EXEC | Redis Lua |
|---|---|---|---|
| 原子性 | ✅ | ✅（队列整体） | ✅（脚本整体） |
| 回滚 | ✅ | ❌ | ❌ |
| 中间结果可见 | ❌（隔离） | ❌ | ❌ |
| 跨 key 隔离 | 由隔离级别控制 | 不提供 | 不提供 |
| 适合 | 复杂业务事务 | 简单命令批处理 | 复杂原子逻辑 |

---

## 6. 持久化（RDB / AOF）

| 方式 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **RDB** | 定时 fork 子进程 dump 快照 | 文件紧凑、恢复快 | 可能丢最近几分钟数据 |
| **AOF** | 记录每条写命令（append-only） | 数据更安全（可配置 everysec / always） | 文件大，恢复慢 |
| 混合（7.0+ 默认） | RDB 头 + AOF 增量 | 兼具两者优点 | — |

生产推荐：

- 不能容忍丢数据 → AOF `appendfsync everysec`
- 缓存场景（可丢）→ RDB 即可
- 推荐开启混合持久化

---

## 7. 高可用（主从复制 / 哨兵 / Cluster）

| 模式 | 能力 | 适用 |
|---|---|---|
| **主从复制** | 读扩展（从读主写） | 简单读写分离 |
| **Sentinel 哨兵** | 主从 + 自动故障转移 | 中小规模高可用 |
| **Cluster 集群** | 16384 槽分片 + 内置主从 | 大规模（> 单机内存 / 写并发） |

Cluster 关键点：

- key 通过 CRC16(key) % 16384 落到槽
- **多 key 操作必须在同一槽**（用 hash tag `{user:1}.profile` `{user:1}.order`）
- 不支持多数据库（只有 db0）

---

## 8. Python `redis-py` 集成示例

[`redis-py`](https://github.com/redis/redis-py) 是官方驱动。

```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,    # 自动把 bytes 解码成 str（推荐）
)

# string
r.set("greeting", "hello", ex=60)         # ex=60 表示 60 秒过期
print(r.get("greeting"))

r.incr("counter")                          # 自增
r.incrby("counter", 10)

# hash
r.hset("user:1", mapping={"name": "alice", "age": 30})
print(r.hgetall("user:1"))

# list（队列）
r.lpush("msgs", "hello", "world")
print(r.lrange("msgs", 0, -1))
print(r.rpop("msgs"))                      # 从右侧弹出

# zset（排行榜）
r.zadd("rank", {"alice": 100, "bob": 200, "carol": 150})
print(r.zrevrange("rank", 0, 9, withscores=True))

# 分布式锁（基础版）
import time, uuid
lock_key = "lock:order:42"
token = str(uuid.uuid4())
if r.set(lock_key, token, nx=True, px=10000):  # 10 秒过期
    try:
        # ... 业务逻辑
        pass
    finally:
        # 用 Lua 安全释放（CAS：只删自己的锁）
        release = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        else
            return 0
        end
        """
        r.eval(release, 1, lock_key, token)

# pipeline（批处理，减少网络往返）
with r.pipeline(transaction=False) as p:
    p.incr("counter")
    p.incr("counter")
    p.incr("counter")
    p.execute()
```

---

## 9. 常见使用注意

- **不要把 Redis 当主数据库**：内存贵，丢了很痛；持久化是兜底，不是备份。
- **慎用 `KEYS *`**：O(N) 阻塞单线程，生产必用 `SCAN`。
- **避免 bigkey**：单个 key 不要存超过几十 KB（list / hash / set 同理），会卡单线程。
- **设置过期时间**：无过期 key 容易撑爆内存。
- **分布式锁要带 token + Lua 释放**：避免误删别人的锁。
- **内存淘汰策略**（`maxmemory-policy`）：默认 `noeviction`（写满报错），常用 `allkeys-lru` / `volatile-lru`。
- **Cluster 多 key**：跨 key 操作必须保证在同一槽（用 hash tag `{...}`）。

---

## 关联笔记

- MongoDB：[[Hub/01_MongoDB笔记]]
- 关系型对比与选型：[[Hub/04_关系型数据库对比与选型笔记]]
- 消息队列：[[Hub/06_RabbitMQ笔记]]
- Demo：`workspace/db/redis_demo.py`