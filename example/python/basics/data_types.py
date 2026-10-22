"""Python 数据类型与转换演示

涵盖：隐式类型转换、显式类型转换、type/isinstance 区分
运行：python data_types.py
"""


def implicit_conversion():
    """隐式类型转换：较低数据类型自动转为较高数据类型"""
    print("=== 隐式类型转换 ===")
    num_int = 123
    num_flo = 1.23
    num_new = num_int + num_flo

    print("num_int 数据类型为:", type(num_int))
    print("num_flo 数据类型为:", type(num_flo))
    print("num_new 值为:", num_new)
    print("num_new 数据类型为:", type(num_new))


def explicit_conversion():
    """显式类型转换：使用 int()、float()、str() 等内置函数"""
    print("\n=== 显式类型转换 ===")
    # int()
    print(int(1), int(2.8), int("3"))
    # float()
    print(float(1), float(2.8), float("3.0"), float("4.2"))
    # str()
    print(str("s1"), str(2), str(3.0))


def type_vs_isinstance():
    """type() 不会认为子类是父类类型，isinstance() 会"""
    print("\n=== type vs isinstance ===")

    class Animal:
        pass

    class Dog(Animal):
        pass

    dog = Dog()
    print("type(dog) == Dog:", type(dog) == Dog)        # True
    print("type(dog) == Animal:", type(dog) == Animal)  # False
    print("isinstance(dog, Dog):", isinstance(dog, Dog))        # True
    print("isinstance(dog, Animal):", isinstance(dog, Animal))  # True
    print("isinstance(dog, object):", isinstance(dog, object))  # True


def bool_truthiness():
    """布尔类型与其他类型的比较与转换"""
    print("\n=== bool 规则 ===")
    a, b = True, False
    print("int(True)=", int(a), "float(False)=", float(b), "str(True)=", str(a))

    # 非零数字和非空容器视为 True
    print("bool(0)=", bool(0), "bool('')=", bool(""), "bool([])=", bool([]))
    print("bool(1)=", bool(1), "bool('x')=", bool("x"), "bool([0])=", bool([0]))


if __name__ == "__main__":
    implicit_conversion()
    explicit_conversion()
    type_vs_isinstance()
    bool_truthiness()