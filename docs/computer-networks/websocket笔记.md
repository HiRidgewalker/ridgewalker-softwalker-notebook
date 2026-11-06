---
title: "WebSocket 笔记"
---

# WebSocket 笔记

> 由旧稿重写。原笔记是阮一峰风格的概念罗列，本笔记在此基础上**补全协议层细节**、**给出可运行的 Python / JS 代码**、并**直接回答「双向通信」到底是什么意思、服务端怎么主动推送、服务端怎么群发/单播、如何发现在线/离线客户端**。
>
> 对应协议规范：[RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)。
> Python 库：[websockets](https://websockets.readthedocs.io/) + [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)。

## 目录

1. 「双向通信」到底是什么意思
2. 「服务器怎么发现客户端」——不需要发现，靠"连接"
3. 协议基础（RFC 6455 速查）
4. Python 服务端：ConnectionManager 模式
5. 6 个核心场景（全部给可运行代码）
6. 浏览器 / Python / Node.js 三种客户端
7. 生产考量
8. 常见坑
9. WebSocket vs SSE vs 长轮询

---

## 1. 「双向通信」到底是什么意思

很多人对 WebSocket 的"双向"有误解，先把概念钉死。

### 1.1 HTTP 是半双工、单向角色

```
客户端 ──请求──► 服务端
客户端 ◄──响应── 服务端

特点：
- 客户端必须先发请求
- 服务端只能被动响应
- 一来一回，连接就关
```

服务端**没有"主动喊一声"的能力**。要模拟推送，只能靠客户端不断发请求问（轮询）或挂一个不返回的请求（长轮询）。

### 1.2 WebSocket 是全双工、双方平等

```
客户端 ◄──────────────────► 服务端
              │
       一次 HTTP 握手后升级为 WebSocket
       双方地位平等，任一方都可主动发消息
       连接长期保持（直到某一方 close）
```

握手仍由**客户端发起**（HTTP Upgrade 请求），但**握手成功后服务器即可主动 push，无需客户端先发请求**。

### 1.3 为什么这个特性重要

| 业务 | HTTP 怎么做 | WebSocket 怎么做 |
|---|---|---|
| 聊天 | 客户端每 1s 问一次有新消息吗 | 服务端收到对方消息后立刻推 |
| 实时行情 | 客户端轮询 / 长轮询 | 服务端价格变化立刻推 |
| 协同编辑 | 同上 | 服务端把别人的操作立刻推过来 |

**延迟从天/分钟级降到毫秒级**，且大幅减少无效请求。

---

## 2. 「服务器怎么发现客户端」——不需要发现，靠"连接"

这是初学者最容易卡住的地方。

### 2.1 没有"发现"这个动作

> **WebSocket 服务器没有"发现客户端"的魔法**。客户端必须先建立 WS 连接，服务器才会持有这个连接对象，然后才能对它发消息。
>
> 类比：微信服务器怎么"发现"你想给你发消息？答案是**你先注册账号（建立连接）**，服务器才知道有你这个人。

### 2.2 连接对象（WebSocket / ClientConnection）

每个建立好的连接对应一个**长生命周期的对象**：

```python
# FastAPI
websocket: WebSocket          # 一个连接 = 一个对象

# raw websockets 库
websocket: ServerConnection   # 一个连接 = 一个对象
```

服务器把这个对象放进一个数据结构（dict / set）里保存起来，**直到客户端断开才移除**。

### 2.3 唯一标识 client_id

服务器收到连接时通常从 URL / Query / Token 提取一个 `client_id`，作为这个连接的"身份证"。

```
ws://example.com/ws/chat?client_id=user_42&token=xxx
                                  └─────┬────┘
                                    服务器提取作为 key
```

没有 `client_id`，服务器就只知道"有个连接"，没法精准定位某个客户端。

### 2.4 推送流程

```
1. 客户端连上 ws://host/ws?client_id=A
2. 服务器创建 ws_A 对象，存入 {A: ws_A}
3. 服务器要发消息给 A：
     await ws_A.send_text("hi A")   ← 通过保存的对象直接 send
4. 客户端断网：ws_A 抛 WebSocketDisconnect → 服务器从 dict 删除 A
```

**所以"主动推送"不是网络层面的魔法，而是应用层维护一个连接表。**

---

## 3. 协议基础（RFC 6455 速查）

### 3.1 握手：HTTP Upgrade

客户端请求：

```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

服务端响应（握手成功）：

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

- `Sec-WebSocket-Accept` = `base64(sha1(client_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))`
- 客户端必须校验此值（防伪造）

### 3.2 数据帧格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
```

| 字段 | 作用 |
|---|---|
| `FIN` | 是否为消息的最后一帧 |
| `opcode` | `0x1` text / `0x2` binary / `0x8` close / `0x9` ping / `0xA` pong |
| `MASK` | **客户端→服务端必须为 1**（防代理缓存投毒） |
| `Payload len` | 7 bit / +16 bit / +64 bit（按需扩展） |

> 实际写代码时**不必处理帧格式**——`websockets` 库 / 浏览器 `WebSocket` API 都已封装。

### 3.3 控制帧

- **Ping (0x9)**：心跳探测，接收端**必须回 Pong (0xA)**
- **Close (0x8)**：关闭握手，附状态码 + reason

### 3.4 关闭状态码

| 码 | 含义 |
|---|---|
| `1000` | 正常关闭 |
| `1001` | 端点离开（浏览器关页、服务端宕机） |
| `1002` | 协议错误 |
| `1008` | 违反策略（认证失败） |
| `1009` | 消息过大 |
| `1011` | 服务器内部错误 |

---

## 4. Python 服务端：ConnectionManager 模式

### 4.1 为什么需要 ConnectionManager

每个 WS 应用都要解决：**怎么保存活跃连接？怎么按 ID 找到它？怎么广播？**

模式就是「**活跃连接字典 + 增删查改**」。把它封装成 `ConnectionManager` 类，所有 endpoint 共用。

### 4.2 完整实现（FastAPI 版）

```python
# example/ws/server.py 核心片段
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

class ConnectionManager:
    """管理所有活跃 WebSocket 连接，提供连接/单播/广播/在线列表能力。"""

    def __init__(self) -> None:
        # client_id -> WebSocket（生产单进程够用；多机要换 Redis pub/sub）
        self.active: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.active[client_id] = ws

    def disconnect(self, client_id: str) -> None:
        self.active.pop(client_id, None)

    async def send_to(self, client_id: str, message: str) -> bool:
        """单播。返回是否成功。"""
        ws = self.active.get(client_id)
        if ws is None:
            return False
        await ws.send_text(message)
        return True

    async def broadcast(self, message: str, exclude: Optional[str] = None) -> int:
        """群发。exclude 排除的 client_id（如消息发送者）。返回成功数。"""
        success = 0
        for cid, ws in list(self.active.items()):       # 用 list() 防迭代中修改
            if cid == exclude:
                continue
            try:
                await ws.send_text(message)
                success += 1
            except Exception:
                self.disconnect(cid)                      # 发送失败说明已断，清理
        return success

    def online(self) -> list[str]:
        return list(self.active.keys())
```

> 完整可运行版本（含 REST 触发推送 endpoint、心跳、客户端断线清理）见
> [`example/ws/server.py`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/server.py)。

---

## 5. 6 个核心场景（全部给可运行代码）

### 场景 1：客户端 → 服务端

```python
@app.websocket("/ws/{client_id}")
async def ws_endpoint(ws: WebSocket, client_id: str):
    await manager.connect(client_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            print(f"[recv] from {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### 场景 2：服务端 → 单个客户端（指定推送）

通过 REST 接口触发，**这就是"服务端主动推送"**：

```python
from fastapi import HTTPException

@app.post("/push/{client_id}")
async def push_to_client(client_id: str, payload: dict):
    """REST 接口触发 WS 推送：业务调用方不用连 WS，直接 HTTP 即可。"""
    ok = await manager.send_to(client_id, payload["message"])
    if not ok:
        raise HTTPException(404, f"client {client_id} not online")
    return {"ok": True}
```

### 场景 3：服务端 → 群发所有连接

```python
@app.post("/broadcast")
async def broadcast(payload: dict):
    n = await manager.broadcast(payload["message"])
    return {"delivered_to": n}
```

### 场景 4：群发但排除发送者（聊天群常用）

```python
# 客户端 A 发消息，希望广播给 B/C/D，但不回显给自己
@app.websocket("/ws/{client_id}")
async def ws_endpoint(ws: WebSocket, client_id: str):
    await manager.connect(client_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"{client_id}: {data}", exclude=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### 场景 5：查询在线客户端列表

```python
@app.get("/online")
async def online_list():
    return {"online": manager.online(), "count": len(manager.online())}
```

### 场景 6：检测客户端离线

- 被动检测：`receive_*` 抛 `WebSocketDisconnect` → 在 except 中清理
- 主动检测：心跳（ping/pong）超时 → 服务端主动断开

```python
# 主动心跳（FastAPI + websockets 库底层支持）
# raw websockets 库: serve(..., ping_interval=30, ping_timeout=10)
# FastAPI: 用 starlette 的 receive() 处理 ping 帧
```

---

## 6. 三种客户端

### 6.1 浏览器 JavaScript（最常用）

```javascript
// example/ws/client_browser.html 核心逻辑
const clientId = "browser_" + Math.random().toString(36).slice(2, 8);
const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

ws.onopen = () => console.log("connected as", clientId);
ws.onmessage = (event) => {
    // 收到服务端推送 → 显示在页面上
    const li = document.createElement("li");
    li.textContent = `[recv] ${event.data}`;
    document.getElementById("messages").appendChild(li);
};
ws.onclose = () => console.log("disconnected");

function send() {
    ws.send(input.value);  // 浏览器 API 自动处理帧 + masking
    input.value = "";
}
```

### 6.2 Python 客户端

```python
# example/ws/client_python.py
import asyncio
import websockets

async def main():
    client_id = "py_alice"
    uri = f"ws://localhost:8000/ws/{client_id}"
    async with websockets.connect(uri) as ws:
        # 发送
        await ws.send("hello from python")
        # 接收（每条消息独立协程）
        async for msg in ws:
            print(f"[recv] {msg}")

asyncio.run(main())
```

### 6.3 Node.js 客户端

```javascript
// example/ws/client_js_console.js
const WebSocket = require("ws");
const clientId = "node_bob";
const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

ws.on("open", () => {
    console.log("connected");
    ws.send("hello from node");
});
ws.on("message", (data) => console.log("[recv]", data.toString()));
ws.on("close", () => console.log("disconnected"));
```

---

## 7. 生产考量

### 7.1 单进程 vs 多进程

```python
# 单进程：上面的 ConnectionManager 直接够用
manager = ConnectionManager()

# 多进程（uvicorn --workers N）：每个 worker 独立 dict，A 进程的用户无法收到 B 进程推的消息
# 解法：换 Redis pub/sub / PostgreSQL LISTEN-NOTIFY / 专用 broadcaster

# encode/broadcaster（FastAPI 官方推荐）
# pip install broadcaster[redis]
```

### 7.2 认证

握手阶段读 Query / Cookie 鉴权，**鉴权失败直接关闭连接**：

```python
from fastapi import Query, WebSocketException, status

@app.websocket("/ws/{client_id}")
async def ws_endpoint(
    ws: WebSocket,
    client_id: str,
    token: str = Query(...),
):
    if token != VALID_TOKEN:           # 实际用 JWT 验签
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(client_id, ws)
    ...
```

### 7.3 心跳与超时

| 层 | 机制 | 库默认 |
|---|---|---|
| 协议层 ping/pong | 服务端定期发 ping，客户端回 pong | raw `websockets`：`ping_interval=20, ping_timeout=20` |
| 应用层心跳 | 应用发 `{type: "ping"}` JSON，服务器回 `{type: "pong"}` | 自己实现 |

超时未响应 → 服务端断开 + 清理 ConnectionManager。

### 7.4 跨域

浏览器 WebSocket **也受同源策略限制**（握手阶段 Origin 头），用 FastAPI 的 CORSMiddleware：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
)
```

### 7.5 反向代理 / wss

生产用 nginx 终止 TLS + 转发到 WS 后端：

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;        # 1 天，避免长时间无消息被 nginx 切断
}
```

### 7.6 消息大小限制

默认 `max_size = 2 MiB`（raw websockets）。超过会抛 `PayloadTooBig` / 关闭连接。**禁止用 WS 传大文件**。

---

## 8. 常见坑

| 坑 | 现象 | 修法 |
|---|---|---|
| 客户端断网后服务器还在 `active` 里 | dict 越来越大 | `try/except WebSocketDisconnect` → `manager.disconnect` |
| `broadcast` 内 `await ws.send_text` 阻塞 | 一个慢客户端卡死所有消息 | 并发 `asyncio.gather(*tasks, return_exceptions=True)`，单条失败不拖累 |
| 浏览器 `WebSocket` 不自动重连 | 网络抖动就永久断 | 自己实现指数退避（1s/2s/4s/8s 上限 30s） |
| 服务端主动 `close()` 后再 `send()` | `RuntimeError: Cannot call send once a close has been sent` | close 前确认无待发消息，或用 finally |
| 握手后没调 `accept()` | 客户端一直连不上 | FastAPI 必须 `await ws.accept()` |
| `receive_text()` 收到二进制消息 | 抛 `TypeError` | 用 `receive()` 拿原始帧判断 `text/binary` |
| `ConnectionManager` 在多进程下"看不见"其他 worker | 推送不到 | 换 Redis pub/sub |
| 心跳间隔太长（>60s） | 移动网络 NAT 超时把连接掐掉 | `ping_interval=20~30` 秒 |
| 忘记 `set_header Connection upgrade` | nginx 后 WS 握手 502 | nginx 加 WS 转发头（见 7.5） |

---

## 9. WebSocket vs SSE vs 长轮询

| 维度 | WebSocket | SSE (Server-Sent Events) | 长轮询 |
|---|---|---|---|
| **方向** | 双向（client ↔ server） | 仅 server → client | 仅 server → client（模拟） |
| **协议** | WS（独立协议） | HTTP chunked | HTTP |
| **浏览器 API** | `new WebSocket(...)` | `new EventSource(...)` | `XMLHttpRequest` |
| **自动重连** | ❌ 自己实现 | ✅ 浏览器原生 | 自己实现 |
| **认证** | Query/Cookie | 标准 HTTP Cookie | 标准 HTTP Cookie |
| **代理友好度** | 中（需要 Upgrade 头） | 高（普通 HTTP） | 高 |
| **适用** | 聊天、游戏、协同、实时控制 | 行情、通知、日志流 | 简单推送 / 兼容老浏览器 |
| **Python 实现** | `websockets` / FastAPI | `sse-starlette` / `starlette.sse` | 普通 HTTP |

**选型原则：**

- **双向通信**（聊天、协同、实时游戏）→ WebSocket
- **单向推送**（行情、日志、通知）→ SSE（更简单，浏览器原生重连）
- **极致兼容老浏览器** → 长轮询

---

## 关联笔记

- 协议分层（WebSocket 在哪一层）：`[[TCP_IP四层网络模型笔记]]`
- 反向代理 / nginx 终止 TLS：`[[nginx]]`（如已收录）
- 实时数据流（与消息队列对比）：`[[RabbitMQ笔记]]` / `[[Kafka笔记]]`
- Python 异步运行时：`[[Python异步编程（asyncio）]]`
- FastAPI 应用：`[[FastAPI笔记]]`

## Demo

完整可运行代码（服务端 + 3 种客户端 + REST 触发推送）：

- [`example/ws/server.py`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/server.py)
- [`example/ws/client_browser.html`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/client_browser.html)
- [`example/ws/client_python.py`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/client_python.py)
- [`example/ws/client_js_console.js`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/client_js_console.js)
- [`example/ws/README.md`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/ws/README.md)