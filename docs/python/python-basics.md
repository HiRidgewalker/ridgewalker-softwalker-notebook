---
title: "Python 基础"
sidebar_position: 1
---

# Python 基础

> Python 语言核心语法与机制的总览笔记。涵盖原 `python基础语言语法笔记`、`python类、对像详解`、`python---module` 三份笔记的合并内容。
> 可运行 demo 代码统一放在 `example/python/` 下，本文通过 git 远程链接引用。

## 编译型 vs 解释型

| 编译型语言 | 解释型语言 |
| --- | --- |
| C | Python |
| C++ | JavaScript |
| Rust | PHP |

- **编译型**：先由编译器编译成机器码，之后每次执行不再依赖编译器
- **解释型**：每次执行都需要解释器读取并执行源代码
- **Java 介于两者之间**：先编译为字节码，由 JVM 解释执行

## 编码规范

参考外部链接：[Python 编码规范 (Google) | 菜鸟教程](https://www.runoob.com/w3cnote/google-python-styleguide.html)

## 基本语法

### 字符串

- 单引号 `'` 和双引号 `"` 使用完全相同
- 三引号 `'''` 或 `"""` 可指定多行字符串
- 转义符 `\`，加 `r` 前缀可禁用转义（如 `r"this \n"` 显示原始字符）
- 按字面意义级联字符串：`"this " "is " "string"` 等价于 `"this is string"`
- 字符串可用 `+` 连接，用 `*` 重复
- 索引左闭右开：`s[0]` 从左起第一个，`s[-1]` 从右起第一个
- **字符串不可改变**

### 同一行显示多条语句

```python
import sys; x = 'runoob'; sys.stdout.write(x + '\n')
```

### 编码

Python 3 源码默认 UTF-8。如需指定其他编码，在文件顶部声明：

```python
# -*- coding: cp-1252 -*-
```

### import 与 from...import 语法

- `import somemodule`：导入整个模块
- `from somemodule import func`：从模块导入指定函数
- `from somemodule import a, b, c`：导入多个
- `from somemodule import *`：导入全部

## 数据类型

### 标准数据类型

- Number（数字）
- String（字符串）
- bool（布尔类型）
- List（列表）
- Tuple（元组）
- Set（集合）
- Dictionary（字典）

### type 与 isinstance 的区别

- `type()` 不会认为子类是父类类型
- `isinstance()` 会认为子类是父类类型

```python
class Animal: pass
class Dog(Animal): pass

dog = Dog()
type(dog) == Dog       # True
type(dog) == Animal    # False
isinstance(dog, Animal)  # True
```

### 字符串

- 单双引号等价
- 三引号支持多行
- `r` 前缀禁用转义
- 字符串不可改变
- 切片格式：`变量[头下标:尾下标:步长]`

### 布尔类型

- 布尔可与数字/字符串比较：`True == 1`，`False == 0`
- 非零数字和非空容器视为 `True`，只有 `0`、`''`、`[]`、`()` 等视为 `False`
- 可与 `int()`、`float()`、`str()` 互相转换

### List（列表）

- 有序可变序列
- 索引、切片、连接、重复、翻转（`list[::-1]`）

### Tuple（元组）

- **元素不可修改**
- 用 `()` 定义，元素用逗号分隔
- 单元素元组必须加逗号：`(20,)`，否则 `(20)` 是整型
- 空元组：`()`

### Set（集合）

- 无序、元素不重复
- 可做交集、并集、差集、对称差运算
- **创建空集合必须用 `set()`**，`{}` 创建的是空字典

### Dict（字典）

- 无序的键值对集合
- 键必须唯一、不可变（如字符串、数字、元组）
- 同一键重复赋值，后值覆盖前值
- 用 `{}` 或 `dict()` 创建

## 数据类型转换

- **隐式**：低类型自动转高类型（如 `int + float` 得 `float`）
- **显式**：使用 `int()`、`float()`、`str()`、`bool()` 等内置函数

完整可运行示例：[example/python/basics/data_types.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/data_types.py)

## 运算符、math 库、random 库

- 运算符完整列表：[Python3 运算符](https://www.runoob.com/python3/python3-basic-operators.html)
- `math` 库：`math.sqrt()`、`math.pi` 等数学函数
- `random` 库：`random.choice(seq)` 从序列随机挑选

## 字符串、列表、元组、字典、集合

详细 API 参考菜鸟教程：

- [Python3 字符串](https://www.runoob.com/python3/python3-string.html)
- [Python3 列表](https://www.runoob.com/python3/python3-list.html)
- [Python3 元组](https://www.runoob.com/python3/python3-tuple.html)
- [Python3 字典](https://www.runoob.com/python3/python3-dictionary.html)
- [Python3 集合](https://www.runoob.com/python3/python3-set.html)

注意：**列表函数 vs 列表方法**——函数是 Python 内置的，方法是 list 类下定义的。

## 条件控制

### if

条件与代码块不需要 `()` 包裹：

```python
if 表达式1:
    语句
    if 表达式2:
        语句
    elif 表达式3:
        语句
    else:
        语句
elif 表达式4:
    语句
else:
    语句
```

### match...case（Python 3.10+）

完整可运行示例：[example/python/basics/match_case.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/match_case.py)

## 循环语句

- `while`、`for`、`for...else`
- `range()` 函数
- `break` 与 `continue`
- `pass` 空语句（占位用）

`for...else` 特点：循环正常结束后执行 `else`；若 `break` 中断则不执行。

## end 关键字

控制 `print` 输出结尾字符，默认换行可改为其他：

```python
a, b = 0, 1
while b < 1000:
    print(b, end=',')
    a, b = b, a + b
```

## 推导式

四种推导式：列表、字典、集合、元组。**注意：元组推导式返回的是生成器对象**，需用 `tuple()` 转换。

完整可运行示例：[example/python/basics/comprehensions.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/comprehensions.py)

## 迭代器与生成器

- **迭代器**：`iter()` 创建，`next()` 读取，只能往前不能后退
- **生成器**：使用 `yield` 的函数，返回一个迭代器，逐步产生值而非一次性返回

完整可运行示例：[example/python/basics/iterators_generators.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/iterators_generators.py)

## 函数

参数类型：

- 必须参数
- 关键字参数
- 默认参数
- 不定长参数（`*args`、`**kwargs`）
- `lambda` 匿名函数
- `return` 语句

参考：[Python3 函数](https://www.runoob.com/python3/python3-function.html)

## 输入输出

读取键盘输入：

```python
s = input("请输入：")
print("你输入的内容是:", s)
```

## 文件操作

`open(filename, mode)` 返回 file 对象，mode 决定读写模式（`r`、`w`、`a` 等）。

文件对象方法：

- `f.read(size)`：读取指定字节，全部读取传负数或省略
- `f.readline()`：读取一行
- `f.readlines()`：读取所有行，返回列表
- `f.write(string)`：写入字符串，返回写入字符数
- `f.tell()`、`f.seek()`：位置操作
- `f.close()`：关闭文件释放资源

完整可运行示例：[example/python/basics/file_io.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/file_io.py)

参考：[Python3 File 方法](https://www.runoob.com/python3/python3-file-methods.html)、[Python3 OS 文件/目录方法](https://www.runoob.com/python3/python3-os-file-methods.html)

## 错误和异常

参考：[Python3 错误和异常](https://www.runoob.com/python3/python3-errors-execptions.html)

## 面向对象

继承与构造方法示例：

完整可运行示例：[example/python/basics/oop_inherit.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/oop_inherit.py)

## 命名空间与作用域

### 命名空间查找顺序

局部命名空间 → 全局命名空间 → 内置命名空间

### 引入新作用域的语句

只有以下三种会引入新的作用域：

- **module**（模块）
- **class**（类）
- **def、lambda**（函数）

`if/elif/else`、`try/except`、`for/while` 等代码块**不引入新作用域**，内部定义的变量外部也可访问。

### global 与 nonlocal

- `global`：在函数内声明要使用全局变量
- `nonlocal`：在嵌套函数内声明要使用外层（非全局）变量

完整可运行示例：[example/python/basics/namespaces_scope.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/basics/namespaces_scope.py)

## 类与对象

### 实例方法、类方法、静态方法

| 方法类型 | 装饰器 | 第一个参数 | 访问能力 |
|---|---|---|---|
| 实例方法 | 无 | `self` | 实例变量、类变量、实例方法、类方法 |
| 类方法 | `@classmethod` | `cls` | 类变量、类方法（不可访问实例） |
| 静态方法 | `@staticmethod` | 无 | 任何类信息都不能访问，相当于寄居在类上的普通函数 |

完整可运行示例：[example/python/class_methods/instance_class_static.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/class_methods/instance_class_static.py)

## 内置函数

### enumerate()

```python
seq = ['one', 'two', 'three']
for i, element in enumerate(seq):
    print(i, element)
```

## collections 模块

官方文档：[collections --- 容器数据类型](https://docs.python.org/zh-cn/3/library/collections.html)

## tqdm 库

```bash
pip install tqdm
```

```python
from tqdm import tqdm
from time import sleep

text = ""
for char in tqdm(["a", "b", "c", "d"]):
    sleep(0.25)
    text = text + char
```

注意：**`tqdm` 包裹的必须是一个可迭代的对象**。

## argparse 库

参考：[python argparse 模块常见用法](https://blog.csdn.net/RudeTomatoes/article/details/117003291)

## pip 常用命令

```shell
# 临时使用阿里云镜像源（解决下载慢）
pip install 库名 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# 删除第三方库
pip uninstall 库名

# 查看默认 python 版本
python -V
py -0p    # 查看已安装的所有 python 版本及路径

# 生成与安装 requirements.txt
pip freeze > requirements.txt
pip install -r requirements.txt
```

## 模块与包

### sys 模块常用属性

- `sys.argv`：命令行参数列表，与程序交互
- `sys.platform`：当前操作系统
- `sys.executable`：当前 Python 解释器可执行文件的绝对路径
- `sys.modules`：已加载模块的名字到位置的字典映射
- `sys.builtin_module_names`：当前解释器内置模块名的元组
- `sys.path`：Python 搜索模块的路径列表，启动时初始化
- `sys.stdin`、`sys.stdout`、`sys.stderr`：标准输入/输出/错误流
- `sys.__stdin__`、`sys.__stdout__`、`sys.__stderr__`：初始值的备份

### sys.path 与入口文件位置

**核心结论：**

- `sys.path` 的**第一个路径永远是入口文件的直接父目录的绝对路径**
- 同一个项目，不同入口文件，第一个路径会不同
- 这就是为什么"包名与模块名同名"会产生导入冲突

可运行演示：[example/python/modules/sys_path_demo/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/python/modules/sys_path_demo)

### import 与 from...import 的语义区别

- `import module`：把整个模块导入到当前符号列表
- `from module import name`：**不导入整个模块**，只把 `name` 导入到当前命名空间
- `from module import *`：导入模块全部内容到当前命名空间

可运行演示：[example/python/modules/import_vs_from.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/modules/import_vs_from.py)

### __name__ 属性

- 直接运行的 `.py` 文件：`__name__ == '__main__'`
- 被 import 的 `.py` 文件：`__name__ == 模块名`

### dir() 函数

- 不带参数：罗列当前文件定义的所有名称（独立符号表）
- 带参数：列出指定模块的所有名称

可运行演示：[example/python/modules/dir_demo.py](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/python/modules/dir_demo.py)

### 包（package）

- **模块名 A.B** 表示包 A 中的子模块 B，可避免不同库之间的模块重名
- 包含 `__init__.py` 的目录才被识别为包
- `__init__.py` 可包含初始化代码，也可为 `__all__` 赋值控制 `from package import *` 的行为

### from...import 与 import 在导包时的差异

- `import item` 先把 `item` 当作包定义的名称，找不到再按模块导入
- `from package import item` 中，`item` 可以是子模块、子包、函数、类或变量

可运行演示：[example/python/modules/package_init/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/python/modules/package_init)

### 同名包冲突（重要经验）

当包名/模块名存在同名嵌套时，`sys.path` 第一个路径下的同名子目录会被解释器错误地当作包来解析，导致 `ImportError` 或导入到错误的对象。

**个人经验总结**：

- 避免包名、模块名、子包名互相重复
- 优先使用绝对导入，避免相对路径
- 不要让包名和模块名同名
- 同一目录下避免同名模块/包
- 功能层面相同、业务不同的类放在不同包中（如 Java 的 controller、service 分包）

可运行复现：[example/python/modules/name_collision/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/python/modules/name_collision)

### 作用域补充

- 在 Python 中，只有**函数（def、lambda）、模块、包**具有局部作用域
- 其他代码块（if/elif/else、try/except、for/while）**没有局部作用域**

参考：[Python3 命名空间和作用域](https://www.runoob.com/python3/python3-namespace-scope.html)