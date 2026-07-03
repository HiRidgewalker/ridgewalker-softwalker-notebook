# Pydantic 笔记

> 原 `文档/Pydantic.md` 的重新整理版本，专注 **Pydantic v2**，重点是 **Pydantic v2 在 FastAPI 框架中的实战常用特性**。原笔记保留在 `文档/Pydantic.md` 供回溯。
> 演示代码统一放在 `workspace/python/pydantic/`，本笔记通过 git 远程链接引用。

## 1. 速查总览

### 1.1 是什么

Pydantic 是 Python 的**数据验证 + 序列化**库，核心用 Rust 写的 `pydantic-core` 加速。v2 是重大重写（性能比 v1 快 5~50x，类型系统更完善）。

### 1.2 什么时候用

- **FastAPI 请求体 / 响应模型**（最常见）
- **配置管理**（pydantic-settings 加载 .env / 环境变量）
- **数据导入**（CSV / JSON → 强类型对象）
- **CLI 工具参数**（Typer / Click 的 type 校验）
- **LLM 工具调用**（Function Calling 的参数 schema）

### 1.3 在 FastAPI 中的 4 个核心角色

1. **请求体** — `def create(user: UserIn)`，FastAPI 自动读 JSON → 校验 → 注入
2. **响应模型** — `response_model=UserOut`，自动序列化 + 字段过滤
3. **嵌套 body** — `embed=True` 把单字段包成对象
4. **校验错误** — 失败自动 422 + 多字段错误聚合

### 1.4 安装

```bash
# FastAPI 已自带 pydantic
uv add fastapi

# 单独使用 / 配置管理
uv add pydantic
uv add 'pydantic[email]'         # EmailStr / HttpUrl 等需要
uv add pydantic-settings         # BaseSettings
```

---

## 2. 常用模式速查表

### 2.1 BaseModel 基础

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int = 0
    tags: list[str] = Field(default_factory=list)   # 可变默认值

u = User(id=1, name="alice", email="alice@example.com")
u.name                          # 字段访问
u.model_dump()                  # v2 替代 v1 的 .dict()       → dict
u.model_dump_json()             # v2 替代 v1 的 .json()      → str
User.model_validate({"id": 1, "name": "a", "email": "a@b.c"})
User.model_validate_json('{"id": 1, "name": "a", "email": "a@b.c"}')
```

### 2.2 字段类型常用

```python
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal, Optional, Union
from uuid import UUID
from pydantic import EmailStr, HttpUrl, SecretStr, Field

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Demo(BaseModel):
    # 基础
    s: str
    i: int
    b: bool

    # 容器
    tags: list[str]
    mapping: dict[str, int]

    # 联合 / 可选
    maybe: Optional[int] = None         # 等价 int | None
    either: Union[int, str]             # 多种类型

    # 字面量枚举（值必须取自集合）
    side: Literal["buy", "sell"]
    color: Side

    # 验证类
    email: EmailStr
    website: HttpUrl

    # 标识
    uid: UUID
    amount: Decimal

    # 敏感字段（repr 时隐藏，序列化可选）
    password: SecretStr

    # 字段约束
    username: Annotated[str, Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")]
    age: Annotated[int, Field(ge=0, le=150)]
```

### 2.3 校验与错误

```python
from pydantic import ValidationError

# 自动：构造时校验
try:
    User(id="not-int", name="", email="bad")
except ValidationError as e:
    e.errors()        # 错误详情列表（type / loc / msg / input）
    e.json()          # JSON 格式

# 手动
User.model_validate(data)            # 从 dict
User.model_validate_json(json_str)   # 从 JSON 字符串
```

### 2.4 ConfigDict

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,        # 允许用别名或字段名
        str_strip_whitespace=True,    # 自动 strip
        extra="forbid",                # forbid / ignore / allow（默认 ignore）
        frozen=False,                 # 不可变
        validate_assignment=True,     # 赋值时也校验
        from_attributes=True,         # 从 ORM 对象属性读
        use_enum_values=True,         # 序列化时用 enum value 而非对象
    )
```

### 2.5 嵌套模型

```python
class Address(BaseModel):
    city: str
    zip: str

class Company(BaseModel):
    name: str
    primary_address: Address
    addresses: list[Address] = []
    ceo: Optional["User"] = None       # 自引用 / 前向引用

Company.model_rebuild()                # 解析前向引用
```

### 2.6 字段别名（请求/响应字段名不同）

```python
class UserOut(BaseModel):
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")

    model_config = ConfigDict(populate_by_name=True)

# 接收 {"userId": 1, "userName": "a"} → 模型用 user_id / user_name
UserOut.model_validate({"userId": 1, "userName": "a"})

# 序列化为别名
UserOut(user_id=1, user_name="a").model_dump(by_alias=True)
# → {"userId": 1, "userName": "a"}
```

### 2.7 序列化选项

```python
u.model_dump()                       # 原生 Python（datetime 仍是对象）
u.model_dump(mode="json")            # JSON 友好（datetime → ISO 字符串）
u.model_dump(exclude={"email"})      # 排除
u.model_dump(include={"id", "name"}) # 只导出这些
u.model_dump(exclude_none=True)      # 排 None
u.model_dump(exclude_unset=True)     # 排未显式设置的（PATCH 接口重要）
u.model_dump(by_alias=True)          # 用别名输出
```

### 2.8 Field 高级

```python
class User(BaseModel):
    name: str = Field(
        ...,
        min_length=1, max_length=50,
        pattern=r"^[a-zA-Z]+$",
        description="用户名",
        examples=["alice"],           # OpenAPI 示例
        deprecated=True,              # 文档标记弃用
    )
    password: str = Field(..., repr=False, exclude=True)  # 不进 repr / 不进序列化
```

### 2.9 自定义校验

```python
from pydantic import field_validator, model_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def name_must_not_be_spam(cls, v: str) -> str:
        if "spam" in v.lower():
            raise ValueError("name 不能含 spam")
        return v.strip()

    @model_validator(mode="after")
    def check_age_consistency(self) -> "User":
        if self.age < 0:
            raise ValueError("age 不能为负")
        return self
```

### 2.10 Literal / Enum / Discriminated Union（多态请求体）

```python
from typing import Annotated, Union
from pydantic import Field
from pydantic import TypeAdapter

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    woof: str

Pet = Annotated[Union[Cat, Dog], Field(discriminator="pet_type")]

adapter = TypeAdapter(Pet)
adapter.validate_python({"pet_type": "cat", "meow": 3})    # → Cat(meow=3)
adapter.validate_python({"pet_type": "dog", "woof": "hi"}) # → Dog(woof="hi")
```

### 2.11 computed_field（派生字段进序列化）

```python
from pydantic import computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

Rectangle(width=3, height=4).model_dump()  # → {"width": 3, "height": 4, "area": 12.0}
```

### 2.12 BaseSettings（pydantic-settings 加载 .env）

```python
# uv add pydantic-settings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "demo"
    database_url: str
    debug: bool = False
    port: int = 8000
    allowed_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",              # 环境变量前缀
        extra="ignore",
        case_sensitive=False,
    )

# .env 文件示例（与脚本同目录或项目根）：
# APP_DATABASE_URL=postgresql://localhost/mydb
# APP_DEBUG=true
# APP_ALLOWED_HOSTS=["localhost","example.com"]

# 优先级：构造参数 > 环境变量 > .env 文件 > 类默认值
settings = Settings()
```

---

## 3. FastAPI 实战代码片段

所有 demo 在 `workspace/python/pydantic/`，可独立运行。

| Demo | 涵盖 | 链接 |
| --- | --- | --- |
| `pydantic_basics.py` | BaseModel / 字段类型 / 校验 / 嵌套 / 序列化 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/pydantic/pydantic_basics.py) |
| `pydantic_fastapi_demo.py` | **重点**：请求体 / 响应模型 / 字段过滤 / 多态 / 字段别名 / 错误格式 / 嵌套 body | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/pydantic/pydantic_fastapi_demo.py) |
| `pydantic_settings_demo.py` | BaseSettings 加载 .env / 嵌套 settings / lru_cache 单例 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/pydantic/pydantic_settings_demo.py) |

### 3.1 跑 FastAPI demo

```bash
uv run uvicorn workspace.python.pydantic.pydantic_fastapi_demo:app --reload
```

启动后访问 `http://127.0.0.1:8000/docs` 看 Swagger UI，每个路由都有示例。

### 3.2 重点路由

| 路由 | 演示特性 |
| --- | --- |
| `POST /users/` | 基础请求体（BaseModel 注入） |
| `POST /users2/` | 响应模型 + 字段过滤（password 不外泄） |
| `PATCH /users/{user_id}` | `response_model_exclude_unset`（PATCH 重要） |
| `POST /users3/` | 字段别名（请求/响应都走别名） |
| `POST /items/` | Discriminated Union 多态请求体 |
| `GET /users/{user_id}` | 多响应模型（`responses={404: ...}`） |
| `PUT /items/{item_id}` | 嵌套 body（`Body(..., embed=True)`） |

### 3.3 校验错误格式（422 响应）

客户端发错误请求时，FastAPI 自动返回 422 + 详细错误列表：

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": {"id": 1, "email": "a@b.c"}
    },
    {
      "type": "greater_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 0",
      "input": -1
    }
  ]
}
```

---

## 4. 常见坑 + 官方文档链接

### 4.1 `Optional[T]` vs 默认值 `None`

```python
class Auth(BaseModel):
    username: str
    password: str | None              # 类型允许 None，但客户端必须传 key

class Auth2(BaseModel):
    username: str
    password: str | None = None       # 有默认值，可不传
```

| 写法 | 客户端是否必须传 key |
| --- | --- |
| `password: str \| None` | ✅ 必须传，传 `null` 也算 |
| `password: str \| None = None` | ❌ 可不传 |

> 与 FastAPI 笔记的 4.1 呼应。

### 4.2 `model_dump()` vs `model_dump_json()` vs `dict()`

| 方法 | 用途 | 性能 |
| --- | --- | --- |
| `model_dump()` | → Python `dict` | 适合后续在 Python 里处理 |
| `model_dump_json()` | → JSON 字符串 | 适合直接返回 HTTP 响应 |
| `model_dump(mode="json")` | dict 但 datetime 已是 ISO str | 适合拼到其他 JSON 里 |

### 4.3 `extra="forbid"` 的行为

```python
class User(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")

User.model_validate({"name": "a", "extra_field": "x"})
# ValidationError: Extra inputs are not permitted
```

适合 **API 入参严格校验** 的场景（拒绝客户端传未定义字段）。

### 4.4 `response_model` 三件套

```python
@app.post("/users/", response_model=UserOut, response_model_exclude_unset=True, response_model_by_alias=True)
def create_user(user: UserInDb):
    return user
```

- `response_model=UserOut` — 自动按 UserOut 序列化
- `response_model_exclude_unset=True` — 客户端没传的字段不出现（**PATCH 接口关键**）
- `response_model_by_alias=True` — 响应里用字段别名

### 4.5 `response_model_exclude_unset` 的实战用法

PATCH 接口通常只需返回"被改过的字段"，让客户端知道哪几个字段已更新：

```python
class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

@app.patch("/users/{user_id}", response_model=UserPatch, response_model_exclude_unset=True)
def patch_user(user_id: int, patch: UserPatch):
    return patch

# 客户端传 {"name": "newname"} → 响应也只返回 {"name": "newname"}
# 而不是 {"name": "newname", "email": null}
```

### 4.6 `Field` 跟 `Body` 别混

```python
# 错误：路由参数里用 pydantic.Field(embed=True) 不行
@app.put("/items/{id}")
def update(id: int, item: Item = Field(..., embed=True)):  # ❌
    ...

# 正确：路由参数用 fastapi.Body
from fastapi import Body
@app.put("/items/{id}")
def update(id: int, item: Item = Body(..., embed=True)):   # ✅
    ...
```

### 4.7 性能提示

- **字段顺序**：pydantic-core 用 slots 创建模型，**按常用度排**字段（前面字段访问更快）
- **避免过度嵌套**：嵌套过深会增加校验时间
- **大列表用 `TypeAdapter`**：单次验证大量 dict 时用 `TypeAdapter` 复用 schema
- **v2 比 v1 快 5~50x**，新项目直接用 v2

### 4.8 官方文档链接

- Pydantic v2 总览：<https://docs.pydantic.dev/latest/>
- BaseModel：<https://docs.pydantic.dev/latest/concepts/models/>
- 字段类型：<https://docs.pydantic.dev/latest/concepts/fields/>
- 校验器：<https://docs.pydantic.dev/latest/concepts/validators/>
- ConfigDict：<https://docs.pydantic.dev/latest/api/config/>
- 序列化：<https://docs.pydantic.dev/latest/concepts/serialization/>
- Discriminated Union：<https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions>
- computed_field：<https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.computed_field>
- pydantic-settings：<https://docs.pydantic-settings/latest/>
- FastAPI × Pydantic：<https://fastapi.tiangolo.com/zh/tutorial/body/>
