# sql-tools-demo

对应笔记：[[Hub/01_MySQL笔记]] · [[Hub/02_PostgreSQL笔记]] · [[Hub/03_SQLite笔记]] · [[Hub/04_关系型数据库对比与选型笔记]]

三种主流关系型数据库的 Python 连接 + 建表 + 插入 + 查询最小示例，用于对比三套驱动 API 的差异。

## 文件

| 文件 | 驱动 | 是否需要本地服务 |
|---|---|---|
| `sqlite_demo.py` | `sqlite3`（标准库） | ❌ 直接跑 |
| `mysql_demo.py` | `pymysql` | ✅ 需本地 MySQL（默认 `localhost:3306`） |
| `postgres_demo.py` | `psycopg`（v3） | ✅ 需本地 PostgreSQL（默认 `localhost:5432`） |

## 环境准备

### 1. 虚拟环境

按仓库规范，workspace 下所有 Python demo 统一使用 `workspace/.venv/`：

```bash
cd workspace
uv venv .venv
uv pip install --python .venv/bin/python pymysql psycopg[binary]
```

### 2. MySQL / PostgreSQL 服务（可选）

任选一种：

- **本机服务**：安装 MySQL / PostgreSQL 后启动
- **Docker**：
  ```bash
  # MySQL
  docker run -d --name demo-mysql -p 3306:3306 \
      -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=demo \
      mysql:8

  # PostgreSQL
  docker run -d --name demo-postgres -p 5432:5432 \
      -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=demo \
      postgres:16
  ```

## 运行

```bash
# 不需要任何服务
workspace/.venv/bin/python workspace/db/sql-tools-demo/sqlite_demo.py

# 需要本地 MySQL（用户 root / 密码 root，库 demo）
workspace/.venv/bin/python workspace/db/sql-tools-demo/mysql_demo.py

# 需要本地 PG（用户 postgres / 密码 postgres，库 demo）
workspace/.venv/bin/python workspace/db/sql-tools-demo/postgres_demo.py
```

每个脚本都会：

1. 连接数据库
2. 建一张 `user(id, name, age)` 表（如不存在）
3. 插入一行
4. 查全表并打印
5. 关闭连接

## 三种驱动的关键差异

| 维度 | `sqlite3` | `pymysql` | `psycopg` (v3) |
|---|---|---|---|
| 占位符 | `?` | `%s` | `%s` |
| 自动提交 | 默认手动 commit | 默认手动 commit（可用 `autocommit=True`） | 默认手动 commit |
| 返回新 id | `cur.lastrowid` | `cur.lastrowid` | `INSERT ... RETURNING id` + `cur.fetchone()` |
| 连接上下文 | `with sqlite3.connect(...) as conn:` | 手动 `try/finally` | `with psycopg.connect(...) as conn:` |