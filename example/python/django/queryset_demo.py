"""
Django QuerySet 操作演示：过滤 / 聚合 / F / Q / select_related / N+1

跑：
    uv run python example/python/django/queryset_demo.py
"""
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "__main__"],
    USE_TZ=True,
)
django.setup()

from django.db import models
from django.db.models import F, Q, Count, Sum, Avg, Value, OuterRef, Subquery


class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0)

    class Meta:
        app_label = "__main__"


class Tag(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "__main__"


class Article(models.Model):
    title = models.CharField(max_length=200)
    view_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    tags = models.ManyToManyField(Tag, related_name="articles")

    class Meta:
        app_label = "__main__"


# ===== 基础查询 =====
Article.objects.all()                              # 全部
Article.objects.filter(is_published=True)          # 过滤
Article.objects.exclude(view_count=0)              # 反过滤
Article.objects.get(pk=1)                          # 拿单个（找不到/多个都报错）
Article.objects.count()                            # 计数
Article.objects.first() / .last()                  # 第一个 / 最后一个
Article.objects.exists()                           # 是否存在（生成 SELECT 1 ... LIMIT 1）
Article.objects.order_by("-view_count")            # 排序
Article.objects.reverse()                          # 反转（要求已排序）
Article.objects.distinct()                         # 去重

# ===== 字段查找（field__lookup=value）=====
Article.objects.filter(view_count__gt=100)                   # > 100
Article.objects.filter(view_count__gte=100)                  # >=
Article.objects.filter(view_count__lt=100)                   # <
Article.objects.filter(view_count__lte=100)                  # <=
Article.objects.filter(view_count__in=[10, 20, 30])          # IN
Article.objects.filter(title__contains="django")             # 包含（区分大小写）
Article.objects.filter(title__icontains="django")            # 包含（不区分大小写）
Article.objects.filter(title__startswith="Django")           # 以...开头
Article.objects.filter(title__regex=r"^Django.*$")           # 正则
Article.objects.filter(author__name="Alice")                 # 跨关系（外键）
Article.objects.filter(tags__name="python")                  # 多对多

# ===== 链式切片 / values =====
Article.objects.all()[:10]                          # 前 10 条（SQL LIMIT 10）
Article.objects.all()[10:20]                        # 11~20 条（不支持大偏移，分页用 Paginator）
Article.objects.values("id", "title")               # 只取部分字段 → 返回 dict 列表
Article.objects.values_list("id", "title")          # 只取部分字段 → 返回 tuple 列表
Article.objects.values_list("title", flat=True)     # → 返回 str 列表（单字段时）

# ===== F / Q 表达式 =====
# F：引用同表其他字段（常用于自更新、避免竞态）
Article.objects.filter(view_count__gt=F("comment_count") * 2)
Article.objects.update(view_count=F("view_count") + 1)         # 原子自增

# Q：组合复杂查询（& | ~）
Article.objects.filter(
    Q(is_published=True)
    & (Q(view_count__gt=100) | Q(title__icontains="django"))
)
Article.objects.filter(~Q(is_published=True))                  # NOT

# ===== 聚合与注解 =====
# aggregate：返回 dict（全局聚合，单行）
Article.objects.aggregate(
    total=Count("id"),
    avg_views=Avg("view_count"),
    total_views=Sum("view_count"),
)

# annotate：返回 QuerySet（每行带聚合字段）
authors = (
    Author.objects
    .annotate(
        article_count=Count("articles"),
        total_views=Sum("articles__view_count"),
    )
    .order_by("-article_count")
)
for a in authors:
    print(a.name, a.article_count, a.total_views)

# ===== 性能：N+1 问题（最常踩的坑）=====
# 错误写法：每个 author 触发一次 articles 查询 → 1 + N 次查询
# for author in Author.objects.all():
#     print(author.articles.all())         # 触发 N 次额外查询

# 正确：select_related（外键，SQL JOIN，一次拿全）
authors = Author.objects.select_related("profile").all()

# 正确：prefetch_related（多对多 / 反向，第二次 SQL 一次性查出来）
authors = Author.objects.prefetch_related("articles", "articles__tags").all()

# ===== 批量操作 =====
Article.objects.bulk_create([
    Article(title="a", author_id=1),
    Article(title="b", author_id=1),
    Article(title="c", author_id=1),
])                                                  # 一次性 INSERT 多条
Article.objects.bulk_update(articles, ["view_count"])  # 批量 UPDATE（不发信号）

# ===== 创建 / 更新 / 删除 =====
a = Article.objects.create(title="hello", author_id=1)
a.title = "hi"
a.save()
a.delete()                                          # 单条
Article.objects.filter(is_published=False).delete()  # 批量

# ===== 常用模式：get_or_create / update_or_create =====
obj, created = Article.objects.get_or_create(
    slug="hello", defaults={"title": "Hello", "author_id": 1}
)
obj, created = Article.objects.update_or_create(
    slug="hello", defaults={"title": "Hello v2"}
)

# ===== 子查询（高级）=====
# 例：取每篇文章 + 其作者的文章总数
Article.objects.annotate(
    author_total=Subquery(
        Author.objects.filter(pk=OuterRef("author_id"))
        .annotate(c=Count("articles"))
        .values("c")
    )
)
