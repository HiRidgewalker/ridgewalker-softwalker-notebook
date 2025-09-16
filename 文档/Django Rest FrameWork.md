# DRF常见约束
>[!info]+
>注意: 序列化和反序列化是相对与json数据而言

## 通用约束参数（所有字段类型都支持）
### 基础约束
```python
field = serializers.CharField(
    # 是否必填
    required=True,          # 默认True，反序列化时必须提供
    allow_null=False,       # 默认False，是否允许None值
    allow_blank=False,      # 默认False，是否允许空字符串（仅字符串字段）
    
    # 默认值
    default=serializers.empty,  # 字段默认值
    initial=None,          # 表单初始值
    
    # 读写控制
    read_only=False,       # 默认False，是否只读
    write_only=False,      # 默认False，是否只写
    
    # 错误消息
    error_messages=None,   # 自定义错误消息字典
    
    # 其他
    source='*',           # 数据源字段名
    validators=[],        # 自定义验证器列表
    style={},            # 渲染样式
    label=None,          # 字段标签
    help_text='',        # 帮助文本
)
```

## 字符串字段约束
### CharField
```python
name = serializers.CharField(
    max_length=100,        # 最大长度
    min_length=1,          # 最小长度
    allow_blank=False,     # 是否允许空字符串
    trim_whitespace=True,  # 是否去除首尾空白
)
```

### EmailField
```python
email = serializers.EmailField(
    max_length=254,        # 继承CharField的长度约束
    # 自动验证邮箱格式
)
```

### URLField
```python
website = serializers.URLField(
    max_length=200,        # URL最大长度
    # 自动验证URL格式
)
```

## 数值字段约束
### IntegerField
```python
age = serializers.IntegerField(
    max_value=150,         # 最大值
    min_value=0,           # 最小值
)
```

### FloatField
```python
price = serializers.FloatField(
    max_value=9999.99,     # 最大值
    min_value=0.01,        # 最小值
)
```

### DecimalField
```python
amount = serializers.DecimalField(
    max_digits=10,         # 总位数
    decimal_places=2,      # 小数位数
    max_value=999999.99,   # 最大值
    min_value=0,           # 最小值
    coerce_to_string=True, # 是否转为字符串输出
)
```

## 日期时间字段约束
### DateTimeField
```python
created_at = serializers.DateTimeField(
    format='%Y-%m-%d %H:%M:%S',  # 格式化字符串
    input_formats=['iso-8601'],   # 输入格式列表
)
```

### DateField
```python
birth_date = serializers.DateField(
    format='%Y-%m-%d',     # 输出格式
    input_formats=['%Y-%m-%d', '%m/%d/%Y'],  # 输入格式
)
```

## 选择字段约束
### ChoiceField
```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
]

status = serializers.ChoiceField(
    choices=STATUS_CHOICES,    # 选择项
    allow_blank=False,         # 是否允许空值
)
```

### MultipleChoiceField
```python
tags = serializers.MultipleChoiceField(
    choices=TAG_CHOICES,
    allow_empty=False,         # 是否允许空列表
)
```

## 列表字段约束
### ListField
```python
items = serializers.ListField(
    child=serializers.CharField(max_length=100),  # 子字段类型 可以传递 也可以不传递
    min_length=1,              # 列表最小长度
    max_length=10,             # 列表最大长度
    allow_empty=False,         # 是否允许空列表
)
```

## 文件字段约束
### FileField
```python
document = serializers.FileField(
    max_length=100,            # 文件名最大长度
    allow_empty_file=False,    # 是否允许空文件
    use_url=True,              # 是否返回URL
)
```

### ImageField
```python
avatar = serializers.ImageField(
    max_length=100,            # 文件名最大长度
    allow_empty_file=False,    # 是否允许空文件
    use_url=True,              # 是否返回URL
    # 自动验证图片格式
)
```

## 布尔字段约束
### BooleanField
```python
is_active = serializers.BooleanField(
    # 只接受 True/False，不允许None
)
```

### NullBooleanField
```python
is_verified = serializers.NullBooleanField(
    # 接受 True/False/None
)
```

## 实际使用示例
```python
class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=3,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    age = serializers.IntegerField(
        min_value=13,
        max_value=120,
        required=False
    )
    
    bio = serializers.CharField(
        max_length=500,
        allow_blank=True,
        required=False
    )
    
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50),
        max_length=10,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'age', 'bio', 'skills']
```

## 常见约束组合模式
```python
# 必填且不能为空
required_field = serializers.CharField(required=True, allow_blank=False)

# 可选但不能为空字符串
optional_field = serializers.CharField(required=False, allow_blank=False)

# 可选且可以为空
nullable_field = serializers.CharField(required=False, allow_blank=True)

# 只读字段
readonly_field = serializers.CharField(read_only=True)

# 只写字段（如密码）
writeonly_field = serializers.CharField(write_only=True)
```

## DRF函数调用链详解
**序列化访问data属性的调用链:**
![[image-11.png]]

**反序列化访问validated_data属性的方法调用链**
![[image-12.png]]

注意，上述方法所需参数，有的是单个字段，有的是一个对象：
```python
class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()

    def validate_username(self, value):
        # 针对单个字段的验证（value是字段的值）
        print(f"value type: {type(value)}")
        print(f"value: {value}")
        return value

    def validate(self, attrs):
        # 针对整个反序列化数据的验证（attrs是dict）
        print(f"attrs type: {type(attrs)}")
        print(f"attrs value: {attrs}")
        return attrs

    def to_internal_value(self, data):
        # 反序列化：把原始输入 data -> Python 内部字典（validated_data 的来源）
        print("反序列化")
        print(f"type: {type(data)}")
        return super().to_internal_value(data)   # 建议调用父类方法

    def to_representation(self, instance):
        # 序列化：把 instance -> Python 原生类型（JSON化前的dict）
        print("序列化")
        print(f"type: {type(instance)}")
        ret = super().to_representation(instance)  # 建议调用父类方法
        # 可以在这里做额外字段加工
        ret["extra_field"] = "hello world"
        return ret

    def get_full_name(self, obj):
        # 自定义字段方法（常和 SerializerMethodField 配合）
        return f"{obj.username} ({obj.email})"
```

注意，模型类重写有的方法后需要显式的调用父类对应方法:
### 哪些方法需要调用父类方法？
#### 1. **字段级验证**

- `validate_<fieldname>(self, value)` 👉 不需要调用父类方法。因为父类里默认没实现字段验证逻辑，你直接返回 `value` 或者 raise `ValidationError` 就行。
#### 2. **全局验证**
- `validate(self, attrs)` 👉 同样不需要调用父类方法。父类就是个空壳，没逻辑。你直接在 `attrs` 上做检查并返回即可。
#### 3. **反序列化**
- `to_internal_value(self, data)` 👉 通常需要调用 `super().to_internal_value(data)`，否则 DRF 内部的字段校验（比如 `CharField` 的长度、`EmailField` 的格式检查）不会执行。 你可以在调用前后加打印、改数据，但主体逻辑建议交给父类。
#### 4. **序列化**
- `to_representation(self, instance)` 👉 同样建议调用 `super().to_representation(instance)`，否则 DRF 不会帮你把字段序列化成 dict。 你可以在 `ret = super()` 的结果上做加工，比如添加额外字段、删除敏感字段。
#### 5. **自定义字段**
- `get_<fieldname>(self, obj)` 👉 通常和 `SerializerMethodField` 一起用。例如：
```python
    full_name_display = serializers.SerializerMethodField()  
    ​  
    def get_full_name_display(self, obj):  
        return f"{obj.full_name} ({obj.email})"
```
👉 这个方法不需要调用父类方法，因为逻辑全是你自己定义。
#### 总结表格 ✅
| 方法名                   | 参数          | 是否需要 `super()` |
| --------------------- | ----------- | -------------- |
| `validate_<field>()`  | 单个字段值       | ❌ 不需要          |
| `validate()`          | 整个数据 dict   | ❌ 不需要          |
| `to_internal_value()` | 输入数据 data   | ✅ 建议调用         |
| `to_representation()` | instance 对象 | ✅ 建议调用         |
| `get_<field>()`       | instance 对象 | ❌ 不需要          |
