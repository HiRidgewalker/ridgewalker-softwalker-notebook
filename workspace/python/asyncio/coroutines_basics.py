"""asyncio 协程与任务基础

涵盖：
- async def 定义协程函数
- 调用协程函数返回的是 coroutine 对象，不会真正执行
- 必须用 await 才能运行协程
- asyncio.run() 启动事件循环
- asyncio.create_task() 把协程包装成 Task 并调度

运行：python coroutines_basics.py
"""

import asyncio


async def fetch_data(name, delay):
    """模拟一次异步 I/O"""
    print(f"  [{name}] 开始")
    await asyncio.sleep(delay)
    print(f"  [{name}] 完成")
    return f"{name}-result"


async def demo_call_without_await():
    """演示：忘记 await 时协程不会执行"""
    print("=== 调用协程但忘了 await ===")
    coro = fetch_data("A", 0.5)  # 只创建协程对象
    print(f"  type(coro) = {type(coro).__name__}")  # coroutine
    # 协程对象从未被等待，结束时会有 RuntimeWarning


async def demo_await_coroutine():
    """演示：await 触发协程执行并取得返回值"""
    print("\n=== await 一个协程 ===")
    result = await fetch_data("B", 0.3)
    print(f"  result = {result}")


async def demo_create_task():
    """演示：create_task 把协程包装为 Task，立即调度执行"""
    print("\n=== asyncio.create_task ===")
    task = asyncio.create_task(fetch_data("C", 0.2))
    print(f"  task 已创建并开始调度: {task}")
    result = await task  # 等待任务完成
    print(f"  task 结果 = {result}")


async def main():
    await demo_call_without_await()
    await demo_await_coroutine()
    await demo_create_task()


if __name__ == "__main__":
    asyncio.run(main())