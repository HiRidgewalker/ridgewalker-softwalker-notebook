# example/gateway —— API 网关 + 鉴权 + 权限 Demo 总索引

对应笔记：

- `[[鉴权与登录笔记]]`
- `[[权限模型笔记]]`
- `[[API网关笔记]]`

## 文件

| 文件 | 内容 |
|---|---|
| `gateway.py` | FastAPI 网关主程序（4 个中间件 + 路由转发，端口 8000） |
| `service_users.py` | 模拟下游 user 服务（端口 9001） |
| `service_orders.py` | 模拟下游 order 服务（端口 9002） |
| `auth_demo.py` | JWT 双 Token + Casbin enforce CLI（issue/verify/revoke/enforce） |
| `scan_login_demo.py` | 扫码登录 5 步完整流程（含浏览器 demo，端口 9009） |
| `policy/model.conf` | Casbin RBAC 模型（含 keyMatch2 + RESTful 路径匹配） |
| `policy/policy.csv` | 策略与角色继承 |

## 整体架构

```
              ┌────────────────────────────────────┐
              │              Client                │
              └────────────────┬───────────────────┘
                               │
              ┌────────────────▼───────────────────┐
              │     Gateway :8000 (gateway.py)     │
              │   [RequestContext → RateLimit →    │
              │    Auth → ReverseProxy]            │
              └───┬─────────────────────┬──────────┘
                  │                     │
        /api/users/...           /api/orders/...
                  │                     │
              ┌───▼─────┐         ┌────▼─────┐
              │ user    │         │ order    │
              │ :9001   │         │ :9002    │
              └─────────┘         └──────────┘

   独立 demo: 扫码登录 :9009 (scan_login_demo.py)
```

## 准备环境

```bash
cd example

# 虚拟环境（首次）
uv venv .venv
uv pip install --python .venv/bin/python fastapi uvicorn httpx pyjwt casbin requests
```

## 启动顺序

### 1. 起下游服务

```bash
# 终端 1
.venv/bin/python ../gateway/service_users.py
# 监听 127.0.0.1:9001

# 终端 2
.venv/bin/python ../gateway/service_orders.py
# 监听 127.0.0.1:9002
```

### 2. 起网关

```bash
# 终端 3
.venv/bin/python ../gateway/gateway.py
# 监听 0.0.0.0:8000
```

### 3. 起扫码登录 demo（可选）

```bash
# 终端 4
.venv/bin/python ../gateway/scan_login_demo.py
# 监听 127.0.0.1:9009
```

## 演示场景

### 场景 1：网关公开端点

```bash
curl http://localhost:8000/health
# {"status":"ok",...}

curl http://localhost:8000/
# 网关信息
```

### 场景 2：未带 token → 401

```bash
curl -i http://localhost:8000/api/users/123
# HTTP/1.1 401
# {"detail":"Missing bearer token"}
```

### 场景 3：颁发 alice 的 token

```bash
cd example
TOKEN=$(.venv/bin/python ../gateway/auth_demo.py issue alice | grep ACCESS_TOKEN | cut -d= -f2)
echo $TOKEN
# eyJhbGciOiJIUzI1NiIs...
```

### 场景 4：带 token 访问 → 200

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/123
# {"id":123,"name":"Alice","email":"alice@example.com","department":"eng"}

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/orders/1
# {"id":1,"user_id":123,"amount":99.0,"status":"paid"}
```

### 场景 5：Casbin 权限检查（CLI）

```bash
# alice 能读 user（直接策略）
.venv/bin/python ../gateway/auth_demo.py enforce alice /api/users/123 GET
# ALLOW alice GET /api/users/123

# alice 能读 order（admin 继承）
.venv/bin/python ../gateway/auth_demo.py enforce alice /api/orders/1 GET
# ALLOW alice GET /api/orders/1

# alice 想删 order
.venv/bin/python ../gateway/auth_demo.py enforce alice /api/orders/1 DELETE
# ALLOW alice DELETE /api/orders/1   （因为 alice 是 admin，admin ANY）

# carol 不是 admin
.venv/bin/python ../gateway/auth_demo.py enforce carol /api/users/123 DELETE
# DENY carol DELETE /api/users/123
```

### 场景 6：Token 过期

修改源码 `ACCESS_TTL = timedelta(seconds=1)` → 等待 2 秒 → 请求 → 401 "Token expired"

### 场景 7：限流

在网关源码改 `MAX_REQS = 5`，快速发 10 次：

```bash
for i in $(seq 1 10); do
    curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/users/123
done
# 前 5 个是 401（无 token 也计数），第 6 个开始 429
```

### 场景 8：扫码登录（浏览器）

```bash
# 启动
.venv/bin/python ../gateway/scan_login_demo.py
# 浏览器打开 http://localhost:9009/
```

按页面 4 个按钮依次点击：
1. 生成二维码 → 拿到 qr_id 和 sig
2. 把 qr_id + sig 填到第二步 → 模拟 App 扫码（自动确认）
3. 回到 PC 轮询 → 拿到 login_code
4. 用 login_code 换 token → 拿到 access + refresh

### 场景 9：扫码登录（命令行）

```bash
# 终端 A：起扫码登录服务
.venv/bin/python ../gateway/scan_login_demo.py

# 终端 B：命令行模拟 PC 端
.venv/bin/python -c "from example.gateway.scan_login_demo import demo_pc; demo_pc()"
```

## 关键代码位置

| 想看 | 文件 |
|---|---|
| 网关中间件链 | `gateway.py`（5 个中间件 + 装配顺序） |
| Casbin RBAC 模型 | `policy/model.conf` + `policy/policy.csv` |
| JWT 双 Token | `auth_demo.py` `issue_tokens / refresh / revoke` |
| 扫码 5 步 | `scan_login_demo.py`（`/qr/generate` → `/qr/scan` → `/qr/status` → `/qr/login`） |
| 下游服务的 X-User-Id 透传 | `service_users.py` `update_user` / `service_orders.py` `list_orders` |

## 相关 demo

- WebSocket demo：`example/ws/`
- 消息队列 demo：`example/mq/`
- 数据库设计 demo：`example/db-design/`