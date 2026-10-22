"""Celery 演示代码集合。

所有 demo 默认用 Eager 模式（task_always_eager=True），
不需要真启动 Redis / RabbitMQ broker，纯 import 就能跑：

    uv run python workspace/python/celery/celery_basics.py
    uv run python workspace/python/celery/celery_canvas.py
    uv run python workspace/python/celery/celery_robustness.py
    uv run python workspace/python/celery/celery_fastapi_integration.py

Eager 模式下任务同步执行、result.get() 立刻可拿。
生产环境必须关闭 Eager（默认就是关的），worker 单独起：

    celery -A workspace.python.celery.celery_fastapi_integration worker -l info
"""
