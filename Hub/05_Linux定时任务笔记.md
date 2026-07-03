# Linux 定时任务笔记

> 来自 [[linux命令]] 的"定时任务调度"章节（crond + at）。原笔记保留在 `文档/linux命令.md` 供回溯。
> 同系列：[[01_Linux基础与文件管理笔记]]、[[02_Linux用户权限与组管理笔记]]、[[03_Linux进程服务与系统管理笔记]]、[[04_Linux磁盘网络与软件包管理笔记]]。

Linux 下常见的三种"定时/延时执行"方式：

| 方式 | 适合场景 | 精确度 |
| --- | --- | --- |
| `crontab` | 周期性任务（最常用） | 分钟级 |
| `at` | 一次性延时任务 | 分钟级 |
| `systemd timer` | 现代替代 crontab | 秒级，更易管理 |

---

## 1. crontab 周期性任务

### 1.1 crontab 文件格式

```
* * * * *  command
│ │ │ │ │
│ │ │ │ └── 星期几 (0-7, 0 和 7 都是周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

### 1.2 特殊字符

| 字符 | 含义 | 示例 |
| --- | --- | --- |
| `*` | 每 | `* * * * *` 每分钟 |
| `,` | 枚举 | `0 9,18 * * *` 每天 9 点和 18 点 |
| `-` | 范围 | `0 9-17 * * 1-5` 工作日 9 到 17 点整 |
| `/` | 步长 | `*/5 * * * *` 每 5 分钟 |
| `#` | 第几个星期几 | `0 12 * * 1#1` 每月第一个周一 12 点 |
| `L` | 最后 | `0 0 L * *` 每月最后一天 |

### 1.3 常用时间规则示例

```bash
# 每分钟
* * * * * /usr/local/bin/check.sh

# 每 5 分钟
*/5 * * * * /usr/local/bin/check.sh

# 每小时第 0 分
0 * * * * /usr/local/bin/hourly.sh

# 每天凌晨 2:30
30 2 * * * /usr/local/bin/backup.sh

# 每周一凌晨 3:00
0 3 * * 1 /usr/local/bin/weekly.sh

# 每月 1 号凌晨 4:00
0 4 1 * * /usr/local/bin/monthly.sh

# 工作日每 2 小时
0 */2 * * 1-5 /usr/local/bin/workhour.sh
```

### 1.4 crontab 管理命令

```bash
crontab -l                      # 列出当前用户的 crontab
crontab -e                      # 编辑当前用户的 crontab（默认会用 vi）
crontab -r                      # 删除当前用户的全部 crontab（慎用）
crontab file                    # 用 file 替换当前 crontab
sudo crontab -u alice -e        # 编辑 alice 的 crontab
```

### 1.5 环境变量问题（重要坑点）

crontab 执行的 shell 环境变量**极少**，通常：

- 没有你的 `PATH`
- 没有加载 `~/.bashrc`
- `HOME` 是用户家目录，`SHELL` 是 `/bin/sh`

**解决方案**：在 crontab 顶部显式声明：

```crontab
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/deploy

*/5 * * * * cd /opt/app && ./run.sh >> /var/log/app/cron.log 2>&1
```

### 1.6 输出重定向

crontab 默认会把命令的 stdout/stderr 发邮件给用户（如果系统配了 mail）。生产环境应该显式写日志：

```crontab
0 2 * * * /opt/backup/backup.sh >> /var/log/backup/backup.log 2>&1
```

### 1.7 常见坑

| 坑 | 说明 |
| --- | --- |
| `%` 特殊字符 | crontab 里 `%` 会被转义为换行。需要用时加反斜杠 `\%` |
| 命令找不到 | crontab 的 PATH 很窄，**用绝对路径**或在顶部定义 PATH |
| 相对路径 | 执行脚本前先 `cd /path` |
| 没有换行结尾 | crontab 文件最后一行如果不是空行，可能不生效 |
| 权限 | 脚本要有 `x` 权限 |
| 任务重叠 | 任务执行时间超过间隔，会并发。用 `flock` 加锁：`* * * * * flock -n /tmp/my.lock -c '/opt/app/run.sh'` |

---

## 2. at 一次性定时任务

`at` 用于"未来某个时间点执行一次"。

```bash
at now + 5 minutes              # 5 分钟后执行
at 14:00 tomorrow               # 明天 14:00
at 23:00 2025-12-31             # 指定日期时间
atq                             # 列出待执行的任务
atrm 1                          # 删除编号为 1 的任务
```

输入命令后按 `Ctrl + D` 结束。

```bash
$ at now + 1 hour
warning: commands will be executed using /bin/sh
at> /opt/scripts/cleanup.sh
at> <EOT>
job 1 at Tue Jul  2 15:00:00 2025
```

---

## 3. systemd timer（现代推荐）

systemd timer 是 crontab 的现代替代方案，优势：

- 精确到秒
- 自带日志（`journalctl -u myjob.timer`）
- 自动处理任务重叠（`AccuracySec`、`Persistent`）
- 支持依赖、环境变量、权限控制
- 失败可自动重试

### 3.1 创建 service + timer

两个文件：

**`/etc/systemd/system/myjob.service`**

```ini
[Unit]
Description=My scheduled job

[Service]
Type=oneshot
User=deploy
WorkingDirectory=/opt/app
ExecStart=/opt/app/backup.sh
```

**`/etc/systemd/system/myjob.timer`**

```ini
[Unit]
Description=Run myjob every day at 2:30

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true                  # 如果错过执行时间，开机后补跑一次

[Install]
WantedBy=timers.target
```

### 3.2 启用与管理

```bash
systemctl daemon-reload
systemctl start myjob.timer
systemctl enable myjob.timer
systemctl list-timers --all      # 看所有 timer
systemctl status myjob.timer     # 状态
journalctl -u myjob.service      # 看执行日志
```

### 3.3 OnCalendar 语法示例

```ini
OnCalendar=*-*-* 02:30:00        # 每天 2:30
OnCalendar=Mon *-*-* 03:00:00    # 每周一 3:00
OnCalendar=*-*-01 04:00:00       # 每月 1 号 4:00
OnCalendar=*:0/5                 # 每 5 分钟
OnCalendar=hourly                # 每小时
```

---

## 4. 三种方式选型

| 场景 | 推荐 |
| --- | --- |
| 简单周期任务（如日志切割、备份） | `crontab` |
| 一次性延时任务 | `at` |
| 需要日志、依赖、秒级精度、失败重试 | `systemd timer` |
| 需要秒级/复杂调度（如分布式） | 考虑 `cronicle`、` airflow` 等外部调度器 |

---

## 5. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| crontab 任务没执行 | 先看 `/var/log/cron` 或 `journalctl -u cron`，再检查脚本权限、PATH、相对路径 |
| crontab 命令有 `%` | 必须转义 `\%` |
| 脚本在 shell 里能跑但 crontab 不能 | 多半是环境变量/工作目录/PATH 不同 |
| 两个相同任务并发 | 长任务用 `flock` 加锁 |
| systemd timer 没生效 | 是否 `daemon-reload`？是否 `enable`？`OnCalendar` 语法是否正确？ |
| 定时任务失败没通知 | 至少把 stderr 重定向到日志文件，关键任务加邮件/企业微信告警 |