# workspace/mq —— 消息队列 Demo 总索引

对应笔记：

- [[Hub/06_RabbitMQ笔记]]
- [[Hub/07_Kafka笔记]]
- [[Hub/08_消息队列对比与选型笔记]]

## 文件

| 文件 | 内容 |
|---|---|
| `docker-compose.yml` | dev（单节点）+ prod（3 节点）双 profile |
| `rabbitmq_producer.py` | RabbitMQ 生产者（Publisher Confirms + 持久化 + 重试 + DLX）|
| `rabbitmq_consumer.py` | RabbitMQ 消费者（手动 ack + prefetch + 业务异常分类 + 幂等）|
| `kafka_producer.py` | Kafka 生产者（acks=all + idempotence + 压缩 + 批量）|
| `kafka_consumer.py` | Kafka 消费者（手动 commit + read_committed + 静态成员）|

## 启动服务

### dev 模式（单节点，推荐本地/CI）

```bash
cd workspace/mq

# 只起 RabbitMQ
docker compose --profile dev up -d rabbitmq

# 只起 Kafka
docker compose --profile dev up -d kafka

# 两个都起
docker compose --profile dev up -d

# 检查状态
docker compose ps

# RabbitMQ Management UI
open http://localhost:15672   # admin / admin

# Kafka
# localhost:9092

# 停掉 + 清数据
docker compose --profile dev down -v
```

### prod 模式（3 节点集群，参考用）

```bash
docker compose --profile prod up -d

# RabbitMQ 集群需要 join
docker exec rabbitmq-2 rabbitmqctl stop_app
docker exec rabbitmq-2 rabbitmqctl join_cluster rabbit@rabbitmq-1
docker exec rabbitmq-2 rabbitmqctl start_app
docker exec rabbitmq-3 rabbitmqctl stop_app
docker exec rabbitmq-3 rabbitmqctl join_cluster rabbit@rabbitmq-1
docker exec rabbitmq-3 rabbitmqctl start_app
```

> **注意**：3 节点集群在 WSL/低配机器会比较重；生产部署用云厂商托管或 k8s operator。

## 安装 Python 依赖

```bash
uv pip install --python workspace/.venv/bin/python pika confluent-kafka
```

## 运行 Demo

### RabbitMQ

```bash
# 终端 1：生产者（发 5 条订单消息）
workspace/.venv/bin/python workspace/mq/rabbitmq_producer.py

# 终端 2：消费者（手动 ack + 业务异常分类）
workspace/.venv/bin/python workspace/mq/rabbitmq_consumer.py
```

观察：
- 正常消息：日志显示 `processed`
- `amount < 0` → 不可重试错误 → 进 DLQ
- `order_id % 3 == 0` → 可重试错误 → 进 retry 队列 → 30s 后重投

### Kafka

```bash
# 终端 1：生产者（发 10 条订单事件）
workspace/.venv/bin/python workspace/mq/kafka_producer.py

# 终端 2：消费者（手动 commit + 幂等）
workspace/.venv/bin/python workspace/mq/kafka_consumer.py
```

## 三套生产配置对照

| 维度 | RabbitMQ（Quorum）| Kafka |
|---|---|---|
| 可靠性机制 | Publisher Confirms + 持久化 | `acks=all` + `min.insync.replicas=2` |
| 防重机制 | DLX + 消费端幂等 | `enable.idempotence` + EOS 事务 |
| 消费 ack | 手动 `basic_ack` | 手动 `commit()` |
| 流量控制 | prefetch_count 100~300 | `max.poll.records` 500 |
| HA | Quorum 3 节点（Raft）| replication.factor=3 + KRaft |
| 监控 | Management UI + Prometheus | JMX + Prometheus + AKHQ |

## 注意事项

- **RabbitMQ DLX 必须配 Quorum + at-least-once**（生产）
- **Kafka 必须 `acks=all` + `min.insync.replicas=2`**（防数据丢失）
- **消费端必须做幂等**（至少一次投递是默认）
- **Kafka Consumer 不要随便调小 `session.timeout.ms`**（容易触发 rebalance 风暴）
- **生产不要用 `mandatory` 替代 Publisher Confirms**（mandatory 只管 routing）
- **生产不要用 `enable.idempotence=false`**（重复消息会很多）

## 常用 CLI

```bash
# RabbitMQ
rabbitmqctl list_queues name messages_ready messages_unacknowledged
rabbitmqctl set_policy DLX "orders.*" \
  '{"dead-letter-exchange":"orders.dlx"}' --apply-to queues --priority 7

# Kafka（需在容器内执行）
docker exec -it kafka-dev bash
kafka-topics.sh --bootstrap-server localhost:9092 --list
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders \
  --partitions 6 --replication-factor 1   # dev 模式 RF=1
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group order-processor
```

## 相关 demo

- 数据库设计示例：`workspace/db-design/`（慢查询埋点 + Alembic）
- 关系型数据库连接示例：`workspace/db/sql-tools-demo/`
- 向量数据库示例：`workspace/vector-db/`