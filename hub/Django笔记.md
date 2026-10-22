# Django 笔记

> 原 旧稿 + 旧稿 的合并重新整理版本，精炼为 4 章节：速查总览 / 常用模式速查表 / 实战代码片段（指向 example demo）/ 常见坑 + 官方文档链接。
> 旧稿目录已清理，当前以本文为准。
> 演示代码统一放在 `example/python/django/`，本笔记通过 git 远程链接引用。完整可 runserver 的小型项目在 `example/python/django/full_app/`。

## 1. 速查总览

### 1.1 Django + DRF 是什么

- **Django**：Python 最流行的全栈 Web 框架，自带 ORM、模板、Admin、迁移、测试等一整套「开箱即用」能力
- **DRF（Django Rest Framework）**：在 Django 上构建 REST API 的官方推荐扩展，提供 Serializer / ViewSet / Router / 权限 / 认证 / 过滤 / 分页

> 2026 年新项目一般 = Django + DRF（前后端分离），少用传统模板渲染；纯 API 项目甚至可以只装 `django.contrib.contenttypes` / `auth` / `sessions` 几个必要 app。

### 1.2 安装

```bash
# Django + DRF 核心
uv add django djangorestframework

# 常用扩展
uv add django-filter               # 字段级过滤
uv add drf-spectacular             # OpenAPI 文档
uv add django-cors-headers         # CORS
uv add "djangorestframework-simplejwt"  # JWT 鉴权（可选）
uv add django-environ              # 环境变量管理（可选）

# 启动新项目
django-admin startproject mysite .
python manage.py startapp myapp
```

### 1.3 一个最小 Django + DRF 项目

完整可运行版本在 `example/python/django/full_app/`，涵盖模型 + 序列化器 + ViewSet + Router + 过滤 + Swagger UI + 单元测试。

跑起来：

```bash
cd example/python/django/full_app
uv run python manage.py migrate
uv run python manage.py test articles     # 跑测试
uv run python manage.py runserver         # 启服务
# 访问 http://127.0.0.1:8000/api/articles/
# Swagger: http://127.0.0.1:8000/api/docs/
```

---

## 2. 常用模式速查表

```text
# ===== 项目骨架 =====
django-admin startproject mysite .        # 初始化项目（注意末尾的 .）
python manage.py startapp myapp           # 新建 app
python manage.py makemigrations           # 生成迁移文件
python manage.py migrate                  # 应用迁移
python manage.py runserver                # 启服务（默认 8000）
python manage.py createsuperuser          # 不用 Admin 就用不上
python manage.py shell                    # 带 Django 环境的 REPL
python manage.py dumpdata > data.json     # 导出数据
python manage.py loaddata data.json       # 导入数据
python manage.py test                     # 跑测试
python manage.py showmigrations          # 查看迁移状态
python manage.py sqlmigrate app 0001      # 看迁移对应的 SQL

# ===== 模型（models.py） =====
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]                # 默认排序
        indexes = [...]                    # 索引
        constraints = [...]                # UniqueConstraint / CheckConstraint

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS = [("draft", "草稿"), ("published", "已发布")]
    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    view_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

# ===== QuerySet 查询 =====
Article.objects.all()
Article.objects.filter(status="published")
Article.objects.exclude(view_count=0)
Article.objects.get(pk=1)
Article.objects.count() / .exists() / .first() / .last()
Article.objects.order_by("-created_at")
Article.objects.values("id", "title")                    # → dict 列表
Article.objects.values_list("title", flat=True)          # → str 列表

# 字段查找
Article.objects.filter(view_count__gt=100)
Article.objects.filter(view_count__in=[10, 20, 30])
Article.objects.filter(title__icontains="django")
Article.objects.filter(author__name="Alice")             # 跨关系
Article.objects.filter(tags__name="python")              # M2M

# 切片
Article.objects.all()[:10]                               # LIMIT 10
Article.objects.all()[10:20]                             # 11~20（不能大偏移，分页用 Paginator）

# F / Q
from django.db.models import F, Q
Article.objects.filter(view_count__gt=F("comment_count") * 2)
Article.objects.update(view_count=F("view_count") + 1)   # 原子自增
Article.objects.filter(Q(is_published=True) | Q(view_count__gt=100))

# 聚合 / 注解
from django.db.models import Count, Sum, Avg
Article.objects.aggregate(total=Count("id"), avg_views=Avg("view_count"))
Author.objects.annotate(article_count=Count("articles")).order_by("-article_count")

# 性能：N+1 修复
Author.objects.select_related("profile")                 # 外键：SQL JOIN
Author.objects.prefetch_related("articles", "articles__tags")  # M2M：二次查询一次性拉

# 批量
Article.objects.bulk_create([Article(...), Article(...)])
Article.objects.bulk_update(articles, ["view_count"])
Article.objects.filter(is_published=False).delete()      # 批量删除

# 常用模式
obj, created = Article.objects.get_or_create(slug="x", defaults={...})
obj, created = Article.objects.update_or_create(slug="x", defaults={...})

# ===== 视图（FBV vs CBV） =====
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

@require_GET
def hello(request):                       # 函数视图
    return HttpResponse("hi")

class ArticleListView(ListView):          # 类视图
    model = Article
    template_name = "article/list.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):               # 自定义过滤
        return super().get_queryset().filter(is_published=True)

# ===== URL 路由（urls.py） =====
from django.urls import path, include, re_path
from django.urls import reverse             # 反向解析：reverse("article_detail", args=[1])

urlpatterns = [
    path("articles/", article_list),
    path("articles/<int:pk>/", article_detail),
    path("articles/<slug:slug>/", article_by_slug),
    re_path(r"^articles/(?P<year>[0-9]{4})/$", article_by_year),
    path("api/v1/", include("api.urls")),
    path("blog/", include("blog.urls", namespace="blog")),
]

# path converters：str / int / slug / uuid / path
# 自定义 converter：见文档

# ===== Settings 关键项 =====
DEBUG = True / False
ALLOWED_HOSTS = ["*"]                     # 生产收窄
DATABASES = {"default": {"ENGINE": "...", "NAME": "..."}}
INSTALLED_APPS = [...]                    # 注册的 app
MIDDLEWARE = [...]                        # 中间件列表
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # 默认主键类型

# ===== DRF：Serializer =====
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)               # 嵌套
    author_id = serializers.IntegerField(write_only=True)  # 写时用 id
    title_length = serializers.SerializerMethodField()      # 自定义字段

    class Meta:
        model = Article
        fields = ["id", "title", "body", "author", "author_id", "title_length"]
        read_only_fields = ["view_count"]
        extra_kwargs = {"body": {"write_only": True}}

    def get_title_length(self, obj):                        # 对应 title_length
        return len(obj.title)

    def validate_title(self, value):                        # 字段级校验
        if "spam" in value.lower():
            raise serializers.ValidationError("标题不能含 spam")
        return value

    def validate(self, attrs):                               # 对象级校验
        if attrs.get("is_published") and not attrs.get("body"):
            raise serializers.ValidationError("发布时必须有 body")
        return attrs

# ===== DRF：View 层级 =====
# APIView             - 基础
# GenericAPIView      - 加 queryset / serializer_class
# Mixin               - ListModelMixin / RetrieveModelMixin / CreateModelMixin / UpdateModelMixin / DestroyModelMixin
# GenericViewSet      - GenericAPIView + 所有 Mixin
# ModelViewSet        - GenericViewSet + 所有 Mixin（最常用）
# ReadOnlyModelViewSet - 只读版

from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @action(detail=True, methods=["post"])
    def increment(self, request, pk=None):                  # POST /articles/{id}/increment/
        article = self.get_object()
        article.view_count += 1
        article.save()
        return Response({"view_count": article.view_count})

    @action(detail=False, methods=["get"])
    def published(self, request):                           # GET /articles/published/
        qs = self.get_queryset().filter(is_published=True)
        return Response(self.get_serializer(qs, many=True).data)

# ===== DRF：Router =====
from rest_framework.routers import DefaultRouter, SimpleRouter
router = DefaultRouter()
router.register(r"articles", ArticleViewSet, basename="article")
urlpatterns = [path("api/", include(router.urls))]

# ===== DRF：权限 / 认证 =====
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
# 鉴权用：djangorestframework-simplejwt 提供的 JWTAuthentication

# 全局（在 settings.REST_FRAMEWORK 里）：
# "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"]
# "DEFAULT_AUTHENTICATION_CLASSES": [...]

# 单视图覆盖
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

# 自定义权限
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.owner_id == request.user.id

# ===== DRF：过滤 / 搜索 / 排序 / 分页 =====
# 在 settings.REST_FRAMEWORK 里设：
#   "DEFAULT_FILTER_BACKENDS": [
#       "django_filters.rest_framework.DjangoFilterBackend",
#       "rest_framework.filters.SearchFilter",
#       "rest_framework.filters.OrderingFilter",
#   ]
#   "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
#   "PAGE_SIZE": 10

class ArticleViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter                       # django-filter FilterSet
    search_fields = ["title", "body"]                     # ?search=xxx
    ordering_fields = ["created_at", "view_count"]        # ?ordering=-view_count

# 配合的 ArticleFilter：
class ArticleFilter(df_filters.FilterSet):
    view_count__gte = df_filters.NumberFilter(field_name="view_count", lookup_expr="gte")
    title_contains = df_filters.CharFilter(field_name="title", lookup_expr="icontains")
    class Meta:
        model = Article
        fields = ["is_published", "category_id"]

# 查询参数示例：
# ?is_published=true&category_id=1&view_count__gte=10&search=django&ordering=-view_count
```

---

## 3. 实战代码片段

所有 demo 在 `example/python/django/`，可独立运行；完整可 runserver 的小型项目在 `example/python/django/full_app/`。

| Demo | 涵盖 | 链接 |
| --- | --- | --- |
| `models_demo.py` | 字段类型 + 关系字段 + Meta + on_delete 决策 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/django/models_demo.py) |
| `queryset_demo.py` | filter / 聚合 / F / Q / select_related / N+1 修复 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/django/queryset_demo.py) |
| `drf_serializer_demo.py` | Serializer / ModelSerializer / 嵌套 / 校验三层次 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/django/drf_serializer_demo.py) |
| `drf_viewset_demo.py` | ModelViewSet / Router / 权限 / @action | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/python/django/drf_viewset_demo.py) |
| `full_app/` | 完整 Django+DRF 项目（可 runserver / 6 个测试用例） | [目录](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/python/django/full_app/) |

### 3.1 完整项目的 curl 流程

```bash
cd example/python/django/full_app

# 1. 准备
uv run python manage.py migrate
uv run python manage.py shell -c "
from articles.models import Article, Category
cat = Category.objects.create(name='tech')
Article.objects.create(title='hello django', body='content', category=cat, is_published=True)
"

# 2. 启服务
uv run python manage.py runserver

# 3. 另开终端测
curl http://127.0.0.1:8000/api/articles/                           # 列表
curl "http://127.0.0.1:8000/api/articles/?search=django"          # 搜索
curl "http://127.0.0.1:8000/api/articles/?ordering=-view_count"    # 排序
curl -X POST http://127.0.0.1:8000/api/articles/1/increment/       # 自定义动作
curl http://127.0.0.1:8000/api/articles/published/                 # 已发布列表
```

---

## 4. 常见坑 + 官方文档链接

### 4.1 N+1 查询（最常踩）

```python
# ❌ 错误：循环里触发关联查询
for author in Author.objects.all():
    print(author.articles.all())        # 1 + N 次查询

# ✅ 修复：select_related（外键 / OneToOne，SQL JOIN）
authors = Author.objects.select_related("profile").all()

# ✅ 修复：prefetch_related（M2M / 反向，二次 SQL 一次性拉）
authors = Author.objects.prefetch_related("articles", "articles__tags").all()
```

判断方法：开 Django Debug Toolbar 或 `connection.queries` 看每页 SQL 数量。

### 4.2 `on_delete` 决策表

| 场景 | 选 | 原因 |
| --- | --- | --- |
| 父删时子应一并删（Article 删 → Comment 删） | `CASCADE` | 保持数据一致 |
| 父被引用时禁止删（Category 还有文章时不能删 Category） | `PROTECT` | 防止误删 |
| 父删时子保留，外键置 NULL | `SET_NULL` | 需字段 `null=True` |
| 父删时子保留，外键置默认值 | `SET_DEFAULT` | 需字段 `default=...` |
| 业务复杂需递归引用检测 | `RESTRICT`（Django 4+） | 比 PROTECT 更智能 |

### 4.3 CSRF 在 API 项目里的处理

- **SessionAuthentication**：DRF 自动处理 CSRF（用 SessionAuthentication 鉴权的 View 仍走 CSRF 校验）
- **Token / JWT 鉴权**：用 `Authorization` Header，不走 CSRF（前后端分离的标准做法）
- 不要在 `@csrf_exempt` 上粗放豁免，应该在 CSRF 跟你的鉴权方案匹配后再豁免

### 4.4 DRF Serializer 嵌套 / 反向关系

```python
class ArticleSerializer(serializers.ModelSerializer):
    # 读时展开为完整对象
    author = AuthorSerializer(read_only=True)
    # 写时用 author_id（外键写用 id 是惯例，避免传嵌套对象）
    author_id = serializers.IntegerField(write_only=True)

    # 反向关系：tags 在 Article 上是 M2M
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "author", "author_id", "tags"]
```

### 4.5 迁移回滚

```bash
# 回滚到指定迁移（应用 0001 之后的所有迁移会被撤销）
python manage.py migrate articles 0001

# 撤销最近一次迁移（生成反向迁移文件）
python manage.py makemigrations articles
# 然后再写一个反向 migration；不要直接删迁移文件

# 看迁移对应的 SQL
python manage.py sqlmigrate articles 0001

# 看所有 app 的迁移状态
python manage.py showmigrations
```

### 4.6 `save()` 触发信号

- `Model.save()` 会触发 `pre_save` / `post_save` 信号
- `Model.objects.update()` **不会**触发（绕过 save）
- `bulk_update` 不触发；`bulk_create` 不触发（save 信号）

如果业务逻辑重度依赖信号，要在文档里写清楚，避免后续接手的人不知道。

### 4.7 Django 5.x / 6.0 新特性

- **async views**：`async def my_view(request)` + `path` 直接支持（Django 3.1+）
- **async ORM**：`Article.objects.aget(pk=1)` / `aall()` / `afilter()`（Django 4.1+，Django 6 已稳定）
- **`QuerySet.async iterator`**：`async for a in Article.objects.all()` 替代全量加载
- **Queries 简化**：`Model.objects.filter(...)` 的 `Q` 对象支持 `|` / `&` 操作
- **Django 6.0**：`NullBooleanField` 移除（用 `BooleanField(null=True)`）；`DECIMAL` 精度默认调整

### 4.8 常用第三方包速记

| 包 | 用途 |
| --- | --- |
| `django-environ` / `python-decouple` | 环境变量与 .env 文件管理 |
| `djangorestframework-simplejwt` | JWT 鉴权（替代 TokenAuthentication） |
| `django-filter` | 字段级过滤 |
| `drf-spectacular` | OpenAPI 3.0 文档 + Swagger UI |
| `django-cors-headers` | CORS 处理 |
| `celery` + `django-celery-beat` | 异步任务 / 定时任务 |
| `django-storages` | 静态 / 媒体文件存 S3 / OSS |
| `drf-yasg` | 老牌 Swagger 文档（不如 drf-spectacular 新） |
| `django-debug-toolbar` | 调试（看 SQL / 模板渲染时间） |

### 4.9 官方文档链接

- **Django 总览**：<https://docs.djangoproject.com/zh-hans/6.0/>
- **模型 / ORM**：<https://docs.djangoproject.com/zh-hans/6.0/topics/db/models/>
- **QuerySet 查询**：<https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/>
- **迁移**：<https://docs.djangoproject.com/zh-hans/6.0/topics/migrations/>
- **类视图（CBV）**：<https://docs.djangoproject.com/zh-hans/6.0/topics/class-based-views/>
- **URL 路由**：<https://docs.djangoproject.com/zh-hans/6.0/topics/http/urls/>
- **Settings**：<https://docs.djangoproject.com/zh-hans/6.0/ref/settings/>
- **DRF 总览**：<https://www.django-rest-framework.org/>
- **DRF Serializer**：<https://www.django-rest-framework.org/api-guide/serializers/>
- **DRF ViewSet**：<https://www.django-rest-framework.org/api-guide/viewsets/>
- **DRF Router**：<https://www.django-rest-framework.org/api-guide/routers/>
- **DRF 权限**：<https://www.django-rest-framework.org/api-guide/permissions/>
- **DRF 认证**：<https://www.django-rest-framework.org/api-guide/authentication/>
- **DRF 过滤**：<https://www.django-rest-framework.org/api-guide/filtering/>
- **drf-spectacular**：<https://drf-spectacular.readthedocs.io/>
- **django-filter**：<https://django-filter.readthedocs.io/>
