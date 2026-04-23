# 编译型语言和解释型语言
编译型语言

编译型语言需要先经过编译器编译成机器码，之后每次执行就不再依赖编译器

解释型语言

对于解释型语言，每次执行的时候都需要解释器来执行源代码

| 编译型语言 | 解释型语言 |
| --- | --- |
| C | python |
| C++ | javascript |
| Rust | PHP |
| ... | ... |


java是介于编译型和解释型语言之间的

# 标准ASCII码
# python编码规范
[Python 编码规范(Google) | 菜鸟教程 (runoob.com)](https://www.runoob.com/w3cnote/google-python-styleguide.html)

# Python3
## python3基本语法
### 字符串
+ Python 中单引号 **'** 和双引号 **"** 使用完全相同。
+ 使用三引号(**'''** 或 **"""**)可以指定一个多行字符串。
+ 转义符 `**\**`。
+ 反斜杠可以用来转义，使用 **r** 可以让反斜杠不发生转义。 如 **r"this is a line with \n"** 则 **\n** 会显示，并不是换行。
+ 按字面意义级联字符串，如 **"this " "is " "string"** 会被自动转换为 **this is string**。
+ 字符串可以用 **+** 运算符连接在一起，用 ***** 运算符重复。

```python
a1 = "aaa"
a2 = "bbb"
print(a1 + a2)
print(a1 * 3)

"""
aaabbb
aaaaaaaaa
"""
```

+ Python 中的字符串有两种索引方式，从左往右以 **0** 开始，从右往左以 **-1** 开始。
+ Python 中的字符串不能改变。
+ Python 没有单独的字符类型，一个字符就是长度为 1 的字符串。
+ 字符串的截取的语法格式如下：**变量[头下标:尾下标:步长]**

### 同一行显示多条语句
```python
#!/usr/bin/python3
import sys; x = 'runoob'; sys.stdout.write(x + '\n')
```

### 编码
默认情况下，Python 3 源码文件以 **UTF-8** 编码，所有字符串都是 unicode 字符串。 当然你也可以为源码文件指定不同的编码：

```python
# -*- coding: cp-1252 -*-
```

---

### import 与 from...import
```plain
在 python 用 import 或者 from...import 来导入相应的模块。

将整个模块(somemodule)导入，格式为： import somemodule

从某个模块中导入某个函数,格式为： from somemodule import somefunction

从某个模块中导入多个函数,格式为： from somemodule import firstfunc, secondfunc, thirdfunc

将某个模块中的全部函数导入，格式为： from somemodule import *
```

## python3数据类型
### 标准数据类型
+ Number（数字）
+ String（字符串）
+ bool（布尔类型）
+ List（列表）
+ Tuple（元组）
+ Set（集合）
+ Dictionary（字典）

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457436-80b7e91d-3065-48fb-88f3-30c85b3f69a7.png)

### type和isinstance
> + type()不会认为子类是一种父类类型。
> + isinstance()会认为子类是一种父类类型。
>

```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()

print(type(dog))  # <class '__main__.Dog'>
print(type(dog) == Dog)  # True
print(type(dog) == Animal)  # False

print(isinstance(dog, Dog))  # True
print(isinstance(dog, Animal))  # True
print(isinstance(dog, object))  # True
```

### string(字符串)
#### raw string原生字符串
> Python 使用反斜杠 \ 转义特殊字符，如果你不想让反斜杠发生转义，可以在字符串前面添加一个 r
>

### bool(布尔类型)
+ 布尔类型可以和其他数据类型进行比较，比如数字、字符串等。在比较时，Python 会将 True 视为 1，False 视为 0。
+ 布尔类型也可以被转换成其他数据类型，比如整数、浮点数和字符串。在转换时，True 会被转换成 1，False 会被转换成 0。
+ 在 Python 中，所有非零的数字和非空的字符串、列表、元组等数据类型都被视为 True，只有 **0、空字符串、空列表、空元组**等被视为 False。因此，在进行布尔类型转换时，需要注意数据类型的真假性。

```python
a = True
b = False

# 类型转换
print(int(a))   # 1
print(float(b)) # 0.0
print(str(a))   # "True"
```



### List(列表)
```python
list = [ 'abcd', 786 , 2.23, 'runoob', 70.2 ]
tinylist = [123, 'runoob']

print (list)            # 输出完整列表
print (list[0])         # 输出列表第一个元素
print (list[1:3])       # 从第二个开始输出到第三个元素
print (list[2:])        # 输出从第三个元素开始的所有元素
print (tinylist * 2)    # 输出两次列表
print (list + tinylist) # 连接列表
print (list[-1::-1])    # 翻转列表
```

### Tuple（元组）
元组（tuple）与列表类似，**不同之处在于元组的元素不能修改**。元组写在小括号 **()** 里，元素之间用逗号隔开。

```python
tuple = ( 'abcd', 786 , 2.23, 'runoob', 70.2  )
tinytuple = (123, 'runoob')

print (tuple)             # 输出完整元组
print (tuple[0])          # 输出元组的第一个元素
print (tuple[1:3])        # 输出从第二个元素开始到第三个元素
print (tuple[2:])         # 输出从第三个元素开始的所有元素
print (tinytuple * 2)     # 输出两次元组
print (tuple + tinytuple) # 连接元组
```

构造包含 0 个或 1 个元素的元组比较特殊，所以有一些额外的语法规则：

```python
tup1 = ()    # 空元组
tup2 = (20,) # 一个元素，需要在元素后添加逗号
```

**注意：**

+ 1、与字符串一样，元组的元素不能修改。
+ 2、元组也可以被索引和切片，方法一样。
+ 3、注意构造包含 0 或 1 个元素的元组的特殊语法规则。
+ 4、元组也可以使用+操作符进行拼接。

### Set（集合）
Python 中的集合（Set）是一种无序、可变的数据类型，用于存储唯一的元素。

集合中的元素不会重复，并且可以进行交集、并集、差集等常见的集合操作。

在 Python 中，集合使用大括号 **{}** 表示，元素之间用逗号 **,** 分隔。

另外，也可以使用 **set()** 函数创建集合。

注意：创建一个空集合必须用 **set()** 而不是 **{ }**，因为 **{ }** 是用来创建一个空字典。

创建格式：

```python
parame = {value01,value02,...}
或者
set(value)
```

```python
sites = {'Google', 'Taobao', 'Runoob', 'Facebook', 'Zhihu', 'Baidu'}

print(sites)   # 输出集合，重复的元素被自动去掉

# 成员测试
if 'Runoob' in sites :
    print('Runoob 在集合中')
else :
    print('Runoob 不在集合中')


# set可以进行集合运算
a = set('abracadabra')
b = set('alacazam')

print(a)

print(a - b)     # a 和 b 的差集

print(a | b)     # a 和 b 的并集

print(a & b)     # a 和 b 的交集

print(a ^ b)     # a 和 b 中不同时存在的元素
```

### dict(字典)
+ 列表是有序的对象集合，字典是无序的对象集合。两者之间的区别在于：字典当中的元素是通过键来存取的，而不是通过偏移存取。
+ 字典是一种映射类型，字典用 **{ }** 标识，它是一个无序的 **键(key) : 值(value)** 的集合。
+ 键(key)必须使用不可变类型。
+ 在同一个字典中，键(key)必须是唯一的。

```python
dict = {}
dict['one'] = "1 - 菜鸟教程"
dict[2]     = "2 - 菜鸟工具"

tinydict = {'name': 'runoob','code':1, 'site': 'www.runoob.com'}


print (dict['one'])       # 输出键为 'one' 的值
print (dict[2])           # 输出键为 2 的值
print (tinydict)          # 输出完整的字典
print (tinydict.keys())   # 输出所有键
print (tinydict.values()) # 输出所有值
```

## python3数据类型转换
Python 数据类型转换可以分为两种：

+ 隐式类型转换 - 自动完成
+ 显式类型转换 - 需要使用类型函数来转换

### 隐式类型转换
较低数据类型（整数）就会转换为较高数据类型（浮点数）

```python
num_int = 123
num_flo = 1.23

num_new = num_int + num_flo

print("num_int 数据类型为:",type(num_int))
print("num_flo 数据类型为:",type(num_flo))

print("num_new 值为:",num_new)
print("num_new 数据类型为:",type(num_new))

'''
输出结果：
num_int 数据类型为: <class 'int'>
num_flo 数据类型为: <class 'float'>
num_new: 值为: 124.23
num_new 数据类型为: <class 'float'>
'''
```



### 显式类型转换
在显式类型转换中，用户将对象的数据类型转换为所需的数据类型。 我们使用 int()、float()、str() 等预定义函数来执行显式类型转换。

```python
# int()
x = int(1)   # x 输出结果为 1
y = int(2.8) # y 输出结果为 2
z = int("3") # z 输出结果为 3
# float()
x = float(1)     # x 输出结果为 1.0
y = float(2.8)   # y 输出结果为 2.8
z = float("3")   # z 输出结果为 3.0
w = float("4.2") # w 输出结果为 4.2
# str()
x = str("s1") # x 输出结果为 's1'
y = str(2)    # y 输出结果为 '2'
z = str(3.0)  # z 输出结果为 '3.0'
```

以下几个内置的函数可以执行数据类型之间的转换。这些函数返回一个新的对象，表示转换的值:

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457513-fa6edd9b-81f4-4099-814b-e4ff73c15c3c.png)



## python3运算符
<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457572-739c8a97-5972-411c-9dae-22c65a84246b.png)

## python3数字
### 数学函数
#### math库
```python
import math
math.abs(-3)

'''
3
'''
```

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457626-26bf22e9-5747-408c-92db-7bb04d8aa4bc.png)

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457697-7430923e-425f-49ec-b4a1-c3de78b3319a.png)

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457749-5c6e5f24-e88c-454c-84fb-fc17c49b8b57.png)

#### random库
```plain
import random
random.choice([1,2,3,4,5]) # 从该序列中随机挑选一个
```

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457817-13f921a4-5b81-49e9-a96b-b048921184d3.png)

## python3字符串
[Python3 字符串 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-string.html)

+ Python 转义字符
+ Python 字符串运算符
    - 字符串的切片遵循**左闭右开**原则
+ Python 字符串格式化
+ 字面量格式化字符串——**f-string**

```python
w = {'name': 'Runoob', 'url': 'www.runoob.com'}
f'{w["name"]}: {w["url"]}'

'''
'Runoob: www.runoob.com'
'''
```

## python3列表
python3列表函数和方法

+ 函数是python内置的
+ 方法是list类下的方法

[Python3 列表 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-list.html)

## python3元组
+ 元组的元素不能修改。
+ 元组使用小括号 **( )**
+ 元组创建很简单，只需要在括号中添加元素，并使用逗号隔开即可。
+ 创建空元组

```python
tup1 = ()
```

+ 元组中只包含一个元素时，需要在元素后面添加逗号 **,** ，否则括号会被当作运算符使用

```python
>>> tup1 = (50)
>>> type(tup1)     # 不加逗号，类型为整型
<class 'int'>

>>> tup1 = (50,)
>>> type(tup1)     # 加上逗号，类型为元组
<class 'tuple'>
```

[Python3 元组 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-tuple.html)

## python3字典
+ 字典是另一种可变容器模型，且可存储任意类型对象。
+ 字典的每个键值 **key=>value** 对用冒号 **:** 分割，每个对之间用逗号(**,**)分割，整个字典包括在花括号 **{}**
+ 键必须是唯一的，但值则不必。
+ 不允许同一个键出现两次。创建时如果同一个键被赋值两次，后一个值会被记住
+ 值可以取任何数据类型，但键必须是不可变的，如字符串，数字。
+ 创建空字典

```python
# 使用大括号 {} 来创建空字典
emptyDict = {}
```

字典的内置函数和方法：[Python3 字典 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-dictionary.html)

## python3集合
+ 集合（set）是一个无序的不重复元素序列。
+ 可以使用大括号 **{ }** 创建集合，元素之间用逗号 **,** 分隔， 或者也可以使用 **set()** 函数创建集合。

```python
parame = {value01,value02,...}
或者
set(value)
'''
实例：
set1 = {1, 2, 3, 4}            # 直接使用大括号创建集合
set2 = set([4, 5, 6, 7])      # 使用 set() 函数从列表创建集合
'''
```

+ **注意：**创建一个空集合必须用 **set()** 而不是 **{ }**，因为 **{ }** 是用来创建一个空字典。

集合的内置函数和方法：[Python3 集合 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-set.html)

## python3条件控制
### if
+ 条件和代码块不需要使用（）包含起来

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

### match...case(python3.10新增功能)
match 后的对象会依次与 case 后的内容进行匹配，如果匹配成功，则执行匹配到的表达式，否则直接跳过，**_** 可以匹配一切。

```python
match subject:
    case <pattern_1>:
        <action_1>
    case <pattern_2>:
        <action_2>
    case <pattern_3>:
        <action_3>
    case _:
        <action_wildcard>
```

## python3循环语句
+ while
+ for语句
+ for...else

```python
for item in iterable:
    # 循环主体
else:
    # 循环结束后执行的代码
```

> 当循环执行完毕（即遍历完 iterable 中的所有元素）后，会执行 else 子句中的代码，如果在循环过程中遇到了 break 语句，则会中断循环，此时不会执行 else 子句。
>

+ range()函数
    - 使用方法：[Python3 range() 函数用法 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-func-range.html)
+ break 和 continue 语句及循环中的 else 子句

> **break** 语句可以跳出 for 和 while 的循环体。如果你从 for 或 while 循环中终止，任何对应的循环 else 块将不执行。
>
> **continue** 语句被用来告诉 Python 跳过当前循环块中的剩余语句，然后继续进行下一轮循环。
>

+ pass 语句

> Python pass是空语句，是为了保持程序结构的完整性。
>
> pass 不做任何事情，一般用做占位语句
>

## end关键字
关键字end可以用于将结果输出到同一行，或者在输出的末尾添加不同的字符，实例如下：

```python
# Fibonacci series: 斐波纳契数列
# 两个元素的总和确定了下一个数
a, b = 0, 1
while b < 1000:
    print(b, end=',')
    a, b = b, a+b
    
 '''
 1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,
 '''

```

## python3推导式
+ 列表推导式（list）
+ 字典推导式（dict）
+ 集合推导式（set）
+ 元组推导式（tuple）

### 列表推导式
```python
# 列表推导式基本格式
[表达式 for 变量 in 列表] 
[out_exp_res for out_exp in input_list]
或者 
[表达式 for 变量 in 列表 if 条件]
[out_exp_res for out_exp in input_list if condition]

# 例子
>>> names = ['Bob','Tom','alice','Jerry','Wendy','Smith']
>>> new_names = [name.upper()for name in names if len(name)>3]
>>> print(new_names)
['ALICE', 'JERRY', 'WENDY', 'SMITH']
```

> + out_exp_res：列表生成元素表达式，可以是有返回值的函数。
> + for out_exp in input_list：迭代 input_list 将 out_exp 传入到 out_exp_res 表达式中。
> + if condition：条件语句，可以过滤列表中不符合条件的值。
>

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457897-ede63bc9-bdf0-433d-ae02-08f291e3618b.png)

### 字典推导式
```python
# 字典推导式基本格式
{ key_expr: value_expr for value in collection }
或
{ key_expr: value_expr for value in collection if condition }

# 例子
listdemo = ['Google','Runoob', 'Taobao']
# 将列表中各字符串值为键，各字符串的长度为值，组成键值对
>>> newdict = {key:len(key) for key in listdemo}
>>> newdict
{'Google': 6, 'Runoob': 6, 'Taobao': 6}

# 提供三个数字，以三个数字为键，三个数字的平方为值来创建字典：
>>> dic = {x: x**2 for x in (2, 4, 6)}
>>> dic
{2: 4, 4: 16, 6: 36}
>>> type(dic)
<class 'dict'>
```

### 集合推导式
```python
# 集合推导式基本格式
{ expression for item in Sequence }
或
{ expression for item in Sequence if conditional }

# 计算数字 1,2,3 的平方数：
>>> setnew = {i**2 for i in (1,2,3)}
>>> setnew
{1, 4, 9}

# 判断不是 abc 的字母并输出：
>>> a = {x for x in 'abracadabra' if x not in 'abc'}
>>> a
{'d', 'r'}
>>> type(a)
<class 'set'>
```

### 元组推导式
元组推导式可以利用 range 区间、元组、列表、字典和集合等数据类型，快速生成一个满足指定需求的元组。

元组推导式基本格式：

```python
# 元组推导基本格式
(expression for item in Sequence )
或
(expression for item in Sequence if conditional )

# 实例
>>> a = (x for x in range(1,10))
>>> a
<generator object <genexpr> at 0x7faf6ee20a50>  # 返回的是生成器对象

>>> tuple(a)       # 使用 tuple() 函数，可以直接将生成器对象转换成元组
(1, 2, 3, 4, 5, 6, 7, 8, 9)
```

## python3迭代器和生成器
### 迭代器
+ 迭代器是一个可以记住遍历的位置的对象。
+ 迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退。
+ 迭代器有两个基本的方法：**iter()** 和 **next()**。
+ 字符串，列表或元组对象都可用于创建迭代器：

```python
>>> list=[1,2,3,4]
>>> it = iter(list)    # 创建迭代器对象
>>> print (next(it))   # 输出迭代器的下一个元素
1
>>> print (next(it))
2
```

+ 迭代器对象可以使用常规for语句进行遍历

```python
 list=[1,2,3,4]
it = iter(list)    # 创建迭代器对象
for x in it:
    print (x, end=" ")
    
'''
1 2 3 4
'''
```

### 生成器
+ 在 Python 中，使用了 **yield** 的函数被称为生成器（generator）。
+ **yield** 是一个关键字，用于定义生成器函数，生成器函数是一种特殊的函数，可以在迭代过程中逐步产生值，而不是一次性返回所有结果。
+ 跟普通函数不同的是，生成器是一个返回迭代器的函数，只能用于迭代操作，更简单点理解生成器就是一个迭代器。
+ 当在生成器函数中使用 **yield** 语句时，函数的执行将会暂停，并将 **yield** 后面的表达式作为当前迭代的值返回。

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1
 
# 创建生成器对象
generator = countdown(5)
 
# 通过迭代生成器获取值
print(next(generator))  # 输出: 5
print(next(generator))  # 输出: 4
print(next(generator))  # 输出: 3
 
# 使用 for 循环迭代生成器
for value in generator:
    print(value)  # 输出: 2 1
```

[Python3 迭代器与生成器 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-iterator-generator.html)

## python3函数
+ 函数的调用
+ 参数传递
+ 参数
    - 必须参数
    - 关键字参数
    - 默认参数
    - 不定长参数
+ lambda匿名函数
+ return语句

[Python3 函数 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-function.html)

## python3输入输出
### 读取键盘输入
```python
str = input("请输入：");
print ("你输入的内容是: ", str)
```

### 读和写文件
open() 将会返回一个 file 对象，基本语法格式如下:

```python
open(filename, mode)
```

+ filename：包含了你要访问的文件名称的字符串值。
+ mode：决定了打开文件的模式：只读，写入，追加等。所有可取值见如下的完全列表。这个参数是非强制的，默认文件访问模式为只读(r)。

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794457954-73517e6f-5503-40eb-88df-2b4237afd65b.png)

例子：

```python
# 打开一个文件
f = open("/tmp/foo.txt", "r")

str = f.readline()
print(str)

# 关闭打开的文件
f.close()

'''
$ cat /tmp/foo.txt 
Python 是一个非常好的语言。
是的，的确非常好!!
'''
```

### 文件对象的方法
#### f.read()
> 为了读取一个文件的内容，调用 f.read(size), 这将读取一定数目的数据, 然后作为字符串或字节对象返回。
>
> size 是一个可选的数字类型的参数。 当 size 被忽略了或者为负, 那么该文件的所有内容都将被读取并且返回。
>

#### f.readline()
> f.readline() 会从文件中读取单独的一行。换行符为 '\n'。f.readline() 如果返回一个空字符串, 说明已经已经读取到最后一行。
>

#### f.readlines()
> f.readlines() 将返回该文件中包含的所有行。
>
> 如果设置可选参数 sizehint, 则读取指定长度的字节, 并且将这些字节按行分割。
>

#### f.write()
> f.write(string) 将 string 写入到文件中, 然后返回写入的字符数。
>

#### f.tell()
#### f.seek()
#### f.close()
> 在文本文件中 (那些打开文件的模式下没有 b 的), 只会相对于文件起始位置进行定位。
>
> 当你处理完一个文件后, 调用 f.close() 来关闭文件并释放系统的资源，如果尝试再调用该文件，则会抛出异常。
>

[Python3 输入和输出 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-inputoutput.html)

## python3File（文件）方法
[Python3 File 方法 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-file-methods.html)

## python3 OS
[Python3 OS 文件/目录方法 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-os-file-methods.html)

## python3错误和异常
[Python3 错误和异常 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-errors-execptions.html)

## python3面向对象
```python
class people:
    # 定义基本属性
    name = ''
    age = 0
    # 定义私有属性,私有属性在类外部无法直接进行访问
    __weight = 0

    # 定义构造方法
    def __init__(self, n, a, w):
        self.name = n
        self.age = a
        self.__weight = w
        
    def speak(self):
        print(f"我叫{self.name}，今年{self.age}岁。")

# 继承父类people
class student(people):
    grade = ''

    def __init__(self, n, a, w, g):
        # 调用父类构造
        people.__init__(self, n, a, w)
        self.grade = g

    # 覆盖父类的方法
    def speak(self):
        print(f"{self.name}说：我今年{self.age}岁,读{self.grade}年级")


# 实例化类
if __name__ == "__main__":
    # p = people('runoob',10,30)
    # p.speak()
    s = student('ken', 10, 60, 3)
    s.speak()
```

[Python3 命名空间和作用域 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-namespace-scope.html)

## python3命名空间/作用域
### python3命名空间查找顺序
<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794458017-dcff7884-f063-427e-a3a6-32684bc78b95.png)

#### 命名空间查找顺序:
假设我们要使用变量 runoob，则 Python 的查找顺序为：**局部的命名空间 -> 全局命名空间 -> 内置命名空间**。

### pytho引入新的作用域
> Python 中只有模块（module），类（class）以及函数（def、lambda）才会引入新的作用域，其它的代码块（如 if/elif/else/、try/except、for/while等）是不会引入新的作用域的，也就是说这些语句内定义的变量，外部也可以访问，
>

### global 和 nonlocal关键字
#### global
```python
num = 1
def fun1():
    global num  # 需要使用 global 关键字声明
    print(num) 
    num = 123
    print(num)
fun1()
print(num)

'''
输出结果：
1
123
123
'''
```

#### nonlocal
如果要修改嵌套作用域（enclosing 作用域，外层非全局作用域）中的变量则需要 nonlocal 关键字了，如下实例：

```python
def outer():
    num = 10
    def inner():
        nonlocal num   # nonlocal关键字声明
        num = 100
        print(num)
    inner()
    print(num)
outer()

'''
100
100
'''
```

#### global特殊情况
```python
a = 10
def test():
    a = a + 1
    print(a)
test()

'''
报错如下：
Traceback (most recent call last):
  File "test.py", line 7, in <module>
    test()
  File "test.py", line 5, in test
    a = a + 1
UnboundLocalError: local variable 'a' referenced before assignment
'''

# 修改后  使用global
a = 10
def test():
    global a
    a = a + 1
    print(a)
test()
# 输出：11

# 修改后 使用函数传递
a = 10
def test(a):
    a = a + 1
    print(a)
test(a)

# 输出：11
```

[Python3 命名空间和作用域 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-namespace-scope.html)

## python内置函数
### enumerate() 函数
使用方法

```python
seq = ['one', 'two', 'three']
for i, element in enumerate(seq):
    print i, element

'''
0 one
1 two
2 three
'''
```

## collections模块
官方文档：[collections --- 容器数据类型 — Python 3.12.0 文档](https://docs.python.org/zh-cn/3/library/collections.html#)

## tqdm库
### 安装
```python
pip install tqdm
```

### 调用库
```python
from tqdm import tqdm
```

### 使用示例
```python
text = ""
for char in tqdm(["a", "b", "c", "d"]):
    sleep(0.25)
    text = text + char

text

'''
100%|██████████| 4/4 [00:01<00:00,  3.87it/s]
'''
```

### 源码
<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733794458093-bb811b04-b89a-449c-a7a3-b06c32290b47.png)

注意：tqdm包裹的必须是一个可以迭代的对象 



## argparse库
[【精选】python之argparse模块常见用法包含实例(超详细)_python argparse-CSDN博客](https://blog.csdn.net/RudeTomatoes/article/details/117003291)

# pip
pip下载速度慢 可以每次使用临时镜像源

```shell
阿里云镜像源:
    http://mirrors.aliyun.com/pypi/simple
使用方法:
    pip install 库名 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
```

```plain
pip 删除第三方库
    pip uninstall 库名
cmd查看默认python版本
    python -V
查看已经安装的python版本且带路径的列表
    py -0p (是零)
```

## pip 生成requirements.txt文件和下载requirements.txt中的文件
```shell
# 生成
pip freeze > requirements.txt

# 下载
pip install -r requirements.txt
```

