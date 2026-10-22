"""
完整可运行小型 API demo
- 用户注册 / 登录
- 受保护的 /items CRUD
- 统一错误处理
- 一行命令启服务

启动：
    uv run uvicorn workspace.python.fastapi.full_app.main:app --reload

curl 测：

    1. 注册（用户名 alice，密码 alice123）：
       curl -X POST http://127.0.0.1:8000/register \
            -H "Content-Type: application/json" \
            -d '{"username":"alice","full_name":"Alice","password":"alice123"}'

    2. 登录拿 token：
       TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
            -d "username=alice&password=alice123" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

    3. 创建 item（带 token）：
       curl -X POST http://127.0.0.1:8000/items \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"name":"book","price":12.5}'

    4. 列出 item：
       curl http://127.0.0.1:8000/items
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# ===== 配置 =====
SECRET_KEY = "demo-secret-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Items API", version="0.1.0")


# ===== Pydantic 模型 =====
class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    full_name: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=128)


class UserInDB(User):
    hashed_password: str


class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=300)


# ===== 假数据库 =====
users_db: dict[str, UserInDB] = {}
items_db: dict[int, Item] = {}


# ===== 工具函数 =====
def hash_password(p: str) -> str:
    return pwd_context.hash(p)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user(username: str) -> Optional[UserInDB]:
    return users_db.get(username)


def authenticate(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if not username:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = get_user(username)
    if not user:
        raise credentials_exc
    return User(username=user.username, full_name=user.full_name)


# ===== 鉴权路由 =====
@app.post("/register", response_model=User, status_code=201)
def register(req: RegisterRequest):
    if req.username in users_db:
        raise HTTPException(status_code=400, detail="username exists")
    users_db[req.username] = UserInDB(
        username=req.username,
        full_name=req.full_name,
        hashed_password=hash_password(req.password),
    )
    return User(username=req.username, full_name=req.full_name)


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


# ===== 业务路由 =====
@app.get("/items", response_model=List[Item])
def list_items():
    return list(items_db.values())


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item, current_user: User = Depends(get_current_user)):
    new_id = max(items_db.keys(), default=0) + 1
    items_db[new_id] = item
    return item


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="item not found")
    return items_db[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, current_user: User = Depends(get_current_user)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="item not found")
    del items_db[item_id]
