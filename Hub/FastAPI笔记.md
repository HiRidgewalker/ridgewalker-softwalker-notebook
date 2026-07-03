# FastAPI 笔记

> 原 旧稿 + 旧稿 的合并重新整理版本，精炼为 4 章节：速查总览 / 常用模式速查表 / 实战代码片段（指向 workspace demo）/ 常见坑 + 官方文档链接。旧稿目录已清理，当前以本文为准。
> 演示代码统一放在 `workspace/python/fastapi/`，本笔记通过 git 远程链接引用。

## 1. 速查总览

### 1.1 是什么

FastAPI 是基于 **Starlette**（Web 框架）+ **Pydantic**（数据校验）+ **Uvicorn**（ASGI 服务器）的现代 Python Web 框架，主打：

- 高性能（接近 Node.js / Go）
- 类型驱动：编辑器自动补全、参数类型检查
- 自动生成 Swagger UI（`/docs`）和 ReDoc（`/redoc`）

### 1.2 安装

```bash
# 用 uv（推荐）
uv add fastapi "uvicorn[standard]"

# 鉴权 + 密码哈希（用得到就装）
uv add "python-jose[cryptography]" "passlib[bcrypt]" "python-multipart"

# 测试
uv add --dev pytest httpx
```

### 1.3 最小 hello world

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"hello": "world"}
```

启动：

```bash
uv run uvicorn main:app --reload
# 访问 http://127.0.0.1:8000/
# Swagger: http://127.0.0.1:8000/docs
```

完整 hello world（带路径/查询/请求体识别）：[hello_world.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/hello_world.py)

---

## 2. 常用模式速查表

```text
# ===== 路由装饰器 =====
@app.get("/")                        # GET
@app.post("/items")                  # POST
@app.put("/items/{id}")              # PUT
@app.delete("/items/{id}")           # DELETE
@app.patch("/items/{id}")            # PATCH
@app.get("/items", response_model=Item)  # 响应模型（自动序列化 + 过滤字段）
@app.post("/items", status_code=201)    # 默认状态码

# ===== 参数识别规则（核心）=====
@app.get("/items/{item_id}")
def read(item_id: int, q: str = ""):  # 路径里的 int → 路径参数；其他单类型 → 查询
    ...

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create(item: Item):               # Pydantic 模型 → 请求体
    ...

# ===== 数据校验 =====
item_id: int = Path(..., gt=0, le=1000)             # 路径参数校验
q: str = Query(None, min_length=1, max_length=50, pattern="^[a-z]+$")  # 查询参数校验
item: Item = Body(...)                              # 显式声明请求体
importance: int = Body(..., ge=1, le=5, embed=True) # 单值 Body 强制包成 {"importance": ...}
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)                 # Pydantic v2 字段校验

# ===== 依赖注入 =====
def get_db():
    db = ...
    try:
        yield db                  # yield 依赖用于资源清理（DB / 文件 / session）
    finally:
        db.close()

@app.get("/items")
def read(db = Depends(get_db)):   # Depends(fn) 把 fn 返回值注入
    ...

# ===== 错误与异常 =====
raise HTTPException(404, "not found", headers={"X-Err": "x"})  # 标准错误
@app.exception_handler(MyError)    # 自定义异常处理

# ===== 请求上下文 =====
from fastapi import Request, Cookie, Header, Form, File, UploadFile
request: Request                    # 拿原始请求（IP、headers、url）
session_id: str = Cookie(None)      # Cookie 参数
x_token: str = Header(...)          # Header 参数
username: str = Form(...)           # application/x-www-form-urlencoded
file: UploadFile = File(...)        # multipart/form-data 文件

# ===== 响应 =====
@app.get("/x", response_model=Item) # 自动按 Item 序列化
@app.post("/x", status_code=201)    # 自定义状态码
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, HTMLResponse

# ===== 中间件 / CORS =====
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")             # 自定义函数式中间件
async def add_time(request, call_next):
    ...

# ===== 后台任务 =====
from fastapi import BackgroundTasks
@app.post("/send")
def send(bg: BackgroundTasks):
    bg.add_task(send_email, "user@example.com")
    return {"queued": True}

# ===== 鉴权 =====
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def get_user(token: str = Depends(oauth2_scheme)): ...

# ===== 测试 =====
from fastapi.testclient import TestClient
client = TestClient(app)
client.get("/") / client.post("/x", json={...})     # in-process 测，免启服务
```

---

## 3. 实战代码片段

以下 demo 全部放在 `workspace/python/fastapi/`，可独立运行：

| Demo | 涵盖 | 链接 |
| --- | --- | --- |
| `hello_world.py` | 路径/查询/请求体识别规则 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/hello_world.py) |
| `params_demo.py` | Path/Query/Body 校验 + 多请求体 + Field | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/params_demo.py) |
| `depends_and_exception.py` | Depends 基础、yield 依赖、HTTPException、自定义 handler | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/depends_and_exception.py) |
| `middleware_cors.py` | 自定义 HTTP 中间件、CORS、GZip | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/middleware_cors.py) |
| `jwt_auth.py` | OAuth2PasswordBearer + JWT 签发/校验 + bcrypt 哈希 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/jwt_auth.py) |
| `test_client.py` | TestClient 单元测试（含 pytest） | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/test_client.py) |
| `full_app/main.py` | 完整小型 API（注册/登录/items CRUD + curl 测试用例） | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/fastapi/full_app/main.py) |

### 3.1 跑起来看效果

```bash
# 跑最小 demo
uv run uvicorn workspace.python.fastapi.hello_world:app --reload

# 跑完整 API（带鉴权）
uv run uvicorn workspace.python.fastapi.full_app.main:app --reload

# 跑测试
uv run pytest workspace/python/fastapi/test_client.py -v
```

### 3.2 完整 API 的 curl 流程

```bash
# 1. 注册
curl -X POST http://127.0.0.1:8000/register \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","full_name":"Alice","password":"alice123"}'

# 2. 登录拿 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
     -d "username=alice&password=alice123" \
     | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. 创建 item（带 token）
curl -X POST http://127.0.0.1:8000/items \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"book","price":12.5}'

# 4. 列出
curl http://127.0.0.1:8000/items
```

---

## 4. 常见坑 + 官方文档链接

### 4.1 必传 vs 可选字段（Pydantic v2）

```python
class Auth(BaseModel):
    username: str
    password: str | None             # 类型允许 None，但客户端必须传 key（值可为 null）
```

```python
class Auth(BaseModel):
    username: str
    password: str | None = None      # 有默认值，可不传
```

| 写法 | 是否必须传 key |
| --- | --- |
| `password: str \| None` | ✅ 必须传，传 `null` 也算 |
| `password: str \| None = None` | ❌ 可不传，默认 `None` |

> 同样规则适用于 FastAPI 的 `Query`、`Body`、`Header` 等。

### 4.2 同步 vs 异步路由

```python
@app.get("/sync")
def sync_route():           # 同步函数：FastAPI 放线程池跑，不阻塞事件循环
    time.sleep(1)
    return {"ok": True}

@app.get("/async")
async def async_route():    # 异步函数：直接在事件循环跑
    await asyncio.sleep(1)
    return {"ok": True}
```

- **IO 密集**用 `async def` + 异步客户端（httpx、asyncpg、aiomysql）
- **CPU 密集**或调阻塞库（requests、psycopg2、time.sleep）用 `def`（自动线程池）
- ❌ 不要在 `async def` 里调阻塞 IO，会卡死整个事件循环

### 4.3 `Depends` 嵌套与性能

- 每层 `Depends` 都会在每次请求里重新调用
- 同请求内多次用同一个依赖，默认会缓存结果（`use_cache=True`）
- 想要强一致：传 `use_cache=False`
- 想要真缓存：自己用 `functools.lru_cache` 或 Redis

### 4.4 Pydantic v2 常见迁移注意

- `class Config:` + `orm_mode = True` → `model_config = ConfigDict(from_attributes=True)`
- `@validator("x")` → `@field_validator("x")`
- `@root_validator` → `@model_validator(mode="before"/"after")`
- `.dict()` → `.model_dump()`
- `.json()` → `.model_dump_json()`

### 4.5 CORS 预检失败

开发时典型报错：`No 'Access-Control-Allow-Origin' header is present`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 生产环境写具体域名，不要用 ["*"]
    allow_credentials=True,                   # 想带 cookie 时必须 True
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> ⚠️ `allow_origins=["*"]` + `allow_credentials=True` 是非法组合（浏览器拒绝），二选一。

### 4.6 `uvicorn --reload` 与多 worker 不兼容

```bash
# 开发
uvicorn main:app --reload

# 生产：多 worker（不要带 --reload）
uvicorn main:app --host 0.0.0.0 --workers 4

# 或用 gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 4.7 启动后 422

请求体字段名/类型不对，FastAPI 自动返回 422 + 详细错误列表。打开 `/docs` 在 Swagger UI 里直接调，能看到正确格式。

### 4.8 Swagger 看不到新接口

`/docs` 是动态生成的，**不需要**重启；`--reload` 时改了代码自动生效。

### 4.9 官方文档链接

- 总览：<https://fastapi.tiangolo.com/zh/>
- 路径参数：<https://fastapi.tiangolo.com/zh/tutorial/path-params/>
- 查询参数：<https://fastapi.tiangolo.com/zh/tutorial/query-params/>
- 请求体：<https://fastapi.tiangolo.com/zh/tutorial/body/>
- 数据校验：<https://fastapi.tiangolo.com/zh/tutorial/query-params-str-validations/>
- 依赖注入：<https://fastapi.tiangolo.com/zh/tutorial/dependencies/>
- 异常处理：<https://fastapi.tiangolo.com/zh/tutorial/handling-errors/>
- 中间件：<https://fastapi.tiangolo.com/zh/tutorial/middleware/>
- CORS：<https://fastapi.tiangolo.com/zh/tutorial/cors/>
- 鉴权（OAuth2 + JWT）：<https://fastapi.tiangolo.com/zh/tutorial/security/oauth2-jwt/>
- 后台任务：<https://fastapi.tiangolo.com/zh/tutorial/background-tasks/>
- 测试：<https://fastapi.tiangolo.com/zh/tutorial/testing/>
- 部署：<https://fastapi.tiangolo.com/zh/deployment/>
