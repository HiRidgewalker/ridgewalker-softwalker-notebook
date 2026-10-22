"""
模拟下游 order 服务（端口 9002）。

演示：
- 接收网关转发的请求（带 X-User-Id / X-Request-ID 头）
- 返回模拟订单数据
- 根据 X-User-Id 做简单的归属检查（演示 ABAC：只能看自己的订单）

启动：.venv/bin/python workspace/gateway/service_orders.py
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Header, HTTPException, Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] order-service | %(message)s",
)
logger = logging.getLogger("order-service")

app = FastAPI(title="Order Service (demo)")


# 模拟订单（owner_id 表示归属）
ORDERS = {
    1: {"id": 1, "user_id": 123, "amount": 99.0,  "status": "paid"},
    2: {"id": 2, "user_id": 123, "amount": 299.0, "status": "pending"},
    3: {"id": 3, "user_id": 456, "amount": 19.0,  "status": "paid"},
    4: {"id": 4, "user_id": 789, "amount": 1299.0,"status": "shipped"},
}


@app.middleware("http")
async def log_request(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", "-")
    uid = request.headers.get("X-User-Id", "anonymous")
    logger.info("[%s] user=%s %s %s", rid, uid, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/api/orders")
def list_orders(x_user_id: str = Header(default="")):
    """列出当前用户的所有订单（演示 ABAC 属性规则）。"""
    if not x_user_id:
        raise HTTPException(401, "no user id from gateway")
    uid = int(x_user_id)
    mine = [o for o in ORDERS.values() if o["user_id"] == uid]
    return {"orders": mine, "count": len(mine)}


@app.get("/api/orders/{order_id}")
def get_order(order_id: int, x_user_id: str = Header(default="")):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, "order not found")
    if not x_user_id or order["user_id"] != int(x_user_id):
        raise HTTPException(403, "not your order")
    return order


@app.post("/api/orders")
def create_order(payload: dict, x_user_id: str = Header(default="")):
    """创建订单（演示权限检查：必须是登录用户）。"""
    if not x_user_id:
        raise HTTPException(401, "no user id from gateway")
    new_id = max(ORDERS.keys()) + 1
    order = {
        "id": new_id,
        "user_id": int(x_user_id),
        "amount": payload.get("amount", 0),
        "status": "pending",
    }
    ORDERS[new_id] = order
    return order


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9002, log_level="info")