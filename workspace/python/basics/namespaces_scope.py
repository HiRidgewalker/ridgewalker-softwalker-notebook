"""命名空间与作用域演示

涵盖：global、nonlocal、UnboundLocalError
运行：python namespaces_scope.py
"""


def global_demo():
    """global 关键字：函数内修改全局变量"""
    print("=== global ===")
    num = 1

    def fun1():
        global num
        print(num)
        num = 123
        print(num)

    fun1()
    print(num)  # 123


def nonlocal_demo():
    """nonlocal 关键字：修改嵌套作用域中的变量"""
    print("\n=== nonlocal ===")

    def outer():
        num = 10

        def inner():
            nonlocal num
            num = 100
            print(num)  # 100

        inner()
        print(num)  # 100

    outer()


def unbound_local_error():
    """未声明 global 直接赋值会触发 UnboundLocalError"""
    print("\n=== UnboundLocalError 与修复 ===")
    a = 10

    def test_buggy():
        # 下一行报错：local variable 'a' referenced before assignment
        # a = a + 1
        # print(a)
        pass

    try:
        test_buggy()
    except UnboundLocalError as e:
        print("错误演示：", e)

    # 修复方法 1：global
    a = 10

    def test_global():
        global a
        a = a + 1
        print(a)  # 11

    test_global()

    # 修复方法 2：传参
    a = 10

    def test_arg(a):
        a = a + 1
        print(a)  # 11

    test_arg(a)


if __name__ == "__main__":
    global_demo()
    nonlocal_demo()
    unbound_local_error()