---
type: hub
topic: Kafka 生产级
status: created
sources:
  - https://kafka.apache.org/43/operations/kraft/
  - https://kafka.apache.org/43/configuration/consumer-configs/
  - https://kafka.apache.org/43/configuration/producer-configs/
  - https://kafka.apache.org/documentation/#semantics
  - https://kafka.apache.org/documentation/#kraft
  - https://kafka.apache.org/documentation/#basic_ops
  - https://docs.confluent.io/platform/current/installation/docker/config-reference.html
---

# Kafka 笔记（生产级）

> 工业生产环境下的 Kafka 使用：架构 / KRaft / Producer+Consumer 生产配置 / EOS / HA / Docker 部署 / 监控与常见生产坑。
> 配套笔记：[[01_RabbitMQ笔记]] · [[消息队列选型对比笔记]]。
> Demo 代码示例在 `example/mq/`（docker-compose + 生产级 Producer/Consumer + 事务示例）。

## 目录

1. 定位与核心概念
2. KRaft 模式（4.x 强制去 ZK）
3. Docker 生产部署（3 broker + 3 controller）
4. Producer 生产配置
5. Consumer 生产配置
6. Exactly-Once Semantics（EOS）
7. 副本与 ISR：防数据丢失三件套
8. 性能调优
9. 监控指标
10. 常见生产坑

---

## 1. 定位与核心概念

**Apache Kafka** 是一款**分布式、持久化、可重放的发布-订阅消息系统**，本质是**分布式 append-only 日志**。

**核心特点**：
- **高吞吐**（十万~百万 TPS 单集群）
- **持久化**（消息落盘，可保留数天~数月）
- **可重放**（consumer 自己控制 offset，可回放历史）
- **水平扩展**（加 broker / 加分区即可）
- **顺序保证**（分区内严格有序）

**不适合**：复杂路由 / RPC / 低延迟（毫秒级）—— 选 RabbitMQ。

### 1.1 核心概念

| 概念 | 含义 |
|---|---|
| **Broker** | Kafka 服务节点（一个 JVM 进程）|
| **Topic** | 消息主题（逻辑分类）|
| **Partition** | Topic 的物理分片（有序、不可变、追加写）|
| **Offset** | 分区内的消息序号（每个分区独立）|
| **Producer** | 消息生产者 |
| **Consumer** | 消息消费者 |
| **Consumer Group** | 一组消费者共同消费一个 Topic（每条消息只被组内一个 Consumer 消费）|
| **ISR** | In-Sync Replicas（同步副本集）|
| **Replica** | 副本（leader + follower）|
| **Controller** | 集群管理者（KRaft 模式下内置）|
| **ZooKeeper** | 旧版集群协调服务（4.0+ 移除）|

### 1.2 消息模型本质

```
Topic "orders"
├── Partition 0: [msg0, msg1, msg2, msg3, msg4, msg5, ...] (offset 递增)
├── Partition 1: [msg0, msg1, msg2, msg3, ...]
└── Partition 2: [msg0, msg1, msg2, ...]
```

- 消息是**追加写**的日志文件
- Consumer 通过 offset 决定从哪里读
- **不删除已读消息**（保留期内一直存在）
- 不同分区间不保证顺序，**单分区内严格有序**

---

## 2. KRaft 模式（4.x 强制去 ZK）

Kafka 4.0+ **移除 ZooKeeper**，元数据由 Kafka 自身用 Raft 协议管理（KRaft = Kafka Raft）。

### 2.1 KRaft vs ZooKeeper

| 维度 | KRaft | ZooKeeper |
|---|---|---|
| 元数据存储 | Kafka 内部 Raft 集群 | 外部 ZK ensemble |
| 部署组件 | 1 套 | 2 套（Kafka + ZK）|
| 故障容忍 | ⌊N/2⌋ 故障（N=3 容忍 1）| ZK ensemble 自身容忍 |
| 元数据扩展性 | 支持百万级 partition | ZK 节点数限制 |
| Controller 启动 | 秒级 | 分钟级（ZK 加载）|
| 运维复杂度 | 单系统 | 双系统 |
| 适用版本 | Kafka 4.0+ **生产唯一选择** | 已废弃（最后桥接版 3.9）|

### 2.2 角色划分

KRaft 节点通过 `process.roles` 划分：

- `broker`：只做 broker
- `controller`：只做 controller（元数据管理）
- `broker,controller`：双角色，**仅 dev/test**

**生产推荐**：3 controller + N broker 分离部署。

### 2.3 最小生产拓扑

> 3 controller 起步（容 1 故障）；5 节点（容 2 故障）。
> 节点数必须**奇数**。

```
controller1 (id=1) ━━━ Raft ━━━ controller2 (id=2) ━━━ Raft ━━━ controller3 (id=3)
       │                                                              │
       └────────────────── Kafka 数据平面 ────────────────────────────┘
       │                                                              │
   broker1 (id=11)                                              broker2 (id=12)
                                                                       ...
```

### 2.4 核心配置

```properties
# Controller 节点
process.roles=controller
node.id=1
listeners=CONTROLLER://0.0.0.0:9093
controller.listener.names=CONTROLLER
controller.quorum.bootstrap.servers=host1:9093,host2:9093,host3:9093
log.dirs=/var/lib/kafka/controller

# Broker 节点
process.roles=broker
node.id=11
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://broker1:9092
controller.listener.names=CONTROLLER
controller.quorum.bootstrap.servers=host1:9093,host2:9093,host3:9093
log.dirs=/var/lib/kafka/data
```

### 2.5 初始化流程

```bash
# 1. 生成 cluster ID
CLUSTER_ID=$(bin/kafka-storage.sh random-uuid)

# 2. 格式化 controller（第一个节点用 --standalone）
bin/kafka-storage.sh format --cluster-id $CLUSTER_ID --standalone \
  --config config/controller.properties

# 3. 格式化 broker
bin/kafka-storage.sh format --cluster-id $CLUSTER_ID \
  --config config/server.properties --no-initial-controllers

# 4. 启动所有节点
bin/kafka-server-start.sh config/server.properties
```

### 2.6 资源规划

- Controller 节点：5GB 内存 + 5GB 磁盘足够（仅元数据日志）
- Broker 节点：按数据量规划，**磁盘要 SSD / NVMe**

---

## 3. Docker 生产部署

### 3.1 镜像选择

| 镜像 | 说明 |
|---|---|
| `apache/kafka:4.0.0` | 官方（KRaft）|
| `bitnami/kafka:3.9` | Bitnami（含 KRaft）|
| `confluentinc/cp-kafka:7.6.0` | Confluent（兼容性好）|

### 3.2 单节点 dev 模式

```yaml
# docker-compose.yml
services:
  kafka:
    image: apache/kafka:4.0.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_CFG_NODE_ID: "1"
      KAFKA_CFG_PROCESS_ROLES: "broker,controller"
      KAFKA_CFG_LISTENERS: "PLAINTEXT://:9092,CONTROLLER://:9093"
      KAFKA_CFG_ADVERTISED_LISTENERS: "PLAINTEXT://localhost:9092"
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: "1@localhost:9093"
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"
```

**3 节点 KRaft 集群**见 `example/mq/docker-compose.yml`。

---

## 4. Producer 生产配置

> 工业生产环境下的 Producer 配置原则：**先保证不丢，再调吞吐**。

### 4.1 关键配置速查

| 配置 | 推荐值 | 作用 |
|---|---|---|
| `acks` | **`all`**（或 `-1`）| 等所有 ISR 副本确认 |
| `enable.idempotence` | **`true`** | 防止 Producer 重试导致重复 |
| `max.in.flight.requests.per.connection` | 5（idempotence 开时上限）| 允许未确认请求数 |
| `compression.type` | `lz4` / `zstd` | 网络/磁盘压缩 |
| `linger.ms` | 5~20 | 批量等待时间（提升吞吐）|
| `batch.size` | 32KB~64KB | 单批大小 |
| `retries` | 2147483647（max）| 重试次数（`delivery.timeout.ms` 控制上限）|
| `delivery.timeout.ms` | 120000（默认）| 发送总超时（含重试）|
| `key.serializer` | `org.apache.kafka.common.serialization.StringSerializer` |  |
| `value.serializer` | `JSON` / `Avro` / `Protobuf` |  |

### 4.2 `acks` 三档（关键）

| 值 | 行为 | 可靠性 | 性能 |
|---|---|---|---|
| `0` | Producer 发完不等 ack | ❌ 可能丢 | 最快 |
| `1` | Leader 写入即 ack | ⚠️ Leader 故障可能丢 | 折中 |
| `all` | 所有 ISR 副本 ack | ✅ 强一致 | 最慢 |

**生产必须 `acks=all`**。`acks=1` 在 Leader 故障时**已写但未复制**的消息会丢。

### 4.3 `enable.idempotence=true` 的强制约束

开启幂等性后，Kafka 强制：

- `acks=all`（自动设置）
- `retries > 0`（自动设 max）
- `max.in.flight.requests.per.connection ≤ 5`

幂等性解决了**单分区单会话内的重复**，靠 Producer ID + sequence number 去重。

### 4.4 Python 示例

```python
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    acks="all",                                # 强一致
    enable_idempotence=True,                   # 幂等
    max_in_flight_requests_per_connection=5,   # 幂等上限
    compression_type="lz4",
    linger_ms=10,
    batch_size=32*1024,
    retries=2147483647,
    delivery_timeout_ms=120000,
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

future = producer.send("orders", key="order-123", value={"action": "create"})
# 同步等待（阻塞，吞吐低但能拿错误）
try:
    metadata = future.get(timeout=10)
    print(f"partition={metadata.partition} offset={metadata.offset}")
except KafkaError as e:
    print(f"send failed: {e}")
```

### 4.5 异步发送 + callback（生产推荐）

```python
def on_success(metadata):
    print(f"ok: partition={metadata.partition} offset={metadata.offset}")

def on_error(e):
    # 入重试队列 / DLQ
    print(f"failed: {e}")

producer.send("orders", value=data).add_callback(on_success).add_errback(on_error)
```

---

## 5. Consumer 生产配置

### 5.1 关键配置速查

| 配置 | 推荐值 | 作用 |
|---|---|---|
| `group.id` | 必填，业务命名 | Consumer 组 |
| `enable.auto.commit` | **`false`** | 必须手动提交 |
| `auto.offset.reset` | `earliest` / `latest` | 无 offset 时行为 |
| `max.poll.records` | 100~500 | 每次 poll 最大记录数 |
| `max.poll.interval.ms` | 300000（5min）| 两次 poll 最大间隔 |
| `session.timeout.ms` | 30000~60000 | 心跳超时 |
| `heartbeat.interval.ms` | ≤ session/3 | 心跳频率 |
| `isolation.level` | **`read_committed`** | 只读已提交事务 |
| `partition.assignment.strategy` | `CooperativeStickyAssignor` | 协同再平衡 |
| `key.deserializer` / `value.deserializer` | 对应 |  |

### 5.2 手动提交 offset（必须）

```python
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=["localhost:9092"],
    group_id="order-processor",
    enable_auto_commit=False,                   # 必须关
    auto_offset_reset="earliest",
    isolation_level="read_committed",
    max_poll_records=500,
    session_timeout_ms=45000,
    heartbeat_interval_ms=15000,
    key_deserializer=lambda k: k.decode("utf-8"),
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

for msg in consumer:
    try:
        process(msg.value)
        consumer.commit()                       # 同步提交（吞吐低）
        # 或 consumer.commit_async() 异步（吞吐高但可能丢提交）
    except Exception as e:
        # 不提交，下次重投；消费者必须幂等
        logger.error(f"process failed: {e}")
```

### 5.3 提交策略

| 策略 | 行为 | 风险 |
|---|---|---|
| 同步 `commit()` | 等 broker 响应 | 阻塞吞吐 |
| 异步 `commit_async()` | 不等响应 | 失败不重试，偶发丢提交 |
| 手动 commit + 业务事务 | DB 事务成功后再 commit | 复杂但最稳 |

### 5.4 再平衡（Rebalance）

- Consumer 加入/离开 group → 重新分配 partition
- 期间所有 consumer **停止消费**
- 频繁 rebalance = 灾难（消费停滞）

**避免 rebalance 风暴**：
- `session.timeout.ms` 调到 30~60s（默认 45s 适中）
- `max.poll.interval.ms` 调到足够大（处理慢业务的窗口）
- 用 `group.instance.id` 开启**静态成员**，避免 leave/join

### 5.5 顺序保证

- **单 partition 单 consumer**：严格有序
- **多 partition 多 consumer**：不保证全局顺序
- 要全局顺序：单 partition（牺牲吞吐），或按业务 key 分区（同 key 同 partition）

---

## 6. Exactly-Once Semantics（EOS）

Kafka 通过**幂等 Producer + 事务**实现 EOS。

### 6.1 三种语义

| 语义 | 说明 | 风险 |
|---|---|---|
| **At-most-once** | 发送前提交 offset / 不重试 | 丢 |
| **At-least-once** | 重试 + 处理后再提交 | 重复 |
| **Exactly-once** | 幂等 + 事务 + 读已提交 | 性能略低 |

### 6.2 EOS 三件套

1. **幂等 Producer**（`enable.idempotence=true`）：单分区内去重
2. **事务**：跨 partition / 跨 topic 原子写
3. **`isolation.level=read_committed`**：消费者只读已提交消息

### 6.3 事务 Producer 示例

```python
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    transactional_id="order-tx-producer",       # 必须，全局唯一
    enable_idempotence=True,
    acks="all",
)

producer.init_transactions()

try:
    producer.begin_transaction()
    producer.send("orders", value={"action": "create"})
    producer.send("audit-log", value={"action": "audit"})
    # 写数据库（可选，用 send_offsets_to_transaction 关联 offset 提交）
    producer.send_offsets_to_transaction(
        offsets={TopicPartition("orders", 0): OffsetAndMetadata(42, "")},
        group_id="order-processor",
    )
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
    raise
```

### 6.4 消费者侧

```python
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=["localhost:9092"],
    group_id="order-processor",
    enable_auto_commit=False,
    isolation_level="read_committed",           # 必须
)
```

> **注意**：EOS 增加延迟和复杂度，**不到必要时不要用**。多数业务用「at-least-once + 消费端幂等」就够。

---

## 7. 副本与 ISR：防数据丢失三件套

### 7.1 三件套（必配）

```properties
# Topic 级别
replication.factor=3            # 3 副本
min.insync.replicas=2           # 至少 2 个 ISR 才能写

# Producer 级别
acks=all                        # 等所有 ISR ack
```

这三项共同保证：

- 即使 1 个 broker 故障，消息不丢
- 写入时 ISR 不足会失败（不是默默丢）

### 7.2 不丢数据流程

```
Producer 发消息（acks=all）
    ↓
Leader 写入本地日志
    ↓
复制到所有 follower
    ↓
followers 全部 ack（满足 min.insync.replicas=2）
    ↓
返回 ack 给 Producer
```

### 7.3 常见错误配置

| 错配 | 后果 |
|---|---|
| `replication.factor=1` | 单点故障必丢 |
| `min.insync.replicas=1` + `acks=1` | 等于没保护 |
| `acks=0` | 不知道丢没丢 |
| `min.insync.replicas=2` 但 `replication.factor=2` | 副本不足时写失败 |

---

## 8. 性能调优

### 8.1 分区数规划

- 单分区单 consumer 是瓶颈（顺序处理）
- **目标**：分区数 ≥ consumer 数
- 经验值：单分区 1~10 MB/s，每 broker 几十~几百分区
- 分区数定了就**不能减**（只能加）

### 8.2 页缓存（Page Cache）

- Kafka **重度依赖 OS 页缓存**（不是 JVM 堆）
- broker 内存规划：给足系统页缓存（一般留 50% 以上给 OS）
- `KAFKA_HEAP_OPTS=-Xmx6g`（32GB 机器）

### 8.3 零拷贝（Zero-Copy）

- Kafka 用 `sendfile()` 系统调用，磁盘 → 网卡 不经过用户态
- 节省 CPU + 内存

### 8.4 顺序写

- 追加写日志（不修改已写数据）→ 磁盘顺序 I/O
- 比随机写快 100x+

### 8.5 Producer 批量

```properties
linger.ms=20
batch.size=64KB
compression.type=lz4
```

### 8.6 Consumer 批量

```python
# 用 consumer.poll(timeout_ms=1000) 一次拿一批
records = consumer.poll(timeout_ms=1000, max_records=500)
for tp, msgs in records.items():
    for msg in msgs:
        process(msg)
consumer.commit()  # 整批处理完一次性提交
```

---

## 9. 监控指标

### 9.1 关键指标

| 指标 | 来源 | 告警阈值 |
|---|---|---|
| **Consumer Lag** | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*,topic=*,partition=*` | > 10000 告警 |
| **Under Replicated Partitions** | broker 端 | > 0 告警（必查）|
| **Request Latency** | `kafka.network:type=RequestMetrics,name=TotalTimeMs` | p99 > 100ms 告警 |
| **Active Controller Count** | broker 端 | 必须是 1 |
| **Messages In/Per Sec** | broker 端 | 看趋势 |
| **ISR Shrink / Expand Rate** | broker 端 | 频繁变化 = 节点不稳 |

### 9.2 推荐监控方案

- **Prometheus JMX Exporter** 抓 Kafka JMX
- **Grafana Dashboard**：Confluent 官方 / 自建
- **Kafka Exporter**（GitHub）：暴露 Consumer Lag 等

---

## 10. 常见生产坑

| 坑 | 现象 | 解决 |
|---|---|---|
| **数据丢失** | Producer 不知道丢没丢 | `acks=all` + `min.insync.replicas≥2` + `replication.factor≥3` |
| **重复消费** | 业务被多次执行 | 消费端幂等 / EOS |
| **Rebalance 风暴** | 消费持续停滞 | 调 `session.timeout.ms` / `max.poll.interval.ms` + 静态成员 |
| **消费卡住** | 单条消息处理太慢 | 调大 `max.poll.interval.ms` / 业务异步化 |
| **磁盘满** | 老消息不清理 | 配 `retention.ms` / `retention.bytes` |
| **热点 partition** | 单分区吞吐瓶颈 | 改 key 策略 / 加分区 |
| **ZooKeeper 残留** | 4.x 还用 ZK | 迁到 KRaft（3.9 是最后桥接版）|
| **顺序错乱** | 多分区并行 | 业务 key 哈希到同 partition |
| **consumer 提交顺序错** | 异步 commit 丢 | 用同步 commit 或 commit_async + retry |
| **JVM Full GC** | 延迟突增 | 调大堆（但不能超过物理内存 50%）|

### 10.1 生产 Checklist

```
[ ] KRaft 模式（4.x）或 ZK 模式（3.9，最后桥接）
[ ] 3 controller + N broker，奇数
[ ] 磁盘 SSD/NVMe
[ ] Topic 创建时 replication.factor=3 + min.insync.replicas=2
[ ] Producer acks=all + enable.idempotence=true
[ ] Consumer enable.auto.commit=false + 手动提交
[ ] Consumer isolation.level=read_committed
[ ] 消费端幂等
[ ] partition 数 ≥ consumer 数
[ ] 监控：Consumer Lag / Under Replicated / Request Latency
[ ] 告警：Lag > 阈值 / Under Replicated > 0
[ ] JVM 调优（堆 ≤ 物理内存 50%）
```

---

## 关联笔记

- RabbitMQ 详情：[[01_RabbitMQ笔记]]
- 消息队列对比：[[消息队列选型对比笔记]]
- Demo：`example/mq/`（docker-compose + 生产级 Producer/Consumer + 事务示例）