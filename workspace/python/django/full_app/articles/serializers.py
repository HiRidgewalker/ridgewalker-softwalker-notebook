from rest_framework import serializers
from .models import Article, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ArticleSerializer(serializers.ModelSerializer):
    # 嵌套：读时展示 category 详情
    category = CategorySerializer(read_only=True)
    # 写时用 category_id
    category_id = serializers.IntegerField(write_only=True)

    # 自定义展示字段
    title_length = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id", "title", "body", "view_count", "is_published",
            "category", "category_id",
            "title_length",
            "created_at", "updated_at",
        ]
        read_only_fields = ["view_count", "created_at", "updated_at"]

    def get_title_length(self, obj):
        return len(obj.title)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("标题不能为空")
        return value

    def validate(self, attrs):
        if attrs.get("is_published") and not attrs.get("body"):
            raise serializers.ValidationError("发布时必须有 body")
        return attrs
