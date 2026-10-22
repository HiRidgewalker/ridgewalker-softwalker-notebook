"""实例方法、类方法、静态方法对比演示

运行：python instance_class_static.py

三者的关键区别：
- 实例方法：能访问实例变量、类变量、实例方法、类方法
- 类方法（@classmethod）：只能访问类变量、类方法，不能访问实例变量/方法
- 静态方法（@staticmethod）：无类上下文，不能访问任何类信息
"""


class Demo:
    class_var = "类变量"

    def __init__(self, name):
        self.name = name  # 实例变量

    def instance_method(self):
        """实例方法：第一个参数是 self"""
        print(f"实例方法：name={self.name}, class_var={Demo.class_var}")

    @classmethod
    def class_method(cls):
        """类方法：第一个参数是 cls"""
        print(f"类方法：class_var={cls.class_var}")

    @staticmethod
    def static_method(x, y):
        """静态方法：无默认参数，相当于一个寄居在类上的普通函数"""
        return x + y


if __name__ == "__main__":
    d = Demo("张三")
    d.instance_method()                       # 通过实例调用
    Demo.class_method()                       # 通过类调用
    print(f"静态方法：{Demo.static_method(1, 2)}")