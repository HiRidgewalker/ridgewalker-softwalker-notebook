"""
用 fastapi.testclient.TestClient 测 FastAPI 应用
- TestClient 基于 httpx，无需启动真实 uvicorn
- 纯 in-process 调用，速度快
- 适合 pytest

跑测试：
    uv run pytest example/python/fastapi/test_client.py -v
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
def root():
    return {"hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = ""):
    return {"item_id": item_id, "q": q}


@app.post("/items")
def create_item(item: dict):
    return item


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"hello": "world"}


def test_read_item_ok():
    r = client.get("/items/42?q=hello")
    assert r.status_code == 200
    assert r.json() == {"item_id": 42, "q": "hello"}


def test_read_item_type_error():
    # item_id 不是 int → 422 Unprocessable Entity
    r = client.get("/items/abc")
    assert r.status_code == 422


def test_create_item():
    r = client.post("/items", json={"name": "book", "price": 12.5})
    assert r.status_code == 200
    assert r.json() == {"name": "book", "price": 12.5}
