"""
Kafka 生产级 Producer 示例。

演示：
- 生产级配置：acks=all + enable_idempotence=True + max_in_flight=5
- 压缩 + 批量（linger_ms=10 + batch_size=32KB）
- 异步发送 + callback
- 失败重试（delivery_timeout_ms 控制上限）

对应笔记：[[Kafka笔记]] 4 节

启动：
    docker compose --profile dev up -d kafka
    uv pip install --python example/.venv/bin/python confluent-kafka
    example/.venv/bin/python example/mq/kafka_producer.py
"""
from __future__ import annotations

import json
import logging
import time
import uuid

from confluent_kafka import KafkaError, KafkaException, Producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# 生产级配置（按 [[Kafka笔记]] 4 节配）
# ============================================================
PRODUCER_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",                                           # 强一致（必须）
    "enable.idempotence": True,                              # 幂等（必须）
    "max.in.flight.requests.per.connection": 5,              # 幂等上限
    "compression.type": "lz4",
    "linger.ms": 10,                                         # 批量等待
    "batch.size": 32 * 1024,                                 # 32KB
    "retries": 2147483647,                                   # 无限重试
    "delivery.timeout.ms": 120000,                           # 总超时 2min
    "client.id": "order-producer",
}


TOPIC = "orders"


# ============================================================
# 回调
# ============================================================
success_count = 0
fail_count = 0


def on_delivery(err: KafkaError | None, msg: Any) -> None:
    global success_count, fail_count
    if err is not None:
        fail_count += 1
        logger.error("delivery failed: %s", err)
    else:
        success_count += 1
        logger.info(
            "delivered: topic=%s partition=%d offset=%d",
            msg.topic(), msg.partition(), msg.offset(),
        )


# ============================================================
# 发送
# ============================================================
def send_order(producer: Producer, payload: dict) -> None:
    """异步发送一条订单事件。"""
    key = str(payload["order_id"]).encode()      # 同 key 进同 partition（保序）
    value = json.dumps(payload, ensure_ascii=False).encode()

    producer.produce(
        topic=TOPIC,
        key=key,
        value=value,
        on_delivery=on_delivery,
        headers=[("trace_id", str(uuid.uuid4()).encode())],
    )
    # 触发批量发送（不阻塞）
    producer.poll(0)


def main() -> None:
    producer = Producer(PRODUCER_CONFIG)

    try:
        for i in range(1, 11):
            payload = {
                "order_id": i,
                "user_id": 1000 + i,
                "amount": 100.0 + i,
                "ts": int(time.time() * 1000),
            }
            send_order(producer, payload)
            time.sleep(0.01)               # 让批量有效果

        # 等待所有消息发送完成
        remaining = producer.flush(timeout=10)
        if remaining > 0:
            logger.error("%d messages still in queue (not delivered)", remaining)
        else:
            logger.info("all messages delivered: success=%d fail=%d", success_count, fail_count)
    except KafkaException as e:
        logger.error("kafka error: %s", e)


if __name__ == "__main__":
    main()