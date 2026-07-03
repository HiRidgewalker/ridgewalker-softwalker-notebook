"""在 sys.path 第一个路径下，恰好存在同名 module1 子目录时会出错

执行方式（在 module1/module1 目录下）：
    python module2.py

观察 ImportError 或导入到错误对象的现象。
"""

import sys

print("入口文件:", __file__)
print("sys.path 第一个路径:", sys.path[0])

try:
    from module1.module1 import func
    print("导入成功，调用 func：")
    func()
except ImportError as e:
    print(f"导入失败：{e}")