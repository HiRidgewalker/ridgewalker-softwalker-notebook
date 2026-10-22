"""
Pydantic v2 在 FastAPI 中的实战演示（重点）
- 请求体 / 响应模型 / 多态 / 字段别名 / 错误格式 / 嵌套 body

启动：
    uv run uvicorn workspace.python.pydantic.pydantic_fastapi_demo:app --reload

测：
    curl http://127.0.0.1:8000/docs        # Swagger UI 看所有示例
    curl -X POST http://127.0.0.1:8000/users/ \
         -H "Content-Type: application/json" \
         -d '{"id":1,"name":"alice","email":"alice@example.com"}'
"""
from typing import Annotated, Literal, Optional, Union

from fastapi import Body, FastAPI, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI(title="Pydantic v2 × FastAPI Demo")


# ===== 1. 基础请求体 =====
class UserIn(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    age: int = Field(0, ge=0, le=150)


@app.post("/users/", response_model=UserIn)
def create_user(user: UserIn):
    """FastAPI 自动：JSON → UserIn 校验 → 注入函数"""
    return user


# ===== 2. 响应模型 + 字段过滤 =====
class UserInDb(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str             # 内部用，不应返回


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


@app.post("/users2/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user2(user: UserInDb):
    """response_model=UserOut：自动过滤 password 字段"""
    # 即使内部用了 UserInDb，响应里也只会有 id/name/email
    return user


# ===== 3. response_model_exclude_unset（PATCH 常用）=====
class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


@app.patch("/users/{user_id}", response_model=UserPatch, response_model_exclude_unset=True)
def patch_user(user_id: int, patch: UserPatch):
    """exclude_unset=True：客户端没传的字段不在响应里出现"""
    # 只返回客户端实际改过的字段
    return patch


# ===== 4. 字段别名：请求/响应字段名不同 =====
class UserAlias(BaseModel):
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")

    model_config = ConfigDict(populate_by_name=True)


@app.post("/users3/", response_model=UserAlias, response_model_by_alias=True)
def create_user3(user: UserAlias):
    """请求接 {"userId":1,"userName":"a"}，响应也用别名"""
    return user


# ===== 5. 多态请求体（Discriminated Union）=====
class TextItem(BaseModel):
    type: Literal["text"]
    content: str


class ImageItem(BaseModel):
    type: Literal["image"]
    url: str
    width: int
    height: int


Item = Annotated[
    Union[TextItem, ImageItem],
    Field(discriminator="type"),
]


@app.post("/items/")
def create_item(item: Item):
    """FastAPI 根据 type 字段自动选 TextItem 或 ImageItem 校验"""
    return item


# ===== 6. 多响应模型（responses={}）=====
class NotFoundResp(BaseModel):
    detail: str


@app.get(
    "/users/{user_id}",
    response_model=UserOut,
    responses={404: {"model": NotFoundResp}},
)
def get_user(user_id: int):
    if user_id != 1:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="user not found")
    return UserOut(id=1, name="alice", email="alice@example.com")


# ===== 7. 嵌套 body（embed=True）=====
class ItemBase(BaseModel):
    name: str
    price: float


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemBase = Body(..., embed=True)):
    """客户端必须传 {"item": {"name": "...", "price": 0.0}}"""
    return {"item_id": item_id, "item": item}


# ===== 8. 错误格式（422 响应）=====
# 客户端发错误请求时，FastAPI 自动返回 422 + 详细错误列表：
#
# {
#   "detail": [
#     {
#       "type": "missing",
#       "loc": ["body", "name"],
#       "msg": "Field required",
#       "input": {...}
#     },
#     {
#       "type": "greater_than_equal",
#       "loc": ["body", "age"],
#       "msg": "Input should be greater than or equal to 0",
#       "input": -1
#     }
#   ]
# }
