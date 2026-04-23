## 异步文档
[asyncio --- 异步 I/O — Python 3.10.16 文档](https://docs.python.org/zh-cn/3.10/library/asyncio.html)

## 可等待对象种类
+ 协程

```python
import asyncio

async def nested():
    return 42

async def main():
    # Nothing happens if we just call "nested()".
    # A coroutine object is created but not awaited,
    # so it *won't run at all*.
    nested()

    # Let's do it differently now and await it:
    print(await nested())  # will print "42".

asyncio.run(main())
```

+ 任务

```python
import asyncio

async def nested():
    return 42

async def main():
    # Schedule nested() to run soon concurrently
    # with "main()".
    task = asyncio.create_task(nested())

    # "task" can now be used to cancel "nested()", or
    # can simply be awaited to wait until it is complete:
    await task

asyncio.run(main())
```

+ Future (使用的比较少)



## 总结： 什么情况下需要使用async, 什么情况下需要使用await
### 哪些地方要加 `async`
`async` 是用来 **定义异步函数或异步上下文管理器的**，主要用于以下几种情况：

#### 1. `async def` 定义异步函数
```python
# 复制编辑
async def fetch_data():
    return "data"
```

+ 这是最常见的用法。
+ 返回值是一个 **协程对象（coroutine object）**，需要 `await` 才能执行。

---

#### 2. `async with` 异步上下文管理器
```python
# 复制编辑
async with aiofiles.open('file.txt', mode='r') as f:
    content = await f.read()
```

+ 用于异步资源的管理，如 `aiofiles`（异步文件IO），`httpx.AsyncClient()`，数据库连接等。

---

### 3. `async for` 异步迭代器
```python
# 复制编辑
async for line in aio_readlines():
    print(line)
```

+ 比如异步读取流、异步分页API等场景。

---

### 二、哪些地方要加 `await`
`await` 是用来**挂起当前协程，等待另一个协程完成并返回结果**，用于以下对象前面：

#### 1. 异步函数调用
```python
# 复制编辑
result = await fetch_data()
```

+ `fetch_data()` 是一个用 `async def` 定义的函数。
+ 不加 `await`，拿到的是一个 coroutine 对象，不会真正执行。

---

#### 2. 异步库的函数（协程对象）
如：

+ `await asyncio.sleep(1)`
+ `await session.get(url)`（如在 `aiohttp.ClientSession` 中）
+ `await websocket.send("message")`
+ `await db.fetch_one(...)`（如 `databases` 库）

---

#### 3. 等待多个协程（并发执行）
```python
# 复制编辑
results = await asyncio.gather(task1(), task2())
```

+ `gather` 也返回一个协程对象。

---

#### 4. 任务（`asyncio.create_task()` 之后）
```python
# 复制编辑
task = asyncio.create_task(fetch_data())
await task  # 等待任务完成
```

---

### 5. 异步生成器（`async for` 中使用时）
```python
# 复制编辑
async def agen():
    for i in range(3):
        yield i

async for val in agen():
    print(val)
```

---

## 三、常见错误理解 & 对比
| 场景 | 正确写法 | 错误示例 | 原因 |
| --- | --- | --- | --- |
| 定义异步函数 | `async def fn():` | `def fn():` | 少了 `async`<br/>，不能 `await` |
| 调用异步函数 | `await fn()` | `fn()` | 不 `await`<br/> 不会执行 |
| 使用异步上下文管理器 | `async with ...:` | `with ...:` | 不能用同步 `with`<br/> 管理异步对象 |
| 异步迭代 | `async for x in ...:` | `for x in ...:` | 无法迭代异步生成器 |


---

## 四、总结表格
| 用法 | 是否需要 async | 是否需要 await | 示例 |
| --- | --- | --- | --- |
| 定义异步函数 | ✅ | ❌ | `async def my_func():` |
| 调用异步函数 | ❌ | ✅ | `await my_func()` |
| 异步上下文管理器 | ✅ | ✅（内层） | `async with ...:` |
| 异步迭代 | ✅ | ❌（结构语法） | `async for item in agen():` |
| 普通协程 | ❌ | ✅ | `await asyncio.sleep(1)` |
| 并发任务 | ❌ | ✅ | `await asyncio.gather(...)` |
| 创建任务 | ❌ | ✅ | `task = asyncio.create_task(...); await task` |


