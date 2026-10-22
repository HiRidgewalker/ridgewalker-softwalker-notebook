"""
数据校验：Path / Query / Body / Field 的常用校验项

启动：
    uv run uvicorn workspace.python.fastapi.params_demo:app --reload

测试：
    curl -X PUT http://127.0.0.1:8000/items/1?short=ok \
         -H "Content-Type: application/json" \
         -d '{"name":"book","price":12.5,"description":"a book"}'
"""
from typing import Optional

from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()


# 路径参数 + 数值校验
@app.get("/items/{item_id}")
def read_item(
    item_id: int = Path(..., gt=0, le=1000, description="商品 ID，1~1000"),
    short: bool = Query(False, description="是否返回简短版本"),
):
    return {"item_id": item_id, "short": short}


# 查询参数 + 字符串校验
@app.get("/search")
def search(
    q: Optional[str] = Query(None, min_length=1, max_length=50, pattern="^[a-zA-Z0-9]+$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return {"q": q, "page": page, "size": size}


# Pydantic 模型 + Field 校验
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    price: float = Field(..., gt=0)
    tax: Optional[float] = Field(None, ge=0, le=1)


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    full_name: Optional[str] = None


# 多个请求体参数 + 显式 Body
@app.put("/items/{item_id}")
def update_item(
    item_id: int = Path(..., gt=0),
    item: Item = Body(...),
    user: User = Body(...),
    importance: int = Body(..., ge=1, le=5, embed=True),
):
    """
    - item、user 走 Pydantic 模型自动识别为请求体
    - importance 是单值，显式 Body(..., embed=True) 强制包成 {"importance": ...}
    """
    return {
        "item_id": item_id,
        "item": item,
        "user": user,
        "importance": importance,
    }
