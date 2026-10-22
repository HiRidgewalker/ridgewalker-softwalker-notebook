---
type: hub
topic: MySQL
status: refactored
source: legacy-note
---

# MySQL 笔记

> 由旧稿重新整理版本。聚焦 MySQL 核心特性、事务与隔离、存储引擎速览。
> 对比与选型见 [[04_关系型数据库对比与选型笔记]]，PostgreSQL 见 [[02_PostgreSQL笔记]]，SQLite 见 [[03_SQLite笔记]]。
> 旧稿目录已清理，当前以本文为准。

## 目录

1. 定位与适用场景
2. 事务的四大特性（ACID）
3. 并发事务问题
4. 事务的隔离级别
5. 存储引擎速览（InnoDB / MyISAM）
6. 常见使用注意

---

## 1. 定位与适用场景

MySQL 是最流行的开源关系型数据库之一，定位为**通用的 OLTP 数据库**：

- Web 应用后台（中小规模到大规模都常见）
- 读多写少的业务（配合主从复制可横向扩展读）
- 生态成熟：ORM 工具、运维工具、云厂商支持最齐全

不擅长：

- 复杂分析查询（OLAP）—— 适合用 ClickHouse / Doris / PG + 物化视图
- 强一致性的复杂数据约束（PG 在这块更强）

---

## 2. 事务的四大特性（ACID）

| 特性 | 含义 |
|---|---|
| **原子性 (Atomicity)** | 事务是不可分割的最小操作单元，要么全部成功，要么全部失败 |
| **一致性 (Consistency)** | 事务完成前后，所有数据必须保持一致的状态 |
| **隔离性 (Isolation)** | 数据库提供隔离机制，保证事务在不受外部并发操作影响的独立环境下运行 |
| **持久性 (Durability)** | 事务一旦提交或回滚，它对数据库中数据的改变就是永久的 |

---

## 3. 并发事务问题

多个事务并发执行时，常见三类问题：

| 问题 | 表现 |
|---|---|
| **脏读** | 一个事务读到另一个事务**还没提交**的数据 |
| **不可重复读** | 同一事务先后读取同一条记录，**两次读取的数据不同** |
| **幻读** | 按条件查询时没有对应数据行，但插入时又发现这行已存在，像"幻影" |

> 三类问题严重程度：脏读 > 不可重复读 > 幻读。

---

## 4. 事务的隔离级别

SQL 标准定义了 4 个隔离级别，**级别越高数据越安全，但性能越低**：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | ✅ 允许 | ✅ 允许 | ✅ 允许 |
| READ COMMITTED | ❌ 禁止 | ✅ 允许 | ✅ 允许 |
| REPEATABLE READ（MySQL InnoDB 默认） | ❌ 禁止 | ❌ 禁止 | ✅ 允许（InnoDB 通过 MVCC + 间隙锁在很大程度上规避） |
| SERIALIZABLE | ❌ 禁止 | ❌ 禁止 | ❌ 禁止 |

### 4.1 查看与设置隔离级别

```sql
-- 查看当前会话隔离级别
SELECT @@TRANSACTION_ISOLATION;

-- 设置隔离级别
SET [ SESSION | GLOBAL ] TRANSACTION ISOLATION LEVEL
    { READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ | SERIALIZABLE };
```

- `SESSION`：仅当前会话生效
- `GLOBAL`：所有新会话生效，不影响已存在的会话

---

## 5. 存储引擎速览（InnoDB / MyISAM）

MySQL 的核心特性很大程度由存储引擎决定。最常见两个：

| 维度 | InnoDB（默认） | MyISAM |
|---|---|---|
| 事务 | ✅ 支持 ACID | ❌ 不支持 |
| 行级锁 | ✅ | ❌ 只支持表锁 |
| 外键 | ✅ | ❌ |
| MVCC | ✅ | ❌ |
| 崩溃恢复 | ✅（redo/undo log） | ❌ |
| 全文索引 | ✅（5.6+） | ✅（更早支持） |
| 适用场景 | **默认选它**，OLTP、写入、高并发 | 只读 / 报表型历史库（极少用） |

> 新项目一律用 InnoDB。

---

## 6. 常见使用注意

- **默认字符集**：建库时显式指定 `utf8mb4` + `utf8mb4_unicode_ci`，不要用老的 `utf8`（实际是 3 字节，不能存 emoji）。
- **避免 `SELECT \*`**：列出字段，方便加索引、改 schema。
- **小表不一定用 MySQL**：单文件、本地工具类场景优先 SQLite，见 [[03_SQLite笔记]]。
- **复杂类型 / JSON / GIS**：考虑 PostgreSQL，见 [[02_PostgreSQL笔记]]。

---

## 关联笔记

- PostgreSQL：[[02_PostgreSQL笔记]]
- SQLite：[[03_SQLite笔记]]
- 横向对比与选型：[[04_关系型数据库对比与选型笔记]]