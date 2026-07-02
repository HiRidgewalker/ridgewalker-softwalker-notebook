"""Demo Flask：连接 postgres + redis 并演示连通性。"""

import os
import redis
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

redis_client = None
db_status = "skipped"
redis_status = "skipped"
hit_count = 0


def try_connect_db():
    global db_status
    try:
        import psycopg2  # noqa: F401
        db_status = "ok (psycopg2 importable, not actually connecting in demo)"
    except ImportError:
        db_status = "psycopg2 not installed (demo: no-op)"


def try_connect_redis():
    global redis_status, hit_count
    try:
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()
        redis_status = "connected"
        redis_client = r
    except Exception as e:
        redis_status = f"error: {e}"
        redis_client = None


try_connect_db()
try_connect_redis()


@app.get("/")
def index():
    global hit_count
    if redis_client is not None:
        hit_count = redis_client.incr("hits")
    return jsonify(
        message="hello from flask container",
        now=datetime.now().isoformat(),
        db_status=db_status,
        redis_status=redis_status,
        hits=hit_count,
    )


@app.get("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
