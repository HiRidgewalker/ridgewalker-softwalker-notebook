"""
Celery 基础演示：任务定义 / 调用 / 拿结果 / 状态机 / 链路追踪

Eager 模式：不需要真 broker，import 即可跑。
"""
from datetime import datetime, timedelta

from celery import Celery

# ===== 1. 创建 Celery Application =====
app = Celery(
    "demo",
    broker="redis://localhost:6379/0",        # 任意 broker URL，eager 模式下不会真连
    backend="redis://localhost:6379/1",
)

# Eager 模式：任务同步执行、result.get() 立刻可拿
# 生产环境必须删掉 / 设为 False
app.conf.task_always_eager = True
app.conf.task_eager_propagates = True         # eager 模式下异常往上抛


# ===== 2. 任务定义 =====
@app.task(name="demo.add")                    # 显式命名（默认是模块路径）
def add(x, y):
    return x + y


@app.task(bind=True, name="demo.add_with_retry")
def add_with_retry(self, x, y):
    """bind=True 注入 self，可访问 task_id / 主动 retry"""
    return x + y


# ===== 3. 调用 =====
# delay = apply_async 的简写
result = add.delay(1, 2)                       # 简单调用
print("result.id:", result.id)
print("result.get():", result.get())           # 阻塞拿结果
print("result.status:", result.status)         # SUCCESS
print("result.successful():", result.successful())
print()

# apply_async（完整控制）
result = add.apply_async((10, 20))
print(result.get())

# 定时执行
result = add.apply_async((1, 2), countdown=10)              # 10 秒后执行
# result = add.apply_async((1, 2), eta=datetime.now() + timedelta(minutes=5))  # 5 分钟后
# result = add.apply_async((1, 2), expires=datetime.now() + timedelta(hours=1))  # 过期丢弃

# 指定队列 / 优先级（RabbitMQ 有效）
# result = add.apply_async((1, 2), queue="priority", priority=9)


# ===== 4. 任务状态机 =====
# PENDING → STARTED → SUCCESS
#           → FAILURE
#           → RETRY → ... → RETRY → SUCCESS / FAILURE
#           → REVOKED（被撤销）
# PENDING 状态：已发到 broker 但 worker 还没拿到


# ===== 5. 任务链路追踪（canvas / 嵌套调用时关键）=====
@app.task(bind=True)
def get_ids(self):
    """self.request 里有完整的链路 ID。"""
    print("task_id:", self.request.id)
    print("parent_id:", self.request.parent_id)
    print("root_id:", self.request.root_id)
    print("group_index:", self.request.group_index)
    return self.request.id


# 模拟嵌套调用
outer = get_ids.delay()
print("outer.id:", outer.id)
