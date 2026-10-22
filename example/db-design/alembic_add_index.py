"""
从「发现慢 SQL」到「通过 Alembic migration 加索引」的完整示例脚本。

本文件演示一段真实场景的 alembic revision：
- 慢 SQL：SELECT * FROM orders WHERE user_id = 12345 ORDER BY created_at DESC LIMIT 20
- EXPLAIN 发现 type=ALL，扫 50 万行
- 决定加复合索引 (user_id, created_at)

本文件是「可读代码片段」，需要配合真实 alembic 项目使用：
    alembic revision -m "add_orders_user_created_idx"
    # 把本文件的 upgrade / downgrade 粘进去
    alembic upgrade head

对应笔记：[[数据库设计与索引优化笔记]]
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


# ============================================================
# Alembic revision header（alembic 自动生成，复制即可）
# ============================================================
revision = "20260702_1200"               # 本次 migration 的唯一 ID
down_revision = "20260701_1800"          # 上一个 migration（按时间顺序串）
branch_labels = None
depends_on = None


# ============================================================
# upgrade
# ============================================================
def upgrade() -> None:
    """
    完整索引添加流程。

    业务背景：运营报障「我的订单列表加载慢」，慢 SQL：
        SELECT * FROM orders
         WHERE user_id = 12345
         ORDER BY created_at DESC
         LIMIT 20;

    EXPLAIN 结果（修复前）：
        type=ALL, rows=500000, Extra=Using filesort
        （全表扫描 + 内存排序，必须加索引）

    索引设计：
        - 复合索引 (user_id, created_at)
        - 顺序遵循 ESR 原则：等值(user_id) → 排序(created_at)
        - WHERE 等值走 user_id，ORDER BY 走 created_at 索引有序，无需 filesort
    """

    # 1) 普通复合索引（MySQL / PG / SQLite 通用）
    op.create_index(
        "ix_orders_user_created",
        "orders",
        ["user_id", "created_at"],
    )

    # 2) 如果是大表 + PostgreSQL，走 CONCURRENTLY（不锁表）
    #    注意：Alembic 默认每 migration 一个事务，CONCURRENTLY 不能在事务里
    #    方案 A：alembic.ini 配 transaction_per_ddl = False
    #    方案 B：在脚本里手动 COMMIT 切事务
    #    解开下面这段即可使用：
    #
    # op.execute("COMMIT")
    # op.execute(
    #     "CREATE INDEX CONCURRENTLY ix_orders_user_created "
    #     "ON orders (user_id, created_at)"
    # )

    # 3) 如果是 MySQL 大表，建议用 pt-osc 或 gh-ost 在线 DDL，
    #    不要直接 ALTER TABLE。本文件演示的 alembic 只适合中小表。
    #    pt-online-schema-change 示例（命令行，不在 alembic 里）：
    #        pt-online-schema-change \
    #            --alter "ADD INDEX ix_orders_user_created (user_id, created_at)" \
    #            --execute --alter-foreign-keys-method auto \
    #            D=shop,t=orders,h=localhost

    # 4) 同时清理发现的「未使用索引」（按需）
    #    可用 sys.schema_unused_indexes / pg_stat_user_indexes 查
    # op.drop_index("ix_orders_legacy_status", table_name="orders")


# ============================================================
# downgrade
# ============================================================
def downgrade() -> None:
    """
    回滚：必须与 upgrade 对称，否则回滚失败 / 索引遗留。

    生产事故 root cause 中「upgrade 成功、downgrade 失败」是高频问题。
    """
    op.drop_index("ix_orders_user_created", table_name="orders")


# ============================================================
# 完整 checklist（执行前逐项确认）
# ============================================================
CHECKLIST = """
[ ] 慢 SQL 已用 pt-query-digest / pg_stat_statements 确认是热点（不是一次性慢查询）
[ ] EXPLAIN 已看，确认 type=ALL / rows 巨大 / 没走索引
[ ] 复合索引顺序已按 ESR 原则（等值 → 排序 → 范围）
[ ] 唯一索引确认 DB 现有数据无重复（UNIQUE 会因重复失败）
[ ] 大表确认是否走在线 DDL（pt-osc / gh-ost / CONCURRENTLY）
[ ] migration 脚本已写完整的 downgrade
[ ] 已在测试环境跑过 upgrade + downgrade
[ ] 已在 staging 观察索引生效、慢 SQL 消失
[ ] 已通知 DBA / 团队 review migration
[ ] 上线窗口选择低峰期（大表加索引仍可能有 I/O 抖动）
""".strip()


# ============================================================
# 用法示例（伪代码，作为 README 参考）
# ============================================================
USAGE = """
# 1. 生成新的 revision 文件
alembic revision -m "add_orders_user_created_idx"

# 2. 把本文件的 upgrade() / downgrade() 粘进去（替换 alembic 生成的空函数）

# 3. 本地 / 测试环境验证
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# 4. EXPLAIN 验证索引生效
mysql> EXPLAIN SELECT * FROM orders WHERE user_id = 12345 ORDER BY created_at DESC LIMIT 20;
# 应看到：type=ref, key=ix_orders_user_created, rows=1, Extra=Using index condition

# 5. 上线
alembic upgrade head   # 生产执行

# 6. 监控
#    - 看慢查询日志中该 SQL 是否消失
#    - 看 pg_stat_statements / sys.io_global_by_file_by_bytes 等
""".strip()


if __name__ == "__main__":
    # 本文件 main 仅打印 checklist / usage，避免误以为可直接跑
    print("=" * 60)
    print("CHECKLIST")
    print("=" * 60)
    print(CHECKLIST)
    print()
    print("=" * 60)
    print("USAGE")
    print("=" * 60)
    print(USAGE)