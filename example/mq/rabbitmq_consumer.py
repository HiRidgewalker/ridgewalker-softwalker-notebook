"""
RabbitMQ 生产级 Consumer 示例。

演示：
- 手动 ack（auto_ack=False）
- prefetch_count=200（生产推荐值）
- 业务异常分类：可重试 / 不可重试
- 不可重试 → DLX 兜底
- 幂等处理（演示用订单 ID 去重）

对应笔记：[[RabbitMQ笔记]] 6、7 节

启动：
    example/.venv/bin/python example/mq/rabbitmq_consumer.py
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import pika

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


HOST = "localhost"
PORT = 5672
USER = "admin"
PASSWORD = "admin"
QUEUE = "orders"
RETRY_ROUTING_KEY = "orders.retry"      # 重试 routing key
PREFETCH = 200                            # 生产推荐值


# ============================================================
# 模拟业务异常
# ============================================================
class RetryableError(Exception):
    """可重试错误（瞬时故障：网络/DB 抖动）"""
    pass


class FatalError(Exception):
    """不可重试错误（业务逻辑错误：参数非法）"""
    pass


# ============================================================
# 模拟业务处理
# ============================================================
processed_ids: set[str] = set()           # 演示用幂等（生产用 Redis SETNX）


def process_message(payload: dict[str, Any]) -> None:
    """模拟业务处理。

    演示场景：
    - order_id 已处理过：幂等跳过（实际不报错）
    - amount < 0：FatalError（业务错误，nack(requeue=False) 进 DLX）
    - order_id % 3 == 0：RetryableError（瞬时错误，进 retry 队列 30s 后重试）
    """
    order_id = payload.get("order_id")
    if order_id in processed_ids:
        logger.info("duplicate, skip: order_id=%s", order_id)
        return
    if payload.get("amount", 0) < 0:
        raise FatalError(f"invalid amount: {payload['amount']}")
    if order_id % 3 == 0:
        raise RetryableError(f"simulated transient error: order_id={order_id}")
    time.sleep(0.01)                       # 模拟业务耗时
    processed_ids.add(order_id)
    logger.info("processed: order_id=%s amount=%s", order_id, payload.get("amount"))


# ============================================================
# 消费回调
# ============================================================
def on_message(
    ch: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes,
) -> None:
    """核心回调：处理 → ack / nack(requeue=True) / nack(requeue=False)→DLX / 进 retry 队列。"""
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error("invalid JSON, send to DLX: %s", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    try:
        process_message(payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except FatalError as e:
        # 业务错误：直接进 DLX，不重试
        logger.error("fatal, send to DLX: %s", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except RetryableError as e:
        # 瞬时错误：进 retry 队列（30s 后自动重投）
        logger.warning("retryable, send to retry queue: %s", e)
        ch.basic_publish(
            exchange="orders.retry",
            routing_key=RETRY_ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={"x-original-queue": QUEUE},
            ),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)        # 原消息 ack
    except Exception as e:
        # 未预期错误：保守起见 requeue（但要防死循环，靠 x-delivery-limit 兜底）
        logger.exception("unexpected error, requeue: %s", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main() -> None:
    params = pika.ConnectionParameters(
        host=HOST, port=PORT,
        credentials=pika.PlainCredentials(USER, PASSWORD),
        heartbeat=30,
    )
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # 1) 关键：prefetch 调到 200（生产推荐值）
    ch.basic_qos(prefetch_count=PREFETCH)

    # 2) 消费（手动 ack）
    ch.basic_consume(queue=QUEUE, on_message_callback=on_message, auto_ack=False)

    logger.info("consumer started, waiting for messages (prefetch=%d)...", PREFETCH)
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.stop_consuming()
    finally:
        conn.close()


if __name__ == "__main__":
    main()