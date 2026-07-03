"""
Python WebSocket 客户端示例。

演示：
- 连接服务端
- 发送消息
- 异步接收消息
- 心跳
- 优雅断开

对应笔记：[[websocket笔记]] 第 6.2 节

启动：
    .venv/bin/python workspace/ws/client_python.py
"""
from __future__ import annotations

import asyncio
import logging
import sys

import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ws.client")


CLIENT_ID = "py_alice"
TOKEN = "demo_token_123"
URI = f"ws://localhost:8000/ws/{CLIENT_ID}?token={TOKEN}"


async def heartbeat(ws):
    """30s 一次应用层心跳。"""
    try:
        while True:
            await asyncio.sleep(30)
            await ws.send('{"type":"ping"}')
    except (websockets.ConnectionClosed, asyncio.CancelledError):
        pass


async def main():
    async with websockets.connect(URI) as ws:
        logger.info("connected: %s", CLIENT_ID)

        # 启心跳任务
        ping_task = asyncio.create_task(heartbeat(ws))

        # 后台：每隔几秒主动发一条消息
        async def sender():
            for i in range(5):
                await asyncio.sleep(3)
                try:
                    await ws.send(f"hello from python #{i}")
                except websockets.ConnectionClosed:
                    break
            ping_task.cancel()

        sender_task = asyncio.create_task(sender())

        # 主循环：接收
        try:
            async for msg in ws:
                logger.info("[recv] %s", msg)
        except websockets.ConnectionClosed:
            logger.info("connection closed")
        finally:
            ping_task.cancel()
            sender_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("interrupted, exiting")
        sys.exit(0)