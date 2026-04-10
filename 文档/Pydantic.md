模型类的 ConfigDict 类
from pydantic import ConfigDict

# ConfigDict：用于定义 Pydantic 模型的全局配置（校验、序列化、行为控制等）

```python
model_config = ConfigDict(
    populate_by_name=True,      # 允许通过字段名或别名赋值
    str_strip_whitespace=True,  # 自动去除字符串首尾空格
    extra="forbid",             # 禁止传入未定义字段（ignore/allow/forbid）

    frozen=False,               # 是否不可变（True=类似只读对象）
    validate_assignment=True,   # 修改字段时也进行校验
    arbitrary_types_allowed=True,  # 允许使用任意自定义类型

    use_enum_values=True,       # 使用 enum 的 value 而不是枚举对象
    from_attributes=True,       # 支持从对象属性读取数据（ORM 模式）

    json_schema_extra={},       # 自定义 JSON schema 扩展
    ser_json_timedelta="iso8601",  # timedelta 序列化格式
)


```


Pydantic 常用的数据类型
常用数据类型（Pydantic / Python）：

- `int`：整数
- `float`：浮点数
- `str`：字符串
- `bool`：布尔值
- `list` / `List[T]`：列表
- `dict` / `Dict[K, V]`：字典
- `tuple`：元组
- `set`：集合
- `datetime` / `date` / `time`：时间类型
- `Decimal`：高精度数值
- `UUID`：唯一标识
- `Enum`：枚举
- `Optional[T]`：可选值（可为 None）
- `Union[T1, T2]`：多类型
- `Any`：任意类型 
- `EmailStr`：邮箱
- `NameEmail`：姓名+邮箱
- `AnyUrl` / `HttpUrl`：URL
- `IPvAnyAddress`：IP地址
- `UUID1/3/4/5`：UUID
- `SecretStr` / `SecretBytes`：敏感信息
- `PositiveInt` / `NegativeInt`：正/负整数
- `conint` / `constr` / `confloat`：约束类型
- `PaymentCardNumber`：银行卡号
- `Color`：颜色值

Field 类
```python
from pydantic import Field

# Field：用于给模型字段添加元数据与校验规则（默认值、约束、描述等）

name: str = Field(
    ...,                  # 必填字段（无默认值）
    title="Name",         # 字段标题（schema 用）
    description="用户名",   # 字段描述
    min_length=1,         # 最小长度（字符串）
    max_length=50,        # 最大长度
    regex=r"^\w+$",       # 正则校验
    example="john_doe",   # 示例值（文档用）
)

age: int = Field(
    18,                   # 默认值
    ge=0,                 # >= 0
    le=120,               # <= 120
)

price: float = Field(
    ..., 
    gt=0,                 # > 0
    lt=10000,             # < 10000
)

tags: list[str] = Field(
    default_factory=list, # 默认工厂（避免可变对象共享）
)

alias_field: str = Field(
    ..., 
    alias="user_name",    # 别名（外部字段名）
)

status: str = Field(
    ..., 
    deprecated=True,      # 标记字段已废弃
)

secret: str = Field(
    ..., 
    repr=False,           # 不在 repr() 中显示
)
```

