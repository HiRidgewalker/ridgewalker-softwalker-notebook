---
title: "权限模型笔记"
date: 2026-11-06
tags: ["FastAPI","鉴权"]
---

# 权限模型笔记

> 原 旧稿（RBAC / ABAC / ReBAC 三模型对比）的重写。
> 原笔记是定性对比，本笔记在此基础上**补充 Casbin 库的落地实现**（Python 版 PERM 模型、policy 文件、FastAPI 集成、RBAC with Domains、ReBAC 关系建模），让模型能真正用起来。
>
> 登录与鉴权流程见 `[[鉴权与登录笔记]]`。
> 网关中的鉴权中间件见 `[[API网关原理与选型笔记]]`。

## 目录

1. 三模型对比（RBAC / ReBAC / ABAC）
2. RBAC 模型详解
3. ReBAC 模型详解
4. ABAC 模型简述
5. Casbin 库核心（Python 版）
6. RBAC 最小可运行示例（含角色继承）
7. RBAC with Domains（多租户）
8. ReBAC 关系建模（Casbin g2）
9. RESTful 路径权限检查（keyMatch2）
10. Casbin 在 FastAPI 中集成
11. 实战：RBAC + ReBAC 混合

---

## 1. 三模型对比（RBAC / ReBAC / ABAC）

| 模型 | 一句话 | 典型问题 | 典型场景 |
|---|---|---|---|
| **RBAC** | 你**是什么身份** | 你是不是管理员？ | 后台菜单 / 按钮权限 / 组织架构 |
| **ReBAC** | 你**和它什么关系** | 你是这个文档的 owner 吗？ | 协作 / 项目 / 社交 |
| **ABAC** | 你**满足什么条件** | 你是不是这个部门 + 当前是工作时间？ | 数据权限 / 部门隔离 / 时段限制 |

**口诀**：

- RBAC → **身份 / 角色**
- ReBAC → **关系 / 邻居**
- ABAC → **属性 / 规则**

**现实项目里很少只用一种**：

| 场景 | 组合 |
|---|---|
| 企业后台 | RBAC（菜单/按钮） + ABAC（数据范围） |
| 多租户协作 | RBAC（平台角色） + ReBAC（项目成员） |
| 复杂 SaaS | RBAC + ABAC + ReBAC 三者混合 |

---

## 2. RBAC 模型详解

### 2.1 三层结构

```
用户 ──绑定──► 角色 ──绑定──► 权限

Alice ──► admin ──► [删除用户, 管理订单, 查看报表]
Bob   ──► editor ──► [创建文章, 修改文章]
Tom   ──► viewer ──► [查看文章]
```

### 2.2 角色继承

```
admin ──继承──► user
editor ──继承──► user
```

`admin` 自动拥有 `user` 的所有权限，不必重复配置。

### 2.3 为什么 RBAC 是后台系统的默认选择

- **管理简单**：权限挂在角色上，增删用户不动权限
- **符合直觉**：组织架构天然是角色化（部门 / 职位）
- **实现成本低**：一张 user_role 表 + 一张 role_permission 表就够

### 2.4 RBAC 不擅长什么

```text
editor 可以修改文章
```

但具体能改哪些文章？RBAC 答不了：

- 所有文章？
- 自己部门的？
- 自己创建的？

**答不了就走 ReBAC 或 ABAC**（见下文）。

---

## 3. ReBAC 模型详解

### 3.1 核心思想

**权限不是由角色或属性决定，而是由"用户和资源之间的关系"决定。**

```
Alice ──[owner]──► doc_123
Bob   ──[editor]──► doc_123
Carol ──[viewer]──► doc_123

Alice ──[member]──► team_A
team_A ──[owns]──► project_X
project_X ──[contains]──► doc_123
        ↓ 推导
Alice ──[viewer (继承)]──► doc_123   (因为她是 team_A 成员)
```

### 3.2 ReBAC 的直觉理解

| 模型 | 问的问题 |
|---|---|
| RBAC | 你是谁？ |
| ABAC | 你有哪些特征？ |
| ReBAC | **你和这个对象是什么关系？** |

### 3.3 典型 ReBAC 场景

| 场景 | 关系 |
|---|---|
| 协作文档 | owner / editor / viewer |
| GitHub 仓库 | member / outside-collaborator |
| Notion / 飞书 | workspace member + page permission |
| 社交 | friend / follower / blocked |
| 项目 | team member / project owner / approver |

### 3.4 ReBAC 的"关系链推导"

```
用户 --[member]--> 团队
团队 --[owns]--> 项目
项目 --[contains]--> 仓库

        ↓ 推导
用户对该仓库有 [member] 权限
```

这种"从关系图推导权限"是 ReBAC 的核心特点，也是它实现起来比 RBAC 复杂的地方。

---

## 4. ABAC 模型简述

ABAC 通过**属性规则**动态判断：

```text
IF user.department == resource.department
   AND user.level >= 2
   AND action == "read"
THEN allow
```

**四类属性**：

- **用户属性**：部门 / 岗位 / 级别 / 地区
- **资源属性**：创建人 / 所属部门 / 敏感等级 / 状态
- **操作属性**：read / write / approve
- **环境属性**：时间 / IP / 地理位置 / 设备

**适用**：规则复杂多变（金融 / 医疗 / 政务）、需要细粒度条件。

**代价**：规则易膨胀，调试难。所以实际项目通常 RBAC 主导 + ABAC 补充。

---

## 5. Casbin 库核心（Python 版）

[Casbin](https://casbin.apache.org/) 是一个**通用的授权库**，支持多种模型（RBAC / ABAC / ReBAC / RESTful），多种语言（Go / Java / Python / Node.js / PHP）。

**核心思想**：**配置文件定义模型 + 策略文件定义数据**，库帮你做"请求 → 决策"。

### 5.1 PERM 模型（Policy / Effect / Request / Matchers）

任何 Casbin 模型都包含 4 段：

```ini
# 1. 请求定义：用户要做什么请求
[request_definition]
r = sub, obj, act

# 2. 策略定义：一条权限规则是什么样子
[policy_definition]
p = sub, obj, act

# 3. 角色定义（RBAC 用）：用户到角色的映射
[role_definition]
g = _, _

# 4. 匹配器：请求和策略如何匹配（核心规则）
[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act

# 5. 效果：满足策略时的最终决定
[policy_effect]
e = some(where (p.eft == allow))
```

### 5.2 策略文件

```csv
# policy.csv
p, alice, data1, read
p, bob, data2, write
p, data2_admin, data2, read
p, data2_admin, data2, write

g, alice, data2_admin        # alice 继承 data2_admin 的所有权限
```

### 5.3 Python API 速查

```python
import casbin

e = casbin.Enforcer("model.conf", "policy.csv")

# 鉴权（核心）
e.enforce("alice", "data1", "read")       # True（直接策略）
e.enforce("alice", "data2", "write")      # True（通过 g 继承）
e.enforce("bob", "data1", "read")         # False

# 运行时增删策略
e.add_policy("eve", "data3", "read")
e.remove_policy("eve", "data3", "read")

# 角色绑定
e.add_grouping_policy("alice", "data2_admin")
e.remove_grouping_policy("alice", "data2_admin")
e.get_roles_for_user("alice")             # ["data2_admin"]
e.get_implicit_roles_for_user("alice")    # 含继承传递
e.get_users_for_role("data2_admin")       # ["alice"]

# 持久化
e.save_policy()                            # 写回 adapter
```

### 5.4 Adapter 选型

| Adapter | 适用 |
|---|---|
| `FileAdapter`（CSV） | demo / 小项目 |
| `casbin-sqlalchemy-adapter` | 关系型数据库（推荐生产） |
| `casbin-redis-adapter` | 高频读 + 集群 |
| `casbin-mongodb-adapter` | 文档型场景 |

```python
# SQLAlchemy adapter 用法
from casbin_sqlalchemy_adapter import Adapter
import casbin

adapter = Adapter("postgresql://user:pass@host/db")
e = casbin.Enforcer("model.conf", adapter)
e.load_policy()  # 从 DB 加载
```

---

## 6. RBAC 最小可运行示例（含角色继承）

### 6.1 `model.conf`

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

### 6.2 `policy.csv`

```csv
p, alice, data1, read
p, bob, data2, write
p, data2_admin, data2, read
p, data2_admin, data2, write

g, alice, data2_admin
```

### 6.3 验证

```python
import casbin
e = casbin.Enforcer("model.conf", "policy.csv")

e.enforce("alice", "data1", "read")     # True（直接）
e.enforce("alice", "data2", "write")    # True（继承自 data2_admin）
e.enforce("bob", "data2", "write")      # True（直接）
e.enforce("bob", "data1", "read")       # False
```

---

## 7. RBAC with Domains（多租户）

**问题**：同一用户在**不同租户**有不同角色（如：Alice 在公司 A 是 admin，在公司 B 只是 user）。

### 7.1 model.conf（域扩展）

```ini
[request_definition]
r = sub, dom, obj, act

[policy_definition]
p = sub, dom, obj, act

[role_definition]
g = _, _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub, r.dom) && r.dom == p.dom && r.obj == p.obj && r.act == p.act
```

### 7.2 policy.csv

```csv
p, admin, tenant1, data1, read
p, admin, tenant2, data2, read
p, user, tenant2, data2, read

g, alice, admin, tenant1
g, alice, user, tenant2
g, bob, user, tenant2
```

### 7.3 验证

```python
e.enforce("alice", "tenant1", "data1", "read")   # True（admin@tenant1）
e.enforce("alice", "tenant2", "data2", "read")   # True（user@tenant2）
e.enforce("alice", "tenant2", "data1", "read")   # False（tenant1 的 admin 不跨租户）
e.enforce("bob", "tenant1", "data1", "read")     # False（bob 不是 tenant1 成员）
```

---

## 8. ReBAC 关系建模（Casbin g2）

Casbin 默认 `g` 是用户-角色继承；**`g2` 用于角色-角色继承**，但更常见的用法是**用 g 模拟"对象-关系"**。

### 8.1 思路：把"关系"建模为 policy

```csv
# 用户与资源的关系
p, doc_owner, doc_123, read
p, doc_owner, doc_123, write
p, doc_owner, doc_123, delete
p, doc_editor, doc_123, read
p, doc_editor, doc_123, write
p, doc_viewer, doc_123, read

# 谁是什么关系
g, alice, doc_owner, doc_123
g, bob, doc_editor, doc_123
g, carol, doc_viewer, doc_123
```

### 8.2 model.conf

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _, _        # 用户, 关系角色, 资源

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub, r.obj) && r.obj == p.obj && r.act == p.act
```

### 8.3 验证

```python
e.enforce("alice", "doc_123", "delete")   # True（owner）
e.enforce("bob", "doc_123", "write")      # True（editor）
e.enforce("carol", "doc_123", "read")     # True（viewer）
e.enforce("carol", "doc_123", "write")    # False
```

> 生产环境关系数量爆炸（每个文档 × 3 种关系），需要把关系存数据库（adapter），
> 不要写 CSV 文件。

---

## 9. RESTful 路径权限检查（keyMatch2）

**场景**：权限按 URL 路径 + HTTP 方法控制（如 `alice` 能访问 `/api/users/*` GET，admin 能访问 `/api/*` 任意方法）。

### 9.1 model.conf

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && keyMatch2(r.obj, p.obj) && (r.act == p.act || r.act == "ANY")
```

### 9.2 policy.csv

```csv
p, alice, /api/users/*, GET
p, bob, /api/orders/*, GET
p, admin, /api/*, ANY

g, alice, admin                # alice 继承 admin 所有权限
```

### 9.3 验证

```python
e.enforce("alice", "/api/users/123", "GET")     # True
e.enforce("alice", "/api/orders/1", "GET")      # True（admin 继承）
e.enforce("bob", "/api/users/123", "GET")       # False
e.enforce("admin", "/api/anything", "DELETE")   # True（ANY）
```

`keyMatch2` 支持的路径模式：

- `/foo/:id` 匹配 `/foo/123`
- `/foo/*` 匹配 `/foo/anything/more`

---

## 10. Casbin 在 FastAPI 中集成

### 10.1 单例 Enforcer

```python
# deps.py
import casbin
from functools import lru_cache

@lru_cache()
def get_enforcer() -> casbin.Enforcer:
    return casbin.Enforcer("policy/model.conf", "policy/policy.csv")

# 用 SQLAlchemy adapter
# from casbin_sqlalchemy_adapter import Adapter
# @lru_cache()
# def get_enforcer():
#     adapter = Adapter("sqlite:///casbin.db")
#     return casbin.Enforcer("policy/model.conf", adapter)
```

### 10.2 依赖链：先鉴权（JWT）→ 再鉴权（Casbin）

```python
# main.py
from fastapi import Depends, FastAPI, HTTPException
from deps import get_enforcer
from auth import get_current_user          # 见 [[鉴权与登录笔记]]

app = FastAPI()
enforcer = get_enforcer()


def check_permission(sub: str, obj: str, act: str):
    if not enforcer.enforce(sub, obj, act):
        raise HTTPException(403, "Forbidden")


@app.get("/api/users/{user_id}")
def get_user(
    user_id: int,
    user: dict = Depends(get_current_user),
):
    check_permission(user["sub"], f"/api/users/{user_id}", "GET")
    return {"user_id": user_id}


@app.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    user: dict = Depends(get_current_user),
):
    check_permission(user["sub"], f"/api/users/{user_id}", "DELETE")
    # ... 业务逻辑
    return {"deleted": user_id}
```

### 10.3 多租户 Casbin

```python
def check_permission_with_tenant(sub: str, tenant: str, obj: str, act: str):
    if not enforcer.enforce(sub, tenant, obj, act):     # 见 §7 模型
        raise HTTPException(403, "Forbidden")
```

---

## 11. 实战：RBAC + ReBAC 混合

### 11.1 场景

某 SaaS 平台：

- 平台层面：用户有 **admin / member** 角色（RBAC）
- 项目层面：用户与项目有 **owner / collaborator / viewer** 关系（ReBAC）

### 11.2 model.conf（同时定义 RBAC 和 ReBAC）

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _                    # RBAC: 用户 - 平台角色
g2 = _, _, _                # ReBAC: 用户 - 资源关系 - 资源 ID

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = (g(r.sub, p.sub) || g2(r.sub, p.sub, r.obj)) \
    && r.obj == p.obj \
    && r.act == p.act
```

> 含义：用户要么通过平台角色（RBAC）要么通过资源关系（ReBAC）满足权限。

### 11.3 policy.csv

```csv
# RBAC: 平台角色权限
p, admin, /api/projects/*, ANY
p, member, /api/projects/*, GET

# ReBAC: 项目关系 → 项目权限
p, owner, /api/projects/proj_123, ANY
p, collaborator, /api/projects/proj_123, GET
p, collaborator, /api/projects/proj_123, POST
p, viewer, /api/projects/proj_123, GET

# 平台角色绑定
g, alice, admin

# ReBAC 关系绑定
g2, alice, owner, proj_123
g2, bob, collaborator, proj_123
g2, carol, viewer, proj_123
```

### 11.4 验证

```python
# alice 是 admin，能操作任何项目
e.enforce("alice", "/api/projects/proj_123", "DELETE")   # True（admin）
e.enforce("alice", "/api/projects/proj_999", "POST")     # True（admin）

# bob 是 proj_123 的 collaborator
e.enforce("bob", "/api/projects/proj_123", "POST")       # True（collaborator）
e.enforce("bob", "/api/projects/proj_123", "DELETE")     # False（collaborator 没 DELETE）
e.enforce("bob", "/api/projects/proj_999", "GET")        # False（不是 proj_999 成员）
```

---

## 关联笔记

- 登录鉴权流程（拿到用户身份）：`[[鉴权与登录笔记]]`
- 网关（鉴权中间件放哪）：`[[API网关原理与选型笔记]]`
- 数据库设计（角色表 / 权限表怎么设计）：`[[数据库设计与索引优化笔记]]`

## Demo

完整代码：

- [`example/gateway/policy/model.conf`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/gateway/policy/model.conf)
- [`example/gateway/policy/policy.csv`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/gateway/policy/policy.csv)
- [`example/gateway/auth_demo.py`](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/gateway/auth_demo.py)

## Sources

- [Casbin 官方文档（Apache）](https://casbin.apache.org/zh/docs/overview)
- [Casbin RBAC with Domains](https://casbin.apache.org/zh/docs/rbac-with-domains)
- [pycasbin GitHub](https://github.com/casbin/pycasbin)

标签：#fastapi
