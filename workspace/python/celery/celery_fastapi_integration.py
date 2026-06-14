"""
Celery × FastAPI 集成演示

生产环境部署方式：
  1. 单独起 worker 进程：
     uv run celery -A workspace.python.celery.celery_fastapi_integration worker -l info
  2. FastAPI 进程不跑任务，只通过 .delay() 发任务到 broker
  3. 客户端通过 GET /tasks/{task_id} 查状态
  4. 集成重试 / 监控 / 告警（参考 celery_robustness.py 的信号）

本 demo 用 Eager 模式跑通，无需真 broker；生产请注释掉 task_always_eager。
"""
import time

from celery import Celery
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ===== 1. Celery Application =====
celery_app = Celery(
    "fastapi_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# 生产鲁棒性配置
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_soft_time_limit=300,
    task_time_limit=600,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
)

# Eager 模式（生产请删除）
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = False


# ===== 2. 任务定义 =====
@celery_app.task(bind=True, name="fastapi_tasks.process_data")
def process_data(self, payload: dict) -> dict:
    """模拟耗时任务，Eager 模式同步执行。"""
    print(f"task {self.request.id} processing {payload}")
    time.sleep(0.1)                              # Eager 模式下 sleep 也走
    return {
        "task_id": self.request.id,
        "received": payload,
        "status": "done",
    }


# ===== 3. FastAPI 集成 =====
app = FastAPI(title="Celery × FastAPI Demo")


class TaskIn(BaseModel):
    data: dict


class TaskOut(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


@app.post("/tasks/", response_model=TaskOut, status_code=202)
def create_task(payload: TaskIn):
    """提交任务，立刻返回 task_id，不阻塞。"""
    async_result = process_data.delay(payload.data)
    return TaskOut(task_id=async_result.id, status="PENDING")


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: str):
    """查任务状态。客户端轮询这个端点拿结果。"""
    async_result = process_data.AsyncResult(task_id)

    if async_result.state == "PENDING":
        return TaskOut(task_id=task_id, status="PENDING")
    if async_result.state == "SUCCESS":
        return TaskOut(task_id=task_id, status="SUCCESS", result=async_result.result)
    if async_result.state == "FAILURE":
        # 不要把 exception 直接返给客户端（可能含敏感信息）
        raise HTTPException(status_code=500, detail="task failed")
    return TaskOut(task_id=task_id, status=async_result.state)


# ===== 4. 用 lru_cache 单例（生产推荐）=====
from functools import lru_cache


@lru_cache
def get_celery():
    return celery_app


# ===== 5. 跑 demo =====
if __name__ == "__main__":
    print("=== 同步调用（Eager 模式）===")
    result = process_data.delay({"x": 1, "y": 2})
    print(f"task_id: {result.id}")
    print(f"status: {result.status}")
    print(f"result: {result.get()}")
    print()

    print("=== Eager 模式下 .get() 立即可拿，AsyncResult(state=...) 需连 backend ===")
    # 生产环境下用：
    # r = process_data.AsyncResult(task_id)
    # print(r.state, r.ready(), r.successful())
