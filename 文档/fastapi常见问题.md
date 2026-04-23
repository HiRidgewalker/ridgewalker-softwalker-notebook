1、接口定义的dto模型类，什么时候前端必须把这个值传递过来，什么时候前端不必把这个值传递过来

```python
class AuthSchemaBase(SchemaBase):
    username: str
    password: str | None
```

像这样，虽然password定义为空，但是必须传递值过来，不管传递的是str还是None

```python
class AuthSchemaBase(SchemaBase):
    username: str
    password: str | None = None
```

像这样，password具有默认值，就可以不必传值过来

