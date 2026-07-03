"""迭代器与生成器演示

运行：python iterators_generators.py
"""


def iterator_demo():
    """迭代器：iter() 创建，next() 读取，只能往前不会后退"""
    print("=== 迭代器 ===")
    data = [1, 2, 3, 4]
    it = iter(data)
    print(next(it))  # 1
    print(next(it))  # 2

    print("--- 用 for 遍历剩余元素 ---")
    for x in it:
        print(x, end=" ")
    print()


def generator_demo():
    """生成器：使用 yield 的函数，返回迭代器"""
    print("\n=== 生成器 ===")

    def countdown(n):
        while n > 0:
            yield n
            n -= 1

    gen = countdown(5)
    print(next(gen))  # 5
    print(next(gen))  # 4
    print(next(gen))  # 3
    print("--- 用 for 遍历剩余 ---")
    for value in gen:
        print(value, end=" ")
    print()


if __name__ == "__main__":
    iterator_demo()
    generator_demo()