---
title: "mini-agent 学习笔记"
sidebar_position: 3
---

# mini-agent 学习笔记

> 由旧稿重新整理而来，定位为**读 [MiniMax-AI/Mini-Agent](https://github.com/MiniMax-AI/Mini-Agent) 源码时记录的 OOP 设计模式笔记**。旧稿中的 Python `ABC` + `@abstractmethod` 用法已整理到本文，当前以本文为准。

## 一、项目背景

[Mini-Agent](https://github.com/MiniMax-AI/Mini-Agent) 是一个轻量 Agent 框架，特点是：

- 代码量不大，结构清晰
- 把"执行层"做了良好的抽象，方便扩展多种 LLM 后端
- 是学习 Agent 系统结构 [Agent总览笔记 > 三、系统结构（七层）](agent-overview.md#三系统结构七层) 中"执行层"设计的好素材

读这个项目的关键切入点：**它的客户端抽象层** —— 用 Python `ABC` + `@abstractmethod` 定义 LLM Client 的统一接口，多家厂商（OpenAI、Anthropic 等）的客户端作为子类实现。

---

## 二、Python `ABC` + `@abstractmethod` 标准用法

读 mini-agent 源码时遇到的核心 OOP 模式，就是 Python 的抽象基类约定。

### 1. 核心定义

- **`ABC`**：抽象基类，**不能直接实例化**
- **`@abstractmethod`**：抽象方法装饰器，**子类必须实现**，否则无法创建对象

### 2. 标准使用步骤

```python
from abc import ABC, abstractmethod

# ① 基类继承 ABC，方法加 @abstractmethod
class BaseClass(ABC):
    def __init__(self):
        self.name = "base"

    @abstractmethod
    def do_something(self):
        pass  # 抽象方法可以写逻辑，也可以只写 pass

# ② 子类必须实现所有抽象方法
class ChildClass(BaseClass):
    def do_something(self):
        print("实现抽象方法")

# ③ 正确使用
child = ChildClass()
child.do_something()

# ❌ 错误：抽象基类不能实例化
base = BaseClass()
```

### 3. 关键规则

1. 只要类继承了 `ABC`，就是抽象类
2. 只要方法带 `@abstractmethod`，子类就必须实现
3. 子类少实现一个，**实例化时直接报错**：`Can't instantiate abstract class Child with abstract method do_something`
4. 抽象类不能直接创建对象
5. 抽象方法可以写代码逻辑，子类依然必须重写

### 4. 异步抽象方法

`async` 方法**同样支持** `@abstractmethod`：

```python
class Base(ABC):
    @abstractmethod
    async def run(self):
        pass

class Child(Base):
    async def run(self):  # 必须实现
        pass
```

---

## 三、在 mini-agent 项目里的对应形态

mini-agent 的 LLM 客户端层就是这种模式的典型应用：

```python
class LLMClientBase(ABC):
    @abstractmethod
    async def generate(...):
        """统一的 generate 接口"""
        pass

    @abstractmethod
    def _prepare_request(...):
        """请求构造逻辑交给子类"""
        pass

# 子类必须实现上面 2 个方法
class OpenAIClient(LLMClientBase):
    async def generate(...):
        ...

    def _prepare_request(...):
        ...
```

这种设计的工程价值：

| 优势 | 说明 |
| --- | --- |
| **接口统一** | Agent 主体只调 `LLMClientBase.generate()`，不关心具体厂商 |
| **扩展简单** | 新增 LLM 提供方只需要写一个子类 |
| **契约明确** | 漏实现抽象方法 → 启动时就报错，不会等到运行时才暴露 |
| **配合异步** | `async` 抽象方法支持现代 LLM SDK 的高并发调用 |

对应到 [Agent总览笔记 > 三、系统结构（七层）](agent-overview.md#三系统结构七层) 中的"执行层"概念 —— **执行层和具体厂商解耦的关键，就是这种抽象基类约束**。

---

## 四、读完源码后的总结

1. `ABC` = 抽象类，不能实例化
2. `@abstractmethod` = 强制子类实现
3. 不实现 → 子类无法创建对象，启动即报错
4. 异步方法也可以用 `@abstractmethod`

> 配套 demo：[example/agent/abstract-base-class/abstraction_demo.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/agent/abstract-base-class/abstraction_demo.py)

---

## 五、相关笔记

- Agent 能力模型与系统结构：[Agent总览笔记](agent-overview.md)
- 代表开源项目对比：[Agent开源项目笔记](agent-open-source-projects.md)
- Skills 概念与构建：[Skills笔记](../skills/skills.md)
- MCP 协议：[MCP笔记](../mcp/mcp.md)
