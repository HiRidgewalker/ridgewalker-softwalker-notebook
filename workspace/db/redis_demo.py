"""
redis-py demo —— 需要本地 Redis 服务（默认 localhost:6379）。

对应笔记：[[Hub/02_Redis笔记]]
"""
import uuid
import redis

# decode_responses=True 让所有返回都是 str，免去反复 .decode()
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)


def cleanup() -> None:
    """清干净便于反复跑"""
    for key in r.scan_iter(match="demo:*"):
        r.delete(key)


def main() -> None:
    cleanup()

    # 1) string
    r.set("demo:greeting", "hello", ex=60)
    print(f"[string] get = {r.get('demo:greeting')}")
    r.incr("demo:counter")
    r.incrby("demo:counter", 10)
    print(f"[string] counter = {r.get('demo:counter')}")

    # 2) hash
    r.hset("demo:user:1", mapping={"name": "alice", "age": "30"})
    print(f"[hash] hgetall = {r.hgetall('demo:user:1')}")

    # 3) list（消息队列，最新在左）
    r.delete("demo:msgs")
    r.lpush("demo:msgs", "hello", "world", "foo")
    print(f"[list] lrange = {r.lrange('demo:msgs', 0, -1)}")
    print(f"[list] rpop   = {r.rpop('demo:msgs')}")

    # 4) set
    r.sadd("demo:tags:1", "python", "redis", "backend")
    r.sadd("demo:tags:2", "python", "ai")
    print(f"[set] sinter = {r.sinter('demo:tags:1', 'demo:tags:2')}")

    # 5) zset（排行榜）
    r.zadd("demo:rank", {"alice": 100, "bob": 200, "carol": 150})
    print(f"[zset] zrevrange = {r.zrevrange('demo:rank', 0, 9, withscores=True)}")

    # 6) 分布式锁（基础版 + Lua 安全释放）
    lock_key = "demo:lock:order:42"
    token = str(uuid.uuid4())
    acquired = r.set(lock_key, token, nx=True, px=10000)
    print(f"[lock] acquired = {acquired}")

    if acquired:
        try:
            # 业务逻辑省略
            pass
        finally:
            release_lua = """
            if redis.call('GET', KEYS[1]) == ARGV[1] then
                return redis.call('DEL', KEYS[1])
            else
                return 0
            end
            """
            released = r.eval(release_lua, 1, lock_key, token)
            print(f"[lock] released = {bool(released)}")

    # 7) Lua 脚本做"取较大值"原子操作
    r.set("demo:max_value", 0)
    set_max_lua = """
    local cur = tonumber(redis.call('GET', KEYS[1]) or '0')
    local new = tonumber(ARGV[1])
    if new > cur then
        redis.call('SET', KEYS[1], new)
        return 1
    end
    return 0
    """
    r.eval(set_max_lua, 1, "demo:max_value", 100)
    r.eval(set_max_lua, 1, "demo:max_value", 50)
    print(f"[lua] max_value = {r.get('demo:max_value')}")  # 应该是 100

    # 8) pipeline（批处理，省网络往返）
    with r.pipeline(transaction=False) as p:
        p.incr("demo:counter")
        p.incr("demo:counter")
        p.incr("demo:counter")
        results = p.execute()
    print(f"[pipeline] counter = {r.get('demo:counter')}, last3 increments = {results}")

    cleanup()


if __name__ == "__main__":
    try:
        # 连一下判断服务在不在
        r.ping()
        main()
    except redis.exceptions.ConnectionError as e:
        print(f"[error] 连不上 Redis：{e}")
        print("提示：检查本地 Redis 是否启动，或参考 workspace/db/README.md 用 docker 起一个：")
        print("  docker run -d -p 6379:6379 --name demo-redis redis:7-alpine")