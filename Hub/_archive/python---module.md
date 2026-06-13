# python模块
## python sys模块
sys.argv: 提供命令行与程序交互性



sys.platform：本机系统



#### sys.executable：该属性是一个字符串，在正常情况下，其值是当前运行的 Python 解释器对应的可执行程序所在的绝对路径。python解释器绝对路径
#### sys.modules： 该属性是一个字典，包含的是各种已加载的模块的模块名到模块具体位置的映射。
#### sys.builtin_module_names：该属性是一个字符串元组，其中的元素均为当前所使用的的 Python 解释器内置的模块名称。
#### sys.path： 该属性是一个由字符串组成的列表，其中各个元素表示的是 Python 搜索模块的路径；在程序启动期间被初始化。
#### sys.stdin
#### sys.stdout
这几个属性中保存的就是最初定向的“标准输入”、“标准输出”和“标准错误”流。在适当的时侯，我们可以借助这三个属性将`sys.stdin`、`sys.stdout`和`sys.err`恢复为初始值。

```plain
sys.__stdin__`，`sys.__stdout__`，`sys.__stderr__
```





## module 模块
sys.path包含了一个python解释器自动查找所需模块的路径的列表

注意以下两个文件结构

```plain
python——decorators
|——python-sys
|	|——demo1.py
    |——demo
        |——demo3.py
|——demo1.py
```

解释，python-decorators是项目文件夹，python-sys是项目文件夹下的一个package

在demo1.py和demo2.py中执行sys.path会得到两个有区别的结果，如下：

```plain
demo1.py
____
['D:\\desktop\\python_decorators\\python_sys', 'D:\\desktop\\python_decorators', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_display', 'D:\\server\\anaconda\\envs\\tool_env\\python38.zip', 'D:\\server\\anaconda\\envs\\tool_env\\DLLs', 'D:\\server\\anaconda\\envs\\tool_env\\lib', 'D:\\server\\anaconda\\envs\\tool_env', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32\\lib', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\Pythonwin', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_matplotlib_backend']
____

demo2.py
____
['D:\\desktop\\python_decorators', 'D:\\desktop\\python_decorators', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_display', 'D:\\server\\anaconda\\envs\\tool_env\\python38.zip', 'D:\\server\\anaconda\\envs\\tool_env\\DLLs', 'D:\\server\\anaconda\\envs\\tool_env\\lib', 'D:\\server\\anaconda\\envs\\tool_env', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32\\lib', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\Pythonwin', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_matplotlib_backend']
___


demo3
____
['D:\\desktop\\python_decorators\\python_sys\\demo', 'D:\\desktop\\python_decorators', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_display', 'D:\\server\\anaconda\\envs\\tool_env\\python38.zip', 'D:\\server\\anaconda\\envs\\tool_env\\DLLs', 'D:\\server\\anaconda\\envs\\tool_env\\lib', 'D:\\server\\anaconda\\envs\\tool_env', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\win32\\lib', 'D:\\server\\anaconda\\envs\\tool_env\\lib\\site-packages\\Pythonwin', 'D:\\downloadapp\\PyCharm 2023.2.5\\plugins\\python\\helpers\\pycharm_matplotlib_backend']
____

```

根据上述可以看出同一个项目不同文件层级位置python文件的解释器自动查找所需模块的路径列表只有第一个路径不一样，第一个路径是该python文件直接父目录的绝对路径





import

import 导入的模块会储存到当前符号列表中，使用from...则不会导入模块到到当前符号列表中，只导入import后的变量当前文件列表中



from...import...

这个声明不会把整个模块导入到当前的命名空间中,只会导入import后面指定的部分到当前命名空间，注意，虽然把外部变量、对象导入到了当前命名空间，但是当运行的时候还是会去定义的文件中执行，这里只是一个引用



from ... import *

把一个模块的所有内容全都导入到当前的命名空间也是可行的



.py文件`__name__`属性

如果一个.py文件自生运行，那么它的`__name__`为`__main__`,如果是外部引入，那么这个模块的`__name__`属性就是该.py文件的文件名



.py文件dir()函数

内置的函数 dir() 可以找到模块内定义的所有名称。相当于当前文件独立于其他文件的一个符号表，也可以叫命名空间

如果没有给定参数，那么 dir() 函数会罗列出当前.py文件定义的所有名称

```plain
import python_module

# from python_module import a1
a = 1
b = 2
c = 3

# 不带参数，查看当前文件定义变量
print(dir())


# 带参数，查看指定module命名空间变量
print(dir(python_module))
```







包 package

模块名称A.B,表示包A中的子模块B

就好像使用模块的时候，你不用担心不同模块之间的全局变量相互影响一样，采用点模块名称这种形式也不用担心不同库之间的模块重名的情况。







目录只有包含一个叫做 `__init__.py` 的文件才会被认作是一个包

最简单的情况，放一个空的 :file:**init**.py就可以了。当然这个文件中也可以包含一些初始化代码或者为（将在后面介绍的） __all__变量赋值。



from...import...导包和import导包的差异

注意当使用 **from package import item** 这种形式的时候，对应的 item 既可以是包里面的子模块（子包），或者包里面定义的其他名称，比如函数，类或者变量。

import 语法会首先把 item 当作一个包定义的名称，如果没找到，再试图按照一个模块去导入。如果还没找到，抛出一个 **:exc:****ImportError** 异常。





1. `__init__.py`** 文件的执行**：
    - 在包中，`__init__.py` 文件会在包被导入时自动执行。
    - 你可以在这个文件中定义初始化代码，比如初始化包中的一些变量或导入子模块。





### sys.path是否会因执行文件的不同而改变，gpt解答：结论不会改变，始终是入口文件的sys.path
> 在 Python 项目中，Python 解释器搜索包和模块的路径通常是由 `sys.path` 的值决定的。`sys.path` 是一个包含目录路径的列表，解释器会按照这个列表中的路径顺序依次搜索模块和包。
>
> ### `sys.path` 的构成
> + **入口文件的目录**：Python 解释器首先会搜索入口文件所在的目录。
> + **环境变量 PYTHONPATH**：如果设置了这个环境变量，它的值会被添加到 `sys.path`。
> + **标准库路径**：Python 安装目录中的标准库路径。
> + `site-packages`** 目录**：这是安装第三方库的默认位置。
>
> 无论你在项目中的哪个文件中导入模块，Python 解释器的搜索路径（即 `sys.path`）都是一样的，只是根据入口文件的位置可能会有所不同。
>
> ### Flask 项目包结构举例
> 假设我们有一个 Flask 项目，其目录结构如下：
>
> 在这个结构中，`run.py` 是项目的入口文件，通常用于启动 Flask 应用。
>
> #### `sys.path` 的情况
> 1. **运行 **`run.py`** 时**：
>     - 当你执行 `python run.py` 时，`sys.path` 会包含 `run.py` 所在的目录 `/my_flask_project`。
>     - 这样，`app` 和 `config` 目录都可以直接被导入，因为它们位于 `sys.path` 中的某个路径下。
> 2. **在 **`app/routes.py`** 文件中**：
>     - 如果你在 `app/routes.py` 中尝试导入 `config/config.py`，可以使用 `from config import config`，此时解释器仍然使用 `sys.path` 中的路径进行搜索，不会因为你在 `routes.py` 中就改变路径。
>
> ### 结论
> Python 解释器在搜索模块和包时使用的路径是由 `sys.path` 决定的，`sys.path` 的内容取决于入口文件的位置以及其他因素（如环境变量）。即使在项目中不同的 `.py` 文件中，搜索路径也是一致的。
>

```plain
arduino复制代码/my_flask_project
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│
├── config/
│   ├── __init__.py
│   ├── config.py
│
├── run.py
└── venv/   # 虚拟环境目录
```





python引入模块采用绝对引用，不要采用相对应用，可读性差，同时不要让包名和模块名重名，会导致导入错误

<!-- 这是一张图片，ocr 内容为： -->
![](images/image-20240826230548376.png) 

<!-- 这是一张图片，ocr 内容为： -->
![](images/image-20240826230628588.png) 

<!-- 这是一张图片，ocr 内容为： -->
![](images/image-20240826230639735.png)

会发生以上的错误，我个人理解的为什么会出现这种错误，因为sys.path的第一个路径就是`'D:\\desktop\\test_python_import\\module1'`当前模块，而当前模块恰好有一个module.py的，解释器就认为这个符合，引入后没有找到子目录下的module1模块，所以产生了错误，综上原因，处理python引用最好的办法：`功能层面相同，业务不同的类放在一块，比如java controller，service分别放到不同包中，这样就不会出现同包引用产生不可预料的错误，同时避免包名和模块名相同，避免产生无法预料的错误`



> 上述情况gpt回答如下：
>
> 
>
> 在这种情况下，确实可能会导致错误。具体来说，这涉及到 Python 的导入机制和 `sys.path` 的配置。
>
> ### 场景描述
> 假设你的项目结构如下：
>
> 在 `module1/module1/module2.py` 中，你有如下导入语句：
>
> ### 导入机制分析
> 1. `sys.path`** 配置**:
>     - 当你执行 `module1/module1/module2.py` 时，`sys.path` 的第一个路径通常是当前执行脚本的目录，也就是 `/my_project/module1/module1`。
>     - 然后，它会继续向上搜索，依次包含 `/my_project/module1` 和 `/my_project`。
> 2. **导入冲突**:
>     - 在这个例子中，`from module1.module1 import func` 的目标是从 `/my_project/module1/module1/module1.py` 文件中导入 `func`。
>     - 然而，由于 `sys.path` 中第一个路径 `/my_project/module1/module1` 包含有一个同名的 `module1` 目录（即 `/my_project/module1/module1/module1`），Python 解释器可能会错误地在此处找到包 `module1`。
>     - 这样，解释器会尝试从 `/my_project/module1/module1/module1` 导入 `func`，但这个目录中并没有合适的内容，可能导致导入失败或导入错误的对象。
>
> ### 如何解决
> 为了避免这种问题，通常有以下几种方法：
>
> 1. **<font style="background-color:#f3bb2f;">避免同名冲突</font>**<font style="background-color:#f3bb2f;">: 尽量避免在同一目录下使用相同名称的模块或包，以防止意外的导入冲突。</font>
> 2. **使用绝对导入**:
>     - <font style="background-color:#f3bb2f;">确保使用绝对导入，避免相对路径导入的混淆。确保项目的结构和命名清晰，避免包名和模块名重复。</font>
> 3. **调整 **`sys.path`:
>
> 这样，`sys.path` 的第一个路径将是 `/my_project`，确保导入行为是预期的。
>
>     - <font style="background-color:#f3bb2f;">通过修改 </font>`sys.path`<font style="background-color:#f3bb2f;"> 来指定明确的搜索路径。例如，可以在 </font>`module2.py`<font style="background-color:#f3bb2f;"> 中添加如下代码：</font>
>
> ### 总结
> 在 Python 中，如果模块的导入路径存在同名的包或模块，确实有可能导致导入冲突。为了避免这种情况，应该谨慎设计包和模块的名称，并确保导入路径的配置符合预期。
>

```plain
bash复制代码/my_project
│
├── module1/
│   ├── __init__.py
│   ├── module1/
│   │   ├── __init__.py
│   │   ├── module1.py  # 定义了 func 函数
│   │   └── module2.py  # 包含导入语句
│   └── other_module.py  # 定义了同名的 func 函数
```

```plain
python复制代码# module1/module1/module2.py

from module1.module1 import func
```

```plain
python复制代码import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
```



python作用域

[Python3 命名空间和作用域 | 菜鸟教程 (runoob.com)](https://www.runoob.com/python3/python3-namespace-scope.html)



在python中，只有函数（def, lamba）、模块、包具有局部作用域，其他都没有局部作用域

