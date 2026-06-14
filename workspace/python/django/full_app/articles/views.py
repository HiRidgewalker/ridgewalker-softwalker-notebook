from django_filters import rest_framework as df_filters
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Article
from .serializers import ArticleSerializer


class ArticleFilter(df_filters.FilterSet):
    """django-filter 字段级过滤。

    - ?is_published=true
    - ?view_count__gte=10
    - ?category_id=1
    """

    view_count__gte = df_filters.NumberFilter(field_name="view_count", lookup_expr="gte")
    view_count__lte = df_filters.NumberFilter(field_name="view_count", lookup_expr="lte")
    title_contains = df_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Article
        fields = ["is_published", "category_id"]


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related("category").all()
    serializer_class = ArticleSerializer

    # 三种过滤/搜索/排序后端（settings.REST_FRAMEWORK 也配了）
    filter_backends = [
        df_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ArticleFilter
    search_fields = ["title", "body"]                 # ?search=django
    ordering_fields = ["created_at", "view_count"]    # ?ordering=-view_count
    ordering = ["-created_at"]

    # 自定义动作：POST /articles/{id}/increment/
    @action(detail=True, methods=["post"])
    def increment(self, request, pk=None):
        article = self.get_object()
        article.view_count += 1
        article.save(update_fields=["view_count", "updated_at"])
        return Response({"id": article.id, "view_count": article.view_count})

    # 自定义动作（不需要 pk）：GET /articles/published/
    @action(detail=False, methods=["get"])
    def published(self, request):
        qs = self.get_queryset().filter(is_published=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
