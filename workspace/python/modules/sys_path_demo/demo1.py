"""demo1：在 sys_path_demo 根目录下执行

预期 sys.path 第一个路径 = 当前文件所在目录（即 sys_path_demo 本身的绝对路径）
"""
import sys

if __name__ == "__main__":
    print("入口文件:", __file__)
    print("sys.path 第一个路径:", sys.path[0])