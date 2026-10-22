"""
DRF Serializer 演示：Serializer vs ModelSerializer + 嵌套 + 校验

跑：
    uv run python example/python/django/drf_serializer_demo.py
"""
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "rest_framework",
        "__main__",
    ],
    USE_TZ=True,
    REST_FRAMEWORK={
        "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
        "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    },
)
django.setup()

from django.db import models
from rest_framework import serializers


# ===== 示例 model =====
class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "__main__"


class Tag(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = "__main__"


class Article(models.Model):
    STATUS_CHOICES = [("draft", "草稿"), ("published", "已发布")]

    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    view_count = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="articles")
    tags = models.ManyToManyField(Tag, related_name="articles", blank=True)

    class Meta:
        app_label = "__main__"

    def __str__(self):
        return self.title


# ===== 1. Serializer（手写字段） =====
class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


# ===== 2. ModelSerializer（自动从 model 推导） =====
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "body", "status", "view_count", "author", "tags"]


# ===== 3. ModelSerializer + 字段覆盖 + 校验 + 嵌套 =====
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    # 嵌套：把 author 字段展开为 AuthorSerializer
    author = AuthorSerializer(read_only=True)
    # 写时用 author_id（外键写用 id）
    author_id = serializers.IntegerField(write_only=True)

    # 自定义展示字段
    title_upper = serializers.SerializerMethodField()
    is_popular = serializers.SerializerMethodField()

    # 嵌套反向关系
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id", "title", "body", "status", "view_count",
            "author", "author_id",
            "tags",
            "title_upper", "is_popular",
        ]
        read_only_fields = ["view_count"]                # 这几个不接受输入
        extra_kwargs = {
            "body": {"write_only": True},                # body 写入但不返回
        }

    # SerializerMethodField 的方法命名规则：get_<field_name>
    def get_title_upper(self, obj):
        return obj.title.upper()

    def get_is_popular(self, obj):
        return obj.view_count > 100

    # 字段级校验（单字段）
    def validate_title(self, value):
        if "spam" in value.lower():
            raise serializers.ValidationError("标题不能包含 spam")
        return value

    # 对象级校验（跨字段）
    def validate(self, attrs):
        if attrs.get("status") == "published" and not attrs.get("body"):
            raise serializers.ValidationError("发布时必须有 body")
        return attrs


# ===== 字段类型速记 =====
# 基础：   CharField / IntegerField / FloatField / DecimalField / BooleanField
# 验证：   EmailField / URLField / SlugField / UUIDField / IPAddressField
# 特殊：   DateField / DateTimeField / TimeField / DurationField
# 选择：   ChoiceField(choices=CHOICES) / MultipleChoiceField
# 集合：   ListField(child=...) / DictField(child=...)
# 文件：   FileField / ImageField
# 关系：   PrimaryKeyRelatedField / StringRelatedField / SlugRelatedField / HyperlinkedRelatedField
# 自定义： SerializerMethodField

# ===== 通用参数 =====
# required=True           # 必填（默认 True）
# allow_null=False        # 允许 None
# allow_blank=False       # 允许空字符串（仅字符串字段）
# default=...             # 默认值（常用 serializers.empty 占位「无默认」）
# read_only / write_only  # 读写控制（password 用 write_only）
# source="field_name"     # 从其他字段取值（如 source="user.username"）
# validators=[...]        # 自定义校验器列表
# error_messages={...}    # 自定义错误消息

# ===== Meta 选项 =====
# model = Model            # 关联的 model
# fields = "__all__"       # 所有字段
# fields = ["a", "b"]      # 显式字段列表（推荐，安全）
# exclude = ["a", "b"]     # 排除列表（与 fields 互斥）
# read_only_fields = [...] # 只读字段
# extra_kwargs = {...}     # 给字段批量传参
# depth = 1                # 自动展开外键（浅展开，少用，可控性差）

# ===== 校验三层次 =====
# 1. 字段级：validate_<field>(self, value) → 校验单个字段
# 2. 对象级：validate(self, attrs)        → 校验整个对象
# 3. DB 层： Meta.constraints (UniqueConstraint / CheckConstraint)
