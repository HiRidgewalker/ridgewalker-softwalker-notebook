"""
sqlite3 demo —— 不需要任何服务，直接跑。

对应笔记：[[SQLite笔记]]
"""
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "demo.db"


def main() -> None:
    # 文件不存在会自动创建
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                age   INTEGER
            )
        """)

        cur.execute(
            "INSERT INTO user (name, age) VALUES (?, ?)",
            ("alice", 30),
        )
        new_id = cur.lastrowid  # SQLite: 直接拿
        print(f"[insert] new id = {new_id}")

        cur.execute("SELECT id, name, age FROM user ORDER BY id")
        print("[select] rows =")
        for row in cur.fetchall():
            print(" ", row)

    # 清理
    if DB_FILE.exists():
        DB_FILE.unlink()


if __name__ == "__main__":
    main()