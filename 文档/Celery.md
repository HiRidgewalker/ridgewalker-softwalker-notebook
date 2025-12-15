celery文章:
[两万字长文让你彻底掌握celery](https://mp.weixin.qq.com/s/2EE2OIO3mE-FJV1rhkNn6A)
[django结合celery使用](https://mp.weixin.qq.com/s/jemAdhpxZ0mbYJBx7ijeRw)

celery架构
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