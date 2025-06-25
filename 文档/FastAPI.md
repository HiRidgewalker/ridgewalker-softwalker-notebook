document: [fastapi在线文档](https://fastapi.tiangolo.com/zh/)
第三方： [[Pydantic]]
## fastapi函数参数识别规则
- **路径**中声明了相同参数的参数，是路径参数
- 类型是（`int`、`float`、`str`、`bool` 等）**单类型**的参数，是**查询**参数
- 类型是 **Pydantic 模型**的参数，是**请求体**

## 数据校验
### 查询数据校验
> Query()

 你可以为查询参数声明额外的校验和元数据。
通用的校验和元数据：
- `alias`
- `title`
- `description`
- `deprecated`
特定于字符串的校验：
- `min_length`
- `max_length`
- `regex`

### 路径参数校验
>Path()

你能够以与**查询参数和字符串校验**相同的方式使用 `Query`、`Path`（以及其他你还没见过的类）声明元数据和字符串校验。

而且你还可以声明数值校验：

- `gt`：大于（`g`reater `t`han）
- `ge`：大于等于（`g`reater than or `e`qual）
- `lt`：小于（`l`ess `t`han）
- `le`：小于等于（`l`ess than or `e`qual）

### 请求体参数校验
> Body()

## fastapi请求体各种常见类别处理方式

[请求体-多个参数](https://fastapi.tiangolo.com/zh/tutorial/body-multiple-params/#_2)

