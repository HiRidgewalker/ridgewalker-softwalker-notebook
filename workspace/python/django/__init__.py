"""Django + DRF 演示代码集合。

每个 demo 用 `settings.configure()` 内联配置 + `django.setup()` 启动 Django，
无需独立 Django 项目，可独立运行：

    uv run python workspace/python/django/models_demo.py
    uv run python workspace/python/django/queryset_demo.py
    uv run python workspace/python/django/drf_serializer_demo.py
    uv run python workspace/python/django/drf_viewset_demo.py

完整可 runserver 的项目见 full_app/ 子目录。
"""
