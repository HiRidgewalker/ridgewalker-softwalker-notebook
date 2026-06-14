"""
FastAPI 最小例子：路径参数 / 查询参数 / 请求体的识别规则

启动：
    uv run uvicorn workspace.python.fastapi.hello_world:app --reload

访问：
    http://127.0.0.1:8000/             # GET 根
    http://127.0.0.1:8000/items/42?q=hello   # GET 路径 + 查询
    http://127.0.0.1:8000/docs         # Swagger UI
    http://127.0.0.1:8000/redoc        # ReDoc
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hello FastAPI")


@app.get("/")
def root():
    return {"hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = ""):
    """
    参数识别规则：
    - item_id 出现在路径里 → 路径参数（int 强转）
    - q 不在路径里、是单类型 + 有默认值 → 查询参数
    """
    return {"item_id": item_id, "q": q}


class Item(BaseModel):
    name: str
    price: float


@app.post("/items")
def create_item(item: Item):
    """
    item 是 Pydantic 模型 → 自动识别为请求体
    """
    return {"name": item.name, "price": item.price}
