---
title: "Docker 镜像、容器与网络"
sidebar_position: 2
---

# Docker 镜像、容器与网络

> 来自 [I_Docker笔记](./I_Docker笔记.md) 的命令详解章节。旧稿目录已清理，当前以本文为准。

---

## 1. 镜像（Image）

### 1.1 镜像的本质

镜像是一个**只读的分层文件系统**（UnionFS）。每一层是上一个层的一个增量修改，所有层叠加构成最终的文件系统视图。

```text
┌────────────────────────┐
│   Layer 5: app code    │  ← 你 COPY 的源码
├────────────────────────┤
│   Layer 4: pip install │  ← 装的依赖
├────────────────────────┤
│   Layer 3: python:3.11 │  ← 基础镜像
├────────────────────────┤
│   Layer 2: base image  │
└────────────────────────┘
```

> 分层带来两个关键收益：**复用**（不同镜像可共享基础层）+ **缓存**（构建时未变的层直接复用）。

### 1.2 镜像命名规范

```text
[registry/][namespace/]<name>[:<tag>]
```

- `nginx` → `docker.io/library/nginx:latest`（默认）
- `mysql:8.0` → 指定 tag（推荐生产用固定 tag，不要用 `latest`）
- `registry.cn-hangzhou.aliyuncs.com/myteam/myapp:v1.2` → 私有仓库

### 1.3 镜像命令详解

```bash
# 拉取
docker pull nginx:1.27                 # 默认走 docker.io
docker pull registry.cn-hz.com/myimg:v1 --platform linux/amd64  # 多平台镜像指定

# 本地管理
docker images                          # 列表
docker images -a                       # 含中间层
docker images --filter "dangling=true" # 看悬空镜像（无 tag）
docker image prune                     # 删悬空
docker image prune -a                  # 删所有未被容器使用的镜像
docker rmi nginx:1.27                   # 按 name:tag 删
docker rmi $(docker images -q)         # 全删（危险）

# 打标签（用于推送）
docker tag myapp:local registry.example.com/team/myapp:v1.0

# 推送 / 拉取
docker push registry.example.com/team/myapp:v1.0
docker pull registry.example.com/team/myapp:v1.0

# 导出 / 导入（用于离线传输）
docker save -o myapp.tar myapp:v1
docker load -i myapp.tar

# 查构建历史
docker history myapp:v1                # 看每层大小 + 命令

# 查元数据
docker inspect myapp:v1                 # JSON 格式详细
docker inspect --format '{{.Architecture}}' myapp:v1
```

### 1.4 镜像 vs 容器关系

```text
镜像（只读模板）  ─── docker run ───▶  容器（运行实例 + 顶层可写层）
                                              │
                                              └── docker commit ──▶ 新镜像
```

- 容器是基于镜像的运行实例，**多容器可共享同一镜像**（如 mysql 启两个实例）
- 修改容器不会影响原镜像；要固化修改用 `docker commit`（一般不推荐，应该用 Dockerfile）

---

## 2. 容器（Container）

### 2.1 容器生命周期

```text
   created ──▶ running ──▶ paused ──▶ stopped ──▶ removed
       │           │           │          │
       └── docker rm           └── docker rm（先 stop）
```

| 状态 | 含义 | 触发 |
| --- | --- | --- |
| `created` | 已创建未启动 | `docker create` |
| `running` | 运行中 | `docker start` |
| `paused` | 暂停（cgroup freezer） | `docker pause` |
| `exited` | 停止 | 容器内主进程退出 |
| `dead` | 异常 | 需 `docker rm -f` |

### 2.2 容器命令详解

#### 创建与启动

```bash
# docker run = create + start + attach 前台
docker run -d --name web nginx:1.27               # 后台
docker run -it --rm alpine:latest sh              # 交互式，退出即删
docker run -d --name db \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

# --restart 策略
--restart no                  # 默认，退出不重启
--restart on-failure          # 非 0 退出才重启
--restart on-failure:5        # 最多重试 5 次
--restart always              # 总是重启（daemon 启动也拉起）
--restart unless-stopped      # always，但手动 stop 的不会重启（生产推荐）
```

#### 查看与日志

```bash
docker ps                     # 运行中
docker ps -a                  # 全部
docker ps -q                  # 只输出 ID
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"

docker logs web               # 看日志
docker logs -f web            # 实时跟踪（类似 tail -f）
docker logs --tail 100 web    # 最后 100 行
docker logs --since "1h" web  # 最近 1 小时
```

> **时区问题**：`docker logs` 默认 UTC。如果容器内部是 UTC 时间，需要：
> - 容器启动时 `-e TZ=Asia/Shanghai`（镜像支持的话）
> - 或宿主机跑 `docker run -e TZ=Asia/Shanghai ...`

#### 进入容器与文件传输

```bash
docker exec -it web bash       # 进容器开 bash
docker exec -it web sh         # alpine 镜像只有 sh
docker exec web ps aux         # 不进 shell，直接执行命令
docker exec -u root -it web bash  # 以 root 进入（普通用户镜像）

docker cp web:/etc/nginx/nginx.conf ./   # 容器 → 主机
docker cp ./index.html web:/usr/share/nginx/html/  # 主机 → 容器
```

#### 启停 / 删除

```bash
docker start web               # 启动已停止的
docker stop web                # 优雅停止（SIGTERM → 10s 后 SIGKILL）
docker kill web                # 强杀（SIGKILL）
docker restart web             # 重启
docker rm web                  # 删停止的容器
docker rm -f web               # 强制删（运行中也能）
docker rm $(docker ps -aq)     # 删所有容器（危险）

docker container prune         # 清理所有停止的
```

#### 资源监控与元数据

```bash
docker stats                   # 实时 CPU / 内存 / 网络（类似 top）
docker stats --no-stream       # 一次性输出
docker top web                 # 容器内进程
docker inspect web             # JSON 全量元数据
docker inspect --format '{{.NetworkSettings.IPAddress}}' web  # 取某字段
```

#### 提交容器为镜像（不推荐）

```bash
docker commit web myweb:v1     # 把容器当前状态保存为新镜像
```

> ⚠️ commit 出来的镜像无法追溯修改历史，**生产环境应使用 Dockerfile 重建**。commit 只用于调试临时场景。

### 2.3 容器常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 容器启动后立刻退出 | 前台进程（CMD）执行完即退出 | 加 `-d` 或确保 CMD 是前台服务 |
| `docker exec` 报 `executable file not found` | 镜像里没有 `bash`（如 alpine） | 改用 `sh` |
| 修改容器内文件，重启后丢失 | 容器可写层不持久化 | 用挂载卷（见 [III_Docker数据卷与挂载笔记](./III_Docker数据卷与挂载笔记.md)） |
| 容器与宿主机时区不一致 | 默认 UTC | `-e TZ=Asia/Shanghai` 或挂载 `/etc/localtime` |
| `cannot connect to the Docker daemon` | daemon 没启动或当前用户无权限 | `sudo systemctl start docker` + 加 docker 组 |

---

## 3. 网络（Network）

### 3.1 核心概念

Docker 网络用来让**容器之间、容器与宿主机、容器与外部**通信。本质是宿主机上的虚拟网桥 + veth pair。

### 3.2 网络模式对比

| 模式 | 说明 | 适用场景 |
| --- | --- | --- |
| **bridge**（默认） | 虚拟网桥，容器有独立 IP，通过 NAT 访问外网 | 单主机多容器 |
| **host** | 容器直接用宿主机网络栈，无隔离 | 高性能 / 需要容器绑特定端口 |
| **none** | 无网络，仅 lo | 极端隔离场景 |
| **container:\<id\>** | 共享另一个容器的网络栈 | sidecar 模式 |
| **custom bridge**（用户创建） | 可手工指定子网、网关 | 多容器需要互通且易命名 |
| **overlay** | 跨主机网络 | Swarm / 多机集群 |
| **macvlan** | 给容器分配独立 MAC，像物理设备 | 需要容器在局域网中可见 |

### 3.3 网络命令详解

```bash
# 列表与创建
docker network ls
docker network create my-net                           # 默认 bridge 驱动
docker network create --driver bridge \
    --subnet 172.20.0.0/16 \
    --gateway 172.20.0.1 \
    my-net                                              # 指定子网
docker network create --driver overlay my-overlay      # Swarm 用

# 容器接入 / 离开
docker network connect my-net web                      # 已运行容器接入
docker network disconnect my-net web

# 启动时指定网络
docker run -d --network my-net --name api myapi
docker run -d --network host --name ng nginx           # host 模式

# 查详情
docker network inspect my-net
docker network inspect --format '{{range .Containers}}{{.Name}} {{end}}' my-net

# 清理
docker network rm my-net
docker network prune                                    # 清理无用网络
```

### 3.4 容器间通信

**同一自定义网络**：

```bash
docker network create my-net
docker run -d --network my-net --name db postgres:16
docker run -d --network my-net --name api myapi
# api 内可用主机名 db 直接访问
```

**默认 bridge 网络**：容器间只能用 IP 互通，**不能用容器名**（DNS 解析需用自定义网络）。

> **最佳实践**：所有需要互相通信的容器放在**同一个用户自定义 bridge 网络**中，自动获得 DNS 解析。

### 3.5 端口映射详解

```bash
-p 8080:80           # 主机 8080 → 容器 80（指定 TCP）
-p 8080:80/tcp       # 同上显式
-p 8080:80/udp       # UDP
-p 127.0.0.1:8080:80 # 只绑本地回环（外部访问不到）
-p 8080:80 -p 8443:443  # 多个端口
-P                   # 把镜像 EXPOSE 的所有端口随机映射到主机
```

### 3.6 实战：fastapi + postgres 互通

```bash
docker network create app-net

docker run -d --name db \
  --network app-net \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

docker run -d --name api \
  --network app-net \
  -e DATABASE_URL=postgresql://postgres:secret@db:5432/postgres \
  -p 8000:8000 \
  myapi:latest

# api 容器内用主机名 "db" 直接连 postgres
```

> 多服务编排更推荐用 Docker Compose（见 [V_Docker Compose笔记](./V_Docker%20Compose笔记.md)），但手写网络是这个的底子。

---

## 4. 常用工具命令

```bash
# 看镜像 / 容器 / 卷占空间
docker system df

# 一键清理（停掉所有容器，删未用镜像/网络/卷，加 -a 连无容器用的镜像也删）
docker system prune
docker system prune -a --volumes

# 看 docker 信息摘要
docker info

# 查看本地 docker 版本
docker version

# 实时事件流
docker events --since "10m"
```
