# example/db —— 数据库 Demo 总索引

对应笔记：

- 关系型：[[MySQL笔记]] · [[PostgreSQL笔记]] · [[SQLite笔记]] · [[关系型数据库选型对比笔记]]
- NoSQL：[[MongoDB笔记]] · [[Redis笔记]]

每种数据库一个最小 Python demo，演示「连接 + 建表/建集 + 插入 + 查询 + 关键差异点」。

## Demo 列表

| Demo | 驱动 | 需要本地服务 | 对应笔记 |
|---|---|---|---|
| `sqlite_demo.py` | `sqlite3`（标准库） | ❌ | [[SQLite笔记]] |
| `mysql_demo.py` | `pymysql` | ✅ MySQL 3306 | [[MySQL笔记]] |
| `postgres_demo.py` | `psycopg`（v3） | ✅ PostgreSQL 5432 | [[PostgreSQL笔记]] |
| `mongodb_demo.py` | `pymongo` | ✅ MongoDB 27017 | [[MongoDB笔记]] |
| `redis_demo.py` | `redis-py` | ✅ Redis 6379 | [[Redis笔记]] |

> `sqlite_demo.py` 在 `example/db/sql-tools-demo/` 子目录下，其他 demo 直接在 `example/db/` 下。

## 环境准备

### 1. 虚拟环境

本例是独立项目，在 `example/db/` 目录下创建自己的虚拟环境：

```bash
cd example/db
uv venv .venv
```

### 2. 安装依赖

```bash
uv pip install --python .venv/bin/python \
    pymysql \
    "psycopg[binary]" \
    pymongo \
    redis
```

> 受网络限制，`uv pip install` 可能拉不到包。装不上的话用国内镜像：
>
> ```bash
> uv pip install --python .venv/bin/python \
>     --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
>     pymysql "psycopg[binary]" pymongo redis
> ```

### 3. 启动数据库服务（按需）

任选 docker 或本机服务：

```bash
# MySQL
docker run -d --name demo-mysql -p 3306:3306 \
    -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=demo \
    mysql:8

# PostgreSQL
docker run -d --name demo-postgres -p 5432:5432 \
    -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=demo \
    postgres:16

# MongoDB
docker run -d --name demo-mongo -p 27017:27017 mongo:7

# Redis
docker run -d --name demo-redis -p 6379:6379 redis:7-alpine
```

## 运行

```bash
# 无需服务
.venv/bin/python example/db/sql-tools-demo/sqlite_demo.py

# 需要本地服务
.venv/bin/python example/db/mysql_demo.py
.venv/bin/python example/db/postgres_demo.py
.venv/bin/python example/db/mongodb_demo.py
.venv/bin/python example/db/redis_demo.py
```

每个脚本都会：

1. 连接数据库
2. 建表 / 建集合（必要时清空旧数据）
3. 插入若干条
4. 演示查询 / 更新 / 删除 / 关键差异点（事务、Lua、聚合等）
5. 关闭连接 / 清场

连不上对应服务时，脚本会打印 docker 启动提示，不会直接 crash。

## 驱动关键差异速查

| 维度 | `sqlite3` | `pymysql` | `psycopg` v3 | `pymongo` | `redis-py` |
|---|---|---|---|---|---|
| 占位符 | `?` | `%s` | `%s` | 字典 | 关键字参数 |
| 自动提交 | 手动 | 手动（`autocommit=True` 可改） | 手动 | 自动 | 自动（pipeline 内可控） |
| 返回新 id | `cur.lastrowid` | `cur.lastrowid` | `INSERT ... RETURNING` | `res.inserted_id` | — |
| 连接上下文 | `with` | 手动 | `with` | 手动 | 手动 |
| 异步版本 | aiosqlite | aiomysql | psycopg async | motor / AsyncMongoClient | redis.asyncio |