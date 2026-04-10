# `ABC` + `@abstractmethod` 完整使用方法（极简、准确）

## 1. 核心定义

- **`ABC`**：抽象基类，**不能直接实例化**
- **`@abstractmethod`**：抽象方法装饰器，**子类必须实现**，否则无法创建对象

---

## 2. 标准使用步骤

### ① 导入依赖

python

运行

```
from abc import ABC, abstractmethod
```

### ② 基类继承 `ABC`，方法加 `@abstractmethod`

python

运行

```
class BaseClass(ABC):  # 继承 ABC
    def __init__(self):
        self.name = "base"

    @abstractmethod  # 装饰抽象方法
    def do_something(self):
        # 抽象方法可以写逻辑，也可以只写 pass
        pass
```

### ③ 子类必须实现所有抽象方法

**必须实现**：基类里**所有带 `@abstractmethod` 的方法**

python

运行

```
class ChildClass(BaseClass):
    # 必须实现 do_something
    def do_something(self):
        print("实现抽象方法")
```

### ④ 正确使用

python

运行

```
# ✅ 正确：子类实现了所有抽象方法
child = ChildClass()
child.do_something()

# ❌ 错误：抽象基类不能实例化
base = BaseClass()
```

---

## 3. 关键规则（必记）

1. **只要类继承了 `ABC`，就是抽象类**
2. **只要方法带 `@abstractmethod`，子类就必须实现**
3. 子类**少实现一个**，**实例化时报错**
4. 抽象类**不能直接创建对象**
5. 抽象方法可以写代码逻辑，子类依然必须重写

---

## 4. 常见错误演示

python

运行

```
class Child(BaseClass):
    # 没有实现 do_something
    pass

# ❌ 报错：Can't instantiate abstract class Child with abstract method do_something
child = Child()
```

---

## 5. 异步抽象方法（你代码里的场景）

`async` 方法**同样支持** `@abstractmethod`：

python

运行

```
class Base(ABC):
    @abstractmethod
    async def run(self):
        pass

class Child(Base):
    async def run(self):  # 必须实现
        pass
```

---

## 6. 你现在的类对应的正确用法

python

运行

```
class LLMClientBase(ABC):
    @abstractmethod
    async def generate(...):
        pass

    @abstractmethod
    def _prepare_request(...):
        pass

# 子类必须实现上面 2 个方法
class OpenAIClient(LLMClientBase):
    async def generate(...):
        ...

    def _prepare_request(...):
        ...
```

---

### 总结

1. **`ABC` = 抽象类，不能实例化**
2. **`@abstractmethod` = 强制子类实现**
3. **不实现 → 子类无法创建对象，直接报错**
4. **异步方法也可以用**