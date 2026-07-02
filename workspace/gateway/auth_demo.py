"""
鉴权 demo：JWT 双 Token + Casbin 权限检查。

演示（对应 [[Hub/鉴权与登录笔记]] §9 + [[Hub/权限模型笔记]] §10）：
- 账号密码登录 → 颁发 access + refresh 双 token
- refresh 换新双 token
- 撤销 refresh（jti 黑名单）
- Casbin RBAC enforce 检查（结合 role 继承 + RESTful 路径）

运行：
    # 1. 颁发 alice 的 token
    .venv/bin/python workspace/gateway/auth_demo.py issue alice

    # 2. 验证 token
    .venv/bin/python workspace/gateway/auth_demo.py verify <token>

    # 3. 撤销
    .venv/bin/python workspace/gateway/auth_demo.py revoke <jti>

    # 4. Casbin enforce（带角色继承 + RESTful 路径）
    .venv/bin/python workspace/gateway/auth_demo.py enforce alice /api/users/123 GET
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import casbin
import jwt

# ============================================================
# 配置（必须与 gateway.py 一致）
# ============================================================
SECRET = os.environ.get("JWT_SECRET", "demo-secret-please-change-in-prod")
ALG = "HS256"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=7)

# 模拟用户库（生产用 DB）
USERS = {
    "alice": {"password": "alice_pwd", "sub": "alice", "roles": ["member"]},
    "bob":   {"password": "bob_pwd",   "sub": "bob",   "roles": ["member"]},
    "carol": {"password": "carol_pwd", "sub": "carol", "roles": ["member"]},
}


# ============================================================
# JWT 双 Token（生产用 Redis 存 jti 活跃列表；这里用 dict 模拟）
# ============================================================
ACTIVE_REFRESH: dict[str, str] = {}          # jti -> sub


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def login(username: str, password: str) -> dict | None:
    """账号密码登录，返回 {access_token, refresh_token} 或 None。"""
    user = USERS.get(username)
    if not user or user["password"] != password:
        return None
    return issue_tokens(user["sub"], extra={"roles": user["roles"]})


def issue_tokens(sub: str, extra: dict | None = None) -> dict:
    """签发 access + refresh 双 token。"""
    base = {"sub": sub, "iat": _now()}
    if extra:
        base.update(extra)

    access_jti = str(uuid.uuid4())
    access = jwt.encode(
        {**base, "jti": access_jti,
         "exp": _now() + ACCESS_TTL, "type": "access"},
        SECRET, algorithm=ALG,
    )

    refresh_jti = str(uuid.uuid4())
    refresh = jwt.encode(
        {**base, "jti": refresh_jti,
         "exp": _now() + REFRESH_TTL, "type": "refresh"},
        SECRET, algorithm=ALG,
    )
    ACTIVE_REFRESH[refresh_jti] = sub

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": int(ACCESS_TTL.total_seconds()),
    }


def refresh(refresh_token: str) -> dict | None:
    """refresh 换新双 token（旧 refresh 立即失效）。"""
    try:
        payload = jwt.decode(refresh_token, SECRET, algorithms=[ALG])
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "refresh":
        return None
    jti = payload.get("jti")
    if jti not in ACTIVE_REFRESH:
        return None                          # 已被撤销

    ACTIVE_REFRESH.pop(jti, None)            # 撤销旧 refresh
    return issue_tokens(
        payload["sub"],
        extra={"roles": payload.get("roles", [])},
    )


def revoke(jti: str) -> None:
    """撤销 refresh token（jti 黑名单）。"""
    ACTIVE_REFRESH.pop(jti, None)


def verify(token: str) -> dict | None:
    """校验 access token，返回 payload。"""
    try:
        return jwt.decode(
            token, SECRET, algorithms=[ALG],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None


# ============================================================
# Casbin 权限检查（对应 [[Hub/权限模型笔记]] §6）
# ============================================================
_ENFORCER: casbin.Enforcer | None = None


def get_enforcer() -> casbin.Enforcer:
    global _ENFORCER
    if _ENFORCER is None:
        here = os.path.dirname(os.path.abspath(__file__))
        _ENFORCER = casbin.Enforcer(
            os.path.join(here, "policy", "model.conf"),
            os.path.join(here, "policy", "policy.csv"),
        )
    return _ENFORCER


def check_permission(sub: str, obj: str, act: str) -> bool:
    """Casbin enforce：含角色继承 + RESTful 路径匹配。"""
    return get_enforcer().enforce(sub, obj, act)


# ============================================================
# CLI
# ============================================================
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "issue":
        # issue alice
        username = sys.argv[2] if len(sys.argv) > 2 else "alice"
        # demo 直接签发，不校验密码
        tokens = issue_tokens(username, extra={"roles": ["member"]})
        print(f"ACCESS_TOKEN={tokens['access_token']}")
        print(f"REFRESH_TOKEN={tokens['refresh_token']}")
        return

    if cmd == "login":
        # login alice alice_pwd
        username = sys.argv[2]
        password = sys.argv[3]
        tokens = login(username, password)
        if not tokens:
            print("login failed")
            sys.exit(1)
        print(f"ACCESS_TOKEN={tokens['access_token']}")
        print(f"REFRESH_TOKEN={tokens['refresh_token']}")
        return

    if cmd == "verify":
        token = sys.argv[2]
        payload = verify(token)
        if payload is None:
            print("INVALID")
            sys.exit(1)
        print(f"VALID: sub={payload['sub']} roles={payload.get('roles')}")
        return

    if cmd == "revoke":
        jti = sys.argv[2]
        revoke(jti)
        print(f"revoked {jti}")
        return

    if cmd == "enforce":
        # enforce alice /api/users/123 GET
        sub = sys.argv[2]
        obj = sys.argv[3]
        act = sys.argv[4]
        ok = check_permission(sub, obj, act)
        print(f"{'ALLOW' if ok else 'DENY'} {sub} {act} {obj}")
        sys.exit(0 if ok else 1)

    print(f"unknown command: {cmd}")
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()