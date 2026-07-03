"""
pymysql demo —— 需要本地 MySQL 服务（默认 localhost:3306, user=root, pass=root, db=demo）。

对应笔记：[[01_MySQL笔记]]
"""
import pymysql

CONFIG = dict(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="demo",
    charset="utf8mb4",
    autocommit=False,
)


def main() -> None:
    conn = pymysql.connect(**CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `user` (
                    `id`   INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(64) NOT NULL,
                    `age`  INT
                )
            """)

            cur.execute(
                "INSERT INTO `user` (`name`, `age`) VALUES (%s, %s)",
                ("alice", 30),
            )
            new_id = cur.lastrowid  # pymysql: 直接拿
            print(f"[insert] new id = {new_id}")

            cur.execute("SELECT id, name, age FROM `user` ORDER BY id")
            print("[select] rows =")
            for row in cur.fetchall():
                print(" ", row)
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except pymysql.err.OperationalError as e:
        print(f"[error] 连不上 MySQL：{e}")
        print("提示：检查本地 MySQL 是否启动，或参考 README 用 docker 起一个：")
        print("  docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=demo mysql:8")