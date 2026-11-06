---
title: "PostgreSQL 笔记"
---

# PostgreSQL 笔记

> 原 旧稿 为空文件，本 Hub 笔记从零搭建。聚焦 PG 的核心特性、事务、JSONB、扩展机制与典型场景。
> 对比与选型见 [关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)，MySQL 见 [MySQL笔记](../mysql/MySQL笔记.md)，SQLite 见 [SQLite笔记](../sqlite/SQLite笔记.md)。
> 原 旧稿 旧稿目录已清理，当前以本文为准。

## 目录

1. 定位与适用场景
2. 核心特性总览
3. 事务与隔离级别
4. JSONB：关系库的文档能力
5. 扩展机制（Extension）
6. 常用数据类型速览
7. Python `psycopg` 集成示例
8. 常见使用注意

---

## 1. 定位与适用场景

PostgreSQL（简称 PG）是**功能最强大的开源关系型数据库**，社区口号是「世界上最先进的开源数据库」。

定位：

- 强 OLTP + 中等 OLAP 一体（一个库搞定事务 + 复杂分析）
- 数据完整性优先（严格的 SQL 标准实现、强类型、外键、约束）
- 复杂数据建模（JSON、数组、范围、GIS、全文检索）

适用场景：

- 数据模型复杂、业务对**数据一致性 / 完整性**要求高的系统（金融、订单、计费）
- 需要 **JSON 半结构化数据** + 关系查询混用的场景（替代部分 MongoDB 用法）
- 地理信息（PostGIS）、全文检索、时间序列、CUBE / 物化视图
- 写多读多、需要细粒度并发控制的 Web 后端

不擅长：

- 极简嵌入式场景（用 SQLite 即可）
- 超大规模 OLAP（专用数仓 Doris / ClickHouse 更适合）

---

## 2. 核心特性总览

| 维度 | PostgreSQL |
|---|---|
| SQL 标准 | **最贴近 SQL 标准**（MySQL 历史包袱多） |
| 事务 | 完整 ACID，默认 MVCC |
| 并发控制 | MVCC + 多种隔离级别，READ COMMITTED 为默认 |
| 索引 | B-tree / Hash / GIN / GiST / BRIN / SP-GiST，覆盖绝大多数场景 |
| 数据类型 | 丰富：JSONB / 数组 / 范围 / hstore / UUID / 自定义类型 |
| 扩展机制 | 官方 / 社区 extensions（PostGIS、pg_trgm、pgvector 等） |
| 复制 | 流复制（streaming replication）、逻辑复制 |
| 编程接口 | 支持存储过程（PL/pgSQL）、Python、JS 等多种语言 |

> 一句话：**MySQL 是「简单好用」的关系库，PostgreSQL 是「功能强大、约束严格」的关系库**。

---

## 3. 事务与隔离级别

PG 完整支持 SQL 标准的 4 个隔离级别，**默认是 READ COMMITTED**（与 MySQL 默认 REPEATABLE READ 不同）：

| 隔离级别               | 脏读                        | 不可重复读 | 幻读           |
| ------------------ | ------------------------- | ----- | ------------ |
| READ UNCOMMITTED*  | ❌（PG 内部视作 READ COMMITTED） | ✅     | ✅            |
| READ COMMITTED（默认） | ❌                         | ✅     | ✅            |
| REPEATABLE READ    | ❌                         | ❌     | ✅（PG 中同样会出现） |
| SERIALIZABLE       | ❌                         | ❌     | ❌            |

> *PG 不允许真正的 READ UNCOMMITTED，会被静默提升为 READ COMMITTED。

```sql
-- 查看
SHOW transaction_isolation;

-- 设置当前事务
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT ...;
COMMIT;
```

PG 在 REPEATABLE READ 下使用的是 **snapshot isolation**（快照隔离），不是经典意义上的"可重复读但仍有幻读"——会出现 serialization anomaly（写偏序），但不会出现脏读 / 不可重复读。

需要严格防幻读 → 用 `SERIALIZABLE`（PG 在该级别会做 SSI 序列化异常检测，性能损耗比 MySQL 小）。

---

## 4. JSONB：关系库的文档能力

PG 提供两种 JSON 类型：

| 类型 | 特点 |
|---|---|
| `json` | 存原始文本，保留空格 / 重复键，每次访问要解析 |
| `jsonb` | **二进制存储，解析后写入**，支持索引，**几乎总是选这个** |

```sql
CREATE TABLE event (
    id      BIGSERIAL PRIMARY KEY,
    type    TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 插入
INSERT INTO event (type, payload)
VALUES ('signup', '{"user": "alice", "plan": "pro"}');

-- 查询（用 ->> 取字段为文本，-> 取字段为 JSON）
SELECT * FROM event WHERE payload->>'plan' = 'pro';

-- 加 GIN 索引，查询走索引
CREATE INDEX idx_event_payload ON event USING gin (payload);
```

用 `jsonb` 时常见操作符：

| 操作符 | 含义 |
|---|---|
| `->` | 取字段，返回 JSON |
| `->>` | 取字段，返回文本 |
| `@>` | 包含（左 JSON 是否包含右 JSON） |
| `?` | 顶层是否包含某个 key |
| `#>` | 按路径取值 |

---

## 5. 扩展机制（Extension）

PG 强大的一半来自扩展。常用：

| 扩展 | 作用 |
|---|---|
| `pg_trgm` | 三字符组模糊匹配 / 相似度搜索 |
| `pgcrypto` | 加密函数（gen_random_uuid 替代品） |
| `uuid-ossp` | UUID 函数 |
| `PostGIS` | 地理信息（点、线、面、距离、索引） |
| `pgvector` | 向量相似度检索（AI / RAG 场景） |
| `pg_stat_statements` | SQL 性能统计 |
| `hstore` | 键值对 |
| `ltree` | 树形结构路径 |

启用：

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector
```

---

## 6. 常用数据类型速览

PG 的类型系统比 MySQL 丰富很多，常用的：

| 类型 | 用途 |
|---|---|
| `SERIAL` / `BIGSERIAL` | 自增整数（PG 原生） |
| `UUID` | 通用唯一标识 |
| `JSONB` | 结构化 JSON |
| `TEXT` / `VARCHAR(n)` | 文本（PG 中 `TEXT` 与 `VARCHAR` 性能等价） |
| `TIMESTAMPTZ` | 带时区的时间戳（推荐，**不用 `TIMESTAMP`**） |
| `DATE` / `TIME` / `INTERVAL` | 日期 / 时间 / 时间间隔 |
| `NUMERIC(p, s)` | 精确小数（金额用这个，**不要用 float**） |
| `BOOLEAN` | 布尔 |
| `ARRAY` | 任意类型的数组（`INT[]`, `TEXT[]` 等） |
| `INET` / `CIDR` | IP 地址 |
| 自定义类型 / ENUM | 枚举 |

---

## 7. Python `psycopg` 集成示例

最常用的 Python 驱动是 [`psycopg`](https://www.psycopg.org/)（v3）：

```python
import psycopg

conn = psycopg.connect(
    "host=localhost port=5432 dbname=demo user=demo password=demo"
)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id   BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age  INTEGER
        )
    """)
    cur.execute(
        "INSERT INTO user (name, age) VALUES (%s, %s) RETURNING id",
        ("alice", 30)
    )
    new_id = cur.fetchone()[0]

    cur.execute("SELECT id, name, age FROM user")
    for row in cur.fetchall():
        print(row)

conn.commit()
conn.close()
```

> 占位符用 `%s`（不是 MySQL 的 `%s`、不是 SQLite 的 `?`）。
> 推荐用 `with` 自动管理 cursor；连接池用 `psycopg_pool`。

---

## 8. 常见使用注意

- **默认隔离级别是 READ COMMITTED**，与 MySQL 不同，迁移时注意。
- **金额用 `NUMERIC`**：`FLOAT` / `DOUBLE` 都有精度问题。
- **时间用 `TIMESTAMPTZ`**：应用层一律 UTC，PG 会自动转换。
- **`TEXT` vs `VARCHAR`**：PG 中性能等价，按语义选择。
- **改字段名 / 类型**用 `ALTER TABLE`，PG 多数 `ALTER` 不锁表（新版），但大表加默认值还是可能锁——参考 `ALTER TABLE ... ADD COLUMN ... DEFAULT ...` 在 PG 11+ 不重写表。
- **跨库查询**用 `dblink` / `postgres_fdw`（PG 自带 foreign data wrapper）。

---

## 关联笔记

- MySQL：[MySQL笔记](../mysql/MySQL笔记.md)
- SQLite：[SQLite笔记](../sqlite/SQLite笔记.md)
- 横向对比与选型：[关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)
- 向量检索（pgvector）：[Qdrant笔记](../qdrant/Qdrant笔记.md)（向量数据库章节）