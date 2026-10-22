# full_app

完整可 `runserver` 的 Django + DRF 演示项目，对应 `Hub/Django笔记.md` 第 3 章。

## 跑起来

```bash
cd example/python/django/full_app

# 1. 迁移
uv run python manage.py migrate

# 2. 跑测试（验证项目本身能工作）
uv run python manage.py test articles

# 3. 启服务
uv run python manage.py runserver
```

启动后访问：

- `http://127.0.0.1:8000/api/articles/` — 列表（支持 `?search=` / `?ordering=` / `?is_published=true` / `?category_id=1` / `?view_count__gte=10`）
- `http://127.0.0.1:8000/api/articles/{id}/` — 详情
- `http://127.0.0.1:8000/api/articles/{id}/increment/` — 自定义动作（POST 累加 view_count）
- `http://127.0.0.1:8000/api/articles/published/` — 已发布列表（自定义 list 动作）
- `http://127.0.0.1:8000/api/docs/` — Swagger UI
- `http://127.0.0.1:8000/api/redoc/` — ReDoc
- `http://127.0.0.1:8000/api/schema/` — OpenAPI schema

## 手工测（curl）

```bash
# 1. 创建分类
curl -X POST http://127.0.0.1:8000/api/articles/ \
     -H "Content-Type: application/json" \
     -d '{"title":"hello","body":"world","category_id":1}'

# 2. 列出（带搜索 + 排序）
curl "http://127.0.0.1:8000/api/articles/?search=hello&ordering=-view_count"

# 3. 累加 view_count
curl -X POST http://127.0.0.1:8000/api/articles/1/increment/
```

## 项目结构

```
full_app/
├── manage.py
├── full_app/                # project package
│   ├── settings.py          # DRF / cors-headers / drf-spectacular 配置
│   ├── urls.py              # 根路由（api/ + schema + docs）
│   ├── wsgi.py
│   └── asgi.py
└── articles/                # app
    ├── models.py            # Article + Category
    ├── serializers.py       # ArticleSerializer + CategorySerializer
    ├── views.py             # ArticleViewSet + FilterSet + 自定义 action
    ├── urls.py              # DefaultRouter
    ├── tests.py             # APIClient 测试
    └── migrations/
```

## 涵盖的知识点

- 模型：ForeignKey + on_delete=PROTECT + Meta 索引
- 序列化：ModelSerializer + 嵌套 + SerializerMethodField + 字段级/对象级校验
- 视图：ModelViewSet + @action 自定义动作（detail / detail=False）
- 路由：DefaultRouter 自动生成
- 过滤：django-filter（字段级、范围查询）+ SearchFilter + OrderingFilter
- 性能：select_related 避免 N+1
- API 文档：drf-spectacular 自动生成 OpenAPI + Swagger
- CORS：开发期放行
