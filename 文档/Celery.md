## celery文章
[两万字长文让你彻底掌握celery](https://mp.weixin.qq.com/s/2EE2OIO3mE-FJV1rhkNn6A)
[django结合celery使用](https://mp.weixin.qq.com/s/jemAdhpxZ0mbYJBx7ijeRw)
## celery架构
![[image-18.png]] 
- producer：生产者，专门用来生产任务（task）；
    
- celery beat：任务调度器，调度器进程会读取配置文件的内容，周期性地将配置文件里面到期需要执行的任务发送给消息队列，说白了就是生产定时任务；
    
- broker：任务队列，用于存放生产者和调度器生产的任务。一般使用消息队列或者 Redis 来存储，当然具有存储功能的数据库也是可以的。这一部分是 celery 所不提供的，需要依赖第三方。作用就是接收任务，存进队列；
    
- worker：任务的执行单元，会将任务从队列中顺序取出并执行；
    
- backend：用于在任务结束之后保存状态信息和结果，以便查询，一般是数据库，当然只要具备存储功能都可以作为 backend；

启动worker
```shell
celery -A app worker -l info -P eventlet

# 常见扩展参数
-n worker1@%h     # 指定 worker 名称
-Q queue1,queue2  # 指定监听的队列
-c 4              # 并发数（默认=CPU核数）
-P eventlet       # 指定并发模式（可选：prefork, solo, eventlet, gevent）
--logfile=/path/to/worker.log
```

启动定时任务
```shell
celery -A tasks.period_task1.py beat -l info

# 常见扩展参数
--logfile=/path/to/beat.log
--scheduler django_celery_beat.schedulers:DatabaseScheduler
```
![[image-19.png]]
## celery参数详解
`celery.config_from_object`

![image-20251210145029121](file://D:\desktop\celery%E7%9F%A5%E8%AF%86%E7%82%B9%E5%BF%AB%E9%80%9F%E6%8E%8C%E6%8F%A1\assets\image-20251210145029121.png?lastModify=1765983249)
### 配置和默认值

![image-20251210145217745](file://D:\desktop\celery%E7%9F%A5%E8%AF%86%E7%82%B9%E5%BF%AB%E9%80%9F%E6%8E%8C%E6%8F%A1\assets\image-20251210145217745.png?lastModify=1765983249)
默认自动加载该配置文件
### 示例配置文件

![image-20251210145351143](file://D:\desktop\celery%E7%9F%A5%E8%AF%86%E7%82%B9%E5%BF%AB%E9%80%9F%E6%8E%8C%E6%8F%A1\assets\image-20251210145351143.png?lastModify=1765983249)
### 配置变量名称小写

![image-20251210145605019](file://D:\desktop\celery%E7%9F%A5%E8%AF%86%E7%82%B9%E5%BF%AB%E9%80%9F%E6%8E%8C%E6%8F%A1\assets\image-20251210145605019.png?lastModify=1765983249)
### 消息路由
重要的参数
 `task_queues`
 `task_routes`
 `worker_direct`
 `task_create_missing_queues`
 `task_create_missing_queue_type`
 `task_create_missing_queue_exchange_type`
 `task_default_queue`
 `task_default_queue_type`
 `task_default_exchange`
 `task_default_exchange_type`
 `task_default_routing_key`
## worker
#### `worker_prefetch_multiplier`
> 要限制代理一次只能向每个进程传递一条消息，请将 [`worker_prefetch_multiplier`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-worker_prefetch_multiplier) 设置为 1。将该设置更改为 0 将允许 worker 继续消费任意数量的消息。
## Celery的常用命令：
### Worker相关命令
**启动Worker：**
```bash
celery -A your_project worker -l info
# -A 指定应用名称
# -l 指定日志级别（debug/info/warning/error/critical）

# 后台启动
celery -A your_project worker -l info --detach

# 指定并发数
celery -A your_project worker -l info --concurrency=4

# 指定队列
celery -A your_project worker -Q queue1,queue2 -l info
```
**停止Worker：**
```bash
# 优雅停止（处理完当前任务）
celery -A your_project control shutdown

# 或直接使用进程信号
pkill -9 -f 'celery worker'

# 如果使用了--detach，可以找到进程ID后kill
ps aux | grep celery
kill -TERM <pid>  # 优雅停止
kill -9 <pid>     # 强制停止
```
**查看Worker状态：**
```bash
# 查看活跃的workers
celery -A your_project inspect active

# 查看已注册的任务
celery -A your_project inspect registered

# 查看worker统计信息
celery -A your_project inspect stats

# 查看所有workers
celery -A your_project status

# 实时监控
celery -A your_project events
```
### Beat（定时任务）相关命令
**启动Beat调度器：**
```bash
celery -A your_project beat -l info

# 后台启动
celery -A your_project beat -l info --detach

# 指定schedule数据库文件
celery -A your_project beat -l info --schedule=/path/to/celerybeat-schedule
```
**同时启动Worker和Beat：**
```bash
celery -A your_project worker -B -l info
# -B 或 --beat 表示同时启动beat
```
**停止Beat：**
```bash
pkill -f 'celery beat'
```
### 其他实用命令
**清空队列：**
```bash
celery -A your_project purge
```
**查看队列中的任务：**
```bash
celery -A your_project inspect reserved
celery -A your_project inspect scheduled
```
**撤销任务：**
```bash
celery -A your_project control revoke <task_id>
```
**重启Worker（重新加载代码）：**
```bash
celery -A your_project control pool_restart
```
Celery Redis配置
```python
#!/usr/bin/env python  
# _*_ coding: utf-8 _*_  
  
import os  
from email.policy import default  
  
from celery import Celery  
from kombu import Queue  
  
from main.config import SYS_NAME  
# Set the default Django settings module for the 'celery' program.  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')  
  
app = Celery('celery',  
             broker="redis://:root@192.168.14.131:6379/0",  
             # backend="",  
             broker_transport_options={  
                 'global_keyprefix': f"{SYS_NAME}_",  
             },  
             result_backend_transport_options={  
                 'global_keyprefix': f"{SYS_NAME}_",  
             })  
  
# Using a string here means the worker doesn't have to serialize  
# the configuration object to child processes.  
# - namespace='CELERY' means all celery-related configuration keys  
#   should have a `CELERY_` prefix.  
app.config_from_object('django.conf:settings', namespace='CELERY')  
  
# 默认配置  
app.conf.update(  
    # 任务的最大执行时间  
    task_time_limit = 1 * 10 * 60, # 单个任务最多执行10分钟  
  
    # 任务结果过期时间  
    result_expires=3600,  
  
    # 任务序列化方式  
    task_serializer='json',  
    result_serializer='json',  
    accept_content=['json'],  
  
    # 时区设置  
    timezone='Asia/Shanghai',  
    enable_utc=True  
)  
  
# 声明队列  
app.conf.task_queues = {  
    Queue('default'),  
    Queue('queue_one'),  
    Queue('queue_two')  
}  
  
# 路由配置  
app.conf.task_routes = {  
    "apps.demo_app.tasks.timed_task_one": {  
        "queue": "queue_one"  
    },  
    "apps.demo_app.tasks.async_task_one": {  
        "queue": "queue_two"  
    },  
    "*": {  
        "queue": "default"  
    }  
}  
  
# 定时任务  
app.conf.beat_schedule = {  
    "timed_task-every-5-second": {  
        'task': "apps.demo_app.tasks.timed_task_one",  
        'schedule': 5.0,  
    }  
}  
  
# Load task modules from all registered Django apps.  
# app.autodiscover_tasks(["apps.demo_app"])  
app.autodiscover_tasks()
```
Celery Rabbitmq配置
配置参数
```python
#!/usr/bin/env python  
# _*_ coding: utf-8 _*_  
  
from kombu import Exchange, Queue  
  
# 使用RabbitMQ作为broker  
broker_url = "amqp://ingest:SobeyHive2016@172.16.151.202:6672//ingest"  
  
# 使用直接交换机  
terminator_service_exchange = Exchange("terminator_service_exchange", type="direct", durable=True)  
  
# 声明队列，并绑定 routing_keytask_queues = (  
    Queue(  
        name="terminator_convert_service_pdf_queue",  
        exchange=terminator_service_exchange,  
        routing_key="tcs_pdf_key",  
        durable=True,  # 队列持久化  
    ),  
    Queue(  
        name="terminator_convert_service_txt_queue",  
        exchange=terminator_service_exchange,  
        routing_key="tcs_txt_key",  
        durable=True,  
    ),  
    # Queue(  
    #     name="docling_task_queue",    #     exchange=terminator_service_exchange,    #     routing_key="dt_key",    #     durable=True,    # ),)  
  
# 明确指定任务与 routing_key 的映射  
task_routes = {  
    "terminator.convert.service.pdf": {"queue": "terminator_convert_service_pdf_queue", "routing_key": "tcs_pdf_key"},  
    "terminator.convert.service.txt": {"queue": "terminator_convert_service_txt_queue", "routing_key": "tcs_txt_key"},  
}  
  
# 消息确认模式  
task_acks_late = False  # worker 执行成功后才 acktask_reject_on_worker_lost = True  # worker 异常退出时重发任务  
  
# ========== 关键配置：一次只消费一个任务 ==========worker_prefetch_multiplier = 1  # 每个 worker 进程一次只预取 1 个任务  
worker_max_tasks_per_child = None  # worker 不自动回收（可选）  
  
# 任务结果（可选）  
# result_backend = "redis://localhost:6379/0"  # 推荐使用 Redis，或者完全删除此行  
  
# 任务与队列持久化  
task_default_delivery_mode = "persistent"  
  
# 可选：时区与日志  
timezone = "Asia/Shanghai"  
enable_utc = False
```
实例化
```python
import os  
from celery import Celery  
from common.basics.logging import LOGGING  
import logging.config  
  
logging.config.dictConfig(LOGGING)  
  
# Set the default Django settings module for the 'celery' program.  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')  
  
app = Celery("celery")  
app.config_from_object("main.celery_config")  
app.autodiscover_tasks()
```
## celery workerpool(工作线程池)
### 正确的概念
#### 1. **worker_concurrency**
表示 **一个 Worker 进程可以同时执行多少个任务**（并发执行槽位数量）
```python
worker_concurrency = 2

# 意味着：
# - Worker 有 2 个执行槽位
# - 最多同时执行 2 个任务
# - 类似于线程池大小或进程池大小
```
#### 2. **worker_prefetch_multiplier**
表示 **每个执行槽位预取多少个任务**
```python
worker_prefetch_multiplier = 4

# 意味着：
# - 每个执行槽位预取 4 个任务
# - 总预取数 = worker_prefetch_multiplier × worker_concurrency
```
### 计算公式
```python
总预取任务数 = worker_prefetch_multiplier × worker_concurrency

# 例如：
worker_prefetch_multiplier = 4
worker_concurrency = 2
# → 总预取数 = 4 × 2 = 8 个任务
```
### 图解说明
```python
# 配置示例
worker_prefetch_multiplier = 4
worker_concurrency = 2
```

```
┌─────────────────────────────────────────────────────────┐
│                    Worker 进程                           │
│                                                          │
│  从 Broker 预取: 4 × 2 = 8 个任务到本地                 │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 本地任务队列: [Task3, Task4, Task5, Task6,        │ │
│  │                Task7, Task8]                        │ │
│  └────────────────────────────────────────────────────┘ │
│                          ↓ 分配任务                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │           执行池 (concurrency=2)                    │ │
│  │                                                     │ │
│  │  ┌──────────────────┐    ┌──────────────────┐     │ │
│  │  │  执行槽位 1      │    │  执行槽位 2      │     │ │
│  │  │  正在执行 Task1  │    │  正在执行 Task2  │     │ │
│  │  └──────────────────┘    └──────────────────┘     │ │
│  │                                                     │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```
### 详细执行流程
```python
worker_prefetch_multiplier = 4
worker_concurrency = 2

# 时刻 T0: Worker 启动
# - 从 RabbitMQ/Redis 预取 8 个任务到本地
# - 本地队列: [1,2,3,4,5,6,7,8]

# 时刻 T1: 开始执行
# - 槽位1: 执行任务1
# - 槽位2: 执行任务2
# - 本地队列: [3,4,5,6,7,8]

# 时刻 T2: 任务1执行完成
# - 槽位1: 从本地队列取任务3，开始执行
# - 槽位2: 仍在执行任务2
# - 本地队列: [4,5,6,7,8]

# 时刻 T3: 任务2执行完成
# - 槽位1: 仍在执行任务3
# - 槽位2: 从本地队列取任务4，开始执行
# - 本地队列: [5,6,7,8]

# 时刻 T4: 任务3执行完成
# - 槽位1: 从本地队列取任务5
# - 同时，Worker 从 broker 再预取 1 个任务（补充到8个）
# - 本地队列: [6,7,8,9]

# ... 循环往复
```
### worker_concurrency 的不同实现方式
根据 `worker_pool` 配置，concurrency 的实现方式不同：
```python
# 1. prefork (默认) - 多进程
worker_pool = 'prefork'
worker_concurrency = 4
# → 创建 4 个子进程
# → 每个进程执行一个任务
# → 适合 CPU 密集型任务

# 2. gevent - 协程
worker_pool = 'gevent'
worker_concurrency = 1000
# → 使用 gevent 协程
# → 可以设置很大的并发数
# → 适合 I/O 密集型任务

# 3. eventlet - 协程
worker_pool = 'eventlet'
worker_concurrency = 1000
# → 使用 eventlet 协程
# → 类似 gevent

# 4. solo - 单线程
worker_pool = 'solo'
# → 无并发，一次只执行一个任务
# → 用于调试
```
### 实际示例对比
#### 示例 1: 小并发 + 大预取
```python
worker_concurrency = 2          # 同时执行 2 个任务
worker_prefetch_multiplier = 10 # 每个槽位预取 10 个

# 总预取: 2 × 10 = 20 个任务在 Worker 本地

# 优点: 吞吐量高，减少网络往返
# 缺点: 
# - 如果有多个 Worker，任务分配不均
# - 20 个任务都被这个 Worker "占住"了
```

```
Worker A: 预取 20 个 [████████████████████] 
          执行中 2 个，等待 18 个

Worker B: 预取 0 个 [] 
          空闲 ← 不公平！
```
#### 示例 2: 大并发 + 小预取
```python
worker_concurrency = 10         # 同时执行 10 个任务
worker_prefetch_multiplier = 1  # 每个槽位只预取 1 个

# 总预取: 10 × 1 = 10 个任务

# 优点: 任务分配均匀
# 缺点: 可能有网络延迟
```

```
Worker A: 预取 10 个 [██████████]
          执行中 10 个

Worker B: 预取 10 个 [██████████]
          执行中 10 个

← 公平分配！
```
### 查看实际配置

```bash
# 启动 Worker 时可以看到配置
celery -A your_app worker --loglevel=info

# 输出示例：
# - concurrency: 4 (prefork)
# - prefetch multiplier: 4
# - max tasks per child: None

# 查看运行时配置
celery -A your_app inspect stats

# 输出包括：
# "pool": {
#     "max-concurrency": 4,
#     "processes": [12345, 12346, 12347, 12348],
#     "prefetch-count": 16  ← 这里是总预取数
# }
```
### 推荐配置
```python
# 场景1: CPU 密集型任务
worker_pool = 'prefork'
worker_concurrency = CPU核心数  # 例如 4
worker_prefetch_multiplier = 1   # 避免任务堆积

# 场景2: I/O 密集型任务
worker_pool = 'gevent'
worker_concurrency = 100-1000    # 可以很大
worker_prefetch_multiplier = 1-2  # 小一点

# 场景3: 任务执行时间差异大
worker_concurrency = 按需设置
worker_prefetch_multiplier = 1   # 关键！避免短任务被长任务阻塞

# 场景4: 任务执行时间均匀
worker_concurrency = 按需设置
worker_prefetch_multiplier = 4   # 默认值即可
```
### 总结
```python
# worker_concurrency: 同时能执行几个任务（执行槽位数）
# worker_prefetch_multiplier: 每个槽位预取几个任务

# 一个 Worker 总共预取的任务数 = concurrency × prefetch_multiplier

# 记忆口诀：
# concurrency = 手的数量（能同时干几件事）
# prefetch_multiplier = 每只手旁边放几个待办任务
```

