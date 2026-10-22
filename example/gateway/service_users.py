"""
模拟下游 user 服务（端口 9001）。

演示：
- 接收网关转发的请求（带 X-User-Id / X-Request-ID 头）
- 返回模拟用户数据
- 根据 X-User-Id 做"已登录用户只能改自己"的最简权限检查

启动：.venv/bin/python example/gateway/service_users.py
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] user-service | %(message)s",
)
logger = logging.getLogger("user-service")

app = FastAPI(title="User Service (demo)")


# 模拟数据库
USERS = {
    123: {"id": 123, "name": "Alice", "email": "alice@example.com", "department": "eng"},
    456: {"id": 456, "name": "Bob",   "email": "bob@example.com",   "department": "ops"},
    789: {"id": 789, "name": "Carol", "email": "carol@example.com", "department": "qa"},
}


@app.middleware("http")
async def log_request(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", "-")
    uid = request.headers.get("X-User-Id", "anonymous")
    logger.info("[%s] user=%s %s %s", rid, uid, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    return user


@app.put("/api/users/{user_id}")
def update_user(
    user_id: int,
    payload: dict,
    x_user_id: str = Header(default=""),
):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(404, "user not found")
    # 最简检查：调用方 X-User-Id 必须等于 user_id（"改自己"）
    if x_user_id != str(user_id):
        raise HTTPException(403, "can only update yourself")
    user.update({k: v for k, v in payload.items() if k in ("name", "email")})
    return user


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, x_user_id: str = Header(default="")):
    """admin 才允许删除（演示用，实际应该 Casbin 强制）。"""
    if x_user_id not in ("123",):  # alice 是 admin
        raise HTTPException(403, "admin only")
    USERS.pop(user_id, None)
    return {"deleted": user_id}


@app.get("/api/users")
def list_users():
    return {"users": list(USERS.values()), "count": len(USERS)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9001, log_level="info")