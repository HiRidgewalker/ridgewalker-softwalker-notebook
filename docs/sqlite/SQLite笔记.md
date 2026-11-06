---
title: "SQLite 笔记"
---

# SQLite 笔记

> 由旧稿重新整理版本。聚焦 SQLite 嵌入式特点、命令与语法、数据类型。
> 对比与选型见 [关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)，MySQL 见 [MySQL笔记](../mysql/MySQL笔记.md)，PostgreSQL 见 [PostgreSQL笔记](../postgresql/PostgreSQL笔记.md)。
> 旧稿目录已清理，当前以本文为准。

## 目录

1. 定位与适用场景
2. 命令 vs SQL 语句
3. 数据类型（5 种存储类 / Type Affinity）
4. Python `sqlite3` 集成示例
5. 常见使用注意

---

## 1. 定位与适用场景

SQLite 是一个**进程内库**，实现了自给自足的、无服务器的、零配置的、事务性的 SQL 数据库引擎。

核心特点：

- **嵌入式**：不是独立进程，链接到应用程序里
- **零配置**：不需要安装、启动服务、配置用户
- **单文件**：整个数据库就是一个磁盘文件，便于拷贝/备份
- **事务性**：完整支持 ACID
- **静态或动态链接**：按需链接到应用

适用场景：

- 桌面应用 / 移动 App 的本地存储（Android/iOS/macOS 内置）
- 单用户工具脚本、小型项目原型
- 测试与开发环境（替代内存数据库做轻量集成测试）
- 嵌入式设备、浏览器内部存储（HTML5 Web SQL 实际就基于 SQLite）

不擅长：

- 高并发写入（全局写锁，并发写会串行化）
- 大数据量（> 几十 GB 后性能与维护性下降）
- 多客户端通过网络同时访问（无内置网络协议）

---

## 2. 命令 vs SQL 语句

这是 SQLite 的"小坑"：**sqlite 命令不以分号结束，SQL 语句仍然以分号结束**。

```bash
$ sqlite3 mydb.db
sqlite> .help          # sqlite 命令（点命令），不加分号
sqlite> .tables        # 列出所有表
sqlite> .schema user   # 查看建表语句
sqlite> .quit          # 退出

sqlite> SELECT * FROM user;   # SQL 语句，正常加分号
```

常用点命令速查：

| 命令 | 作用 |
|---|---|
| `.help` | 帮助 |
| `.quit` / `.exit` | 退出 |
| `.databases` | 当前连接到的数据库 |
| `.tables` | 列出所有表 |
| `.schema [name]` | 查看表结构 |
| `.headers on` / `.mode column` | 美化输出 |

> 详细命令列表：[SQLite 命令 | 菜鸟教程](https://www.runoob.com/sqlite/sqlite-commands.html)
> 完整语法：[SQLite 语法 | 菜鸟教程](https://www.runoob.com/sqlite/sqlite-syntax.html)

---

## 3. 数据类型（5 种存储类 / Type Affinity）

SQLite 是**动态类型**（不像 MySQL/PG 那样有严格的列类型）。任意列可以存放任意类型的数据，但每个列有一个推荐的"亲和类型"（Type Affinity）。

### 3.1 5 种存储类（Storage Classes）

数据实际存储时只用这 5 种类型：

| 存储类 | 说明 |
|---|---|
| `NULL` | 空值 |
| `INTEGER` | 整数（1, 2, 3, 4, 6, 8 字节，按值大小自动选） |
| `REAL` | 浮点数（IEEE 754 8 字节） |
| `TEXT` | 文本（UTF-8 / UTF-16） |
| `BLOB` | 二进制大对象，按输入原样存放 |

### 3.2 Type Affinity（推荐类型）

建表时声明的类型会被映射成一种亲和类型，控制值的转换行为：

| 声明类型示例 | 亲和类型 |
|---|---|
| `INT`, `INTEGER`, `TINYINT`, `BIGINT` | INTEGER |
| `CHAR`, `VARCHAR`, `TEXT`, `CLOB` | TEXT |
| `REAL`, `DOUBLE`, `FLOAT` | REAL |
| `BLOB`（无参数） | BLOB |
| 其他 | NUMERIC（会尝试存为 INTEGER / REAL / TEXT） |

> **关键启示**：声明 `VARCHAR(255)` 并不限制长度，也不能靠它保证类型——SQLite 真的不在乎列声明。约束要靠 `CHECK` 显式写。
> 详细规则：[SQLite 数据类型 | 菜鸟教程](https://www.runoob.com/sqlite/sqlite-data-types.html)

---

## 4. Python `sqlite3` 集成示例

Python 标准库自带 `sqlite3`，无需安装额外依赖。

```python
import sqlite3

# 1. 连接（文件不存在会自动创建）
conn = sqlite3.connect("demo.db")
cur = conn.cursor()

# 2. 建表
cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT    NOT NULL,
        age   INTEGER
    )
""")

# 3. 插入
cur.execute("INSERT INTO user (name, age) VALUES (?, ?)", ("alice", 30))
conn.commit()

# 4. 查询
for row in cur.execute("SELECT id, name, age FROM user"):
    print(row)

# 5. 关闭
conn.close()
```

> 用 `with sqlite3.connect(...) as conn:` 可以自动 commit / 关闭，更安全。

---

## 5. 常见使用注意

- **不要把 SQLite 用成"客户端-服务器"数据库**：没有网络协议，要远程访问得自己加一层服务（litestream、rqlite 等）。
- **并发写会排队**：写锁是数据库级的，N 个并发写会串行化，读不受影响。
- **写性能不是瓶颈**：单线程下 SQLite 写入其实非常快，瓶颈在并发写和磁盘随机 IO。
- **备份 = 拷贝文件**：可以用 `VACUUM INTO 'backup.db'` 做一致性的在线备份（推荐用这条，不要直接 cp）。
- **类型不严**：查询时可以用 `typeof(x)` 看实际存储类，避免依赖列声明做判断。

---

## 关联笔记

- MySQL：[MySQL笔记](../mysql/MySQL笔记.md)
- PostgreSQL：[PostgreSQL笔记](../postgresql/PostgreSQL笔记.md)
- 横向对比与选型：[关系型数据库选型对比笔记](/blog/关系型数据库选型对比笔记)