---
title: "Dockerfile 笔记"
sidebar_position: 4
---

# Dockerfile 笔记

> 来自 [I_Docker笔记](./I_Docker笔记.md) 的"Dockerfile 编写"章节。旧稿目录已清理，当前以本文为准。

Dockerfile 是 Docker 镜像的"源文件"，通过 `docker build` 生成镜像。**生产环境容器应该全部由 Dockerfile 构建**，而不是 `docker commit`。

---

## 1. 基础语法

### 1.1 格式

```dockerfile
# 注释以 # 开头
INSTRUCTION arguments

# 不区分大小写（约定大写区分指令和小写参数）
FROM ubuntu:22.04
```

### 1.2 构建命令

```bash
docker build -t myapp:v1 .              # . 表示当前目录找 Dockerfile
docker build -t myapp:v1 -f Dockerfile.prod .
docker build --build-arg VERSION=1.2 -t myapp:v1 .   # 传构建参数
docker build --no-cache -t myapp:v1 .               # 强制全量重建
docker build --pull -t myapp:v1 .                   # 总是拉最新基础镜像
```

### 1.3 构建上下文

```text
docker build -t myapp:v1 .
                       ↑
       构建上下文根目录（build context）
       当前 . 中的所有文件都会被打包传给 daemon
```

> ⚠️ 上下文太大 = 构建慢。用 `.dockerignore` 排除。

```.dockerignore
.git
node_modules
__pycache__
*.pyc
.venv
.env
README.md
tests
docs
```

---

## 2. 指令详解（按使用频次）

### 2.1 `FROM` — 基础镜像

```dockerfile
FROM ubuntu:22.04
FROM python:3.12-slim
FROM node:20-alpine
FROM scratch                    # 空镜像，做超小二进制
FROM python:3.12-slim AS builder   # 给当前 stage 起名（多阶段构建用）
```

> **永远显式指定 tag**。不要用 `latest`，不可复现。

### 2.2 `RUN` — 执行命令

```dockerfile
# shell 形式（默认 /bin/sh -c）
RUN apt-get update && apt-get install -y curl

# exec 形式（推荐，避免 shell 字符串解析问题）
RUN ["apt-get", "install", "-y", "curl"]

# 多行用 && 串联，避免无用中间层
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

### 2.3 `COPY` 与 `ADD`

```dockerfile
COPY ./src /app/src
COPY package.json package-lock.json /app/
COPY . /app/                # 配合 .dockerignore 防止误拷

# ADD 多了两个特性（一般用不到）：
#   1. 自动解压（target 必须是目录）
#   2. 支持 URL / tar
ADD https://example.com/file.tar.gz /tmp/

# ⚠️ 优先用 COPY，避免 ADD 的"隐式行为"
```

### 2.4 `CMD` — 容器启动命令

```dockerfile
# shell 形式
CMD python app.py

# exec 形式（推荐，更清晰）
CMD ["python", "app.py"]

# 作为 ENTRYPOINT 参数
CMD ["--port=8080"]
```

- 只能有**一个** `CMD`，多写只生效最后一个
- `docker run myapp arg1` 里的参数会**覆盖 `CMD`**
- 与 `ENTRYPOINT` 一起用见下文

### 2.5 `ENTRYPOINT` — 不可覆盖的启动命令

```dockerfile
ENTRYPOINT ["python", "app.py"]

# 此时 docker run myapp --port=8080
# 实际执行：python app.py --port=8080
```

| | CMD | ENTRYPOINT |
| --- | --- | --- |
| 默认值 | `["python", "app.py"]` | `["python"]` |
| `docker run myapp a b` → | `python app.py`（a b 被忽略） | `python app.py a b` |

```dockerfile
# 二者组合写法（最常见）
ENTRYPOINT ["python", "app.py"]
CMD ["--port=8080"]     # run 时不传参就默认

# docker run myapp --port=9000 → python app.py --port=9000
```

### 2.6 `ENV` — 环境变量

```dockerfile
ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1
ENV PATH=/app/bin:$PATH

# 运行时同样可以用 -e 覆盖
# docker run -e TZ=UTC myapp
```

### 2.7 `WORKDIR` — 工作目录

```dockerfile
WORKDIR /app
# 之后所有 RUN / CMD / COPY 都以 /app 为基准
# 与 cd 不同：WORKDIR 不会继承父目录
```

### 2.8 `EXPOSE` — 文档性端口声明

```dockerfile
EXPOSE 8080
EXPOSE 8080/tcp
EXPOSE 8080 9090/udp

# 只是声明，不真正发布；运行时要 -p 8080:8080 才能从外面访问
```

### 2.9 `VOLUME` — 匿名挂载点

```dockerfile
VOLUME ["/data"]

# 告诉 Docker 该目录是"外部存储"，运行时随机分配匿名卷
# 不能写具体宿主机路径
```

### 2.10 `USER` — 切换运行用户

```dockerfile
RUN useradd -m appuser
USER appuser
WORKDIR /home/appuser

# 不要用 root 运行业务进程（安全原则）
```

### 2.11 `ARG` / `ENV` — 构建参数

```dockerfile
ARG VERSION=latest
FROM python:3.12-slim
ARG PYTHON_VERSION=3.12
RUN echo "Building version $VERSION with python $PYTHON_VERSION"

# docker build --build-arg VERSION=1.2 .
```

| | ARG | ENV |
| --- | --- | --- |
| 生效范围 | 仅构建期 | 构建期 + 运行时 |
| 可见性 | 仅 build 阶段 RUN 内可见 | 容器运行时亦可见 |

### 2.12 `LABEL` — 元数据

```dockerfile
LABEL maintainer="me@example.com"
LABEL version="1.0"
LABEL org.opencontainers.image.source="https://github.com/foo/bar"
```

### 2.13 `HEALTHCHECK` — 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# docker ps 时显示 (healthy) / (unhealthy)
```

### 2.14 `STOPSIGNAL` — 停止信号

```dockerfile
STOPSIGNAL SIGTERM      # 默认就是 SIGTERM
```

### 2.15 其他指令

- `MAINTAINER`（已废弃）→ 用 `LABEL maintainer=`
- `ONBUILD`（较少用）：在子镜像构建时触发
- `SHELL`：覆盖默认 shell

---

## 3. 多阶段构建

### 3.1 为什么需要

传统做法：单个 Dockerfile，包含编译工具 → 镜像巨大且有攻击面。

多阶段构建：**第一阶段编译**，**第二阶段只拷产物**，最终镜像极小。

### 3.2 实战：Go 应用

```dockerfile
# 阶段 1：编译
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/app .

# 阶段 2：运行
FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=builder /out/app /usr/local/bin/app
EXPOSE 8080
ENTRYPOINT ["app"]
```

最终镜像只有 alpine + 二进制，**通常 < 20MB**。

### 3.3 实战：Python 应用

```dockerfile
# 阶段 1：装依赖到 venv
FROM python:3.12-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 阶段 2：只拷 venv + 代码
FROM python:3.12-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . .
CMD ["python", "app.py"]
```

### 3.4 多阶段命名与复制

```dockerfile
FROM alpine AS stage-a
RUN echo "data-a" > /file-a

FROM alpine AS stage-b
RUN echo "data-b" > /file-b

FROM alpine
COPY --from=stage-a /file-a /file-a
COPY --from=stage-b /file-b /file-b
COPY --from=0 /file-a /file-a     # 用编号也行（0 起步）
```

---

## 4. 构建缓存优化

### 4.1 缓存机制

Docker 按**指令顺序**逐层缓存。某一层发生了变化，**它后面的所有层都失效**。

### 4.2 调整 COPY 顺序（最关键）

```dockerfile
# ❌ 错误：代码一改，前面任何依赖安装都重做
COPY . /app
RUN pip install -r requirements.txt

# ✅ 正确：先放变化少的依赖文件，再做 pip install
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app
```

> 这样改代码不重建依赖层。

### 4.3 合并 RUN

```dockerfile
# ❌ 每次 apt-get install 都是独立层，留缓存
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ 合到一层
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

### 4.4 `--mount=type=cache`（BuildKit）

启用 BuildKit 后可以使用高级缓存：

```dockerfile
# syntax=docker/dockerfile:1.7

FROM golang:1.22
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build ./...
```

BuildKit 缓存持久化到 build 缓存中（可挂到 named volume 跨构建复用）。

启用方式：

```bash
# 方式 1：环境变量
DOCKER_BUILDKIT=1 docker build -t myapp .

# 方式 2：daemon 配置（推荐）
# /etc/docker/daemon.json
{ "features": { "buildkit": true } }
```

### 4.5 镜像体积优化清单

| 手段 | 效果 |
| --- | --- |
| 选小基础镜像（alpine / distroless / scratch） | 几百 MB → 几 MB |
| `--no-install-recommends`（apt） | 减少无用依赖 |
| 多阶段构建 | 编译工具不进最终镜像 |
| `apk add --no-cache`（alpine） | 跳过 apk 索引缓存 |
| `.dockerignore` | 避免构建上下文膨胀 |
| 合并 RUN | 减少冗余层 |
| 清缓存 `rm -rf /var/lib/apt/lists/*` | apt 缓存可几十 MB |

---

## 5. 完整示例

### 5.1 Python Flask

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]
```

### 5.2 Node 应用

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN addgroup -S app && adduser -S app -G app && chown -R app /app
USER app

EXPOSE 3000
CMD ["node", "server.js"]
```

---

## 6. 最佳实践清单

✅ **DO**

- 显式指定 tag（不要 `latest`）
- 用 `.dockerignore` 限制构建上下文
- COPY 顺序：**先变化少的、后变化多的**（解锁缓存）
- 多阶段构建，最终镜像只放运行需要的最小内容
- 用非 root 用户跑应用（`USER` 指令）
- 关键步骤加注释（一段时间后没人记得 `RUN` 在干啥）
- HEALTHCHECK 让编排系统知道容器是否健康
- 依赖清缓存（`rm -rf /var/lib/apt/lists/*` / `--no-cache`）

❌ **DON'T**

- 不要 `apt-get upgrade`（破坏镜像可复现性，由基础镜像更新）
- 不要一个容器塞多个进程（`systemctl start a && systemctl start b`）→ 用 Compose/编排
- 不要把密码/secret 写进 Dockerfile，用 ARG + 运行时 ENV，或者用 secret 管理
- 不要用 `latest`
- 不要 `docker commit` 当做最终交付
- 不要在容器里存数据 → 挂卷

---

## 7. 调试技巧

```bash
# 看镜像历史与每层大小
docker history myapp:v1

# 看具体某层镜像内容（用 builder 镜像）
docker run --rm -it <image-id> sh

# 构建时输出更详细日志（BuildKit）
DOCKER_BUILDKIT=1 docker build --progress=plain -t myapp:v1 .

# 看单个层命令
docker history --no-trunc myapp:v1

# 临时进容器验证
docker run --rm -it myapp:v1 bash   # 镜像里要有 bash
```