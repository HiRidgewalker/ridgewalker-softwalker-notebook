"""Python 推导式演示：列表 / 字典 / 集合 / 元组

运行：python comprehensions.py
"""


def list_comprehension():
    """列表推导式：[表达式 for 变量 in 可迭代对象 if 条件]"""
    print("=== 列表推导式 ===")
    names = ['Bob', 'Tom', 'alice', 'Jerry', 'Wendy', 'Smith']
    new_names = [name.upper() for name in names if len(name) > 3]
    print(new_names)
    # ['ALICE', 'JERRY', 'WENDY', 'SMITH']


def dict_comprehension():
    """字典推导式：{key_expr: value_expr for value in collection if 条件}"""
    print("\n=== 字典推导式 ===")
    listdemo = ['Google', 'Runoob', 'Taobao']
    newdict = {key: len(key) for key in listdemo}
    print(newdict)  # {'Google': 6, 'Runoob': 6, 'Taobao': 6}

    dic = {x: x ** 2 for x in (2, 4, 6)}
    print(dic, type(dic))


def set_comprehension():
    """集合推导式：{表达式 for item in Sequence if 条件}"""
    print("\n=== 集合推导式 ===")
    setnew = {i ** 2 for i in (1, 2, 3)}
    print(setnew)  # {1, 4, 9}

    a = {x for x in 'abracadabra' if x not in 'abc'}
    print(a, type(a))


def tuple_comprehension():
    """元组推导式返回的是生成器，需用 tuple() 转换"""
    print("\n=== 元组推导式（生成器）===")
    a = (x for x in range(1, 10))
    print(a)               # <generator object <genexpr> at 0x...>
    print(tuple(a))        # (1, 2, 3, 4, 5, 6, 7, 8, 9)


if __name__ == "__main__":
    list_comprehension()
    dict_comprehension()
    set_comprehension()
    tuple_comprehension()