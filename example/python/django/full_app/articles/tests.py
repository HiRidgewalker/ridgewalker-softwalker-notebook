"""
articles app 的单元测试

跑：
    cd example/python/django/full_app
    uv run python manage.py test articles
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Article, Category


class ArticleAPITestCase(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="tech")
        self.article = Article.objects.create(
            title="hello django",
            body="content here",
            category=self.cat,
            is_published=True,
        )
        self.client = APIClient()

    def test_list_articles(self):
        r = self.client.get("/api/articles/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["results"]), 1)

    def test_search_articles(self):
        r = self.client.get("/api/articles/?search=django")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["results"]), 1)

    def test_filter_by_category(self):
        r = self.client.get(f"/api/articles/?category_id={self.cat.id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["results"]), 1)

    def test_increment_action(self):
        r = self.client.post(f"/api/articles/{self.article.id}/increment/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["view_count"], 1)

    def test_create_article(self):
        r = self.client.post(
            "/api/articles/",
            data={"title": "new", "body": "b", "category_id": self.cat.id},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Article.objects.count(), 2)

    def test_create_article_validation(self):
        # 发布时 body 为空 → 422
        r = self.client.post(
            "/api/articles/",
            data={"title": "new", "body": "", "category_id": self.cat.id, "is_published": True},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
