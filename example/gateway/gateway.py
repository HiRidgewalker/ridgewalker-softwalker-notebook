"""
FastAPI 网关 Demo（生产级中间件链）。

演示（对应 [[API网关笔记]] §5-6）：
- TrustedHostMiddleware：防 Host 注入
- RequestContextMiddleware：生成 X-Request-ID + 耗时日志
- RateLimitMiddleware：滑动窗口限流（单进程内存版）
- AuthMiddleware：Bearer Token 校验（用 auth_demo.py 签发的 token）
- ReverseProxyMiddleware：按 path 前缀路由到下游

启动：
    # 终端 1：下游 user 服务
    .venv/bin/python example/gateway/service_users.py

    # 终端 2：下游 order 服务
    .venv/bin/python example/gateway/service_orders.py

    # 终端 3：网关
    .venv/bin/python example/gateway/gateway.py
    # 监听 0.0.0.0:8000

测试：
    curl http://localhost:8000/health
    TOKEN=$(.venv/bin/python example/gateway/auth_demo.py issue alice)
    curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/123
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from collections import defaultdict, deque
from typing import Awaitable, Callable

import httpx
import jwt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s | %(message)s",
)
logger = logging.getLogger("gateway")


# ============================================================
# 配置
# ============================================================
SECRET = os.environ.get("JWT_SECRET", "demo-secret-please-change-in-prod")
ALG = "HS256"

# 下游服务路由表（path 前缀 -> 服务地址）
ROUTES: dict[str, str] = {
    "/api/users": "http://127.0.0.1:9001",
    "/api/orders": "http://127.0.0.1:9002",
}

# 公开路径（无需鉴权）
PUBLIC_PATHS = {"/", "/health", "/healthz", "/docs", "/openapi.json", "/redoc"}


# ============================================================
# 中间件 1：TrustedHost（防 Host Header 注入）
# ============================================================
# 由 TrustedHostMiddleware 直接实现，单独 add_middleware


# ============================================================
# 中间件 2：RequestContext（X-Request-ID + 访问日志）
# ============================================================
class RequestContextMiddleware(BaseHTTPMiddleware):
    """生成/透传 X-Request-ID，记录访问日志。"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "[%s] %s %s -> %s (%.1fms)",
            request_id, request.method, request.url.path,
            response.status_code, elapsed_ms,
        )
        return response


# ============================================================
# 中间件 3：RateLimit（滑动窗口，单进程内存版）
# ============================================================
class RateLimitMiddleware(BaseHTTPMiddleware):
    """按 (client_ip, path_prefix) 滑动窗口限流。

    生产多 worker / 多机必须换 Redis（INCR + EXPIRE）。
    """

    WINDOW_SEC = 60
    MAX_REQS = 100

    def __init__(self, app):
        super().__init__(app)
        self.buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # 取真实 IP（需要 ProxyHeadersMiddleware 在外层）
        client_ip = (
            request.headers.get("X-Real-IP")
            or (request.client.host if request.client else "unknown")
        )
        prefix = self._match_prefix(request.url.path)
        key = (client_ip, prefix)
        now = time.time()

        bucket = self.buckets[key]
        while bucket and bucket[0] < now - self.WINDOW_SEC:
            bucket.popleft()

        if len(bucket) >= self.MAX_REQS:
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=429,
                headers={"Retry-After": str(self.WINDOW_SEC),
                         "X-Request-ID": request.state.request_id},
            )

        bucket.append(now)
        return await call_next(request)

    @staticmethod
    def _match_prefix(path: str) -> str:
        for p in ROUTES:
            if path.startswith(p):
                return p
        return "/"


# ============================================================
# 中间件 4：Auth（JWT 校验）
# ============================================================
class AuthMiddleware(BaseHTTPMiddleware):
    """解析 Authorization: Bearer xxx，校验 JWT，user 挂到 request.state.user。"""

    async def dispatch(self, request: Request, call_next):
        # 公开路径直接放行
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # OPTIONS 预检放行（CORS）
        if request.method == "OPTIONS":
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing bearer token"},
                status_code=401,
                headers={"X-Request-ID": request.state.request_id},
            )

        token = auth[7:]
        try:
            payload = jwt.decode(
                token, SECRET, algorithms=[ALG],
                options={"require": ["exp", "sub"]},
            )
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                {"detail": "Token expired"},
                status_code=401,
                headers={"X-Request-ID": request.state.request_id},
            )
        except jwt.InvalidTokenError as e:
            return JSONResponse(
                {"detail": f"Invalid token: {e}"},
                status_code=401,
                headers={"X-Request-ID": request.state.request_id},
            )

        request.state.user = payload
        return await call_next(request)


# ============================================================
# 中间件 5：ReverseProxy（按 path 转发到下游）
# ============================================================
HOP_BY_HOP = {"content-encoding", "content-length", "transfer-encoding", "connection"}


class ReverseProxyMiddleware(BaseHTTPMiddleware):
    """根据 path 前缀匹配 ROUTES，转发到对应下游服务。"""

    def __init__(self, app, routes: dict[str, str], timeout: float = 30.0):
        super().__init__(app)
        self.routes = routes
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        upstream = self._match_upstream(request.url.path)
        if not upstream:
            return await call_next(request)            # 网关自身路由（如 /health）

        # 构造转发 headers
        headers = dict(request.headers)
        # 删除 hop-by-hop
        for h in HOP_BY_HOP:
            headers.pop(h, None)
        # 注入追踪 / 用户信息
        headers["X-Real-IP"] = (
            request.headers.get("X-Real-IP")
            or (request.client.host if request.client else "unknown")
        )
        headers["X-Request-ID"] = request.state.request_id
        if hasattr(request.state, "user"):
            headers["X-User-Id"] = str(request.state.user.get("sub", ""))
            headers["X-User-Roles"] = ",".join(request.state.user.get("roles", []))

        # body 只能读一次，先缓存
        body = await request.body()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                upstream_resp = await client.request(
                    method=request.method,
                    url=f"{upstream}{request.url.path}",
                    params=request.query_params,
                    headers=headers,
                    content=body,
                )
            except httpx.RequestError as e:
                logger.error("upstream %s error: %s", upstream, e)
                return JSONResponse(
                    {"detail": f"Upstream error: {e}"},
                    status_code=502,
                    headers={"X-Request-ID": request.state.request_id},
                )

        # 过滤 hop-by-hop headers 再回给客户端
        resp_headers = {
            k: v for k, v in upstream_resp.headers.items()
            if k.lower() not in HOP_BY_HOP
        }
        resp_headers["X-Request-ID"] = request.state.request_id

        return Response(
            content=upstream_resp.content,
            status_code=upstream_resp.status_code,
            headers=resp_headers,
            media_type=upstream_resp.headers.get("content-type"),
        )

    @staticmethod
    def _match_upstream(path: str) -> str | None:
        for prefix, upstream in ROUTES.items():
            if path.startswith(prefix):
                return upstream
        return None


# ============================================================
# 网关装配
# ============================================================
app = FastAPI(title="API Gateway Demo")

# TrustedHost（防 Host 注入）
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS（浏览器跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ProxyHeaders（nginx 后取真实 IP，必须在中间件链最外层）
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 业务中间件（顺序：context → rate limit → auth → reverse proxy）
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(ReverseProxyMiddleware, routes=ROUTES, timeout=30.0)


# ============================================================
# 网关自身路由
# ============================================================
@app.get("/health")
async def health():
    return {"status": "ok", "ts": time.time()}


@app.get("/")
async def index():
    return {
        "gateway": "FastAPI API Gateway Demo",
        "routes": ROUTES,
        "public_paths": list(PUBLIC_PATHS),
    }


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")