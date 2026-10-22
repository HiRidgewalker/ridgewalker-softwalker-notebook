"""import 与 from...import 的区别演示

核心结论：
- import module：把整个模块导入到当前符号列表，可通过 module.xxx 访问
- from module import name：仅把指定名字导入到当前命名空间，模块本身不在符号列表中

运行：python import_vs_from.py
"""

import sys
import os

# 将当前目录加入 sys.path，以便能 import 同目录下的 demo 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    # 模拟：定义一个简单的模块（通过字符串编译）
    module_source = """
a = 1
b = 2

def hello():
    print('hello from demo')
"""

    # === 方式 1：import 整个模块 ===
    import types
    mod1 = types.ModuleType("demo")
    exec(module_source, mod1.__dict__)

    print("=== import 整个模块 ===")
    print("mod1 在当前命名空间:", "mod1" in dir())  # True（如果通过 import 关键字）
    print("可访问 mod1.a:", mod1.a)

    # === 方式 2：from...import 指定名字 ===
    print("\n=== from...import 指定名字 ===")
    namespace = {}
    exec("from demo import a, hello", {"demo": mod1}, namespace)
    print("namespace 中有 a:", "a" in namespace)
    print("namespace 中有 hello:", "hello" in namespace)
    print("namespace 中没有 demo（模块本身未导入）:", "demo" not in namespace)


if __name__ == "__main__":
    main()