"""
Redis 键设计模板示例。

演示：
- 7 种典型场景的 key 模板（缓存 / Session / 限流 / 分布式锁 / 计数器 / Stream / Pub-Sub）
- Cluster Hash Tag `{...}` 用法（强制同 slot）
- 限流的 INCR + EXPIRE 原子化（pipeline）
- 分布式锁的安全释放（Lua 脚本）

对应笔记：[[Hub/05_数据库设计相关笔记]]

注意：本文件演示 key 构造模式与 Lua 脚本逻辑；
如要实跑，需要 redis 服务或 fakeredis：
    uv pip install --python workspace/.venv/bin/python redis fakeredis
"""

from __future__ import annotations

import uuid

# ============================================================
# 通用 key 模板（字符串拼接，避免散落在代码各处）
# ============================================================

def cache_user_profile(user_id: int) -> str:
    """缓存：cache:user:profile:{id}"""
    return f"cache:user:profile:{user_id}"

def session_key(session_id: str) -> str:
    """Session：sess:{sessionId}"""
    return f"sess:{session_id}"

def rate_limit_key(user_id: int, window: str = "1m") -> str:
    """
    限流：ratelimit:{userId}:window
    注意大括号包 userId，确保同用户的所有窗口 key 落到同一 slot
    （这样可以用 MGET 一次拿多个窗口的计数）
    """
    return f"ratelimit:{{{user_id}}}:{window}"

def distributed_lock_key(resource: str, resource_id: int | str) -> str:
    """分布式锁：lock:resource:{id}"""
    return f"lock:{resource}:{resource_id}"

def counter_key(scene: str, obj_id: int | str) -> str:
    """计数器：counter:{scene}:{id}"""
    return f"counter:{scene}:{obj_id}"

def stream_key(topic: str) -> str:
    """Stream：stream:events:{topic}"""
    return f"stream:events:{topic}"

def pubsub_channel(user_id: int) -> str:
    """Pub/Sub channel：channel:notifications:{userId}"""
    return f"channel:notifications:{{{user_id}}}"


# ============================================================
# 限流：INCR + EXPIRE 原子化（pipeline 或 Lua）
# ============================================================

RATE_LIMIT_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

# 用 Lua 脚本保证原子性；pipeline 在多数客户端是非原子的
# redis.register_script(RATE_LIMIT_LUA)
#
# def is_rate_limited(redis, user_id: int, limit: int, window_sec: int) -> bool:
#     key = rate_limit_key(user_id, "1m")
#     count = redis.eval(RATE_LIMIT_LUA, 1, key, window_sec)
#     return count > limit


# ============================================================
# 分布式锁：安全释放（Lua 脚本，保证「只删自己持有的锁」）
# ============================================================

LOCK_RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
"""

# def acquire_lock(redis, key: str, ttl_sec: int = 10) -> str | None:
#     token = uuid.uuid4().hex
#     ok = redis.set(key, token, nx=True, ex=ttl_sec)
#     return token if ok else None
#
# def release_lock(redis, key: str, token: str) -> bool:
#     # 用 Lua 保证「校验 + 删除」原子化，避免误删别人的锁
#     result = redis.eval(LOCK_RELEASE_LUA, 1, key, token)
#     return result == 1


# ============================================================
# Cluster Hash Tag 演示（逻辑示意）
# ============================================================

def demo_hash_tag_concept() -> None:
    """
    Redis Cluster 的 key 分 slot 演示（不需要真连 Redis）。

    规则：只 hash 第一个 {..} 之间的内容
        - user:1000:profile         → hash 整个 key
        - user:{1000}:profile       → hash "1000"
        - foo{{bar}}zap             → hash "{bar}zap"（第一个 {...}）
        - {}（空 hash tag）         → hash 整个 key（不生效）

    多 key 必须在同一 slot 才能用 MGET / MSET / 事务 / Lua：
        ❌ MGET user:1000:profile user:1000:settings  → CROSSSLOT error
        ✅ MGET user:{1000}:profile user:{1000}:settings → OK

    反例（热点 shard）：
        ❌ 所有 key 都加 {global} → 整个集群流量集中到一个 shard
    """


# ============================================================
# 演示输出
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Redis Key 模板示例")
    print("=" * 60)

    examples = [
        ("缓存",            cache_user_profile(1000)),
        ("Session",         session_key("abc123def456")),
        ("限流",            rate_limit_key(1000, "1m")),
        ("限流（5min）",     rate_limit_key(1000, "5m")),
        ("分布式锁",        distributed_lock_key("order", 5678)),
        ("计数器",          counter_key("views", "homepage")),
        ("Stream",          stream_key("order_created")),
        ("Pub/Sub channel", pubsub_channel(1000)),
    ]
    for name, key in examples:
        print(f"  {name:20s} → {key}")

    print()
    print("=" * 60)
    print("Cluster Hash Tag 规则速查")
    print("=" * 60)
    print("  user:1000:profile          → hash 整个 key (默认)")
    print("  user:{1000}:profile        → hash '1000' (强制同 slot)")
    print("  foo{{bar}}zap        → hash '{bar}zap' (只识别第一对)")
    print("  {}                         → 不生效，hash 整个 key")
    print()
    print("禁忌：所有 key 都用 {global} → 热点 shard，集群退化为单机")