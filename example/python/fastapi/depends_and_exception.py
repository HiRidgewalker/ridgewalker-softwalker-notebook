"""
依赖注入 + 异常处理

启动：
    uv run uvicorn example.python.fastapi.depends_and_exception:app --reload

要点：
- Depends(fn) 把 fn 的返回值注入到路由参数
- yield 依赖用于资源清理（DB session、文件句柄等）
- HTTPException 抛标准错误
- 自定义 exception_handler 统一处理自定义异常
"""
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()


# ===== 1. 基础依赖 =====
def get_query_token(token: str = ""):
    if token != "secret":
        raise HTTPException(status_code=401, detail="invalid token")
    return token


@app.get("/items")
def read_items(token: str = Depends(get_query_token)):
    return {"token": token}


# ===== 2. yield 依赖：资源清理 =====
def get_db():
    db = {"connected": True}
    try:
        yield db
    finally:
        db["connected"] = False
        # 真实场景：db.close()、session.close()、file.close()


@app.get("/users")
def read_users(db: dict = Depends(get_db)):
    return {"db": db}


# ===== 3. HTTPException =====
@app.get("/items/{item_id}")
def get_item(item_id: int):
    items = {1: "a", 2: "b"}
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="item not found",
            headers={"X-Error": "not-found"},
        )
    return {"item": items[item_id]}


# ===== 4. 自定义异常 + handler =====
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"item {exc.item_id} not found"},
    )


@app.get("/items2/{item_id}")
def get_item2(item_id: int):
    if item_id != 1:
        raise ItemNotFoundError(item_id)
    return {"item": "a"}
