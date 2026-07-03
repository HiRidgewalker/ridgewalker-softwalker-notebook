---
type: hub
topic: API 网关
status: refactored
source: 文档/网关(gateway).md
---

# API 网关笔记

> 原 `文档/网关(gateway).md` 的重写。原笔记仅有 2 个外部链接，本笔记**系统介绍网关的定位、能力、与反向代理的区别**，并**给出一个可运行的 FastAPI 网关 Demo**（4 个中间件 + 路由转发 + 完整流程图）。
>
> 鉴权与登录见 `[[鉴权与登录笔记]]`；权限模型（Casbin / RBAC / ReBAC）见 `[[权限模型笔记]]`。

## 目录

1. 什么是网关 + 为什么需要
2. 网关核心能力清单
3. 网关 vs 反向代理 vs Ingress vs Sidecar
4. 网关选型（Kong / APISIX / Spring Cloud Gateway / 自研）
5. Python FastAPI 网关 Demo 流程图
6. 关键中间件实现要点
7. 生产部署清单
8. 网关常见坑
9. 关联笔记

---

## 1. 什么是网关 + 为什么需要

**API 网关（API Gateway）** 是系统的**唯一对外入口**，所有外部流量先经过网关，再到内部的具体服务。

### 1.1 为什么需要网关

没有网关时：

```
[客户端 A] ──┐
[客户端 B] ──┼──► [用户服务]   各自要处理：鉴权、限流、CORS、日志…
[客户端 C] ──┼──► [订单服务]   重复代码散落在每个服务
             └──► [商品服务]
```

有网关后：

```
[所有客户端] ──► [网关]  ──► [用户服务 / 订单服务 / 商品服务]
                       │
                       └─ 统一处理：鉴权 / 限流 / 路由 / 日志
```

**核心价值**：

- **统一入口**：客户端只需对接网关
- **集中治理**：鉴权、限流、日志、安全策略**一处实现**
- **解耦**：客户端不感知后端服务的拆分 / 合并 / 替换
- **安全**：隐藏内部服务拓扑、过滤恶意请求

### 1.2 网关的常见别名

- **Edge Service**（边缘服务）
- **BFF**（Backend For Frontend，为特定前端定制的网关层）
- **API Gateway**（最常见）
- **Ingress**（K8s 术语）

---

## 2. 网关核心能力清单

| 能力 | 说明 |
|---|---|
| **路由** | 按 path / host / header / query 把请求分发到不同下游 |
| **鉴权** | JWT 校验、OAuth2 introspection、API Key 校验 |
| **限流** | 按 IP / 用户 / 路径 / 租户维度限流 |
| **熔断** | 下游超时或 5xx 比例超阈值时快速失败，避免拖垮 |
| **缓存** | 缓存 GET 响应（Redis / 内存） |
| **日志** | 结构化访问日志、请求 ID 链路追踪 |
| **监控** | QPS / 延迟 / 错误率指标暴露（Prometheus） |
| **协议转换** | HTTP → gRPC / WebSocket / GraphQL |
| **CORS** | 跨域统一处理 |
| **请求改写** | path 重写、header 注入、请求/响应体转换 |
| **安全** | WAF、防 SQL 注入、防爬虫、黑白名单 |

---

## 3. 网关 vs 反向代理 vs Ingress vs Sidecar

| 类型 | 定位 | 典型 |
|---|---|---|
| **反向代理** | 转发请求 + 负载均衡，**运维层** | nginx / HAProxy |
| **API 网关** | 反向代理 + **业务层能力**（鉴权/限流/灰度） | Kong / APISIX / Spring Cloud Gateway |
| **Ingress** | K8s 中的网关抽象（标准 + 多种实现） | Ingress-NGINX / Traefik / Contour |
| **服务网格 Sidecar** | 每个服务实例旁的代理（**东西向流量**） | Envoy + Istio / Linkerd |

**关系**：

- **反向代理 ⊂ API 网关**（网关 = 反向代理 + 业务能力）
- **Ingress ⊂ API 网关**（Ingress 是 K8s 生态的网关实现）
- **Sidecar ≠ 网关**（一个管南北向出口，一个管东西向内部通信，但都用 Envoy）

**架构位置**：

```
客户端 ──► [反向代理/LB] ──► [API 网关] ──► [微服务 A, B, C]
                                  │
                                  └──► [鉴权/限流/路由]
```

> 网关通常**不和**反向代理合并（除非追求极致简单）：nginx 终止 TLS + 网关做业务，
> 是生产标配。

---

## 4. 网关选型

| 场景 | 推荐 | 说明 |
|---|---|---|
| **小团队 / 学习 / 内部工具** | FastAPI 自研（见本文 demo） | 灵活、贴合业务、Python 全栈 |
| **中大型 / 多语言后端** | **APISIX** / **Kong** | Lua 插件丰富、高性能、社区活跃 |
| **Spring 体系** | Spring Cloud Gateway | 集成 Spring 全家桶 |
| **K8s 流量入口** | Ingress-NGINX / Traefik | 标准 Ingress |
| **云原生全功能** | Envoy + Istio Gateway | 服务网格统一 |
| **Serverless** | AWS API Gateway / 阿里云 API 网关 | 托管、免运维 |

**自研网关的边界**：流量不大 + 业务简单 + Python 技术栈 → 自研够用。
流量大 + 多团队 + 复杂路由 → 上 APISIX。

---

## 5. Python FastAPI 网关 Demo 流程图

### 5.1 整体架构

```
                    ┌────────────────────┐
                    │      Client        │
                    └──────────┬─────────┘
                               │ HTTPS
                    ┌──────────▼─────────┐
                    │  TLS Termination   │  ← nginx / 云 LB
                    └──────────┬─────────┘
                               │ HTTP
                    ┌──────────▼─────────────────────────┐
                    │      Gateway (FastAPI)               │
                    │                                       │
                    │  [Middleware 链]                      │
                    │   ① TrustedHostMiddleware              │  防 Host 注入
                    │   ② RequestContextMiddleware            │  生成 X-Request-ID
                    │   ③ RateLimitMiddleware                │  滑动窗口限流
                    │   ④ AuthMiddleware                     │  JWT 校验
                    │   ⑤ ReverseProxyMiddleware             │  路由转发
                    │                                       │
                    └──────┬──────────┬──────────┬─────────┘
                           │          │          │
                  /api/users      /api/orders  /api/products
                           │          │          │
                    ┌──────▼──┐  ┌────▼───┐  ┌────▼────┐
                    │  User   │  │ Order  │  │Product  │
                    │ Service │  │Service │  │ Service │
                    │ :9001   │  │ :9002  │  │ :9003   │
                    └─────────┘  └────────┘  └─────────┘
```

### 5.2 中间件顺序为什么重要

**先 `add_middleware` 的在外层**（请求从外到内经过，响应反过来）：

```
请求流：  Client → ①TrustedHost → ②RequestContext → ③RateLimit → ④Auth → ⑤ReverseProxy → Downstream
响应流：  Downstream → ⑤ → ④ → ③ → ② → ① → Client
```

**错误顺序示例**：

- ❌ `Auth` 在 `RateLimit` 内：未鉴权的请求也消耗限流名额
- ❌ `ReverseProxy` 在 `Auth` 内：未鉴权就转发到下游，下游要重复鉴权
- ✅ 正确：限流在最外（早期丢弃）、鉴权居中（带 user 上下文）、转发在最内

### 5.3 关键路径

```
1. TrustedHostMiddleware
   - 检查 Host 头，拒绝恶意构造（如 Host: evil.com）
   - 防 Host Header 注入

2. RequestContextMiddleware
   - 生成/透传 X-Request-ID（链路追踪）
   - 记录访问日志（method, path, status, latency）
   - 请求耗时埋点

3. RateLimitMiddleware
   - 按 (client_ip, path_prefix) 做滑动窗口
   - 超限返回 429 + Retry-After
   - 防止恶意刷接口

4. AuthMiddleware
   - 解析 Authorization: Bearer xxx
   - 校验 JWT 签名 / 过期 / 黑名单
   - 把 user 信息挂到 request.state.user

5. ReverseProxyMiddleware
   - 根据 path 前缀匹配 ROUTES 表
   - 用 httpx 转发到下游
   - 透传 X-Request-ID / X-User-Id / X-Forwarded-For
```

---

## 6. 关键中间件实现要点

完整代码见 `workspace/gateway/gateway.py`。

### 6.1 RequestContextMiddleware（请求上下文）

```python
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info("[%s] %s %s -> %s (%.1fms)",
                    request_id, request.method, request.url.path,
                    response.status_code, elapsed_ms)
        return response
```

### 6.2 RateLimitMiddleware（滑动窗口限流）

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    WINDOW_SEC = 60
    MAX_REQS = 100
    def __init__(self, app):
        super().__init__(app)
        self.buckets = defaultdict(deque)

    async def dispatch(self, request, call_next):
        key = (request.client.host, request.url.path.split("/")[1])
        now = time.time()
        bucket = self.buckets[key]
        while bucket and bucket[0] < now - self.WINDOW_SEC:
            bucket.popleft()
        if len(bucket) >= self.MAX_REQS:
            return JSONResponse({"detail": "Too Many Requests"},
                                status_code=429,
                                headers={"Retry-After": str(self.WINDOW_SEC)})
        bucket.append(now)
        return await call_next(request)
```

> ⚠️ 这是**单进程内存版**，多 worker / 多机要换 Redis（用 INCR + EXPIRE 实现）。

### 6.3 AuthMiddleware（JWT 校验）

```python
class AuthMiddleware(BaseHTTPMiddleware):
    PUBLIC_PATHS = {"/health", "/", "/login"}

    async def dispatch(self, request, call_next):
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"detail": "Missing bearer token"},
                                status_code=401)

        try:
            payload = jwt.decode(auth[7:], SECRET,
                                 algorithms=["HS256"],
                                 options={"require": ["exp", "sub"]})
            request.state.user = payload
        except jwt.InvalidTokenError as e:
            return JSONResponse({"detail": f"Invalid token: {e}"},
                                status_code=401)
        return await call_next(request)
```

### 6.4 ReverseProxyMiddleware（路由转发）

```python
class ReverseProxyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, routes: dict[str, str]):
        super().__init__(app)
        self.routes = routes

    async def dispatch(self, request, call_next):
        upstream = self._match(request.url.path)
        if not upstream:
            return await call_next(request)             # 网关自身路由

        headers = dict(request.headers)
        headers["X-Real-IP"] = request.client.host
        headers["X-Request-ID"] = request.state.request_id
        if hasattr(request.state, "user"):
            headers["X-User-Id"] = str(request.state.user.get("sub"))

        body = await request.body()                     # body 只能读一次

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                upstream_resp = await client.request(
                    method=request.method,
                    url=f"{upstream}{request.url.path}",
                    params=request.query_params,
                    headers=headers, content=body,
                )
            except httpx.RequestError as e:
                return JSONResponse({"detail": f"Upstream error: {e}"},
                                    status_code=502)

        # 过滤 hop-by-hop headers（防双重压缩）
        excluded = {"content-encoding", "content-length",
                    "transfer-encoding", "connection"}
        resp_headers = {k: v for k, v in upstream_resp.headers.items()
                       if k.lower() not in excluded}
        return Response(content=upstream_resp.content,
                        status_code=upstream_resp.status_code,
                        headers=resp_headers,
                        media_type=upstream_resp.headers.get("content-type"))
```

### 6.5 中间件装配

```python
app = FastAPI()
ROUTES = {
    "/api/users": "http://127.0.0.1:9001",
    "/api/orders": "http://127.0.0.1:9002",
}

app.add_middleware(RequestContextMiddleware)      # 最外层：request_id
app.add_middleware(RateLimitMiddleware)          # 限流
app.add_middleware(AuthMiddleware)               # 鉴权
app.add_middleware(ReverseProxyMiddleware,       # 转发
                    routes=ROUTES)
```

---

## 7. 生产部署清单

### 7.1 必备

- ✅ TLS 终止：nginx / 云 LB
- ✅ `ProxyHeadersMiddleware`（在 nginx 后取真实客户端 IP）
  ```python
  from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
  app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
  ```
- ✅ 健康检查端点 `/health`（给 LB / k8s 用）
- ✅ 优雅关闭（uvicorn 自带 SIGTERM 处理）
- ✅ 多 worker（`uvicorn --workers 4`）—— **注意**：内存版限流 / ConnectionManager 在 worker 间不共享

### 7.2 推荐

- 限流改 Redis（`aioredis` + 滑动窗口 Lua）
- 熔断（`tenacity` + `pybreaker`，下游超时 / 5xx 自动隔离）
- Prometheus 指标暴露（`prometheus-fastapi-instrumentator`）
- 链路追踪（`opentelemetry-instrumentation-fastapi`）
- 限流 / 鉴权策略热加载（不用重启网关）

### 7.3 网关也要高可用

```
        ┌─ Gateway 1 ─┐
LB ───► │             │ ──► 下游服务
        └─ Gateway 2 ─┘
```

- 多实例 + 健康检查
- 蓝绿 / 灰度发布（按权重切流量）
- 配置中心统一管理（Consul / Nacos）

---

## 8. 网关常见坑

| 坑 | 现象 | 修法 |
|---|---|---|
| **中间件顺序写反** | 鉴权在限流前 → 未鉴权请求消耗限流名额 | 按 5.2 顺序调整 |
| **没加 `ProxyHeadersMiddleware`** | 网关看到的 IP 都是 `127.0.0.1` | nginx 后必须加 |
| **body 读两次** | `await request.body()` 调两次，第二次空 | 转发前缓存到局部变量 |
| **没过滤 hop-by-hop headers** | content-encoding 双重压缩 → 客户端解压失败 | 过滤 `content-encoding` / `transfer-encoding` / `connection` |
| **限流是内存版但多 worker** | 单 worker 限流 100，整体可能是 400 | 改 Redis 分布式限流 |
| **网关同步调用下游，下游慢拖垮网关** | 网关全在等 | 加超时 + 熔断 + 异步 |
| **忘记 CORS** | 浏览器 OPTIONS 预检失败 | `CORSMiddleware` |
| **网关无认证 / 公开 health 被攻击** | `/health` 等被恶意刷 | 限流 + 只监听内网 |
| **路由冲突** | 两个服务都用 `/api/v1/users` | path 前缀必须唯一 |
| **网关自身没限流** | 网关被 DDoS 拖垮 | 网关也要限流 + 入口 LB 抗 DDoS |

---

## 关联笔记

- 鉴权流程（JWT / OAuth2 / 扫码）：`[[鉴权与登录笔记]]`
- 权限模型（拿到 token 后能做什么）：`[[权限模型笔记]]`
- 反向代理 / TLS：`[[nginx]]`（如已收录）
- 容器编排（Ingress）：`[[kubernetes]]`
- 服务网格（Sidecar 形态的网关）：`[[DevOps]]`

## Demo

完整可运行代码（FastAPI 网关 + 2 个模拟下游服务 + JWT 鉴权 + Casbin 权限检查 + 扫码登录）：

- [`workspace/gateway/gateway.py`](../workspace/gateway/gateway.py)
- [`workspace/gateway/service_users.py`](../workspace/gateway/service_users.py)
- [`workspace/gateway/service_orders.py`](../workspace/gateway/service_orders.py)
- [`workspace/gateway/auth_demo.py`](../workspace/gateway/auth_demo.py)
- [`workspace/gateway/scan_login_demo.py`](../workspace/gateway/scan_login_demo.py)
- [`workspace/gateway/policy/`](../workspace/gateway/policy/)（Casbin 模型 + 策略）
- [`workspace/gateway/README.md`](../workspace/gateway/README.md)