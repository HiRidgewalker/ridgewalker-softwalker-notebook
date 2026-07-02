# Docker Compose 笔记

> 来自 [[Hub/01_Docker笔记]] 的"Compose 编排"章节。原笔记保留在 `文档/Docker Compose.md` 供回溯。

Docker Compose 用一个 YAML 文件定义**一组关联容器**（多服务网络 + 卷），一键启动。

---

## 1. v1 vs v2（重要）

| | v1（`docker-compose`） | v2（`docker compose`，空格） |
| --- | --- | --- |
| 命令 | `docker-compose up` | `docker compose up` |
| 形态 | 独立 Python 工具 | Docker CLI 的子命令（Go 实现） |
| Compose 文件 | `docker-compose.yml`（默认名） | `compose.yml` 或 `docker-compose.yml` |
| 现状 | 已停止维护 | 当前主推 |

> **新项目用 v2**（`docker compose`）。本笔记后续示例默认 v2。

---

## 2. 文件结构

### 2.1 顶层字段

```yaml
version: "3.9"           # 可选，v2 推荐省略
name: my-stack          # 项目名（替代默认目录名）

services:               # 必填
  web:
    ...
  db:
    ...

networks:               # 可选
  ...

volumes:                # 可选
  ...

configs:                # 可选（swarm 用）
  ...

secrets:                # 可选（swarm 用）
  ...
```

### 2.2 一个最小例子

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "8080:80"
```

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
docker compose down
```

---

## 3. service 配置详解

### 3.1 镜像与构建

```yaml
services:
  api:
    # 方式 1：用现成镜像
    image: myapi:v1.0

    # 方式 2：从 Dockerfile 构建
    build:
      context: ./              # 构建上下文
      dockerfile: Dockerfile   # 相对 context
      args:
        VERSION: "1.0"         # --build-arg 参数
      target: builder          # 多阶段构建的目标 stage

    # 方式 3：构建 + tag 同时生效
    image: myapi-built:local
    build: .
```

### 3.2 端口映射

```yaml
ports:
  - "8080:80"                 # "主机:容器"
  - "127.0.0.1:8080:80"       # 只对本地回环开放
  - "8080:80/tcp"             # 指定协议
  - "8080-8090:8080-8090"     # 端口范围
  - "53:53/tcp"
  - "53:53/udp"
```

### 3.3 环境变量

```yaml
environment:
  - DEBUG=true
  - DATABASE_URL=postgres://db/mydb
  - TZ=Asia/Shanghai

env_file:
  - .env                       # 从文件读（一行一个 KEY=value）
```

```bash
# .env 文件
DEBUG=true
POSTGRES_PASSWORD=secret
```

> Compose 会自动加载项目根目录的 `.env` 文件到环境变量。

### 3.4 数据卷挂载（参见 [[Hub/03_Docker数据卷与挂载笔记]]）

```yaml
volumes:
  # 命名卷（Docker 管理）
  - dbdata:/var/lib/postgresql/data

  # bind mount（开发期）
  - ./src:/app/src

  # bind mount 长写法（更明确）
  - type: bind
    source: ./init.sql
    target: /docker-entrypoint-initdb.d/init.sql
    read_only: true

  # tmpfs
  - type: tmpfs
    target: /tmp
    tmpfs:
      size: 100m
```

顶层声明卷：

```yaml
volumes:
  dbdata:
    driver: local
    driver_opts:
      type: none
      device: /mnt/fast-ssd/db
      o: bind
```

### 3.5 网络

```yaml
networks:
  frontend:
  backend:

services:
  web:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend
```

> 同一网络内服务可通过**服务名**互相访问（如 `db:5432`）。

### 3.6 启动顺序：depends_on

```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy   # 等 db 健康再启动 web
      redis:
        condition: service_started
```

- 默认 `depends_on` 只等**容器启动**，不等"服务可用"
- `condition: service_healthy` 配合下面 `healthcheck` 才算真等

### 3.7 健康检查

```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 30s
```

### 3.8 重启策略

```yaml
restart: "no"              # 默认
restart: always           # 总是
restart: on-failure        # 失败才
restart: unless-stopped    # 推荐（生产）
```

### 3.9 资源限制

```yaml
deploy:                      # 主要 Swarm 用，Compose 局部也支持
  resources:
    limits:
      cpus: "1.5"
      memory: 512M
    reservations:
      cpus: "0.5"
      memory: 256M

# 简单方式（Compose 局部）：
mem_limit: 512m
cpus: 1.5
```

### 3.10 命令、入口、用户

```yaml
entrypoint: ["python"]
command: ["app.py", "--port=8080"]
user: "1000:1000"           # UID:GID
working_dir: /app
```

### 3.11 完整 service 示例

```yaml
services:
  api:
    build:
      context: .
      args:
        VERSION: "1.2"
    image: myapi:1.2
    container_name: myapi
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Shanghai
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/mydb
    volumes:
      - ./logs:/app/logs
    networks:
      - appnet
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 1G
```

---

## 4. networks 顶层配置

```yaml
networks:
  default:                  # 隐式存在
    driver: bridge
  appnet:
    driver: bridge
    name: my-app-net        # 自定义真实网络名
    ipam:
      config:
        - subnet: 172.30.0.0/16
          gateway: 172.30.0.1
```

---

## 5. volumes 顶层配置

```yaml
volumes:
  dbdata:                          # 匿名/具名卷
  cache:
    driver: local
    driver_opts:
      type: tmpfs
      device_size: 200m
  shared-from-other-stack:         # 引用外部已存在的卷
    external: true
    name: other-stack_dbdata
```

---

## 6. Compose 命令速查（v2）

```bash
# 启动
docker compose up -d                       # 后台
docker compose up                          # 前台 + 看日志
docker compose up --build                  # 启动前构建
docker compose up --force-recreate         # 删旧容器重建

# 查看
docker compose ps                          # service 状态
docker compose ps -a                       # 含停止的
docker compose logs -f                     # 所有 service 日志
docker compose logs -f api                 # 某个 service
docker compose top                         # 容器内进程

# 操作
docker compose start/stop/restart [srv]   # 启停
docker compose exec api bash              # 进容器
docker compose run --rm api python manage.py migrate   # 临时跑命令
docker compose run api env                 # 看环境变量

# 构建
docker compose build                       # build 所有有 build 配置的
docker compose build api                   # 只 build api
docker compose pull                        # 拉所有 image

# 清理
docker compose down                        # 停 + 删容器、网络
docker compose down -v                     # 还删卷（小心！）
docker compose down --rmi all              # 还删镜像
docker compose down --remove-orphans       # 删 stack 中无引用的容器
```

---

## 7. 实战案例：web + postgres + redis

### 7.1 项目结构

```text
myproject/
├── compose.yml
├── .env
├── app/
│   ├── Dockerfile
│   └── ...
└── init.sql
```

### 7.2 `compose.yml`

```yaml
name: myproject

services:
  web:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://appuser:${POSTGRES_PASSWORD}@db:5432/mydb
      REDIS_URL: redis://redis:6379/0
      TZ: Asia/Shanghai
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: mydb
    volumes:
      - dbdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "appuser", "-d", "mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - backend
    restart: unless-stopped

volumes:
  dbdata:
  redisdata:

networks:
  backend:
    driver: bridge
```

### 7.3 `.env`

```bash
POSTGRES_PASSWORD=your-strong-password
```

### 7.4 `app/Dockerfile`

参见 [[Hub/04_Dockerfile笔记]] 中的 Python 应用示例。

### 7.5 操作

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
docker compose exec db psql -U appuser -d mydb
docker compose down           # 保留卷
docker compose down -v        # 不保留
```

---

## 8. 常见坑点

### 8.1 服务名才是主机名

容器间访问用 `http://api:8080` 而不是 IP，因为每次启动 IP 会变。

### 8.2 depends_on 不等健康

`depends_on` 默认等容器**启动**；要等服务可用，得加 `condition: service_healthy` 配合 `healthcheck`。

### 8.3 删除时的取舍

| 命令 | 容器 | 网络 | 卷 | 镜像 |
| --- | --- | --- | --- | --- |
| `down` | ✅ | ✅ | ❌ | ❌ |
| `down -v` | ✅ | ✅ | ✅ | ❌ |
| `down --rmi all` | ✅ | ✅ | ❌ | ✅ |

> -v 是**数据刺客**。生产环境慎重；日常开发加 -v 干净重启。

### 8.4 端口冲突

```bash
# ./8000:8000
# Error: bind: address already in use
# 解决：改端口或停占用端口的进程
```

### 8.5 `.env` 优先级

Compose 加载顺序：

1. shell 环境变量（最高优先）
2. `compose.yml` 所在目录的 `.env`
3. 字段默认值

### 8.6 `ports` vs `expose`

- `ports`：把端口发布到**主机**（也能让其他网络可达）
- `expose`：只在服务的容器内网络暴露，主机和其他容器看不到

### 8.7 多 compose 文件拆分

```bash
docker compose -f compose.yml -f compose.override.yml up -d
```

```yaml
# compose.override.yml（开发期覆盖）
services:
  web:
    volumes:
      - ./src:/app/src    # 实时同步代码
```

### 8.8 Profile（按场景启子集）

```yaml
services:
  web:
    profiles: [frontend]
  db:
    profiles: [backend]
  nginx:
    profiles: [proxy]
```

```bash
docker compose --profile frontend --profile backend up -d
```

适合："有 / 没有 nginx"、"有 / 没有调试工具"的开关。

---

## 9. 一句话总结

- Compose 是**单机多容器**的编排工具；多机用 Swarm/K8s。
- 开发期用 bind mount 同步代码 + named volume 持久化数据。
- 一定要配 `healthcheck` + `depends_on: condition: service_healthy`，否则启动顺序乱串。
- `.env` 管秘密 / 配置；`compose.yml` 不要写密码。