# workspace/ws —— WebSocket Demo 总索引

对应笔记：`[[Hub/websocket笔记]]`

## 文件

| 文件 | 内容 |
|---|---|
| `server.py` | FastAPI WebSocket 服务端，含 `ConnectionManager` + REST 触发推送 + 心跳看护 |
| `client_browser.html` | 浏览器客户端（原生 `WebSocket` API + 自动重连） |
| `client_python.py` | Python 客户端（用 `websockets` 库） |
| `client_js_console.js` | Node.js 客户端（用 `ws` npm 包） |

## 启动服务

### 1. 准备 Python 虚拟环境

```bash
cd workspace

# 首次：建虚拟环境
uv venv .venv
uv pip install --python .venv/bin/python fastapi uvicorn websockets
```

### 2. 启动服务端

```bash
cd workspace
.venv/bin/python ../ws/server.py
# 监听 0.0.0.0:8000
```

打开浏览器访问 `http://localhost:8000/online` 可以看到当前在线列表（空）。

### 3. 启动客户端（选其一）

#### 浏览器（推荐，最直观）

```bash
# 直接双击或浏览器打开
open ../ws/client_browser.html     # macOS
xdg-open ../ws/client_browser.html # Linux
```

- 默认 client_id 自动生成（如 `browser_a3k2jf`）
- 点击「连接」即可
- token 默认 `demo_token_123`（与服务端 `VALID_TOKEN` 一致）

#### Python 客户端

```bash
.venv/bin/python workspace/ws/client_python.py
```

- client_id 是 `py_alice`
- 自动每 3 秒发一条消息，共 5 条

#### Node.js 客户端

```bash
# 首次：装 ws 库
npm install ws --prefix /tmp/ws-demo
NODE_PATH=/tmp/ws-demo/node_modules node workspace/ws/client_js_console.js
```

- client_id 是 `node_bob`
- 自动每 3 秒发一条消息

## 演示场景（覆盖笔记中的疑问）

### 场景 1：客户端 → 服务端（基础）

浏览器 A 连接 → 在输入框发消息 → 服务端控制台打印 `[recv] from browser_xxx: ...`

### 场景 2：服务端主动推送（**重点验证**）

开两个终端，一个用 Python 客户端（client_id=`py_alice`），另一个运行：

```bash
curl -X POST http://localhost:8000/push/py_alice \
  -H "Content-Type: application/json" \
  -d '{"message":"hello from server push"}'
```

Python 客户端会**立刻**收到消息，无需它先发起请求——这就是"服务端主动推送"。

### 场景 3：群发 + 排除发送者

打开两个浏览器标签（A、B），在 A 发消息 → B 会收到带 `[msg] browser_A: ...` 的内容，A 自己不会收到回显（exclude 实现）。

### 场景 4：服务端群发所有

```bash
curl -X POST http://localhost:8000/broadcast \
  -H "Content-Type: application/json" \
  -d '{"message":"system notice: maintenance in 5 min"}'
```

所有连接（包括发送者）都会收到。

### 场景 5：在线列表 + 离线检测

```bash
# 开两个浏览器都连上
curl http://localhost:8000/online
# {"online":["browser_xxx","browser_yyy"],"count":2}

# 关掉其中一个标签
curl http://localhost:8000/online
# 5s 内会自动变成 {"count":1} —— WebSocketDisconnect 触发 disconnect 清理
```

### 场景 6：心跳与超时

服务端每 30 秒会发应用层 ping，客户端回 pong。若 60 秒内无任何交互（含 pong），`heartbeat_watcher` 会**主动 close** 那个客户端。

可以用浏览器开 DevTools → Network → WS 帧视图，看 ping/pong 帧。

### 场景 7：单播失败处理

```bash
# 给一个不存在的 client_id 推
curl -X POST http://localhost:8000/push/nonexistent \
  -H "Content-Type: application/json" \
  -d '{"message":"hi"}'
# 返回 404 {"detail":"client nonexistent not online"}
```

## REST 接口速查

| 方法 | 路径 | 用途 |
|---|---|---|
| `POST` | `/push/{client_id}` | 单播（主动推送） |
| `POST` | `/broadcast` | 群发所有 |
| `GET` | `/online` | 在线列表 |

## 测试矩阵（建议同时打开）

| 客户端 | client_id | 验证 |
|---|---|---|
| 浏览器标签 1 | `browser_alice` | 浏览器 UI |
| 浏览器标签 2 | `browser_bob` | 群发 |
| Python 终端 | `py_alice` | 服务端推送 |
| Node.js 终端 | `node_bob` | 跨语言兼容 |

## 常见问题

- **浏览器连不上**：检查 token 是否为 `demo_token_123`；浏览器 DevTools → Console 看 1008 关闭码
- **Python 客户端装不上**：`uv pip install --python workspace/.venv/bin/python websockets`
- **Node.js 找不到 ws**：`npm install ws --prefix /tmp/ws-demo`
- **多 worker 看不到其他进程连接**：dev 用单进程即可；生产用 Redis pub/sub（见笔记第 7.1 节）

## 相关 demo

- 消息队列（实时数据流的另一方案）：`workspace/mq/`
- 关系型数据库连接示例：`workspace/db/sql-tools-demo/`