"""文件读写演示

涵盖：open()、read()、readline()、readlines()、write()、with 语句
运行：python file_io.py
"""

import os

TMP_FILE = "/tmp/foo_demo.txt"


def write_demo():
    """写入示例文件"""
    with open(TMP_FILE, "w") as f:
        f.write("Python 是一个非常好的语言。\n")
        f.write("是的，的确非常好!!\n")


def read_all():
    """read() 一次性读取全部内容"""
    print("=== read() ===")
    with open(TMP_FILE, "r") as f:
        print(f.read())


def read_lines():
    """for 循环逐行读取"""
    print("=== 逐行读取 ===")
    with open(TMP_FILE, "r") as f:
        for line in f:
            print(line.rstrip())


def cleanup():
    if os.path.exists(TMP_FILE):
        os.remove(TMP_FILE)


if __name__ == "__main__":
    write_demo()
    read_all()
    read_lines()
    cleanup()