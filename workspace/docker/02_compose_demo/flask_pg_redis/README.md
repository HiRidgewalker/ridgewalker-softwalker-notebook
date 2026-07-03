# Compose Demo：flask + postgres + redis

对应：[[05_Docker Compose笔记]] 的"实战案例：web + postgres + redis"。

## 文件

- `compose.yml`：编排 web + db + redis 三服务，含 healthcheck + depends_on 启动顺序控制。
- `Dockerfile`：web 服务镜像。
- `app.py`：Flask 应用，演示服务名互通（`db`、`redis` 用作主机名）。
- `.env`：放密码的示例文件。

## 运行

```bash
cd 02_compose_demo/flask_pg_redis

# 启动（后台、构建镜像）
docker compose up -d --build

# 看服务状态
docker compose ps

# 应该看到三列都 healthy / running
# web    -> http://localhost:8000/
# db     -> 通过主机名 "db:5432" 从 web 容器访问
# redis  -> 通过主机名 "redis:6379" 从 web 容器访问

# 验证 Flask 连通
curl http://localhost:8000/
# 会返回 JSON，含 redis_status 和 hits

# 看 web 日志
docker compose logs -f web

# 进 postgres
docker compose exec db psql -U appuser -d mydb

# 进 redis
docker compose exec redis redis-cli ping

# 进 web 容器
docker compose exec web sh

# 清理（含卷）
docker compose down -v
```

## 关键点

- **服务名 = 主机名**：`web` 服务里 `redis://redis:6379/0` 解析到 `redis` 服务
- `depends_on: condition: service_healthy`：等 db 和 redis 健康后再起 web
- **卷持久化**：`pgdata`、`redisdata` 命名卷；用 `docker compose down -v` 才删
- `restart: unless-stopped`：单机 "持久自恢复" 推荐策略
- `${POSTGRES_PASSWORD}` 从 `.env` 解析
