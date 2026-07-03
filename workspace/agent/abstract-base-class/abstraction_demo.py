"""抽象基类（ABC + @abstractmethod）演示

运行：workspace/.venv/bin/python abstraction_demo.py
（或任意 python3 解释器）

涵盖的知识点：
1. ABC 抽象类不能直接实例化
2. @abstractmethod 强制子类实现
3. 子类未实现 → 实例化时报错
4. 抽象方法的"实现与否"是实例化时的硬约束
5. 异步抽象方法同样支持
6. 模拟 mini-agent 项目里的 LLM 客户端抽象（统一接口、多实现）
"""

from abc import ABC, abstractmethod


# ============================================================
# 1. 基础抽象类演示
# ============================================================

class Animal(ABC):
    """抽象基类：所有动物"""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def speak(self):
        """每种动物都有自己的叫声"""
        pass


class Dog(Animal):
    def speak(self):
        return f"{self.name}: 汪汪汪"


class Cat(Animal):
    def speak(self):
        return f"{self.name}: 喵喵喵"


# ============================================================
# 2. 漏实现抽象方法的子类（演示报错）
# ============================================================

class SilentAnimal(Animal):
    """故意不实现 speak，演示实例化时会报错"""
    pass


# ============================================================
# 3. 异步抽象方法
# ============================================================

class AsyncWorker(ABC):
    @abstractmethod
    async def run(self):
        pass


class HelloWorker(AsyncWorker):
    async def run(self):
        return "hello"


# ============================================================
# 4. 模拟 mini-agent 里的 LLM 客户端抽象
# ============================================================

class LLMClientBase(ABC):
    """统一接口：所有 LLM 客户端都要实现 generate"""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def _prepare_request(self, prompt: str) -> dict:
        """请求构造逻辑交给子类"""
        pass


class FakeOpenAIClient(LLMClientBase):
    async def generate(self, prompt: str) -> str:
        req = self._prepare_request(prompt)
        return f"[FakeOpenAI] model={req['model']}, reply to: {prompt}"

    def _prepare_request(self, prompt: str) -> dict:
        return {"model": "gpt-x", "messages": [{"role": "user", "content": prompt}]}


class FakeAnthropicClient(LLMClientBase):
    async def generate(self, prompt: str) -> str:
        req = self._prepare_request(prompt)
        return f"[FakeAnthropic] model={req['model']}, reply to: {prompt}"

    def _prepare_request(self, prompt: str) -> dict:
        return {"model": "claude-x", "prompt": prompt}


# ============================================================
# 主流程
# ============================================================

if __name__ == "__main__":
    # 1. 正确：实现抽象方法的子类
    dog = Dog("旺财")
    cat = Cat("小花")
    print(dog.speak())
    print(cat.speak())

    # 2. 抽象基类不能直接实例化（取消注释会报错）
    # animal = Animal("无名")  # ❌ TypeError

    # 3. 漏实现抽象方法的子类 → 实例化时报错
    try:
        silent = SilentAnimal("哑巴")
    except TypeError as e:
        print(f"❌ 预期报错：{e}")

    # 4. 异步抽象方法
    import asyncio
    worker = HelloWorker()
    print(asyncio.run(worker.run()))

    # 5. mini-agent 风格的 LLM 客户端抽象
    import asyncio

    async def main():
        clients = [FakeOpenAIClient(), FakeAnthropicClient()]
        for c in clients:
            print(await c.generate("你好"))

    asyncio.run(main())