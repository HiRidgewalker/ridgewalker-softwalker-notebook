"""
Pydantic v2 基础演示：BaseModel + 字段 + 校验 + 嵌套 + 序列化

跑：
    uv run python workspace/python/pydantic/pydantic_basics.py
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal, Optional, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    SecretStr,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)


# ===== 1. BaseModel 基础 =====
class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int = 0                                    # 默认值
    tags: list[str] = Field(default_factory=list)   # 可变默认值要用 default_factory
    registered_at: datetime = Field(default_factory=datetime.now)

    # ConfigDict（Pydantic v2 用法，替代 v1 的 class Config）
    model_config = ConfigDict(
        populate_by_name=True,    # 允许用别名或字段名
        str_strip_whitespace=True,
        extra="forbid",            # forbid / ignore / allow
        frozen=False,
        validate_assignment=True,  # 赋值时也校验
        from_attributes=True,      # 从 ORM 对象读属性
    )

    # 字段级校验
    @field_validator("name")
    @classmethod
    def name_must_not_be_spam(cls, v: str) -> str:
        if "spam" in v.lower():
            raise ValueError("name 不能含 spam")
        return v.strip()

    # 对象级校验
    @model_validator(mode="after")
    def check_age_consistency(self) -> "User":
        if self.age < 0:
            raise ValueError("age 不能为负")
        return self

    # 派生字段（参与序列化）
    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"


# ===== 2. 构造 / 访问 / 序列化 =====
u = User(id=1, name="alice", email="alice@example.com")
u.name                                        # 字段访问
u.model_dump()                                # v2 替代 v1 的 .dict()
u.model_dump_json()                           # v2 替代 v1 的 .json()
u.model_dump(exclude={"email"})               # 排除字段
u.model_dump(include={"id", "name"})          # 只导出这些
u.model_dump(exclude_none=True)               # 排 None
u.model_dump(exclude_unset=True)              # 排未显式设置的（PATCH 常用）
u.model_dump(mode="json")                     # 转 JSON 友好（datetime → str）

# 从 dict / JSON 构造
User.model_validate({"id": 1, "name": "a", "email": "a@b.c"})
User.model_validate_json('{"id": 1, "name": "a", "email": "a@b.c"}')

# 错误聚合
try:
    User(id="not-int", name="", email="bad")
except ValidationError as e:
    e.errors()       # 错误详情列表
    e.json()         # JSON 格式


# ===== 3. 字段类型常用 =====
class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Types(BaseModel):
    # 基础
    s: str
    i: int
    f: float
    b: bool

    # 容器
    tags: list[str]
    mapping: dict[str, int]
    pair: tuple[int, str]

    # 联合 / 可选
    maybe: Optional[int] = None            # T | None
    either: Union[int, str] = 0            # 多种类型

    # 字面量枚举（值必须取自集合）
    side: Literal["buy", "sell"]

    # 标准 Enum
    color: Color  # 见下方定义

    # 验证类
    email: EmailStr
    website: HttpUrl

    # 标识
    uid: UUID
    amount: Decimal

    # 敏感字段（不在 repr / 序列化里直接出现）
    password: SecretStr

    # 字段约束
    username: Annotated[str, Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")]
    age: Annotated[int, Field(ge=0, le=150)]


# ===== 4. 嵌套模型 =====
class Address(BaseModel):
    city: str
    zip: str


class Company(BaseModel):
    name: str
    addresses: list[Address] = Field(default_factory=list)         # 嵌套列表
    primary_address: Optional[Address] = None                       # 嵌套对象
    ceo: Optional["User"] = None                                    # 自引用 / 前向引用

Company.model_rebuild()  # 解析前向引用


# ===== 5. 字段别名（请求/响应字段名不同）=====
class UserOut(BaseModel):
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")

    model_config = ConfigDict(populate_by_name=True)


# 接收 {"userId": 1, "userName": "a"} → 模型用 user_id / user_name
UserOut.model_validate({"userId": 1, "userName": "a"})

# 输出时用别名
UserOut(user_id=1, user_name="a").model_dump(by_alias=True)
# → {"userId": 1, "userName": "a"}


# ===== 6. Discriminated Union（多态请求体）=====
class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow: int


class Dog(BaseModel):
    pet_type: Literal["dog"]
    woof: str


Pet = Annotated[Union[Cat, Dog], Field(discriminator="pet_type")]


def parse_pet(data: dict):
    """根据 pet_type 字段自动选 Cat 或 Dog。"""
    from pydantic import TypeAdapter

    adapter = TypeAdapter(Pet)
    return adapter.validate_python(data)


parse_pet({"pet_type": "cat", "meow": 3})   # → Cat(meow=3)
parse_pet({"pet_type": "dog", "woof": "hi"})  # → Dog(woof="hi")


# ===== 7. 序列化模式对比 =====
u = User(id=1, name="alice", email="alice@example.com", registered_at=datetime.now())

u.model_dump()                # 原生 Python 对象（datetime 仍是 datetime）
u.model_dump(mode="json")     # JSON 友好（datetime → ISO 字符串）
u.model_dump_json()           # 直接出 JSON 字符串
