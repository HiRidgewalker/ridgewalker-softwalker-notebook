"""
中间件 + CORS

启动：
    uv run uvicorn workspace.python.fastapi.middleware_cors:app --reload

要点：
- add_middleware 注册 CORS / GZip 等「类中间件」
- @app.middleware("http") 装饰器写「函数式中间件」
- 自定义中间件拿到的 request 是 Starlette Request，call_next 走后续处理
"""
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# ===== CORS =====
# 开发时常见：前端在 3000 端口、API 在 8000 端口，需要 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== GZip 压缩 =====
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ===== 自定义中间件：记录请求耗时 =====
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response


@app.get("/")
def root():
    return {"hello": "world"}


# 测 CORS：
# curl -i -H "Origin: http://localhost:3000" http://127.0.0.1:8000/
# 响应头应包含: access-control-allow-origin: http://localhost:3000
