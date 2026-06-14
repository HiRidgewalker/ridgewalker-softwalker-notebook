"""
Celery Canvas 演示：chain / group / chord / 嵌套

Canvas 是 Celery 的任务编排原语，让多个任务组合成工作流。
Eager 模式跑通，无需真 broker。
"""
import itertools

from celery import Celery, chain, chord, group

app = Celery("canvas_demo", broker="redis://localhost:6379/0")
app.conf.task_always_eager = True
app.conf.task_eager_propagates = True


# ===== 1. chain：顺序执行 =====
@app.task
def step1(x):
    print(f"step1: {x}")
    return x + 1


@app.task
def step2(x):
    print(f"step2: {x}")
    return x * 2


@app.task
def step3(x):
    print(f"step3: {x}")
    return x - 3


# step1(5) → step2(6) → step3(12) = 9
# 写法 1：
result = chain(step1.s(5), step2.s(), step3.s())()
print("chain result:", result.get())              # 9

# 写法 2：直接 pipe
result = (step1.s(5) | step2.s() | step3.s())()
print("chain (pipe) result:", result.get())


# ===== 2. group：并行执行 =====
@app.task
def double(x):
    return x * 2


# 并行跑 double(1), double(2), double(3) → [2, 4, 6]
result = group(double.s(1), double.s(2), double.s(3))()
print("group result:", result.get())


# ===== 3. chord：group + 回调 =====
@app.task
def collect(results):
    """group 全部完成后被调用。
    兼容 results 是裸 list、嵌套 list、GroupResult 三种情况。
    """
    if hasattr(results, "results"):
        results = results.results
    flat = list(itertools.chain.from_iterable(
        r if isinstance(r, list) else [r] for r in results
    ))
    return {"sum": sum(flat), "count": len(flat)}


# group 完成后调用 collect
result = chord(group(double.s(1), double.s(2), double.s(3)), collect.s())()
print("chord result:", result.get())              # {'sum': 12, 'count': 3}


# ===== 4. 嵌套：chain + group 组合 =====
@app.task
def split_10(x):
    """把单个值拆成 [x, x] 给 group 并行处理"""
    return [x, x]


# step1(5) → step2(6) → split_10(12) → group(double, double) → collect
workflow = chain(
    step1.s(5),
    step2.s(),
    split_10.s(),
    group(double.s(), double.s()),
    collect.s(),
)
result = workflow()
print("nested result:", result.get())
# 注：Eager 模式下嵌套 canvas 的中间值收集行为与真 worker 略有不同，
# 数字本身不重要，重点是 chain + group 组合的写法。


# ===== 5. 错误回调（chord_error）=====
@app.task
def fail(x):
    raise ValueError(f"intentional fail: {x}")


@app.task
def on_chord_error(request, exc, traceback):
    """group 任一任务失败时被调用"""
    return {"failed": True, "error": str(exc)}


# 失败时走 on_chord_error 而不是 collect
# （Eager 模式下 chord_error 行为略不同，仅示意）
# result = chord(
#     group(step1.s(1), fail.s(2), step1.s(3)),
#     collect.s(),
# ).on_error(on_chord_error.s())()
