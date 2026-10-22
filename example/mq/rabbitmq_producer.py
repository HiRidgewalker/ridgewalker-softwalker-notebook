"""
RabbitMQ 生产级 Producer 示例。

演示：
- Quorum Queue 声明（x-queue-type=quorum）
- Publisher Confirms（生产必须开）
- 失败重试 + nack 处理
- mandatory 标志 + on_return callback（路由不到处理）
- 持久化消息（delivery_mode=2）

对应笔记：[[01_RabbitMQ笔记]] 5、6、7 节

启动：
    docker compose --profile dev up -d rabbitmq
    uv pip install --python example/.venv/bin/python pika
    example/.venv/bin/python example/mq/rabbitmq_producer.py
"""
from __future__ import annotations

import json
import logging
import time
import uuid

import pika

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# 配置
# ============================================================
HOST = "localhost"
PORT = 5672
USER = "admin"
PASSWORD = "admin"

EXCHANGE = "orders"
QUEUE = "orders"
ROUTING_KEY = "order.created"
DLX_EXCHANGE = "orders.dlx"
DLQ_QUEUE = "orders.dead"           # 死信队列（兜底）
RETRY_EXCHANGE = "orders.retry"
RETRY_QUEUE = "orders.retry.30s"    # 重试队列（30s TTL 后回到主队列）


# ============================================================
# 拓扑声明
# ============================================================
def declare_topology(ch: pika.adapters.blocking_connection.BlockingChannel) -> None:
    """生产环境推荐：先声明好所有 exchange / queue / binding。

    顺序：先声明 DLX 相关，再声明主队列（主队列要引用 DLX）。
    """
    # 1) DLX
    ch.exchange_declare(
        exchange=DLX_EXCHANGE, exchange_type="direct", durable=True,
    )
    ch.queue_declare(queue=DLQ_QUEUE, durable=True)
    ch.queue_bind(queue=DLQ_QUEUE, exchange=DLX_EXCHANGE, routing_key="orders.dead")

    # 2) 重试队列：消息进这里后 30s 过期，再被 DLX 转发回主 exchange
    ch.exchange_declare(
        exchange=RETRY_EXCHANGE, exchange_type="direct", durable=True,
    )
    ch.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 30_000,                        # 30s 过期
            "x-dead-letter-exchange": EXCHANGE,             # 过期后回到主 exchange
            "x-dead-letter-routing-key": ROUTING_KEY,
        },
    )
    ch.queue_bind(queue=RETRY_QUEUE, exchange=RETRY_EXCHANGE, routing_key="orders.retry")

    # 3) 主 exchange + 主队列（Quorum + DLX）
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(
        queue=QUEUE,
        durable=True,
        arguments={
            "x-queue-type": "quorum",                              # Quorum Queue
            "x-delivery-limit": 20,                                # 失败 20 次进死信
            "x-dead-letter-exchange": DLX_EXCHANGE,
            "x-dead-letter-routing-key": "orders.dead",
        },
    )
    ch.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)

    logger.info("topology declared: quorum queue %s with DLX", QUEUE)


# ============================================================
# 消息发布
# ============================================================
def publish_with_confirm(
    ch: pika.adapters.blocking_connection.BlockingChannel,
    payload: dict,
    *,
    max_retries: int = 3,
) -> bool:
    """
    发布单条消息，开 Publisher Confirms，失败重试。

    返回 True = broker 已 confirm，False = 发送失败。
    """
    body = json.dumps(payload, ensure_ascii=False).encode()
    msg_id = str(uuid.uuid4())

    for attempt in range(1, max_retries + 1):
        try:
            ch.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,              # 持久化
                    content_type="application/json",
                    message_id=msg_id,
                    timestamp=int(time.time()),
                ),
                mandatory=True,                   # 路由不到触发 on_return
            )
            logger.info("published: msg_id=%s attempt=%d", msg_id, attempt)
            return True
        except pika.exceptions.UnroutableError:
            logger.error("unroutable: msg_id=%s (no queue bound)", msg_id)
            return False
        except pika.exceptions.NackError:
            logger.warning("nack from broker: msg_id=%s attempt=%d", msg_id, attempt)
            if attempt < max_retries:
                time.sleep(0.1 * attempt)         # 退避
                continue
            return False
        except pika.exceptions.AMQPConnectionError as e:
            logger.error("connection error: %s", e)
            return False

    return False


def main() -> None:
    params = pika.ConnectionParameters(
        host=HOST, port=PORT,
        credentials=pika.PlainCredentials(USER, PASSWORD),
        heartbeat=30, blocked_connection_timeout=10,
    )
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # 1) 开启 Publisher Confirms（生产必须）
    ch.confirm_delivery()

    # 2) 声明拓扑
    declare_topology(ch)

    # 3) 发送 5 条测试消息
    for i in range(1, 6):
        payload = {"order_id": i, "amount": 100.0 + i, "user_id": 1000 + i}
        ok = publish_with_confirm(ch, payload)
        print(f"order {i}: {'OK' if ok else 'FAILED'}")

    conn.close()


if __name__ == "__main__":
    main()