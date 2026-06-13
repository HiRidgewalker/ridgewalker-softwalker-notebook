"""asyncio 并发执行：gather、create_task、wait_for

涵盖：
- 串行 vs 并发的耗时对比
- asyncio.gather 并发运行多个协程，保持结果顺序
- gather(return_exceptions=True) 把异常作为结果返回
- asyncio.wait_for 给任务加超时
- asyncio.create_task 主动调度并保存任务引用

运行：python concurrency.py
"""

import asyncio
import time


async def fetch(name, delay):
    print(f"  [{name}] 开始, sleep {delay}s")
    await asyncio.sleep(delay)
    return f"{name}-result"


async def serial_run():
    """串行执行：总耗时是各任务之和"""
    print("--- 串行执行 ---")
    start = time.perf_counter()
    r1 = await fetch("A", 1)
    r2 = await fetch("B", 1)
    r3 = await fetch("C", 1)
    print(f"  总耗时 = {time.perf_counter() - start:.2f}s")
    return [r1, r2, r3]


async def concurrent_gather():
    """gather 并发：总耗时接近最慢的一个"""
    print("\n--- asyncio.gather 并发 ---")
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch("A", 1),
        fetch("B", 1),
        fetch("C", 1),
    )
    print(f"  总耗时 = {time.perf_counter() - start:.2f}s")
    print(f"  结果顺序 = {results}")  # 与传入顺序一致


async def gather_exception_handling():
    """gather 的异常处理：return_exceptions=True"""
    print("\n--- gather 异常处理 ---")

    async def fail():
        await asyncio.sleep(0.1)
        raise ValueError("模拟失败")

    async def ok():
        await asyncio.sleep(0.2)
        return "ok"

    # 默认情况下，gather 中任意协程抛异常都会传播给 await gather 这行
    results = await asyncio.gather(fail(), ok(), return_exceptions=True)
    for i, r in enumerate(results):
        print(f"  task{i}: {type(r).__name__} -> {r}")


async def with_timeout():
    """wait_for 超时控制"""
    print("\n--- asyncio.wait_for 超时 ---")
    try:
        await asyncio.wait_for(fetch("慢任务", 3), timeout=1.0)
    except asyncio.TimeoutError:
        print("  任务超时，已取消")


async def task_done_callback():
    """create_task + add_done_callback：任务完成时通知"""
    print("\n--- Task 回调 ---")

    def on_done(t: asyncio.Task):
        print(f"  回调触发: result={t.result()}")

    task = asyncio.create_task(fetch("D", 0.5))
    task.add_done_callback(on_done)
    await task


async def main():
    await serial_run()
    await concurrent_gather()
    await gather_exception_handling()
    await with_timeout()
    await task_done_callback()


if __name__ == "__main__":
    asyncio.run(main())