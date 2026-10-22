"""async with 异步上下文管理器与 async for 异步迭代器

涵盖：
- 异步上下文管理器协议：__aenter__ / __aexit__
- 异步迭代器协议：__aiter__ / __anext__
- @asynccontextmanager 装饰器简化异步上下文管理器定义

运行：python async_with_for.py
"""

import asyncio
from contextlib import asynccontextmanager


class AsyncConnection:
    """自定义异步上下文管理器：模拟异步连接"""

    async def __aenter__(self):
        print("  [连接] 建立")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("  [连接] 关闭")
        await asyncio.sleep(0.1)
        return False  # 不吞异常

    async def query(self, sql):
        await asyncio.sleep(0.2)
        return f"[query] {sql}"


class AsyncRange:
    """自定义异步迭代器"""

    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.2)
        value = self.current
        self.current += 1
        return value


@asynccontextmanager
async def managed_resource(name):
    """用装饰器快速定义异步上下文管理器"""
    print(f"  [资源] {name} 初始化")
    try:
        yield name
    finally:
        print(f"  [资源] {name} 清理")


async def demo_async_with():
    print("=== async with ===")
    async with AsyncConnection() as conn:
        result = await conn.query("SELECT 1")
        print(f"  结果: {result}")
    print()

    async with managed_resource("temp.txt") as res:
        print(f"  使用资源: {res}")


async def demo_async_for():
    print("\n=== async for ===")
    async for i in AsyncRange(3):
        print(f"  异步迭代值: {i}")


async def main():
    await demo_async_with()
    await demo_async_for()


if __name__ == "__main__":
    asyncio.run(main())