"""
Celery 生产环境鲁棒性演示

涵盖：
- acks_late + reject_on_worker_lost（任务不丢）
- 软超时 / 硬超时
- 自动重试 + 指数退避 + 抖动
- 手动重试
- 任务过期
- 限速
- 信号系统（task_prerun / task_postrun / task_failure / worker_ready）

Eager 模式跑通，无需真 broker。
"""
import time
from datetime import datetime, timedelta

from celery import Celery, signals
from celery.exceptions import MaxRetriesExceededError, Retry, SoftTimeLimitExceeded

app = Celery("robust_demo", broker="redis://localhost:6379/0")
app.conf.task_always_eager = True
app.conf.task_eager_propagates = False          # Eager 下让重试能演示

# ===== 1. acks_late：任务执行完才 ack =====
# 默认：worker 拿到任务就 ack → 崩溃就丢
# 推荐：acks_late=True → 任务执行完才 ack，崩溃自动重新入队
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True      # worker 崩溃时 broker 重新入队


# ===== 2. 超时控制 =====
app.conf.task_soft_time_limit = 5               # 软超时：抛 SoftTimeLimitExceeded
app.conf.task_time_limit = 10                   # 硬超时：worker 直接 kill 任务进程


# ===== 3. 自动重试 + 指数退避 + 抖动 =====
class NetworkError(Exception):
    pass


@app.task(
    bind=True,
    autoretry_for=(NetworkError, TimeoutError),    # 哪些异常自动重试
    retry_backoff=True,                            # 指数退避（1s, 2s, 4s, 8s, ...）
    retry_backoff_max=60,                          # 退避上限
    retry_jitter=True,                             # 加随机抖动（防雷击）
    max_retries=3,                                 # 最多重试 3 次
    acks_late=True,
)
def call_external_api(self, url):
    """调用外部 API，自动重试 + 退避"""
    raise NetworkError(f"can't reach {url}")


# ===== 4. 手动重试 =====
@app.task(bind=True, max_retries=3)
def manual_retry_task(self, x):
    try:
        if x < 0:
            raise ValueError("x must be non-negative")
        return x * 2
    except ValueError as exc:
        # 主动重试：1 秒后再试
        raise self.retry(exc=exc, countdown=1, max_retries=3)


# ===== 5. 任务过期 =====
app.conf.task_expires = 3600                    # 1 小时后还没被消费 → 丢弃


# ===== 6. 限速 =====
# 任务级
@app.task(rate_limit="10/m")                    # 每分钟最多 10 次
def rate_limited_task():
    return "ok"


# 全局
app.conf.task_default_rate_limit = "100/s"


# ===== 7. 软超时捕获 =====
@app.task(bind=True, soft_time_limit=3, time_limit=5)
def long_task(self):
    """演示 SoftTimeLimitExceeded：捕获后做清理。"""
    try:
        time.sleep(10)                           # Eager 模式下没有真 sleep；这里用 try 演示
    except SoftTimeLimitExceeded:
        print("soft time limit hit, cleaning up...")
        raise


# ===== 8. 信号系统（生产告警关键）=====
@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
    print(f"[signal] {task.name}[{task_id}] starting, args={args}")


@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, state=None, **kw):
    print(f"[signal] {task.name}[{task_id}] done, state={state}, retval={retval}")


@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kw):
    """任务失败时推告警 / 写日志 / 推 Sentry。"""
    print(f"[signal] ALERT: {sender.name}[{task_id}] failed: {exception}")
    # 实际生产中：
    # sentry_sdk.capture_exception(exception)
    # alert_oncall(f"task {sender.name} failed: {exception}")


@signals.task_retry.connect
def task_retry_handler(sender=None, request=None, reason=None, **kw):
    print(f"[signal] {sender.name}[{request.id}] retrying, reason={reason}")


@signals.worker_ready.connect
def worker_ready_handler(sender=None, **kw):
    print(f"[signal] worker {sender} ready")


@signals.worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kw):
    print(f"[signal] worker {sender} shutting down")


# ===== 9. 跑 demo =====
if __name__ == "__main__":
    print("=== 1. acks_late 已开启 ===")
    print(app.conf.task_acks_late)
    print()

    print("=== 2. 超时配置 ===")
    print(f"soft_time_limit: {app.conf.task_soft_time_limit}s")
    print(f"time_limit: {app.conf.task_time_limit}s")
    print()

    print("=== 3. 自动重试（autoretry_for）===")
    # 注意：Eager 模式下 autoretry_for 会真的循环重试
    # 这里只演示配置，不真跑（避免输出刷屏）
    print(f"autoretry_for: {call_external_api.autoretry_for}")
    print(f"retry_backoff: {call_external_api.retry_backoff}")
    print(f"retry_jitter: {call_external_task_safe.retry_jitter if False else call_external_api.retry_jitter}")
    print()

    print("=== 4. 手动重试 ===")
    try:
        manual_retry_task.delay(-1)
    except Retry:
        print("任务主动 retry（符合预期）")
    except MaxRetriesExceededError:
        print("重试次数用完（符合预期）")
    print()

    print("=== 5. 限速配置 ===")
    print(f"rate_limit (rate_limited_task): {rate_limited_task.rate_limit}")
    print(f"task_default_rate_limit: {app.conf.task_default_rate_limit}")
    print()

    print("=== 6. 信号触发 ===")
    # 跑个会成功的任务，触发 task_prerun + task_postrun 信号
    @app.task
    def hello():
        return "world"

    hello.delay()
    print()

    # 跑个会失败的任务，触发 task_failure 信号
    @app.task
    def fail():
        raise ValueError("demo failure")

    try:
        fail.delay()
    except ValueError as e:
        print(f"任务失败（符合预期）: {e}")
