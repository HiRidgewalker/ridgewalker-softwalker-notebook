"""Pydantic v2 演示代码集合。

每个 demo 用 `settings.configure()` 内联配置 + `django.setup()` 等价
手法（或纯 Pydantic 不用 Django）启动，可独立运行：

    uv run python workspace/python/pydantic/pydantic_basics.py
    uv run python workspace/python/pydantic/pydantic_fastapi_demo.py   # 启 FastAPI 后
    uv run python workspace/python/pydantic/pydantic_settings_demo.py
"""
