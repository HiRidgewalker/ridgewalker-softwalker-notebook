"""
Kafka 生产级 Consumer 示例。

演示：
- 手动 commit offset（enable_auto_commit=False）
- isolation.level=read_committed（事务已提交）
- 幂等处理（演示用订单 ID 去重）
- 失败处理：不 commit，下次重投
- 静态成员（group.instance.id）减少 rebalance

对应笔记：[[02_Kafka笔记]] 5 节

启动：
    workspace/.venv/bin/python workspace/mq/kafka_consumer.py
"""
from __future__ import annotations

import json
import logging
import signal
import time
from typing import Any

from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# 生产级配置
# ============================================================
CONSUMER_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-processor",
    "group.instance.id": "order-processor-1",        # 静态成员，减少 rebalance
    "enable.auto.commit": False,                      # 必须手动 commit
    "auto.offset.reset": "earliest",
    "isolation.level": "read_committed",              # 事务已提交
    "max.poll.records": 500,
    "session.timeout.ms": 45000,
    "heartbeat.interval.ms": 15000,                   # ≤ session/3
    "max.poll.interval.ms": 300000,                   # 5min
    "partition.assignment.strategy": "cooperative-sticky",
}


TOPIC = "orders"


# ============================================================
# 幂等处理（演示用，生产用 Redis SETNX / DB 唯一索引）
# ============================================================
processed_ids: set[str] = set()


def process_message(payload: dict[str, Any]) -> None:
    """模拟业务处理。"""
    order_id = payload.get("order_id")
    if order_id in processed_ids:
        logger.info("duplicate, skip: order_id=%s", order_id)
        return
    time.sleep(0.01)
    processed_ids.add(order_id)
    logger.info("processed: order_id=%s amount=%s", order_id, payload.get("amount"))


# ============================================================
# 优雅退出
# ============================================================
running = True


def _signal_handler(sig: int, frame: Any) -> None:
    global running
    logger.info("received signal %d, shutting down...", sig)
    running = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ============================================================
# 消费循环
# ============================================================
def main() -> None:
    consumer = Consumer(CONSUMER_CONFIG)
    consumer.subscribe([TOPIC])

    logger.info("consumer started, topic=%s group=%s", TOPIC, CONSUMER_CONFIG["group.id"])

    try:
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("kafka error: %s", msg.error())
                continue

            try:
                payload = json.loads(msg.value())
                process_message(payload)
            except (json.JSONDecodeError, KeyError) as e:
                logger.error("bad message, skip (will not commit): %s", e)
                continue                                  # 不 commit，下次重投
            except Exception as e:
                logger.exception("process failed, skip: %s", e)
                continue                                  # 同上，依赖幂等

            # 同步 commit offset（生产可用 commit_async 提升吞吐）
            try:
                consumer.commit(message=msg, asynchronous=False)
            except KafkaException as e:
                logger.error("commit failed: %s", e)

    finally:
        logger.info("closing consumer...")
        try:
            consumer.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()