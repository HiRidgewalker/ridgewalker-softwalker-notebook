---
type: hub
topic: RabbitMQ 生产级
status: created
sources:
  - 旧稿
  - https://www.rabbitmq.com/docs/quorum-queues
  - https://www.rabbitmq.com/docs/dlx
  - https://www.rabbitmq.com/docs/confirms
  - https://www.rabbitmq.com/streams.html
  - https://www.rabbitmq.com/docs/parameters
  - https://www.rabbitmq.com/docs/clustering
  - https://www.rabbitmq.com/docs/management
---

# RabbitMQ 笔记（生产级）

> 工业生产环境下的 RabbitMQ 使用：核心角色 / 交换机 / 队列类型选型 / 可靠性机制 / 死信 / HA / Docker 部署 / 监控与常见生产坑。
> 本笔记旧稿 仅含教程大纲（Hello World / 工作队列 / 发布订阅 / 路由 / 主题 / RPC 六章空壳），已完整重构；旧稿目录已清理，当前以本文为准。
> 单库详情参考官方文档。Demo 代码示例在 `example/mq/`（docker-compose + Publisher Confirms + Consumer Acks + DLX 重试）。

## 目录

1. 定位与核心角色
2. AMQP 核心概念
3. 4 种交换机（Exchange）模式
4. 队列类型选型矩阵：Classic vs Quorum vs Stream
5. 可靠性：Publisher Confirms（生产必须）
6. 可靠性：Consumer Acks（手动 ack + prefetch）
7. 死信机制（DLX）：触发条件 / 配置 / 重试
8. 高可用架构：Quorum Queue + Federation / Shovel
9. Docker 生产部署（3 节点集群）
10. 监控指标 + 常见生产坑

---

## 1. 定位与核心角色

**RabbitMQ** 是一款基于 **AMQP 0.9.1** 协议的开源消息代理（Message Broker），主打：

- **复杂路由**（4 种交换机模式）
- **低延迟**（微秒级）
- **成熟生态**（多语言客户端 + Management UI + Federation）

**不适合**：超大规模日志流（> 百万 TPS）—— 那种场景选 Kafka。

---

## 2. AMQP 核心概念

| 概念 | 角色 | 备注 |
|---|---|---|
| **Producer** | 消息生产者 | 发送消息到 Exchange |
| **Consumer** | 消息消费者 | 从 Queue 拉取消息 |
| **Queue** | 消息队列 | 消息存放地，FIFO |
| **Exchange** | 交换机 | 接收 Producer 消息并按规则路由到 Queue |
| **Binding** | 绑定 | Exchange ↔ Queue 的连接规则 |
| **Routing Key** | 路由键 | Producer 附带，Exchange 据此路由 |
| **Channel** | 信道 | TCP 连接上的逻辑多路复用 |
| **Vhost** | 虚拟主机 | 命名空间隔离 |

**消息流**：`Producer → Exchange → (Binding + Routing Key) → Queue → Consumer`

Producer **永远不直接发到 Queue**，必须经过 Exchange。

---

## 3. 4 种交换机（Exchange）模式

| 类型 | 路由规则 | 典型场景 |
|---|---|---|
| **direct** | 精确匹配 routing key | 点对点任务分发 |
| **topic** | `*` / `#` 模糊匹配 | 日志分级（`log.error.*`） |
| **fanout** | 忽略 routing key，广播到所有绑定 Queue | 广播通知、Pub/Sub |
| **headers** | 匹配 headers 而非 routing key | 复杂条件路由（极少用） |
| ~~consistent hash~~ | 4.0 移除 | — |

### 3.1 direct（点对点）

```python
# Producer 发到 exchange "tasks"，routing_key = "order.created"
channel.basic_publish(exchange="tasks", routing_key="order.created", body=msg)

# Queue 绑定 routing_key = "order.created"
channel.queue_bind(queue="order_queue", exchange="tasks", routing_key="order.created")
```

### 3.2 topic（主题模糊匹配）

- `*` 匹配一个单词
- `#` 匹配零或多个单词（以 `.` 分隔）

```text
# Producer 发：routing_key = "order.created.vip"
# Queue 绑定 routing_key = "order.*.vip"   → 命中
# Queue 绑定 routing_key = "order.#"      → 命中
# Queue 绑定 routing_key = "*.created.*"  → 命中
```

**典型用法**：
- 日志系统：`log.error.*`、`log.warn.*`、`log.*.payment`
- 订单事件：`order.created`、`order.paid`、`order.*.vip`

### 3.3 fanout（广播）

忽略 routing key，绑定到该 Exchange 的所有 Queue 都会收到一份。

**典型用法**：缓存失效广播、配置中心推送。

### 3.4 headers（按 header 路由）

根据消息的 `headers` 字段匹配（`x-match: any` / `all`）。性能差，极少用。

---

## 4. 队列类型选型矩阵：Classic vs Quorum vs Stream

RabbitMQ 4.0 之后，生产队列**必须用 Quorum**（镜像队列已删除）。

| 维度 | Classic | Quorum | Stream |
|---|---|---|---|
| 复制 | ❌ 单节点 | ✅ Raft（3/5/7 节点）| ✅ 副本可配 |
| 持久化 | 可选 | 始终 | 始终 |
| 内存存储 | ✅ | ❌（仅磁盘 + 页缓存）| ❌（仅磁盘 + 页缓存）|
| 投递限制 / Poison 防护 | ❌ | ✅ 默认 20 次（`x-delivery-limit`）| ❌ |
| 死信（DLX）| ✅ | ✅ | ❌ 不支持 |
| 优先级 | ✅ | ✅ 0~31 强制 | ❌ |
| 非破坏性读取（replay）| ❌ | ❌ | ✅ 核心特性 |
| 适用规模 | 临时队列 / 通知 | **默认生产选择** | 大 backlog / Kafka 式 |

### 4.1 选型决策

```
消息需要 replay 或 backlog 很大（> 5M）？
├── 是 → Stream
└── 否 → 需要高可用 + 不丢消息？
         ├── 是 → ✅ Quorum（默认）
         └── 否 → Classic（仅临时/通知）
```

### 4.2 Quorum Queue 声明

```python
import pika

params = pika.ConnectionParameters(host="localhost")
conn = pika.BlockingConnection(params)
ch = conn.channel()

ch.queue_declare(
    queue="orders",
    durable=True,
    arguments={
        "x-queue-type": "quorum",            # 关键
        "x-delivery-limit": 20,              # 失败 20 次进死信
    },
)
```

> **硬限制**：Quorum Queue 一旦声明不可改为 Classic；需要删队列重建。

### 4.3 Quorum 队列规模

- 3 节点集群最多 ~5000 个 Quorum Queue
- 单队列默认 3 副本，**副本数不能超过集群节点数**
- 副本建议奇数：3（容 1 故障）、5（容 2 故障），不超过 7

---

## 5. 可靠性：Publisher Confirms（生产必须）

> **生产环境默认必须开 Publisher Confirms**，否则 publisher 完全不知道消息是否到达 broker。

### 5.1 为什么必须开

`basic_publish` 默认是**异步 fire-and-forget**：

- 网络抖动 → 消息丢失
- broker 队列满 → 消息被丢弃
- broker 写入失败 → 消息丢失

`mandatory` 标志只能解决「路由不到」问题，不能解决「broker 没收到」。

### 5.2 三种可靠性级别

| 机制 | 可靠性 | 性能 | 说明 |
|---|---|---|---|
| 不开 confirms | ❌ 可能丢 | 最快 | 仅调试用 |
| `confirm.select` | ✅ broker 收到 | 折中 | 主流选择 |
| 事务（`tx.select`）| ✅ 强一致 | 慢 100x+ | **不要用**，被 confirms 取代 |

### 5.3 使用示例（pika）

```python
ch.confirm_delivery()  # 开启 confirms

try:
    ch.basic_publish(
        exchange="orders",
        routing_key="order.created",
        body=json.dumps(msg).encode(),
        properties=pika.BasicProperties(delivery_mode=2),  # 2 = 持久化
    )
    print("broker confirmed")
except pika.exceptions.UnroutableError:
    print("路由不到任何队列（用 mandatory + on_return 处理）")
except pika.exceptions.NackError:
    print("broker nack，需要重发或入死信")
```

### 5.4 异步 confirm（生产推荐）

同步 confirm 一条一条等延迟高，生产用**批量 confirm**：

```python
ch.confirm_delivery()
outstanding = []

def on_confirm(frame):
    if frame.method.frames.count == 0:
        # 全部已 confirm
        ...

# 批量发送，最后一次性 wait
for msg in batch:
    ch.basic_publish(...)
outstanding.append(mid)

# 或用 confirm.select 异步模式 + callback
```

### 5.5 性能权衡

- Quorum Queue 持久化消息 fsync 到磁盘后才 confirm，**延迟几百 ms** 是正常的
- 批量发送 + 异步 confirm 提升吞吐
- 不要用 `mandatory` 解决 confirm 问题（mandatory 只管 routing）

---

## 6. 可靠性：Consumer Acks（手动 ack + prefetch）

### 6.1 ack 模式

| 模式 | 行为 | 生产可用？ |
|---|---|---|
| `auto_ack=True` | 消息发到 socket 即认为成功 | ❌ |
| `auto_ack=False` + 手动 `basic_ack` | 处理完再 ack | ✅ 必须 |
| `basic.nack(requeue=True)` | 拒绝并重入队 | ⚠️ 防死循环 |
| `basic.nack(requeue=False)` | 拒绝 → DLX | ✅ 失败处理 |

### 6.2 prefetch（QoS）

`basic.qos(prefetch_count=N)`：限制单个 Consumer 未确认消息数。

**推荐值**：
- 业界常用 **100~300**（吞吐与均衡的最佳点）
- `1` 太保守（高延迟环境浪费吞吐）
- Quorum Queue 单 Consumer 上限 **2000**
- 不要超过 2000（要更高吞吐请用 Stream）

```python
ch.basic_qos(prefetch_count=200)  # 推荐值
```

### 6.3 手动 ack 示例

```python
def on_message(ch, method, properties, body):
    try:
        process(body)                    # 业务处理
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except RetryableError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)   # 可重试错误
    except FatalError:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # 进 DLX
        # 或 ch.basic_reject(...) 单条

ch.basic_consume(queue="orders", on_message_callback=on_message)
```

### 6.4 幂等性（必须）

> **消费端必须做幂等**。RabbitMQ 保证「至少一次」投递，网络抖动 / 消费者崩溃 → 同一条消息可能被投递多次。

幂等方案：

- 数据库唯一索引（最稳）
- Redis SETNX（带 TTL）
- 业务 ID + 已处理集合

### 6.5 顺序保证

- 单队列 + 单消费者：**FIFO 顺序**
- 多消费者并行：顺序**不保证**
- 要严格顺序：用 Stream 的 Single Active Consumer，或拆队列（按业务 ID 路由到固定队列）

---

## 7. 死信机制（DLX）：触发条件 / 配置 / 重试

### 7.1 什么是 DLX

**Dead Letter Exchange**：普通队列中处理失败的消息，自动转发到 DLX，进入「死信队列」供后续处理（重试 / 告警 / 人工兜底）。

### 7.2 触发条件（满足任一）

1. 消息被 `nack` / `reject` 且 `requeue=False`
2. 消息 TTL 过期
3. 队列长度超限
4. Quorum Queue 投递次数超 `x-delivery-limit`

### 7.3 配置方式

**两种方式，推荐 Policy**（可热更新）：

| 方式 | 优 | 劣 |
|---|---|---|
| **Policy**（推荐）| 动态改，运维友好 | 需 `rabbitmqctl` / Management API |
| `x-arguments` 硬编码 | 声明时一次到位 | 改不了，删队列重建 |

```bash
# Policy 方式
rabbitmqctl set_policy DLX "orders.*" \
  '{"dead-letter-exchange":"orders.dlx",
    "dead-letter-routing-key":"orders.dead"}' \
  --apply-to queues --priority 7
```

**队列参数方式**（代码层）：

```python
ch.queue_declare(
    queue="orders",
    durable=True,
    arguments={
        "x-queue-type": "quorum",
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "orders.dead",
    },
)
```

### 7.4 经典重试模式：正常 → 失败 → DLX → 重试队列（带 TTL） → 回到正常

```
[Producer] → orders.exchange ──→ orders (Quorum)
                                    │
                                    │ nack(requeue=False)
                                    ↓
                              orders.dlx (DLX)
                                    │
                                    ↓
                          orders.retry (TTL=30s, x-dead-letter-exchange=orders.exchange)
                                    │
                                    │ TTL 过期自动回退
                                    ↓
                              orders.exchange ──→ orders (Quorum)
                              ↑ 失败次数达 x-delivery-limit → orders.parking (人工兜底)
```

**关键**：retry 队列用 TTL + DLX 形成「延时重试」。

### 7.5 死信消息的 header

死信消息自动加 `x-death`（AMQP 0.9.1）数组，包含：

- 死信次数
- 死信原因（`rejected` / `expired` / `maxlen` / `delivery_limit`）
- 原始 queue / exchange / routing-key

```python
def on_dead_letter(ch, method, properties, body):
    x_death = properties.headers.get("x-death", [])
    for d in x_death:
        print(f"queue={d['queue']} reason={d['reason']} count={d['count']}")
```

### 7.6 死信安全警告

> 默认死信是 `at-most-once`（不可靠）；要 `at-least-once` 必须：
> - Quorum Queue（不是 Classic）
> - `dead-letter-strategy=at-least-once`
> - `overflow=reject-publish`（不是 drop-head）
> - 启用 `stream_queue` feature flag

否则 DLX 转发失败时**消息直接丢**。

---

## 8. 高可用架构

### 8.1 集群（Cluster）

- 多个 broker 节点共享元数据（erlang cookie 同步）
- 队列要么是 Quorum（跨节点复制）要么是 Stream
- 客户端可连任意节点（节点间会转发消息）

### 8.2 Quorum Queue（生产默认）

- 3 节点起步，奇数
- Raft 共识，写入需要 `(N/2)+1` 副本确认
- 故障容忍：3 节点容 1，5 节点容 2

### 8.3 Federation（跨集群复制）

- 把一个集群的队列消息**异步**复制到另一个集群
- 用途：跨地域容灾、跨部门共享消息

### 8.4 Shovel（双向搬运）

- 类似 Federation，但**双向**且可定制过滤规则
- 适合迁移、聚合多个数据源

### 8.5 数据安全等级

| 配置 | 数据安全 |
|---|---|
| Classic Queue + 非持久化 | ❌ 一重启全丢 |
| Classic Queue + 持久化 | ⚠️ 节点故障可能丢 |
| Quorum Queue + publisher confirms | ✅ 强一致 |

---

## 9. Docker 生产部署（3 节点集群）

### 9.1 镜像选择

| 镜像 | 说明 |
|---|---|
| `rabbitmq:4-management` | 包含 Management UI（推荐开发/测试） |
| `rabbitmq:4` | 不带 UI（生产推荐，加 Prometheus 插件） |

### 9.2 docker-compose（3 节点 + 负载均衡）

```yaml
# 单节点 dev 模式（一键起）
version: "3.9"
services:
  rabbitmq:
    image: rabbitmq:4-management
    container_name: rabbitmq
    ports:
      - "5672:5672"     # AMQP
      - "15672:15672"   # Management UI
      - "15692:15692"   # Prometheus metrics
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
```

**3 节点集群**：需要共享 erlang cookie + 节点发现，详见 `example/mq/docker-compose.yml`。

### 9.3 启用 Prometheus 监控

```bash
# 进入容器启用插件
rabbitmq-plugins enable rabbitmq_prometheus
# 访问 http://localhost:15692/metrics
```

---

## 10. 监控指标 + 常见生产坑

### 10.1 关键监控指标

| 指标 | 来源 | 阈值参考 |
|---|---|---|
| `rabbitmq_queue_messages_ready` | queue / 准备投递 | > 10w 告警 |
| `rabbitmq_queue_messages_unacked` | queue / 消费中 | > 0 持续增长 → 消费者卡住 |
| `rabbitmq_connections` | 全局 | 异常增长 → 客户端泄漏 |
| `rabbitmq_channel_messages_unconfirmed` | publisher | > 0 持续增长 → 确认失败 |
| `rabbitmq_process_resident_memory_bytes` | 节点 | 看趋势 |
| `rabbitmq_io_sync_count` | 节点 | fsync 频率 |

### 10.2 常见生产坑

| 坑 | 现象 | 解决 |
|---|---|---|
| **消息丢失** | publisher 不知道 broker 收到没 | 开 Publisher Confirms + 持久化 |
| **重复消费** | 业务侧被多扣款 | 消费端做幂等（唯一索引 / SETNX）|
| **消息堆积** | queue messages_ready 持续增长 | 扩 consumer + 排查慢消费 + 加流控 |
| **消费者卡住** | unacked 持续增长 | prefetch 太大 / 业务有锁等待 |
| **顺序错乱** | 多消费者并行消费同一队列 | 单队列单 consumer，或按 key hash 拆队列 |
| **镜像队列被废弃** | 4.0 后 classic 镜像没了 | 迁到 Quorum Queue |
| **Quorum 节点偶数** | 集群容错能力浪费 | 用 3/5/7，奇数 |
| **prefetch=1 太保守** | 高延迟环境吞吐极低 | 调到 100~300 |
| **mandatory 误用** | 以为能防消息丢失 | mandatory 只管 routing，不管持久化 |
| **DLX 不可靠** | Classic 队列死信丢消息 | Quorum + at-least-once 策略 |

### 10.3 生产 Checklist

```
[ ] 队列类型：是否选了 Quorum（除非有特殊原因）
[ ] Publisher Confirms：是否开启（必须）
[ ] 消息持久化：delivery_mode=2 + 队列 durable=True
[ ] Consumer 手动 ack：auto_ack=False
[ ] Prefetch：调到 100~300
[ ] DLX：是否配置 + at-least-once
[ ] 幂等：消费端是否做了
[ ] 监控：unacked / ready / connections / unconfirmed 都接入了
[ ] 告警：unacked > 阈值 / queue ready > 阈值 / connections 异常
[ ] 集群：3/5 节点，奇数
[ ] Federation：跨地域是否需要
```

---

## 关联笔记

- Kafka 详情：[[02_Kafka笔记]]
- 消息队列对比：[[03_消息队列对比与选型笔记]]
- Demo：`example/mq/`（docker-compose + Publisher Confirms + Consumer Acks + DLX 重试）