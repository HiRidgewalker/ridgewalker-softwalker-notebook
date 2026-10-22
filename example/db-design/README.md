# example/db-design —— 数据库设计演示示例

对应笔记：

- [[01_数据库设计相关笔记]]（生产环境数据库设计原则 + 慢 SQL 排查 + 索引优化）

## 文件

| 文件 | 内容 |
|---|---|
| `slow_query_logger.py` | FastAPI + SQLAlchemy 慢查询埋点（Engine + ORM event hook） |
| `alembic_add_index.py` | 从「发现慢 SQL」到「Alembic migration 加索引」的完整 revision 脚本 |
| `redis_key_examples.py` | 7 种典型 Redis key 模板 + Cluster Hash Tag 用法 + 限流 / 分布式锁 Lua |

## 运行

这些是「可读性优先」的代码片段示例，**不需要真连数据库**就能读懂设计模式。

```bash
# 看输出
.venv/bin/python example/db-design/slow_query_logger.py
.venv/bin/python example/db-design/alembic_add_index.py
.venv/bin/python example/db-design/redis_key_examples.py
```

如果要让 `slow_query_logger.py` 真正工作（SQLite in-memory）：

```bash
uv pip install --python .venv/bin/python sqlalchemy
.venv/bin/python example/db-design/slow_query_logger.py
```

## 注意事项

- **不要在生产裸 SQL 加索引**：所有 DDL 必须走 Alembic migration
- **慢查询埋点要分级**：业界常用 200ms 报警 / 1s P0
- **大表加索引要走在线 DDL**：MySQL 用 pt-osc / gh-ost，PG 用 `CREATE INDEX CONCURRENTLY`
- **Redis Cluster 多 key 操作**：必须用 `{...}` hash tag 强制同 slot
- **避免全局 hash tag**：所有 key 都用 `{global}` 会让整个集群退化为单机

## 相关 demo

- 关系型数据库连接示例：`example/db/sql-tools-demo/`（sqlite3 + pymysql + psycopg）
- NoSQL 连接示例：`example/db/mongodb_demo.py` + `example/db/redis_demo.py`
- 向量数据库示例：`example/vector-db/`（Milvus + Qdrant + zvec）