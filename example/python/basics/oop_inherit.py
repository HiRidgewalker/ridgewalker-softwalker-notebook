"""面向对象：继承与构造方法演示

运行：python oop_inherit.py
"""


class People:
    name = ''
    age = 0
    __weight = 0  # 私有属性，类外部无法直接访问

    def __init__(self, n, a, w):
        self.name = n
        self.age = a
        self.__weight = w

    def speak(self):
        print(f"我叫{self.name}，今年{self.age}岁。")


class Student(People):
    grade = ''

    def __init__(self, n, a, w, g):
        People.__init__(self, n, a, w)
        self.grade = g

    # 覆盖父类方法
    def speak(self):
        print(f"{self.name}说：我今年{self.age}岁，读{self.grade}年级")


if __name__ == "__main__":
    s = Student('ken', 10, 60, 3)
    s.speak()