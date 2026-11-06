---
title: "Python 异步编程（asyncio）"
---

# Python 异步编程（asyncio）

> 原 `python--异步编程（asyncio）` 笔记的提炼与完善版本。可运行 demo 在 `example/python/asyncio/` 下，本文件通过 git 远程链接引用。

## 文档参考

- [asyncio --- 异步 I/O（官方文档中文）](https://docs.python.org/zh-cn/3.10/library/asyncio.html)

## 核心模型

asyncio 是 Python 内置的 **单线程协作式并发** 框架，由三部分组成：

| 概念 | 角色 |
|---|---|
| **事件循环（event loop）** | 调度和执行协程，相当于调度器 |
| **协程（coroutine）** | 用 `async def` 定义的函数，调用后返回 coroutine 对象 |
| **任务（Task）** | 被事件循环调度的协程包装，由 `asyncio.create_task` 创建 |

**关键点**：asyncio 是**单线程**的，"并发" 通过在 I/O 等待时让出控制权实现，**不能利用多核 CPU**。CPU 密集型任务不应使用 asyncio。

## 可等待对象（Awaitable）

共三种：

| 类型 | 说明 | 使用频率 |
|---|---|---|
| **协程 coroutine** | `async def` 函数调用后的产物 | 最高 |
| **Task** | `asyncio.create_task` 包装的协程 | 高 |
| **Future** | 底层异步结果占位符 | 低，一般作为库作者接口 |

完整可运行示例：[example/python/asyncio/coroutines_basics.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/asyncio/coroutines_basics.py)

## 关键字使用场景

### async 用在哪里

`async` 用于**定义**异步结构本身：

| 语法 | 作用 |
|---|---|
| `async def fn()` | 定义协程函数 |
| `async with cm` | 异步上下文管理器协议（`__aenter__` / `__aexit__`） |
| `async for x in it` | 异步迭代器协议（`__aiter__` / `__anext__`） |

### await 用在哪里

`await` 用于**挂起当前协程**，等待另一个可等待对象：

| 场景 | 示例 |
|---|---|
| 调用异步函数 | `result = await fetch_data()` |
| 异步 I/O 库 | `await asyncio.sleep(1)`、`await session.get(url)` |
| 并发执行 | `await asyncio.gather(coro1(), coro2())` |
| 等待 Task | `result = await task` |

### 错误对比

| 场景 | 正确 | 错误 | 原因 |
|---|---|---|---|
| 定义异步函数 | `async def fn():` | `def fn():` | 没有 `async` 不能 `await` |
| 调用异步函数 | `await fn()` | `fn()` | 不 await 拿到 coroutine 对象，不会执行 |
| 异步上下文管理器 | `async with ...:` | `with ...:` | 同步 `with` 不能管理异步对象 |
| 异步迭代 | `async for x in ...:` | `for x in ...:` | 无法迭代异步生成器 |

完整可运行示例：[example/python/asyncio/coroutines_basics.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/asyncio/coroutines_basics.py)

## 常用 API

### 启动与运行

- `asyncio.run(coro)`：同步入口，启动事件循环运行顶层协程（Python 3.7+）
- `asyncio.create_task(coro)`：把协程包装为 Task 并立即调度，返回 Task 对象
- `await task`：等待任务完成并取得返回值

### 并发

- `asyncio.gather(*coros, return_exceptions=False)`：并发执行，结果按传入顺序返回
- `asyncio.wait_for(coro, timeout)`：超时控制，超时抛 `asyncio.TimeoutError`
- `task.add_done_callback(fn)`：任务完成回调

### 等待

- `await asyncio.sleep(n)`：异步睡眠，让出控制权
- `asyncio.Queue`：异步队列，用于生产者/消费者

完整可运行示例：[example/python/asyncio/concurrency.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/asyncio/concurrency.py)

## 异步上下文与异步迭代

### async with（异步上下文管理器）

协议方法：`__aenter__` / `__aexit__`。典型场景：

- 异步文件 IO（`aiofiles.open`）
- 异步 HTTP 连接（`aiohttp.ClientSession`、`httpx.AsyncClient`）
- 异步数据库连接（`asyncpg`、`databases`）

简化定义：用 `@asynccontextmanager` 装饰器。

### async for（异步迭代器）

协议方法：`__aiter__` / `__anext__`。典型场景：

- WebSocket / SSE 消息流
- 异步分页 API 拉取
- 异步文件逐行读取

完整可运行示例：[example/python/asyncio/async_with_for.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/asyncio/async_with_for.py)

## 异步生成器

`async def` 函数体中包含 `yield` 即为异步生成器，用 `async for` 消费。

与普通生成器的区别：**每次 yield 之前可以 `await` 异步操作**，因此特别适合分页拉取、消息推送等流式场景。

完整可运行示例：[example/python/asyncio/async_generators.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/asyncio/async_generators.py)

## 串行 vs 并发对比

```text
serial:    A ─────► B ─────► C ─────►   总耗时 ≈ A+B+C
concurrent: A ─────►
            B ─────►                    总耗时 ≈ max(A,B,C)
            C ─────►
```

`asyncio.gather` 让独立的 I/O 任务并行等待，总耗时接近最慢那个。CPU 密集型代码不会因 gather 加速。

## 常见陷阱

1. **协程没 await**：`coro = fetch()` 只创建对象不执行，结束时会发出 `RuntimeWarning: coroutine was never awaited`
2. **同步阻塞调用**：在 `async def` 中调用 `time.sleep()`、`requests.get()` 会阻塞整个事件循环 → 必须用 `asyncio.sleep()` + 异步 HTTP 库
3. **错误处理**：`asyncio.gather` 中任意协程抛异常都会传播给 `await gather` 这行；用 `return_exceptions=True` 把异常作为结果
4. **跨事件循环**：Task 只能在被创建的事件循环里 await，跨循环访问会抛 `RuntimeError`
5. **不要用 asyncio 做 CPU 密集型**：纯 CPU 工作用 `multiprocessing` 或 `ProcessPoolExecutor`

## asyncio vs threading vs multiprocessing

| 场景 | 推荐方案 |
|---|---|
| I/O 密集型 + 高并发（如爬虫、网关） | asyncio |
| I/O 密集型 + 需要兼容旧同步库 | threading |
| CPU 密集型 | multiprocessing |

asyncio 的优势在于**单线程内高并发**，避免线程切换开销和 GIL 限制下线程池的资源争抢。

## 典型应用生态

| 领域 | 常用库 |
|---|---|
| HTTP 客户端 | `aiohttp`、`httpx` |
| 文件 IO | `aiofiles` |
| 数据库 | `asyncpg`、`databases`、`SQLAlchemy[asyncio]` |
| WebSocket | `websockets`、`aiohttp` |
| 消息队列 | `aiokafka`、`aio-pika` |
| Web 框架 | `FastAPI`、`aiohttp` |

## 运行约定

所有 demo 使用 `example/.venv/` 下的 Python 3.12，虚拟环境位于 `example/.venv/`。

```bash
example/.venv/bin/python example/python/asyncio/coroutines_basics.py
```