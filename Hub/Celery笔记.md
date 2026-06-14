# Celery 笔记

> 原 `文档/Celery.md` 的重新整理版本。聚焦 **实战环境使用 Celery** 与 **生产环境鲁棒性**（避免「任务挂掉没人发现」「任务丢了一直没处理」之类的事故），并在最前面把 Celery 内部对象的工作关系理清。原笔记保留在 `文档/Celery.md` 供回溯。
> 所有可运行代码示例统一放在 `workspace/python/celery/`，本笔记通过 git 远程链接引用；启动 worker / FastAPI 等命令都用 `workspace/.venv/bin/python` 跑。

---

## 0. 前置：Celery 内部对象与工作关系

读懂这张图，后面的所有概念（broker、worker、beat、ack、Canvas、信号…）都能一次串起来。

### 0.1 核心对象清单

| 对象 | 角色 | 谁创建 | 谁持有 |
| --- | --- | --- | --- |
| `Celery` Application | 入口对象，统一配置、注册任务、暴露 `task`、`send_task` | 业务代码里 `Celery(...)` 构造 | 全局唯一（worker / producer / beat 都要 import） |
| `Task` | 任务的"模板"（函数 + 装饰器配置） | `@app.task` 把普通函数包成 Task | 存在 `app.tasks` 注册表，worker 启动时加载 |
| `AsyncResult` | 任务发出去后返回的"凭据"，可查状态/取结果 | `task.delay()` / `apply_async()` 内部创建 | 由 backend（Redis/DB）持久化 |
| **Producer**（调用方） | 业务进程（Web / 脚本），`task.delay()` 把消息发到 broker | 业务代码 | 每个发任务的进程都是 producer |
| **Broker**（消息中间件） | 暂存待执行的消息队列（Redis / RabbitMQ / SQS） | 外部服务 | 不属于 Celery 进程；Celery 只是 client |
| **Worker** | 真正执行任务的后台进程 | 命令行 `celery -A xxx worker` 启动 | 一个应用可有多个 worker，多机部署 |
| **Beat** | 定时任务调度器，按 schedule 把任务发到 broker | 命令行 `celery -A xxx beat` 启动 | 通常和 worker 分进程；多机只起一个 |
| **Backend**（结果存储） | 存任务状态与返回值，方便查 | 外部服务（Redis/DB） | 任务结束后写；查 `AsyncResult.state/.get()` 时读 |
| **Canvas** | 任务编排原语（chain/group/chord/chord_error） | 在业务代码里把 Task 拼成工作流 | 由 producer 拆成多条消息发到 broker |
| **Signals** | Celery 内部事件钩子（`task_prerun` / `task_postrun` / `task_failure` / `worker_ready`…） | 业务代码 `@signals.xxx.connect` 注册 | 进程内回调；可推 Sentry / 告警 / 指标 |

### 0.2 一次任务调用，数据走过的路径

```
业务进程 (Producer)                                  Worker 进程
─────────────────                                   ────────────
task.delay(arg)                                                  
  └─ 序列化 (json/pickle)              ┌─ 进程隔离，prefork 池多进程
  └─ 发到 Broker  ◀───── Redis/RabbitMQ ─────▶ Worker 从 Broker 拉取
       (消息体: task_name, args, kwargs,                  │
        task_id, eta, countdown, ...)                    ▼
  └─ 返回 AsyncResult (task_id)         │   加载 Task 模板，按名字 dispatch
                                          │   触发 task_prerun 信号
       (可选) 任务结束                   ▼
       Backend ◀─── 写状态 + 返回值 ──── 执行 task 主体
       Redis/DB
                                          │   触发 task_postrun / task_failure 信号
                                          ▼
       业务进程 .get() ◀─── 读 backend ────  返回 AsyncResult
```

### 0.3 任务状态机（重点：判读 `.state` 的返回值）

```
              发到 broker 但 worker 还没拿到
                          │
                          ▼
                      PENDING
                          │
                  worker 拿到 / 开始执行
                          ▼
                       STARTED
                          │
              ┌───────────┼─────────────┐
              ▼           ▼             ▼
          SUCCESS     FAILURE        RETRY ────▶ (回 STARTED)
              │           │             │
              │           │             └─▶ REVOKED（被撤销）
              │           └────────▶ REVOKED
              ▼
        (Backend 存结果)
```

补充说明：

- **PENDING 不一定是"没执行"**：worker 还没拿到任务 / `task_always_eager` 关闭前都会显示 PENDING；判定"超时"时要结合 `task_id` 是否在 broker 里存在。
- **FAILURE 不会自动重试**：默认行为，需要 `autoretry_for=` 或手动 `self.retry()`。
- **RETRY 是合法状态**：客户端查时要按业务判断是否还要等。

### 0.4 进程拓扑（生产怎么部署）

```
┌─────────────┐    ┌─────────────┐
│ Web 进程 #1 │    │ Web 进程 #2 │   …  多个 producer，水平扩展
│ (FastAPI)   │    │             │
└──────┬──────┘    └──────┬──────┘
       │ task.delay()      │
       └────────┬──────────┘
                ▼
        ┌───────────────┐
        │   Broker      │   Redis / RabbitMQ，单点或集群
        └──────┬────────┘
               │ 拉取
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Worker #1    │  │ Worker #2    │  …  独立进程，可多机
│ (prefork 池) │  │              │
└──────┬───────┘  └──────┬───────┘
       │ 写结果          │
       └───────┬─────────┘
               ▼
        ┌───────────────┐
        │   Backend     │   Redis / DB
        └───────────────┘

       ┌──────────────┐
       │ Beat 调度器   │   多机部署时只能起一个；用 celery-redbeat 解决高可用
       └──────┬───────┘
              │ 定时触发
              ▼
           Broker
```

### 0.5 容易混淆的几对概念

| 概念 A | 概念 B | 区别 |
| --- | --- | --- |
| `task.delay(arg)` | `task.apply_async((arg,))` | delay 是 apply_async 的简写；后者能传 `countdown/eta/queue/priority/expires` |
| `task_acks_late=True` | `task_reject_on_worker_lost=True` | 前者：执行完才 ack；后者：worker 崩溃时把任务放回队列（**两件套必须同时开**，否则仍可能丢） |
| `task_time_limit` | `task_soft_time_limit` | 硬超时（worker 直接 kill 进程）vs 软超时（抛 `SoftTimeLimitExceeded` 让你清理） |
| `worker_concurrency` | `worker_prefetch_multiplier` | 并发执行槽位数 vs 每个槽位预取任务数；总预取 = 二者相乘 |
| `autoretry_for=` | `self.retry()` | 装饰器自动重试 vs 任务体里手动重试（精细控制时点） |
| `chain` | `chord` | chain 是顺序；chord = group + 回调，group 全成功后调回调 |
| `task_eager_propagates` | `task_always_eager` | 前者：Eager 模式下异常往上抛；后者：Eager 模式开关（生产必须关） |
| `task.routes` | `task_queues` | 前者：按任务名映射到队列；后者：声明队列实体（名字、exchange、routing_key） |

---

## 1. 速查总览

### 1.1 是什么

Celery 是 Python 生态最主流的**分布式任务队列**。把"调用函数"和"执行函数"解耦：业务进程只负责把任务消息扔到 broker，后台 worker 进程拉取并执行；任务状态与结果由 backend 持久化。

### 1.2 什么时候用

| 场景 | 适不适合 Celery |
| --- | --- |
| 发送邮件 / 推送 / 短信 | ✅ 经典场景 |
| 异步处理 HTTP 上传（生成缩略图、转码） | ✅ |
| 定时任务（清理、对账、报表） | ✅ 用 Beat |
| 长任务编排（多步骤、可重试、有回调） | ✅ 用 Canvas |
| 实时低延迟 RPC（要求 < 10ms 响应） | ❌ 走消息队列天然有延迟 |
| 单进程内异步并发 | ❌ 用 `asyncio` / `concurrent.futures` |
| 大数据流式处理 | ❌ 用 Kafka / Flink |
| 短任务（< 100ms）且量大 | ⚠️ 队列往返开销比函数本身大，合并批次或换方案 |

### 1.3 安装

```bash
# 基础
uv add celery

# 带 Redis broker / backend 支持
uv add 'celery[redis]'

# 带 RabbitMQ 支持
uv add 'celery[amqp]'

# Sentinel / 集群 Redis
uv add 'celery[sentinel]'
```

### 1.4 最小可运行项目

```python
# app.py
from celery import Celery

app = Celery(
    "demo",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

@app.task
def add(x, y):
    return x + y
```

启动 worker：

```bash
workspace/.venv/bin/celery -A app worker -l info
```

发任务：

```python
from app import add
r = add.delay(1, 2)
print(r.get(timeout=10))      # 3
```

### 1.5 demo 总览（4 个文件）

| Demo | 涵盖 | 链接 |
| --- | --- | --- |
| `celery_basics.py` | 任务定义、调用（delay / apply_async / countdown / eta / expires）、状态机、`self.request` 链路追踪 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_basics.py) |
| `celery_canvas.py` | chain / group / chord / 嵌套 / chord_error | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_canvas.py) |
| `celery_robustness.py` | acks_late、软/硬超时、自动重试 + 退避 + 抖动、手动重试、过期、限速、信号系统 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_robustness.py) |
| `celery_fastapi_integration.py` | FastAPI 提交任务 + 查状态端点、生产配置、`lru_cache` 单例 | [查看](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_fastapi_integration.py) |

> 4 个 demo 全部默认 Eager 模式（`task_always_eager=True`），不需要真起 broker，`uv run python` 即可跑通；生产部署把这一行删掉。

---

## 2. 实战模式速查表

### 2.1 任务定义

```python
# 显式命名（推荐，避免模块路径变化导致任务名漂移）
@app.task(name="demo.add")
def add(x, y):
    return x + y

# bind=True 注入 self，可拿 task_id / 主动 retry
@app.task(bind=True, name="demo.long_task")
def long_task(self):
    print(self.request.id)        # 当前 task_id
    print(self.request.retries)  # 已重试次数
```

完整 demo：<https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_basics.py>

### 2.2 任务调用（三种姿势）

```python
# 1. delay：最简
r = add.delay(1, 2)

# 2. apply_async：完整控制
r = add.apply_async(
    args=(1, 2),
    countdown=10,                 # 10 秒后执行
    # eta=datetime.now() + timedelta(minutes=5),   # 绝对时间
    # expires=datetime.now() + timedelta(hours=1), # 过期丢弃
    queue="priority",             # 进指定队列（RabbitMQ 有效）
    priority=9,                   # 队列内优先级（RabbitMQ 有效）
)

# 3. send_task：按名字发，绕过本地注册（适合跨服务）
from app import app
r = app.send_task("demo.add", args=[1, 2])
```

### 2.3 取结果 / 查状态

```python
r = add.delay(1, 2)

r.id                # task_id（立刻可拿）
r.status            # "PENDING" / "STARTED" / "SUCCESS" / "FAILURE" / "RETRY"
r.ready()           # 是否完成
r.successful()      # 是否成功
r.failed()          # 是否失败
r.get(timeout=10)   # 阻塞拿结果，最多等 10 秒
r.get(propagate=False)  # 失败不抛，返回异常对象
r.traceback         # 失败时的堆栈（字符串）

# AsyncResult 用 task_id 重建（跨进程查）
r2 = add.AsyncResult(r.id)
print(r2.state)
```

### 2.4 任务状态机速查

```
PENDING → STARTED → SUCCESS
                   → FAILURE
                   → RETRY → ... → RETRY → SUCCESS / FAILURE
                   → REVOKED（被撤销）
```

- **PENDING 不等于"没执行"**：broker 里还有，但 worker 还没拉到；判定"卡死"要结合 `task_id` 在 broker 是否存在。
- **FAILURE 不自动重试**：默认行为，要 `autoretry_for=` 或手动 `self.retry()`。

### 2.5 任务链路追踪（Canvas 嵌套时排查关键）

```python
@app.task(bind=True)
def show_ids(self):
    print("task_id:    ", self.request.id)
    print("parent_id:  ", self.request.parent_id)   # 直接上游
    print("root_id:    ", self.request.root_id)     # 整条工作流根
    print("group_index:", self.request.group_index) # 在 group/chord 里的位置
```

### 2.6 装饰器常用参数

| 参数 | 作用 |
| --- | --- |
| `name` | 显式任务名（避免模块路径漂移） |
| `bind=True` | 注入 `self`，可访问 `self.request` 和 `self.retry()` |
| `autoretry_for=(Exc1, Exc2)` | 这些异常自动重试 |
| `retry_backoff=True` | 指数退避（1s, 2s, 4s, 8s...） |
| `retry_backoff_max=60` | 退避上限（秒） |
| `retry_jitter=True` | 加随机抖动（防雷击） |
| `max_retries=3` | 最多重试次数 |
| `acks_late=True` | 执行完才 ack（与全局配置互覆盖） |
| `rate_limit="10/m"` | 限流（每分钟 10 次） |
| `soft_time_limit=300` | 软超时（任务级） |
| `time_limit=600` | 硬超时（任务级） |
| `queue="xxx"` | 默认进哪个队列 |
| `ignore_result=True` | 不存结果（省 backend） |

### 2.7 手动重试（精细控制时点）

```python
@app.task(bind=True, max_retries=3, default_retry_delay=10)
def manual_retry_task(self, x):
    try:
        if x < 0:
            raise ValueError("x must be non-negative")
        return x * 2
    except ValueError as exc:
        # 主动重试：1 秒后再试，丢弃原异常堆栈
        raise self.retry(exc=exc, countdown=1, max_retries=3)
```

### 2.8 Canvas：chain / group / chord / 嵌套

```python
from celery import chain, group, chord

# chain：顺序执行（结果传给下一个）
chain(step1.s(5), step2.s(), step3.s())()        # step1(5)→step2(6)→step3(12) = 9

# group：并行执行
group(double.s(1), double.s(2), double.s(3))()   # [2, 4, 6]

# chord：group + 回调（group 全成功后调 collect）
chord(group(double.s(1), double.s(2), double.s(3)), collect.s())()
# → collect([2, 4, 6]) 一次性收到

# 嵌套：chain + group 组合
chain(
    step1.s(5),
    step2.s(),
    split_10.s(),                    # 把单值拆成 list
    group(double.s(), double.s()),   # 并行处理
    collect.s(),                     # 收尾
)()
```

完整 demo（含 `chord.on_error` 失败回调）：<https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_canvas.py>

### 2.9 信号系统（生产告警 / 监控的关键钩子）

```python
from celery import signals

@signals.task_prerun.connect
def _prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
    print(f"[start] {task.name}[{task_id}] args={args}")

@signals.task_postrun.connect
def _postrun(sender=None, task_id=None, task=None, retval=None, state=None, **kw):
    print(f"[done]  {task.name}[{task_id}] state={state}")

@signals.task_failure.connect
def _failure(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kw):
    # 生产：推 Sentry / 告警 / 写失败日志
    print(f"[FAIL]  {sender.name}[{task_id}] {exception}")

@signals.task_retry.connect
def _retry(sender=None, request=None, reason=None, **kw):
    print(f"[retry] {sender.name}[{request.id}] reason={reason}")

@signals.worker_ready.connect
def _ready(sender=None, **kw):
    print(f"worker {sender} ready")
```

完整 demo：<https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_robustness.py>

### 2.10 消息路由（多队列）

```python
from kombu import Queue

app.conf.task_queues = (
    Queue("default"),
    Queue("priority",    queue_arguments={"x-max-priority": 10}),  # RabbitMQ 优先级
    Queue("slow",        routing_key="slow.#"),
)

app.conf.task_routes = {
    "demo.send_email":      {"queue": "default"},
    "demo.generate_report": {"queue": "slow", "routing_key": "slow.report"},
    "*":                    {"queue": "default"},  # 兜底
}
```

worker 按需监听：

```bash
celery -A app worker -Q default,priority -l info
```

### 2.11 Eager 模式（仅测试 / demo）

```python
app.conf.task_always_eager = True   # 任务同步执行，result.get() 立即可拿
app.conf.task_eager_propagates = True  # 异常往上抛，便于测试
```

> **生产必须关闭**。Eager 模式下 `countdown/eta/routing` 都失效，多用于本地调试和单元测试。

---

## 3. 生产环境鲁棒性

> 目标：避免「任务挂掉没人发现」「任务丢了一直没处理」「Worker 假死但服务看着正常」之类的事故。下面每一条都对应一个常见踩坑点。

### 3.1 任务不丢：acks_late + reject_on_worker_lost

**核心问题**：默认行为下 worker 拿到任务就 ack，**进程崩溃时任务就丢了**。

```python
app.conf.task_acks_late = True                  # 执行完才 ack
app.conf.task_reject_on_worker_lost = True      # worker 崩溃时把任务放回 broker
```

**必须两件套同时开**，否则：
- 只开 `acks_late`：崩溃后任务还在"已 ack 之前"状态，broker 不会重发。
- 只开 `reject_on_worker_lost`：默认"拿到就 ack"，崩溃时已经 ack 了，broker 不知道要重发。

完整 demo：<https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/python/celery/celery_robustness.py>

### 3.2 超时控制：软超时 + 硬超时

```python
app.conf.task_soft_time_limit = 300    # 5 分钟：抛 SoftTimeLimitExceeded，让任务清理
app.conf.task_time_limit = 600         # 10 分钟：worker 直接 kill 进程
```

任务体内捕获软超时做清理：

```python
@app.task(bind=True, soft_time_limit=3, time_limit=5)
def long_task(self):
    try:
        do_work()
    except SoftTimeLimitExceeded:
        cleanup()        # 关连接、删临时文件
        raise
```

**生产建议**：每个任务都设 `time_limit`（硬上限），否则单个任务死循环会拖死整个 worker 池。

### 3.3 自动重试 + 指数退避 + 抖动

```python
@app.task(
    bind=True,
    autoretry_for=(requests.RequestException, TimeoutError),  # 这些异常自动重试
    retry_backoff=True,        # 指数退避：1s, 2s, 4s, 8s...
    retry_backoff_max=60,      # 退避上限 60 秒
    retry_jitter=True,         # 加随机抖动（避免雪崩）
    max_retries=5,             # 最多 5 次
    acks_late=True,
)
def call_external_api(self, url):
    return requests.get(url, timeout=5)
```

**为什么需要 jitter**：多个任务同时失败时，没有抖动会让它们在同一时刻一起重试，把下游服务打挂。

### 3.4 手动重试（精细控制）

```python
@app.task(bind=True, max_retries=3)
def with_logic(self, x):
    try:
        result = step1(x)
        if not result.ok:
            # 业务判断要重试，不是异常驱动
            raise self.retry(countdown=2 ** self.request.retries)
        return result
    except RecoverableError as exc:
        raise self.retry(exc=exc, countdown=10, max_retries=5)
```

### 3.5 限速（防打挂下游）

```python
# 任务级
@app.task(rate_limit="10/m")
def rate_limited_task():
    ...

# 全局默认
app.conf.task_default_rate_limit = "100/s"
```

**注意**：限速是按任务名 / worker 维度算的；多 worker 时实际并发可能超过限速值（每个 worker 各自独立计数）。

### 3.6 任务过期

```python
app.conf.task_expires = 3600       # broker 里的消息 1 小时没被消费就丢弃
# 或单条任务
add.apply_async((1, 2), expires=3600)
```

**用途**：把"过时的任务"自动清掉，避免队列堆积；典型场景：用户取消订单后，对应的"30 分钟后取消"任务没必要再执行。

### 3.7 死信处理（多次失败后归档）

Celery 不直接提供 DLQ，但可以这样接：

```python
@app.task(bind=True, max_retries=3, autoretry_for=(RecoverableError,))
def with_dead_letter(self, payload):
    try:
        do_work(payload)
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            # 真的救不活了，写死信队列
            dead_letter_queue.apply_async((payload, str(exc), self.request.id))
            return
        raise
```

`dead_letter_queue` 可以是另一个 task，进专门的队列由人工 / 定时任务巡检。

### 3.8 监控：Metrics + 健康检查

**指标导出**（推荐用 `celery-exporter` 走 Prometheus）：

```bash
uv add celery-exporter
celery-exporter --broker-url=redis://localhost:6379/0
```

**主动告警**（信号 + 阈值）：

```python
@signals.task_failure.connect
def alert_on_failure(sender=None, task_id=None, exception=None, **kw):
    if "critical" in sender.name:
        alert_oncall(f"CRITICAL task {sender.name} failed: {exception}")

@signals.worker_ready.connect
def on_ready(sender=None, **kw):
    # worker 重启场景：发心跳，监控系统能感知重启
    heartbeat(f"worker {sender} ready")
```

**Flower**（Web UI，看 worker / 任务状态）：

```bash
uv add flower
celery -A app flower --port=5555
# 访问 http://localhost:5555
```

### 3.9 进程管理（防"worker 假死"）

| 工具 | 适用 | 备注 |
| --- | --- | --- |
| systemd | 单机 / 虚拟机 | 最稳，自动重启、看日志（详见 4.1） |
| supervisord | 单机 / 容器内 | 配置简单，UI 友好 |
| docker-compose | 容器化 | worker / beat / flower 分别一个 service |
| Kubernetes + celery-redbeat | 大规模 | beat 必须用 `celery-redbeat` 走 Redis 才支持多副本 |

**worker 假死的常见原因**：
- 任务卡在第三方调用（无超时）→ 配 `time_limit`
- 内存泄漏 → 配 `worker_max_tasks_per_child=1000` 让 worker 定期自杀
- 死锁 / GIL 卡死 → 看 worker 日志、`py-spy dump <pid>`

### 3.10 worker 优雅关闭

```bash
# 优雅停止（处理完当前任务再退）
celery -A app control shutdown

# 撤销某个任务
celery -A app control revoke <task_id>

# 重启 worker 池（不丢任务）
celery -A app control pool_restart
```

**生产部署**：用 systemd / k8s 时，停止前会发 SIGTERM，Celery 默认会处理掉当前任务再退出。

### 3.11 worker 内存保护

```python
# 处理 1000 个任务后自杀重建（防内存泄漏）
app.conf.worker_max_tasks_per_child = 1000

# 处理 100 个任务或 30 分钟后自杀
app.conf.worker_max_memory_per_child = 200 * 1024  # KB
```

### 3.12 序列化与安全

```python
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]        # 拒绝 pickle（防 RCE）
```

> `pickle` 序列化支持任意 Python 对象，但 broker 里的消息可被恶意构造，**生产必须用 json**。如果必须用 pickle，确保 broker 网络隔离。

---

## 4. 部署与运维

### 4.1 systemd 部署（单机 / 虚拟机）

**worker unit**（`/etc/systemd/system/celery-worker.service`）：

```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/srv/myapp
Environment="PATH=/srv/myapp/workspace/.venv/bin"
ExecStart=/srv/myapp/workspace/.venv/bin/celery \
    -A myapp.celery_app worker \
    -l info \
    -Q default,priority \
    --concurrency=4
Restart=always
RestartSec=5
StandardOutput=append:/var/log/celery/worker.log
StandardError=append:/var/log/celery/worker.err

[Install]
WantedBy=multi-user.target
```

**beat unit**（单独起一个）：

```ini
# celery-beat.service
ExecStart=/srv/myapp/workspace/.venv/bin/celery \
    -A myapp.celery_app beat \
    -l info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now celery-worker celery-beat
sudo systemctl status celery-worker
```

### 4.2 docker-compose 部署

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    restart: always

  worker:
    build: .
    command: celery -A myapp.celery_app worker -l info -Q default,priority --concurrency=4
    depends_on: [redis]
    restart: always
    volumes:
      - ./logs/celery:/var/log/celery
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1

  beat:
    build: .
    command: celery -A myapp.celery_app beat -l info --scheduler celery_redbeat.RedBeatScheduler
    depends_on: [redis]
    restart: always
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

  flower:
    build: .
    command: celery -A myapp.celery_app flower --port=5555
    ports: ["5555:5555"]
    depends_on: [redis, worker]
```

```bash
docker compose up -d worker beat flower
docker compose logs -f worker
```

### 4.3 Kubernetes 部署（多副本 + Beat 高可用）

**worker 部署**（无状态，水平扩展）：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 4
  selector:
    matchLabels: { app: celery-worker }
  template:
    metadata:
      labels: { app: celery-worker }
    spec:
      containers:
        - name: worker
          image: myapp:latest
          command: ["celery", "-A", "myapp.celery_app", "worker", "-l", "info", "--concurrency=4"]
          env:
            - name: CELERY_BROKER_URL
              value: redis://redis:6379/0
          resources:
            requests: { cpu: "500m", memory: "512Mi" }
            limits:   { cpu: "2",    memory: "2Gi" }
          livenessProbe:
            exec:
              command: ["celery", "-A", "myapp.celery_app", "inspect", "ping"]
            initialDelaySeconds: 30
            periodSeconds: 30
```

**beat 部署**（用 `celery-redbeat` 走 Redis，多副本也只有一个真调度）：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-beat
spec:
  replicas: 1    # redbeat 内置分布式锁，理论上可以 > 1，但通常 1 个够
  selector:
    matchLabels: { app: celery-beat }
  template:
    metadata:
      labels: { app: celery-beat }
    spec:
      containers:
        - name: beat
          image: myapp:latest
          command:
            - celery
            - -A
            - myapp.celery_app
            - beat
            - -l
            - info
            - --scheduler=celery_redbeat.RedBeatScheduler
          env:
            - name: CELERY_BROKER_URL
              value: redis://redis:6379/0
```

`celery-redbeat` 依赖：

```bash
uv add celery-redbeat
```

### 4.4 常用运维命令速查

```bash
# Worker
celery -A app worker -l info                        # 启动
celery -A app worker -l info --detach               # 后台启动
celery -A app worker -l info -Q queue1,queue2       # 监听指定队列
celery -A app worker -l info -c 4                   # 并发数 4
celery -A app worker -l info -P eventlet            # 指定池

celery -A app control shutdown                      # 优雅停止
celery -A app control pool_restart                  # 重启 worker 池
celery -A app control revoke <task_id>              # 撤销任务

# 状态查看
celery -A app inspect active                        # 正在执行
celery -A app inspect registered                    # 已注册任务
celery -A app inspect stats                         # 统计
celery -A app inspect reserved                      # 预取中
celery -A app inspect scheduled                      # 定时中
celery -A app status                                # 所有 worker

# Beat
celery -A app beat -l info
celery -A app beat -l info --detach

# 队列维护
celery -A app purge                                 # 清空所有队列（危险！）

# 任务追踪
celery -A app result <task_id>                      # 查单个任务结果
```

---

## 5. 常见坑 + 官方文档链接

### 5.1 任务没跑起来 / `result.get()` 阻塞

排查顺序：

1. **worker 起没起**：`ps aux | grep celery` / 看 `celery -A app inspect ping`
2. **broker 通不通**：`redis-cli ping` 或 `rabbitmqctl status`
3. **任务名对不对**：worker 日志会显示 `registered tasks`；不匹配就 `UNREGISTERED`
4. **队列对不对**：worker 启动的 `-Q` 和 `apply_async(queue=...)` 必须匹配
5. **serializer 匹配**：`task_serializer` 和 `accept_content` 要和消息一致
6. **Eager 模式没关**：生产开了 Eager，`task.delay()` 同步执行但不真发到 broker

### 5.2 任务执行了但结果拿不到

- 没配 `result_backend`：配置 `app.conf.result_backend = ...`
- `result_expires` 过期：默认 1 天，过了就清掉
- `ignore_result=True`：任务没存结果
- `result.get()` 阻塞超时：`get(timeout=10)` 后看 `r.state`

### 5.3 任务重复执行

- **`acks_late=False` + worker 崩溃**：消息没 ack 又被重发
- **`task_reject_on_worker_lost=False`**：worker 崩溃时 broker 不知道要重发
- **ack 之后崩溃 + 业务没幂等**：执行完任务再崩，结果 ack 没成功，broker 重发 → 业务必须幂等
- **多个 worker + 队列绑定错**：任务被两个 worker 同时拉

> **核心**：所有可能重试 / 重发的任务，**业务必须幂等**（用 `task_id` 去重、数据库唯一索引等）。

### 5.4 内存泄漏 / worker 越来越慢

- 配 `worker_max_tasks_per_child=1000` 定期重建
- 配 `worker_max_memory_per_child` 触发自杀
- 排查：装 `memray` / `tracemalloc` 找泄漏点

### 5.5 time_zone 错乱

```python
app.conf.timezone = "Asia/Shanghai"
app.conf.enable_utc = True
```

任务里 `datetime.now()` 用 naive，序列化到 broker 后 worker 解读会差 8 小时。**统一用 `datetime.now(timezone.utc)` 或 `django.utils.timezone.now()`**。

### 5.6 django-celery-beat 数据库迁移

```bash
python manage.py migrate django_celery_beat
```

定时任务存在数据库的 `django_celery_beat_periodictask` 表里，修改完调度记得重启 beat。

### 5.7 "我的任务没限住"（rate_limit 没生效）

- 限速是**单 worker 维度**的，3 个 worker 各 10/m 实际是 30/m
- 任务级 `@app.task(rate_limit="10/m")` 优先级高于全局 `task_default_rate_limit`

### 5.8 Beat 多实例

Celery 自带 beat 只能起一个，多机部署会乱发。两种方案：

1. **起一个 beat 容器 / 进程**，其他机器不启 beat
2. **用 `celery-redbeat`**：所有 beat 都注册到 Redis 的分布式锁，谁抢到谁发

### 5.9 import 任务失败（"UNREGISTERED"）

- 装饰器没 import 到：worker 启动要 `import xxx.tasks`，或者用 `app.autodiscover_tasks(["xxx"])`
- 任务名变了：之前 `app.send_task("old.name")` 失败；用显式 `@app.task(name="stable.name")`

### 5.10 官方文档链接

- Celery 总览：<https://docs.celeryq.dev/en/stable/index.html>
- 入门教程：<https://docs.celeryq.dev/en/stable/getting-started/introduction.html>
- 任务定义：<https://docs.celeryq.dev/en/stable/userguide/tasks.html>
- Canvas：<https://docs.celeryq.dev/en/stable/userguide/canvas.html>
- 信号：<https://docs.celeryq.dev/en/stable/userguide/signals.html>
- Beat：<https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html>
- 路由：<https://docs.celeryq.dev/en/stable/userguide/routing.html>
- 监控：<https://docs.celeryq.dev/en/stable/userguide/monitoring.html>
- 配置全表：<https://docs.celeryq.dev/en/stable/userguide/configuration.html>
- django-celery-beat：<https://django-celery-beat.readthedocs.io/>
- celery-redbeat：<https://github.com/sibson/celery-redbeat>
- Flower：<https://flower.readthedocs.io/>
- celery-exporter：<https://github.com/danihodovic/celery-exporter>
