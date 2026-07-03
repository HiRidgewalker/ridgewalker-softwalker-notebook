"""pkg_a 包内的一个模块"""


def hello():
    print("hello from pkg_a.module_a")


class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hi, {self.name}!")