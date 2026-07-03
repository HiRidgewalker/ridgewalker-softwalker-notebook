"""
DRF ViewSet + Router + 权限示例：model + serializer + viewset + url 完整链路

跑：
    uv run python workspace/python/django/drf_viewset_demo.py
"""
import django
from django.conf import settings
from django.urls import path, include

settings.configure(
    DEBUG=True,
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "rest_framework",
        "__main__",
    ],
    ROOT_URLCONF=__name__,
    USE_TZ=True,
    REST_FRAMEWORK={
        "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
        "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    },
)
django.setup()

from django.db import models
from rest_framework import serializers, viewsets, routers
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.authentication import SessionAuthentication, TokenAuthentication


# ===== model =====
class Article(models.Model):
    title = models.CharField(max_length=200)
    view_count = models.IntegerField(default=0)
    author_name = models.CharField(max_length=100, default="")

    class Meta:
        app_label = "__main__"


# ===== serializer =====
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "view_count", "author_name"]


# ===== ViewSet：完整 CRUD 自动生成 =====
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]  # 默认全部允许，可改成 [IsAuthenticated]

    # 自定义动作：POST /articles/{id}/increment/
    @action(detail=True, methods=["post"])
    def increment(self, request, pk=None):
        article = self.get_object()
        article.view_count += 1
        article.save()
        return Response({"view_count": article.view_count})

    # 自定义动作（不需要 pk）：GET /articles/popular/
    @action(detail=False, methods=["get"])
    def popular(self, request):
        qs = self.get_queryset().filter(view_count__gte=100)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ===== Router：自动生成 URL =====
router = routers.DefaultRouter()
router.register(r"articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("api/", include(router.urls)),
]


# ===== DRF View 层级（从底层到高层） =====
# 1. APIView            - 最基础，所有 view 的基类
# 2. GenericAPIView     - 加了 queryset/serializer_class 等通用能力
# 3. Mixin              - ListModelMixin / RetrieveModelMixin / CreateModelMixin / UpdateModelMixin / DestroyModelMixin
# 4. GenericViewSet     - GenericAPIView + 所有 mixin
# 5. ModelViewSet       - GenericViewSet + 所有 mixin（最常用）
# 6. ReadOnlyModelViewSet - 只读版（list + retrieve）


# ===== 手写 APIView（不用 ViewSet） =====
@api_view(["GET", "POST"])
def article_list(request):
    if request.method == "GET":
        qs = Article.objects.all()
        serializer = ArticleSerializer(qs, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ===== 常用装饰器 =====
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def my_view(request):
    return Response({"user": request.user.username})


# ===== 自定义权限类 =====
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.author_name == request.user.username
