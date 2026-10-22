"""
FastAPI + SQLAlchemy 慢查询埋点示例。

演示：
- Engine 级 event hook（before_cursor_execute / after_cursor_execute）
  覆盖 Core 和 ORM 两种执行路径
- ORM 2.0 的 do_orm_execute 补充拿 statement 对象
- 阈值（200ms）+ logging.warning 输出（生产替换为结构化日志）

对应笔记：[[数据库设计与索引优化笔记]]

注意：本文件是「代码片段示例」，不需要真连数据库；如要实跑：
    uv pip install --python example/.venv/bin/python sqlalchemy
"""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session


# ---------- 配置 ----------
SLOW_THRESHOLD_MS = 200     # 业界常用阈值；>500ms 应开 P0 工单
LOGGER_NAME = "app.slow_query"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.WARNING)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    logger.addHandler(handler)


def install_slow_query_logger(engine: Engine, threshold_ms: int = SLOW_THRESHOLD_MS) -> None:
    """
    把慢查询埋点装到指定 Engine。

    用法（在 FastAPI 启动钩子里）：
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        install_slow_query_logger(engine, threshold_ms=200)
    """

    @event.listens_for(engine, "before_cursor_execute")
    def _before(
        conn: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        # 把开始时间挂在 context 上，after 用同一个 context 取
        context._query_start_time = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def _after(
        conn: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        start = getattr(context, "_query_start_time", None)
        if start is None:
            return
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms >= threshold_ms:
            logger.warning(
                "slow query (%.1f ms) [executemany=%s]: %s",
                elapsed_ms, executemany, statement,
            )

    # ORM 2.0 补充：能拿到 ORMStatement 对象，statement.sql() 更可读
    @event.listens_for(Session, "do_orm_execute")
    def _slow_orm(state: Any) -> None:
        # 注意：do_orm_execute 不覆盖 flush 阶段 SQL，
        # flush 阶段靠上面的 before/after_cursor_execute 兜底
        start = time.perf_counter()
        try:
            state.invoke_statement()
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            if elapsed >= threshold_ms:
                logger.warning(
                    "slow ORM (%.1f ms): %s",
                    elapsed,
                    str(state.statement)[:500],   # 防 statement 过长打爆日志
                )


# ---------- 演示 ----------
if __name__ == "__main__":
    # 用 SQLite memory 演示 event hook 工作；不需要外部数据库
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    install_slow_query_logger(engine, threshold_ms=10)   # 演示用 10ms 阈值

    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
        conn.exec_driver_sql("INSERT INTO t (name) VALUES ('a'), ('b'), ('c')")

        # 1) 正常查询（不报警）
        result = conn.exec_driver_sql("SELECT * FROM t")
        print(f"normal query rows: {result.fetchall()}")

        # 2) 模拟慢查询（用 time.sleep 注入到 SQL 之前）
        #    注意：sleep 必须在 cursor.execute 之前才有意义，这里手工控制
        from sqlalchemy import text
        with conn.connection.cursor() as cursor:
            t0 = time.perf_counter()
            cursor.execute("SELECT * FROM t")    # 真查询
            time.sleep(0.05)                     # 模拟耗时
            # 这里手工触发 after 钩子不太现实，下面用单独 exec 来证明日志

        # 3) 真正会触发慢查询埋点的演示：
        #    用 connection.execution_options 注入语句超时不可行，
        #    所以加一个 time.sleep 包裹来模拟（不严谨，仅做 demo）。
        import time as _t
        _t.sleep(0.05)
        conn.exec_driver_sql("SELECT * FROM t WHERE id = 1")

    print("[demo] 上面日志中应能看到 'slow query' 警告（如果 exec 跨过 10ms）")