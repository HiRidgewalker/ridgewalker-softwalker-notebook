"""
Django 模型演示：字段类型 + 关系字段 + Meta 选项

跑：
    uv run python example/python/django/models_demo.py
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


# ===== 示例模型 =====
class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "__main__"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        app_label = "__main__"

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default="")

    class Meta:
        app_label = "__main__"
        ordering = ["name"]


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("published", "已发布"),
        ("archived", "已归档"),
    ]

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    # 关系字段
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    class Meta:
        app_label = "__main__"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]
        constraints = [
            models.UniqueConstraint(fields=["author", "slug"], name="unique_author_slug"),
        ]

    def __str__(self):
        return self.title


# ===== 字段类型速记 =====
# 字符串：CharField(max_length=...) / TextField() / EmailField() / URLField() / SlugField()
# 数值：  IntegerField() / BigIntegerField() / FloatField() / DecimalField(max_digits, decimal_places)
# 布尔：  BooleanField()                                       # NullBooleanField 已在 Django 6.0 移除
# 时间：  DateField() / DateTimeField() / DurationField()      # auto_now=True / auto_now_add=True
# 文件：  FileField() / ImageField() / FilePathField()
# 其他：  UUIDField() / GenericIPAddressField() / JSONField()

# ===== 关系字段 =====
# ForeignKey(OtherModel, on_delete=...)       多对一 → ForeignKey 字段放在「多」的一方
# ManyToManyField(OtherModel, ...)            多对多 → 在任一方声明，related_name 设反向访问名
# OneToOneField(OtherModel, on_delete=...)    一对一

# ===== on_delete 决策 =====
# CASCADE     父删子也删（最常用，如 Article 删了 → Comment 也删）
# PROTECT     父被引用时禁止删（如 Category 还有文章时不能删 Category）
# SET_NULL    父删时子外键置 NULL（需 null=True）
# SET_DEFAULT 父删时子外键置 default 值（需 default=...）
# DO_NOTHING  不做任何处理（DB 会拒绝；不推荐）
# RESTRICT    Django 4.x 新增，递归引用检测（比 PROTECT 更智能）

# ===== Meta 常用选项 =====
# ordering = ["-created_at"]                # 默认排序
# verbose_name / verbose_name_plural        # 单复数显示名
# indexes = [...]                           # 普通索引
# constraints = [...]                       # 约束（UniqueConstraint / CheckConstraint）
# abstract = True                           # 抽象基类（不创建表）
# app_label = "..."                         # 模型不属于任何 app 时指定
# unique_together = [("a", "b")]            # 联合唯一（已弃用，建议用 constraints）

# ===== 字段命名限制（踩坑）=====
# 1. 不能是 Python 保留字
# 2. 不能有连续两个下划线（与查询语法冲突，如 foo__bar）
# 3. 不能以下划线结尾
