"""异步生成器：async def + yield

涵盖：
- 异步生成器定义与消费
- 与普通生成器的区别：每次 yield 前可以挂起等待
- 经典用途：分页拉取、消息流推送、WebSocket 数据流

运行：python async_generators.py
"""

import asyncio


async def ticker(interval, count):
    """每隔 interval 秒产出一个值"""
    for i in range(count):
        await asyncio.sleep(interval)
        yield i


async def paginated_fetch(total_pages, page_size=2):
    """模拟分页拉取，每页之间异步等待"""
    pages = list(range(1, total_pages + 1))
    for page in pages:
        await asyncio.sleep(0.3)  # 模拟网络请求
        items = [f"item-{page}-{i}" for i in range(page_size)]
        yield page, items


async def main():
    print("=== 异步生成器 ticker(0.5s, 4) ===")
    async for tick in ticker(0.5, 4):
        print(f"  tick = {tick}")

    print("\n=== 异步生成器 paginated_fetch ===")
    async for page, items in paginated_fetch(total_pages=3):
        print(f"  page {page}: {items}")


if __name__ == "__main__":
    asyncio.run(main())