---
title: "进程与服务管理笔记"
sidebar_position: 1
---

# 进程与服务管理笔记

> 原 旧稿 / 旧稿 / 旧稿 的合并重写。三者本质上都是
> "**进程守护 + 自动重启 + 可观测性**" 工具，但定位不同、组合使用很常见。本笔记按
> "**先讲清三件套 → 各自核心 → 场景选型 → 常见坑**" 组织。
>
> 容器内进程管理见 [I_Docker笔记](../docker/01-docker-overview.md) / [V_Docker Compose笔记](../docker/05-docker-compose.md)；集群级编排见 [I_Kubernetes基础笔记](../kubernetes/01-kubernetes-basics.md)。

## 目录

1. 三件套定位与全景对比
2. systemd 核心（系统级服务首选）
3. Supervisord 核心（应用进程守护）
4. pm2 核心（Node.js 专用）
5. 对比与选型（按场景）
6. 可观测性（日志 / 监控 / 告警）
7. 常见坑
8. 关联笔记

---

## 1. 三件套定位与全景对比

| 维度 | systemd | Supervisord | pm2 |
|---|---|---|---|
| 出品 | systemd 项目（Linux 主流 init） | Python 社区（supervisord.org） | Keymetrics 公司 / Node 生态 |
| 平台 | Linux（仅） | UNIX-like（Linux/macOS） | Linux / macOS / Windows（受限） |
| 运行身份 | **PID 1**（系统 init） | 普通进程（被 systemd 或手动启动） | 普通守护进程（被 systemd 或 Docker 拉起） |
| 适用语言 | 任意 | 任意（Python/Go/Node 友好） | **主攻 Node.js**，通用进程也可 |
| 配置形式 | unit 文件（INI 风格） | INI 文件 | JS 文件（ecosystem.config.js） |
| 进程模型 | 单进程（multi-process 由 fork 提供） | 支持 `numprocs` 多实例 | cluster mode 内置负载均衡 / fork mode 单实例 |
| 开机自启 | **原生** | 需 systemd / init.d 拉起 | `pm2 startup` 生成 systemd unit |
| 日志系统 | systemd-journald（journalctl） | 自带 logfile + 轮转 / 可转 syslog | 自带 logfile + `pm2-logrotate` 模块 |
| 远程控制 | systemctl（SSH） / cockpit / Web | supervisorctl（CLI） + Web UI（XML-RPC） | pm2 CLI + PM2 Plus（商业）/ 自建 API |
| 可观测性 | journald + node_exporter | Web UI + eventlistener | pm2 内置指标 + Prometheus exporter |
| 典型场景 | 系统服务、数据库、网关、后台 worker | Python/Go 项目自管、单机多应用 | Node.js API（cluster 0 秒重载）、watch 开发 |

一句话定位：

- **systemd** = 系统的 init / 服务管理器（**第一公民**）
- **Supervisord** = 应用级的进程守护器（systemd 之外的轻量替代）
- **pm2** = Node.js 专用进程管家（带 cluster / 0 秒重载等 Node 专属特性）

---

## 2. systemd 核心（系统级服务首选）

systemd 是 Linux 主流 init 系统（PID 1），所有现代发行版（Ubuntu / Debian / CentOS / RHEL / Arch）
默认采用。**生产环境的"系统服务"首选 systemd**。

### 2.1 Unit 文件结构

`/etc/systemd/system/<name>.service`：

```ini
[Unit]
Description=My Backend API
After=network-online.target postgresql.service
Wants=network-online.target          # 弱依赖（失败不影响启动）
# Requires=postgresql.service        # 强依赖（失败则本 unit 失败）

[Service]
Type=notify                          # 见下文说明
User=app
Group=app
WorkingDirectory=/srv/api
ExecStart=/srv/api/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID   # 平滑重载（需程序支持）
ExecStop=/bin/kill -TERM $MAINPID
Restart=always                       # 任何原因退出都拉起
RestartSec=3
StartLimitBurst=5                   # 90 秒内最多 5 次失败
StartLimitIntervalSec=90
WatchdogSec=60                      # 60 秒内必须发 watchdog，否则重启
OOMPolicy=stop                      # OOM 时停止（而非继续吃内存被宿主机杀）
KillMode=mixed                      # 先 SIGTERM 主进程、再 SIGKILL 子进程
TimeoutStopSec=30                   # 优雅停止 30s 超时后 SIGKILL
StandardOutput=journal
StandardError=journal

# 资源限制（cgroup v2）
CPUQuota=200%                       # 最多 2 核
MemoryMax=2G
MemoryHigh=1500M                    # 软上限，超过时优先回收
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

启用与维护：

```bash
sudo systemctl daemon-reload          # 改 unit 后必须 reload
sudo systemctl enable myapi.service   # 开机自启
sudo systemctl start myapi.service
sudo systemctl status myapi.service   # 查看状态（最近日志）
sudo systemctl restart myapi.service  # 重启
sudo systemctl reload myapi.service   # 触发 ExecReload
sudo systemctl disable myapi.service  # 取消自启
```

### 2.2 Type 字段选型

| Type | 行为 | 适用 |
|---|---|---|
| `simple` | 立即认为启动成功（默认） | 前台进程、守护进程由 systemd 视作"已就绪" |
| `forking` | 进程 fork 后父进程退出 | 传统守护进程（如 nginx、redis-server 原生模式） |
| `notify` | 进程主动调用 `sd_notify(READY=1)` | **推荐** — 启动完成才进入 active，确保"真的就绪" |
| `oneshot` | 启动一次后任务完成 | 一次性任务（配合 `RemainAfterExit=yes`） |
| `dbus` | 进程注册 D-Bus 名称 | D-Bus 服务 |

> 推荐组合：`Type=notify` + `ExecStart=/.../uvicorn ...` + 应用代码 `notify`。
> `simple` 会"启动命令一返回就算成功"——启动失败/慢启动时会出现"假死"。

### 2.3 Restart 与崩溃循环防护

- `Restart=always`：任何原因退出都重启
- `Restart=on-failure`：仅失败时重启（退出码非 0 / 信号杀死）
- `Restart=on-success`：仅成功退出才重启（极少用）
- 配合 `RestartSec=` 避免紧贴重启

**防止崩溃循环**：`StartLimitBurst` + `StartLimitIntervalSec` 控制"在 X 秒内最多 Y 次失败"，
超过则 unit 进入 `failed` 状态不再重启，等人工介入。

```ini
Restart=always
RestartSec=3
StartLimitBurst=5
StartLimitIntervalSec=90
```

### 2.4 日志：journalctl 速查

systemd 默认把 stdout/stderr 收进 journald（`StandardOutput=journal`）：

```bash
journalctl -u myapi.service                    # 该 unit 全部日志
journalctl -u myapi.service -f                 # follow（实时跟踪）
journalctl -u myapi.service --since "1 hour ago"
journalctl -u myapi.service --since today -p err   # 仅 error 及以上
journalctl -u myapi.service --no-pager         # 不分页（适合管道）
journalctl _PID=12345                          # 按 PID
journalctl --disk-usage                       # 看占用
sudo journalctl --vacuum-size=500M             # 保留 500M
sudo journalctl --vacuum-time=30d              # 保留 30 天
```

持久化（默认 journald 内存，重启清空）：

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```

### 2.5 启动分析（卡启动时用）

```bash
systemd-analyze                        # 系统总启动时间
systemd-analyze blame                  # 各 unit 启动耗时排序
systemd-analyze critical-chain         # 关键依赖链
```

---

## 3. Supervisord 核心（应用进程守护）

Supervisord 是 Python 写的 client/server 进程管理工具，**不充当 PID 1**，通常被 systemd
或 init.d 拉起后管理应用进程。适合"单台机器 / 单用户 / 多个应用进程"集中管控。

### 3.1 最小可运行配置

`/etc/supervisor/supervisord.conf`：

```ini
[unix_http_server]
file = /var/run/supervisor.sock
chmod = 0700

[supervisord]
logfile = /var/log/supervisord.log
logfile_maxbytes = 50MB
logfile_backups = 10
loglevel = info
pidfile = /var/run/supervisord.pid
nodaemon = false
minfds = 1024
minprocs = 200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl = unix:///var/run/supervisor.sock

; 拆分配置目录
[include]
files = /etc/supervisor/conf.d/*.conf
```

`/etc/supervisor/conf.d/web.conf`：

```ini
[program:web]
command=/srv/web/.venv/bin/gunicorn app:wsgi -b 0.0.0.0:8000 --workers 4
directory=/srv/web
user=www-data
autostart=true
autorestart=true
startsecs=10                     ; 进入 RUNNING 需持续运行 10s
startretries=3                   ; 启动失败重试 3 次
stopsignal=TERM
stopwaitsecs=10                  ; 等待优雅停止 10s 后 SIGKILL
stopasgroup=true                 ; 整进程组发 TERM
killasgroup=true                 ; 整进程组发 KILL
environment=APP_ENV="prod",DB_URL="%(ENV_DB_URL)s"
stdout_logfile=/var/log/web/out.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
stderr_logfile=/var/log/web/err.log
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=5
```

> ⚠️ 关键坑：supervisord **不像 shell 解析引号**，`command=bash -c 'foo ; bar'`
> 会被截断为 `command=bash -c 'foo`。要么写完整脚本路径，要么用 `command=sh -c "..."`
> 整行不带内部引号。

### 3.2 进程组与多实例

```ini
[group:workers]
programs=worker_a,worker_b,worker_c
priority=10

[program:worker_a]
command=/srv/worker/run.sh a
numprocs=2
process_name=%(program_name)s_%(process_num)02d
```

> `numprocs > 1` 时 `process_name` 必须含 `%(process_num)s`。

### 3.3 变更流程（固定两步）

```bash
supervisorctl reread      # 重读配置（识别新增 / 修改的 program）
supervisorctl update      # 应用变更：新增 → 启动；修改 → 重启
supervisorctl status
supervisorctl restart web
supervisorctl tail -f web
supervisorctl reload      # 重载 supervisord 主进程配置
supervisorctl shutdown     # 关闭 supervisord
```

### 3.4 Web UI（可选）

```ini
[inet_http_server]
port = 0.0.0.0:9001
username = admin
password = <strong-password>
```

⚠️ 生产必须限制监听内网 + 强密码（或改 unix socket）。9001 是 Web UI 的默认端口。

### 3.5 事件订阅（接监控）

通过 `[eventlistener:...]` 订阅 `PROCESS_STATE_*` / `PROCESS_LOG_*` 等事件，写入
HTTP / TCP / 自定义脚本——可对接告警系统。

---

## 4. pm2 核心（Node.js 专用）

pm2 是 Node.js 生态的进程管理器，**主打**：

- 内置 **cluster mode**（多核负载均衡）
- **0 秒重载**（reload）—— 集群中逐 worker 替换
- ecosystem.config.js 声明式配置
- 自带内存阈值重启、watch 开发模式

> 非 Node 项目也能用 pm2 跑（`pm2 start python-app.py`），但**没有 Node 专属特性收益**。

### 4.1 fork mode vs cluster mode

| 模式 | 行为 | 适用 |
|---|---|---|
| `fork`（默认） | 单进程，不共享端口 | 任意可执行文件、监听随机端口 |
| `cluster` | master fork N 个 worker，**共享端口**，内置负载均衡 | Node.js HTTP/WS/TCP/UDP 服务 |

```bash
pm2 start app.js -i max       # cluster 模式，进程数 = CPU 核数
pm2 start app.js -i 0         # 同上（推荐写法）
pm2 scale app +3              # 运行时加 3 个实例
pm2 scale app 2               # 缩到 2 个
```

### 4.2 ecosystem.config.js 生产模板

```javascript
module.exports = {
  apps: [{
    name: "api-prod",
    script: "./dist/server.js",
    args: "arg1 arg2",
    instances: "max",
    exec_mode: "cluster",
    max_memory_restart: "500M",         // OOM 防护
    kill_timeout: 5000,                 // SIGTERM 后等 5s 再 SIGKILL
    listen_timeout: 10000,              // 等 listen 事件超时（防启动假死）
    wait_ready: false,                  // true → 进程主动 send('ready') 才纳入负载
    max_restarts: 10,                   // 防崩溃循环
    min_uptime: "30s",                  // 短于此不计重启
    restart_delay: 5000,                // 重启间隔
    watch: false,                       // 生产必关（仅开发用）
    ignore_watch: ["node_modules", "logs"],
    out_file: "/var/log/api/out.log",
    error_file: "/var/log/api/err.log",
    merge_logs: true,
    log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    env: { NODE_ENV: "development" },
    env_production: { NODE_ENV: "production", PORT: 3000 }
  }],
};
```

启动：

```bash
pm2 start ecosystem.config.js --env production
pm2 reload all                # 0 秒重载（仅 cluster 网络应用）
pm2 restart all               # 杀进程再起（有 downtime）
pm2 status
pm2 logs --lines 200
pm2 save                      # 冻结当前进程列表到 ~/.pm2/dump.pm2
pm2 resurrect                 # 从 dump 恢复
```

### 4.3 reload vs restart

| 命令 | 效果 | 适用 |
|---|---|---|
| `pm2 restart all` | 杀进程 → 启动，**有 downtime** | 任意应用 |
| `pm2 reload all` | 逐 worker 替换，**0 秒停机** | **仅 cluster 模式网络应用** |

### 4.4 开机自启

pm2 不自己做 init，**借助 systemd**：

```bash
pm2 startup                          # 输出对应的 systemd unit 安装命令
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u www-data --hp /home/www-data
pm2 start ecosystem.config.js --env production
pm2 save                             # 固化到 ~/.pm2/dump.pm2
# 之后 systemd 单元 pm2-<user>.service 开机时执行 pm2 resurrect
```

### 4.5 Docker 集成（`pm2-runtime`）

容器内不能用 daemon 模式（容器主进程必须前台），用 `pm2-runtime`：

```dockerfile
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm install -g pm2
COPY ecosystem.config.cjs ./
CMD ["pm2-runtime", "ecosystem.config.cjs"]
```

`pm2-runtime` 前台运行，SIGTERM 透传，配合 `restart: always` 实现容器重启自愈。

### 4.6 日志轮转

```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true
```

### 4.7 可观测性：Prometheus 集成

```bash
pm2 set pm2:metrics true             # 启用 :9615 内建指标端点
pm2 install pm2-prometheus-exporter  # 或独立 exporter
```

抓取目标：`pm2-host:9209`（默认端口由 exporter 决定）。

---

## 5. 对比与选型（按场景）

### 5.1 按场景决策表

| 场景 | 首选 | 备选 | 理由 |
|---|---|---|---|
| 系统服务（DB / nginx / 自定义 daemon） | **systemd** | — | 原生 init，资源限制最完整 |
| Python / Go 后端 API（单实例） | **systemd** | supervisord | systemd 资源隔离更完整 |
| Python / Go 项目需多进程管控 + Web UI | supervisord | systemd + tmux/screen | supervisord Web UI + eventlistener 直观 |
| Node.js HTTP API（多核利用） | **pm2 cluster mode** | systemd + 多实例 + nginx upstream | pm2 内置 0 秒重载、cluster 负载均衡 |
| Node.js watch 模式开发 | **pm2 fork + watch** | nodemon | pm2 一致体验 |
| Docker 容器内进程 | **systemd-less + tini** 或 **pm2-runtime** | supervisord | 容器内禁嵌 systemd；推荐 tini 做 PID 1 |
| K8s 内的 Pod | kubelet（不是这三者） | — | 由 K8s 管，不需要 |
| macOS 本地开发 | supervisord | pm2 | macOS 没有 systemd |
| 跨服务器统一管控 | 自建 + 各机本地 systemd | PM2 Plus（商业） | 单机选 systemd；多机需自建或买 SaaS |

### 5.2 反模式（**不该**这么用）

| 反模式 | 问题 | 推荐 |
|---|---|---|
| 容器内嵌 systemd（`--privileged` + `systemd`） | 破坏容器隔离；与 docker stop 行为冲突 | tini / dumb-init 做 PID 1 |
| 容器内嵌 supervisord 管应用 | 多此一举；容器重启已经自愈 | 多进程直接 `CMD ["a", "b", "c"]` 或 shell 脚本 |
| 服务器上 pm2 跑 Python | 浪费 pm2 的 Node 专属特性 | supervisord 或 systemd |
| 单纯用 `nohup` 起后台进程 | 无守护、无重启、无日志、无告警 | systemd 或 pm2 |
| 容器内开 `watch` 模式 | 容器内 watch 文件导致非预期重启 | 生产关闭 `watch` |
| `Type=simple` + `Restart=always` + 启动慢的程序 | 启动失败触发无限重启循环 | 加 `StartLimitBurst` 或改 `Type=notify` |

### 5.3 组合用法（生产常见）

**组合 1：systemd 拉 supervisord，supervisord 拉应用**

```ini
# /etc/systemd/system/supervisord.service
[Service]
ExecStart=/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
Restart=always
```

适合："systemd 开机自启 → supervisord 接管应用进程"，可继续用 supervisord Web UI。

**组合 2：systemd 拉 pm2 daemon**

由 `pm2 startup systemd` 生成 unit，开机时自动 `pm2 resurrect`。

**组合 3：nginx + pm2 + Prometheus**

```
                    ┌──────────────┐
                    │   Cloud LB   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │     nginx    │  TLS / static / rate limit
                    └──────┬───────┘
                           │ 127.0.0.1:3000
              ┌────────────▼────────────┐
              │  pm2-runtime / systemd  │  cluster instances
              └────────────┬────────────┘
                           │ :9615 / :9209
                    ┌──────▼───────┐
                    │  Prometheus  │──► Alertmanager ──► Grafana
                    └──────────────┘
```

---

## 6. 可观测性（日志 / 监控 / 告警）

### 6.1 systemd

- **日志**：journald（`journalctl -u xxx`，见 2.4 节）
- **监控**：`node_exporter`（CPU / Mem / FDs / systemd unit 状态）
  - 关键指标：`node_systemd_unit_state{name="myapi.service",state="active"} == 0` 即异常
- **告警**：Prometheus Alertmanager（unit down / restart 次数过多）

### 6.2 Supervisord

- **日志**：内置 `stdout_logfile` / `stderr_logfile`（自轮转），或转 syslog
- **监控**：Web UI（`inet_http_server`）+ `supervisorctl status`
- **告警**：`[eventlistener:...]` 订阅 `PROCESS_STATE_FATAL` / `PROCESS_STATE_EXITED` 等事件，
  推送到 webhook / Slack / 钉钉
- **Prometheus**：`prometheus-supervisord-exporter`（第三方）

### 6.3 pm2

- **日志**：`pm2 logs` + `pm2-logrotate`
- **指标**：内建 :9615 + `pm2-prometheus-exporter`
- **告警**：Grafana 配合 PromQL
  - `pm2_process_status{name="api"} == 0` → 进程 down
  - `pm2_process_memory{app="api"} > 500MB` → 内存超阈值
  - `pm2_process_restarts_total` 增速 → 崩溃循环
- **商业**：`pm2 plus`（PM2.io）跨服务器 Dashboard，4 台免费

---

## 7. 常见坑

### 7.1 systemd

- **`Type=simple` + 启动慢 + `Restart=always`** → 启动失败 → 立即重启 → 死循环。
  修：加 `StartLimitBurst=5` + `StartLimitIntervalSec=90`，或改 `Type=notify`。
- **`ExecStart` 命令行太长 / 带引号嵌套** → systemd 会按空格切分。修：写脚本文件。
- **`User=root` 跑应用** → 安全风险 + 资源限制失效。修：建专用 user / 用 `DynamicUser=yes`。
- **`KillMode=process` 但程序 fork 子进程** → 子进程成孤儿。修：改 `KillMode=mixed` 或 `control-group`。
- **journald 不持久化 → 重启后日志丢失** → 修：建 `/var/log/journal`。
- **`RestartSec` 设 0** → 紧贴重启，吃 CPU。修：至少 1~3 秒。

### 7.2 Supervisord

- **`command` 含 `;` 或内部引号** → 被截断。修：写脚本或避开。
- **`[inet_http_server]` 监听 `0.0.0.0` + 弱密码** → 公网暴露。修：监听内网 + 强密码 / unix socket。
- **`autorestart=true` 但程序每秒崩** → 资源打满。修：加 `startretries` 上限 + 监控告警。
- **`redirect_stderr=true` 且配 `eventlistener`** → eventlistener 自身进程会乱。修：两者互斥。
- **修改配置后只 reload** → 没生效。修：固定 `reread` → `update` 两步。

### 7.3 pm2

- **`exec_mode=cluster` 但跑的是 Python / 非 HTTP** → 共享端口失效。修：非 HTTP 用 `fork`。
- **生产开 `watch=true`** → 误触重启。修：生产必关。
- **`pm2 reload` 跑在 fork 模式** → 行为等同 restart（停机）。修：cluster 才用 reload。
- **容器内 `pm2 start`（daemon）** → 容器退出时 SIGTERM 不透传。修：用 `pm2-runtime`。
- **`max_memory_restart` 阈值过低** → 抖动重启。修：根据实际 P99 内存设上限。
- **`wait_ready=true` 但应用没发 ready 信号** → 进程永不纳入负载。修：确认应用代码主动 `process.send('ready')`。

---

## 8. 关联笔记

- 容器与进程：`[[I_Docker笔记]]`、`[[V_Docker Compose笔记]]`
- 容器编排（更高层）：`[[I_Kubernetes基础笔记]]`
- 监控：`[[DevOps基础与文化笔记]]`（含 Prometheus / Grafana / node_exporter 用法）
- 应用层日志：`[[Kafka笔记]]`（事件流消费）
- 反向代理：`[[FastAPI笔记]]` 配套部署章节、`[[nginx]]`（如已收录）