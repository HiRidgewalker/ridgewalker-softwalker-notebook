"""
WebSocket 生产级服务端示例（FastAPI）。

演示：
- ConnectionManager：连接管理 + 单播 + 广播 + 在线列表 + 离线清理
- WebSocketDisconnect 异常捕获 → 自动清理
- REST 接口触发主动推送（"服务端主动 push"）
- 群发排除发送者（聊天群常用）
- 心跳（应用层 ping/pong）

对应笔记：[[Hub/websocket笔记]] 第 4-5 节

启动：
    cd workspace
    uv venv .venv
    uv pip install --python .venv/bin/python fastapi uvicorn websockets
    .venv/bin/python ../ws/server.py

浏览器访问：
    open ../ws/client_browser.html
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ws.server")


# ============================================================
# ConnectionManager
# ============================================================
class ConnectionManager:
    """管理所有活跃 WebSocket 连接。

    生产单进程够用；多进程（uvicorn --workers N）需要换 Redis pub/sub，
    因为每个 worker 独立一份 active dict，看不见其他 worker 的连接。
    """

    def __init__(self) -> None:
        # client_id -> WebSocket
        self.active: dict[str, WebSocket] = {}
        # 用于应用层心跳：client_id -> last_pong_ts
        self.last_pong: dict[str, float] = {}

    async def connect(self, client_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.active[client_id] = ws
        self.last_pong[client_id] = time.time()
        logger.info("connected: client_id=%s, online=%d", client_id, len(self.active))

    def disconnect(self, client_id: str) -> None:
        self.active.pop(client_id, None)
        self.last_pong.pop(client_id, None)
        logger.info("disconnected: client_id=%s, online=%d", client_id, len(self.active))

    async def send_to(self, client_id: str, message: str) -> bool:
        """单播。返回是否成功。"""
        ws = self.active.get(client_id)
        if ws is None:
            return False
        try:
            await ws.send_text(message)
            return True
        except Exception as e:
            logger.warning("send_to %s failed: %s", client_id, e)
            self.disconnect(client_id)
            return False

    async def broadcast(self, message: str, exclude: Optional[str] = None) -> int:
        """群发。exclude 用于排除发送者。返回成功数。"""
        success = 0
        # list() 防迭代中修改
        for cid, ws in list(self.active.items()):
            if cid == exclude:
                continue
            try:
                await asyncio.wait_for(ws.send_text(message), timeout=5.0)
                success += 1
            except Exception as e:
                logger.warning("broadcast to %s failed: %s", cid, e)
                self.disconnect(cid)
        return success

    def online(self) -> list[str]:
        return list(self.active.keys())

    def mark_pong(self, client_id: str) -> None:
        self.last_pong[client_id] = time.time()


manager = ConnectionManager()
app = FastAPI(title="ws demo server")

# CORS（浏览器跨域时需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # demo 用，生产改成具体 origin
    allow_credentials=True,
)


# ============================================================
# 简易 token 校验（生产用 JWT）
# ============================================================
VALID_TOKEN = "demo_token_123"


# ============================================================
# WebSocket 端点
# ============================================================
@app.websocket("/ws/{client_id}")
async def ws_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: str = Query(...),
):
    # 握手阶段鉴权
    if token != VALID_TOKEN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(client_id, websocket)

    try:
        while True:
            # 业务消息 + 应用层心跳都通过 receive_text 进来
            data = await websocket.receive_text()

            # 简单协议：客户端可发 JSON {"type": "...", "data": "..."}
            # 也可发纯文本。demo 这里统一按文本处理。
            logger.info("[recv] from %s: %s", client_id, data)

            # 应用层心跳
            if data.strip() == '{"type":"ping"}' or data.strip() == "ping":
                await websocket.send_text('{"type":"pong"}')
                manager.mark_pong(client_id)
                continue

            # 业务消息：广播给其他人（聊天群风格）
            await manager.broadcast(
                f'[msg] {client_id}: {data}',
                exclude=client_id,
            )

    except WebSocketDisconnect as e:
        # 客户端正常断开 / 异常断开都会进这里
        logger.info("client %s disconnected: code=%s reason=%s", client_id, e.code, e.reason)
        manager.disconnect(client_id)


# ============================================================
# REST 接口：业务方调用 HTTP 即可触发 WS 推送
# ============================================================
@app.post("/push/{client_id}")
async def push_to_client(client_id: str, payload: dict):
    """主动推送消息给指定客户端（"服务端主动 push"）。"""
    message = payload.get("message")
    if not message:
        raise HTTPException(400, "message required")
    ok = await manager.send_to(client_id, message)
    if not ok:
        raise HTTPException(404, f"client {client_id} not online")
    return {"ok": True, "client_id": client_id}


@app.post("/broadcast")
async def broadcast(payload: dict):
    """群发所有客户端。"""
    message = payload.get("message")
    if not message:
        raise HTTPException(400, "message required")
    n = await manager.broadcast(message)
    return {"delivered_to": n, "online": len(manager.online())}


@app.get("/online")
async def online_list():
    """查询当前在线客户端列表。"""
    return {"online": manager.online(), "count": len(manager.online())}


# ============================================================
# 心跳看护：定期扫描超时未 pong 的连接，主动断开
# ============================================================
HEARTBEAT_TIMEOUT = 60  # 秒


async def heartbeat_watcher():
    """每 10 秒扫描一次，超时未 pong 的客户端主动断开。"""
    while True:
        await asyncio.sleep(10)
        now = time.time()
        for cid, last in list(manager.last_pong.items()):
            if now - last > HEARTBEAT_TIMEOUT:
                logger.warning("heartbeat timeout, force close: %s", cid)
                ws = manager.active.get(cid)
                if ws is not None:
                    try:
                        await ws.close(code=status.WS_1011_INTERNAL_ERROR)
                    except Exception:
                        pass
                manager.disconnect(cid)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(heartbeat_watcher())


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")