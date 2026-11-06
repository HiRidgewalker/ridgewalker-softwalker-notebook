---
title: "Docker 笔记（总览）"
sidebar_position: 1
---

# Docker 笔记（总览）

> 原 旧稿 + 旧稿 + 旧稿 的重新整理版本。结构上分 5 个 Hub 文件：本文是**总览与 CLI 速查**；[II_Docker镜像与容器笔记](./II_Docker镜像与容器笔记.md) 是**镜像/容器/网络命令详解**；[III_Docker数据卷与挂载笔记](./III_Docker数据卷与挂载笔记.md) 是**挂载方案专题**（bind/volume/tmpfs 对比与选型）；[IV_Dockerfile笔记](./IV_Dockerfile笔记.md) 是**Dockerfile 编写**；[V_Docker Compose笔记](./V_Docker%20Compose笔记.md) 是**Compose 编排**。旧稿目录已清理，当前以本文为准。

---

## 1. Docker 是什么

Docker 是一个**容器化引擎**：把应用程序及其依赖（库、运行时、配置）打包成标准化的"镜像"（Image），再以轻量的"容器"（Container）形式运行。

### 与虚拟机对比

| 维度 | 虚拟机 | Docker 容器 |
| --- | --- | --- |
| 隔离级别 | 硬件级（hypervisor） | 操作系统级（内核共享） |
| 启动速度 | 分钟级 | 秒级 |
| 镜像体积 | GB 级 | MB 级 |
| 性能损耗 | 5%~15% | 接近原生 |
| 底层共享 | 每个 VM 独立内核 | 所有容器共享宿主机内核 |

> 一句话：**容器不是虚拟机**，它本质是宿主机上的一个受限进程组。

---

## 2. 核心概念与架构

### 2.1 三大核心对象

- **镜像（Image）**：只读模板，相当于"类"
- **容器（Container）**：镜像的运行实例，相当于"对象"
- **仓库（Registry）**：镜像分发中心（公有 Docker Hub、私有 Harbor 等）

### 2.2 整体架构

```text
┌──────────────────────────────────────────────┐
│              Docker Client（docker CLI）       │
│   docker run / build / pull / compose ...     │
└──────────────────┬───────────────────────────┘
                   │ REST API
┌──────────────────▼───────────────────────────┐
│              Docker Daemon（dockerd）          │
│  ┌────────────┬────────────┬──────────────┐  │
│  │  Images    │ Containers │  Networks    │  │
│  ├────────────┴────────────┴──────────────┤  │
│  │           Volumes / Plugins             │  │
│  └─────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────────────┐
│           Registry（Docker Hub / 私有仓库）     │
└──────────────────────────────────────────────┘
```

### 2.3 核心组件

| 组件 | 作用 |
| --- | --- |
| **Docker Client** | 用户与 Docker 交互的 CLI，发送命令到 Daemon |
| **Docker Daemon（dockerd）** | 核心服务进程，管理镜像/容器/网络/卷 |
| **REST API** | Client 与 Daemon 之间的通信协议 |
| **Docker Engine** | Client + Daemon + REST API 的统称 |
| **Registry** | 镜像存储与分发中心 |

### 2.4 工作流程

1. Client 发送命令（如 `docker run`）到 Daemon
2. Daemon 解析命令，检查本地是否有镜像
3. 若无，从 Registry 拉取（`docker pull`）
4. 创建容器并启动
5. 返回结果给 Client

---

## 3. 安装

### 3.1 Linux（官方脚本）

```bash
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER   # 当前用户免 sudo
```

### 3.2 macOS / Windows

直接下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 安装包。

### 3.3 WSL2

参考 [WSL笔记](../wsl/WSL笔记.md)。在 WSL2 里安装 Docker Engine（**不要**装 Docker Desktop），性能更好。

### 3.4 验证

```bash
docker version          # 客户端 + 服务端版本
docker info             # 全局信息（镜像数、容器数、存储驱动等）
docker run hello-world  # 跑一个测试容器
```

### 3.5 配置镜像加速（国内环境）

`/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://dockerproxy.cn",
    "https://mirror.baidubce.com"
  ]
}
```

重启生效：`sudo systemctl restart docker`。

---

## 4. CLI 速查总表

> 完整参数与坑点见 [II_Docker镜像与容器笔记](./II_Docker镜像与容器笔记.md)、[III_Docker数据卷与挂载笔记](./III_Docker数据卷与挂载笔记.md)。

### 4.1 镜像（image）

```bash
docker pull <image>:<tag>           # 拉镜像
docker images                       # 本地镜像列表
docker rmi <image>                  # 删镜像
docker tag <src> <dst>              # 打标签
docker push <image>                 # 推到仓库
docker build -t <name>:<tag> .      # 构建镜像
docker save -o file.tar <image>     # 导出镜像
docker load -i file.tar             # 导入镜像
docker history <image>              # 看镜像分层
docker image prune -a               # 清理无用镜像
```

### 4.2 容器（container）

```bash
docker run [opts] <image> [cmd]     # 创建并启动
docker ps                           # 运行中容器
docker ps -a                        # 所有容器（含停止的）
docker start/stop/restart <name>    # 启停
docker rm <name>                    # 删容器
docker logs -f <name>               # 实时日志
docker exec -it <name> bash         # 进容器
docker cp <name>:/path ./local      # 文件互拷
docker inspect <name>               # 查元数据
docker stats                        # 资源占用
docker container prune              # 清理已停止容器
```

### 4.3 网络（network）

```bash
docker network ls                   # 网络列表
docker network create <name>        # 创建网络
docker network rm <name>            # 删网络
docker network connect <net> <ctr>  # 把容器接入网络
docker network inspect <name>       # 查详情
```

### 4.4 卷（volume）

```bash
docker volume ls                    # 卷列表
docker volume create <name>         # 创建卷
docker volume rm <name>             # 删卷
docker volume inspect <name>        # 查详情
docker volume prune                 # 清理孤儿卷
```

### 4.5 系统类

```bash
docker system df                    # 看磁盘占用
docker system prune                 # 一键清理（停掉容器 + 删无用镜像/网络/卷）
docker system info                  # 等价于 docker info
```

---

## 5. docker run 常用参数速查

| 参数 | 含义 | 常用示例 |
| --- | --- | --- |
| `-d` | 后台运行 | `docker run -d nginx` |
| `-it` | 交互式终端 | `docker run -it ubuntu bash` |
| `--rm` | 容器退出后自动删除 | `docker run --rm alpine echo hi` |
| `--name` | 指定容器名 | `--name my-nginx` |
| `-p` | 端口映射 | `-p 8080:80`（宿主机:容器） |
| `-P` | 随机端口映射（暴露所有 EXPOSE 端口） | |
| `-e` | 环境变量 | `-e MYSQL_ROOT_PASSWORD=root` |
| `-v` | 挂载卷 | `-v /host:/container` |
| `--mount` | 挂载（更规范） | `--mount type=bind,source=...,target=...` |
| `--network` | 指定网络 | `--network my-net` |
| `--restart` | 重启策略 | `always / unless-stopped / on-failure` |
| `-u` | 运行用户 | `-u $(id -u):$(id -g)` |
| `--memory` | 内存限制 | `--memory 512m` |
| `--cpus` | CPU 限制 | `--cpus 1.5` |
| `-w` | 工作目录 | `-w /app` |

---

## 6. 参考链接

- 官方文档：<https://docs.docker.com/>
- 中文教程：<https://www.runoob.com/docker/docker-tutorial.html>
- 镜像仓库：<https://hub.docker.com/>
- CLI 参考：<https://docs.docker.com/reference/cli/docker/>