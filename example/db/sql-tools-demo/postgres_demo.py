"""
psycopg (v3) demo —— 需要本地 PostgreSQL 服务（默认 localhost:5432, user=postgres, pass=postgres, db=demo）。

对应笔记：[[PostgreSQL笔记]]
"""
import psycopg

CONFIG = (
    "host=localhost port=5432 dbname=demo user=postgres password=postgres"
)


def main() -> None:
    with psycopg.connect(CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id   BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age  INTEGER
                )
            """)

            # PostgreSQL 习惯：用 RETURNING 拿新 id
            cur.execute(
                'INSERT INTO "user" (name, age) VALUES (%s, %s) RETURNING id',
                ("alice", 30),
            )
            new_id = cur.fetchone()[0]
            print(f"[insert] new id = {new_id}")

            cur.execute('SELECT id, name, age FROM "user" ORDER BY id')
            print("[select] rows =")
            for row in cur.fetchall():
                print(" ", row)


if __name__ == "__main__":
    try:
        main()
    except psycopg.OperationalError as e:
        print(f"[error] 连不上 PostgreSQL：{e}")
        print("提示：检查本地 PG 是否启动，或参考 README 用 docker 起一个：")
        print("  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=demo postgres:16")