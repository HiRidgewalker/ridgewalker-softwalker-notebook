"""demo2：在 subdir 目录下执行

预期 sys.path 第一个路径 = 当前文件所在目录（即 subdir 的绝对路径），而非 sys_path_demo
"""
import sys

if __name__ == "__main__":
    print("入口文件:", __file__)
    print("sys.path 第一个路径:", sys.path[0])