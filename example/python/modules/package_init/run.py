"""包导入演示：from package import item 的两种行为

关键结论：
- import 语法首先把 item 当作包定义的名称，找不到再按模块导入
- from package import item 中，item 可以是子模块、子包、函数、类或变量

运行（在 package_init 目录下）：
    python run.py
"""

import os
import sys

# 将 package_init 的父目录加入 sys.path，便于 import pkg_a
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def demo_from_package_import():
    """正确：import 子模块"""
    from pkg_a.module_a import hello
    print("--- 从子模块导入函数 ---")
    hello()


def demo_from_package_import_class():
    """导入子模块中的类"""
    from pkg_a.module_a import Greeter
    print("\n--- 从子模块导入类 ---")
    g = Greeter("张三")
    g.greet()


def demo_init_runs_on_import():
    """展示 __init__.py 在包被导入时自动执行"""
    print("\n--- 触发包导入（观察 __init__.py 输出）---")
    import pkg_a
    print("pkg_a.__all__ =", getattr(pkg_a, "__all__", None))


if __name__ == "__main__":
    demo_from_package_import()
    demo_from_package_import_class()
    demo_init_runs_on_import()