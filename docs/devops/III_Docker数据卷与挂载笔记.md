---
title: "Docker 数据卷与挂载专题"
sidebar_position: 3
---

# Docker 数据卷与挂载专题

> 来自 [I_Docker笔记](./I_Docker笔记.md) 的"卷"章节。旧稿目录已清理，当前以本文为准。

本篇专注于**容器数据持久化**——三种挂载方式的对比、选型决策、坑点。

---

## 1. 为什么需要挂载

容器默认使用**联合文件系统**，所有改动都在最上层的"可写层"里。**容器被删除 = 可写层丢失 = 数据全没**。

要把数据"持久化"或"共享"出来，必须挂载来自**宿主机**或**外部存储**的目录。

---

## 2. 三种挂载方式对比

### 2.1 总览

| 方式 | 物理位置 | 管理方 | 适合 |
| --- | --- | --- | --- |
| **bind mount** | 宿主机任意路径 | 用户 | 开发期代码同步、读主机配置 |
| **named volume** | Docker 管理的目录（如 `/var/lib/docker/volumes/`） | Docker | 生产环境数据库、用户上传 |
| **tmpfs** | 宿主机内存 | Docker | 敏感临时文件、缓存 |

### 2.2 选型决策树

```text
要不要数据持久化？
├─ 不需要（纯临时） → tmpfs
│                    （如 /tmp、token、临时缓存）
└─ 需要
   ├─ 是开发期、想让代码/配置改动实时生效？
   │  └─ 是 → bind mount
   │        （源码、配置、SSL 证书）
   └─ 否（生产）
      ├─ 多容器需要共享？
      │  └─ 是 → named volume
      └─ 否 → named volume（推荐）或 bind mount（你想直接管理位置时）
```

### 2.3 三种方式详解

#### Bind Mount

将**宿主机的任意路径**直接挂到容器里，**实时双向同步**。

```bash
# 语法 1：-v（简写，老式）
docker run -d -v /host/path:/container/path:ro nginx
#                                  ^^  ro = 只读

# 语法 2：--mount（推荐，类型明确）
docker run -d --mount type=bind,source=/host/path,target=/container/path,readonly nginx

# 实战：开发期把源码挂进容器
docker run -d --name dev \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/tests:/app/tests \
  myapp
```

**特点**：

- ✅ 高性能（直接绕过 unionFS）
- ✅ 主机改文件 → 容器里立刻可见
- ⚠️ 路径必须存在，否则容器启动失败（可加 `:delegated` 等选项放宽）
- ⚠️ 不同主机路径不固定，迁移困难

#### Named Volume

Docker 自己管理的卷，存在 `/var/lib/docker/volumes/<name>/_data`（默认存储驱动）。

```bash
# 显式创建
docker volume create pgdata
docker volume ls
docker volume inspect pgdata

# 启动时自动创建（-v 形式）
docker run -d -v pgdata:/var/lib/postgresql/data postgres:16
#                      └─ 卷名存在则挂，不存在则自动创建

# 启动时自动创建（--mount 形式）
docker run -d --mount source=pgdata,target=/var/lib/postgresql/data postgres:16
```

**特点**：

- ✅ Docker 管理，可备份/迁移（`docker volume` 命令齐全）
- ✅ 跨主机路径无关
- ✅ 容器删除后**卷默认保留**
- ⚠️ 不直接对主机暴露目录（要 `docker volume inspect` 看路径）

#### tmpfs

完全在**内存**里，容器停 = 数据消失。

```bash
docker run -d --tmpfs /tmp nginx              # 老式
docker run -d --mount type=tmpfs,destination=/app/cache,tmpfs-size=100m \
  myapp
```

**特点**：

- ✅ 速度极快（内存 IO）
- ✅ 敏感数据不留痕
- ⚠️ 容器停即丢
- 仅限 Linux，不支持 WSL2/macOS 原生（macOS 上 tmpfs 实现在 VM 内存）

---

## 3. 三种声明语法对比

### 3.1 CLI 形式（`docker run`）

| 语法 | 例子 | 说明 |
| --- | --- | --- |
| `-v 宿主机路径:容器路径` | `-v /host:/container` | bind mount |
| `-v 卷名:容器路径` | `-v pgdata:/data` | named volume |
| `--mount type=bind,source=...,target=...` | 完整路径 | bind mount（显式） |
| `--mount source=...,target=...` | 不写 type | 默认为 volume |
| `--mount type=tmpfs,destination=...` | 内存卷 | tmpfs |

> **区别**：`--mount` 比 `-v` 更严格、报错信息更清楚。生产推荐 `--mount`。

### 3.2 Compose 形式（`docker-compose.yml`）

```yaml
volumes:
  # 引用已存在的命名卷
  pgdata:
    external: true

services:
  db:
    image: postgres:16
    volumes:
      # 命名卷（Docker 管理）
      - pgdata:/var/lib/postgresql/data

      # bind mount（长写法更清晰）
      - type: bind
        source: ./init.sql
        target: /docker-entrypoint-initdb.d/init.sql
        read_only: true

      # tmpfs（仅 Linux）
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100m
```

---

## 4. 易踩坑点

### 4.1 容器删除 ≠ 卷删除（来自原 `Docker.md`）

**默认行为**：

- 容器删除时，**具名卷和匿名卷都保留**。
- **bind mount** 因为是宿主机路径，容器删了也一直在。
- 只有 `docker run ... --rm` + 匿名卷的组合才会在容器删除时自动清卷（因为 `--rm` 会清理容器相关资源）。

```bash
# 容器 + 命名卷
docker run -d -v pgdata:/data postgres  # 容器 rm 后卷还在
docker volume ls                         # 仍能看到 pgdata

# 用 docker compose down -v 才会一起删
docker compose down -v                   # 注意 -v 会把卷也删掉
```

> 这就是为什么"重启容器数据还在"——只要卷还在。

### 4.2 同名软件 ≠ 数据卷自动关联（来自原 `Docker.md`）

```bash
# 第一次
docker run -d --name redis1 -v redisdata:/data redis
# 写入一些 key 后停掉
docker stop redis1 && docker rm redis1

# 第二次，用同一镜像开 redis2，不指定卷
docker run -d --name redis2 redis        # 不会自动挂载 redisdata！

# Redis 启动后会看到全新的空数据库
```

**正确做法**：第二次也必须显式挂上同一个卷：

```bash
docker run -d --name redis2 -v redisdata:/data redis
```

> Docker **不会**主动扫描历史卷并加载。命名卷只是"目录的标签"，挂载与否完全取决于 run 时有没有指定。

### 4.3 bind mount 覆盖容器原有目录

```bash
# 容器 /data 原来有文件
docker run -v /host/empty:/data alpine ls /data   # 空目录

# ⚠️ 宿主机的空目录会"覆盖"容器内目录的内容
# 容器内原本的文件看不见了
```

解决：把宿主机目录先准备好，或用 tmpfs/named volume。

### 4.4 文件权限问题

容器内进程以什么 UID 运行？宿主机目录是什么权限？

```bash
# 查看容器内用户
docker exec web id

# 让容器用宿主机 UID 运行
docker run -u $(id -u):$(id -g) -v $(pwd):/app myapp
```

### 4.5 `:ro` 还是 `:rw`（默认）

```bash
-v /host/config:/etc/app/config:ro   # 容器只读该配置，推荐配置用 ro
```

### 4.6 volumes vs bind mounts 在镜像构建里

```dockerfile
# Dockerfile 里只能写 VOLUME，不能写 bind mount
VOLUME ["/data"]   # 告诉 Docker 这是"外部挂载点"，运行时随机分配匿名卷
```

> 不能在 Dockerfile 里 bind mount 是故意的——保持镜像的可移植性。

---

## 5. 实战案例

### 5.1 mysql（来自原笔记）

```bash
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -e TZ=Asia/Shanghai \
  -e MYSQL_ROOT_PASSWORD=root \
  -v mysqldata:/var/lib/mysql \
  mysql:8.0
```

- `-v mysqldata:/var/lib/mysql`：命名为 mysqldata 的卷，避免容器删除丢数据。
- `-e TZ=Asia/Shanghai`：时区对齐。

### 5.2 redis（来自原笔记）

```bash
docker run \
  -v /home/docker-volume/redis/conf:/usr/local/etc/redis \
  -v redisdata:/data \
  -p 6379:6379 \
  --name redis \
  -d \
  dockerproxy.cn/redis:7.4 \
  redis-server /usr/local/etc/redis/redis.conf
```

> ⚠️ 这里混用了 bind mount（配置目录，**开发场景**用）和 named volume（数据目录，**生产要求持久化**）。

### 5.3 多卷挂载 + 工作目录（来自原笔记）

```bash
docker run -p 80:5000 \
  --mount type=bind,source=/home/user-one/pu-word-volume/docling-volume/tmp,target=/tmp \
  --mount type=bind,source=/home/user-one/pu-word-volume/docling-volume/models,target=/app/models \
  --mount type=bind,source=/home/user-one/pu-word-volume/static,target=/app/static \
  docling-basic-image:1.0 bash
```

三处模型/缓存/静态文件全部 bind mount 到主机，方便重建容器时数据还在。

### 5.4 备份与恢复 named volume

```bash
# 备份：把卷打包成 tar
docker run --rm \
  -v pgdata:/source:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/pgdata.tar.gz -C /source .

# 恢复：解压到新卷
docker volume create pgdata_new
docker run --rm \
  -v pgdata_new:/target \
  -v $(pwd):/backup \
  alpine tar xzf /backup/pgdata.tar.gz -C /target
```

### 5.5 跨主机迁移卷

```bash
# 主机 A
docker run --rm -v pgdata:/from -v $(pwd):/to alpine \
  tar czf /to/pgdata.tar.gz -C /from .

# 主机 B
docker volume create pgdata
docker run --rm -v pgdata:/to -v $(pwd):/from alpine \
  tar xzf /from/pgdata.tar.gz -C /to
```

> 跨主机更优雅的做法是用 volume driver（NFS / EBS / Ceph 等）或迁移到外部存储。

---

## 6. 数据卷命令速查

```bash
docker volume ls                                    # 所有卷
docker volume ls --filter "dangling=true"           # 孤儿卷
docker volume create myvol                          # 创建
docker volume create --driver local myvol           # 指定驱动（一般默认）
docker volume inspect myvol                         # 查详情（路径、驱动）
docker volume rm myvol                              # 删
docker volume prune                                 # 清理孤儿（被引用则不会删）

# 系统级清理（注意会删孤儿卷）
docker system prune --volumes
```

---

## 7. 一句话总结

- **开发**：bind mount（代码同步） + named volume（DB 数据）
- **生产**：named volume 主 + bind mount（配置）作为辅
- **临时**：tmpfs（敏感数据）
- **避免**：容器内有数据却不挂卷（删容器必丢数据）
