# Linux 进程服务与系统管理笔记

> 来自 [[linux命令]] 的"进程管理 + 服务管理"章节。原笔记保留在 `文档/linux命令.md` 供回溯。
> 同系列：[[Hub/01_Linux基础与文件管理笔记]]、[[Hub/02_Linux用户权限与组管理笔记]]、[[Hub/04_Linux磁盘网络与软件包管理笔记]]、[[Hub/05_Linux定时任务笔记]]。

进程和服务是 Linux 运行时的"灵魂"。排查问题日常三连：**查进程 → 看资源 → 读日志**。

---

## 1. 进程查看

### 1.1 `ps` 快照

`ps` 显示的是命令执行瞬间的进程状态，不是实时刷新。

```bash
ps -ef                          # 全格式显示所有进程
ps aux                          # BSD 格式，信息更全（CPU/内存占比）
ps -ef | grep nginx             # 过滤 nginx
ps aux --sort=-%cpu | head      # 按 CPU 占用倒序，看最忙的进程
ps aux --sort=-%mem | head      # 按内存占用倒序
ps -o pid,ppid,cmd -p 1234      # 只看 PID 1234 的指定字段
```

`ps aux` 关键列：

| 列 | 含义 |
| --- | --- |
| USER | 启动用户 |
| PID | 进程 ID |
| %CPU / %MEM | CPU / 内存占用百分比 |
| VSZ / RSS | 虚拟内存 / 实际物理内存（KB） |
| TTY | 关联终端（`?` 表示后台 daemon） |
| STAT | 状态：R 运行、S 睡眠、Z 僵尸、T 停止 |
| START | 启动时间 |
| TIME | 累计 CPU 时间 |
| COMMAND | 启动命令 |

### 1.2 实时查看 `top` / `htop`

```bash
top                             # 实时刷新，按 q 退出
top -p 1234                     # 只监控某个 PID
```

`top` 常用交互键：

| 键 | 作用 |
| --- | --- |
| `P` | 按 CPU 排序 |
| `M` | 按内存排序 |
| `T` | 按运行时间排序 |
| `k` | 输入 PID 后 kill |
| `1` | 显示每个 CPU 核 |
| `H` | 显示线程 |
| `q` | 退出 |

`htop` 是增强版（需安装），支持鼠标、树状、搜索，更推荐日常用：

```bash
# Ubuntu/Debian
sudo apt install htop
# CentOS/RHEL
sudo yum install htop
```

### 1.3 进程树

```bash
pstree                          # 树状展示父子进程
pstree -p                       # 显示 PID
pstree -u                       # 显示用户
```

### 1.4 查找进程

```bash
pgrep nginx                     # 按名字查 PID
pgrep -u www-data               # 按用户查 PID
pidof nginx                     # 查 nginx 主进程 PID
```

---

## 2. 终止进程

### 2.1 `kill`

```bash
kill PID                        # 默认发 SIGTERM（15），请求进程优雅退出
kill -9 PID                     # 发 SIGKILL（9），强制立即终止（不会清理资源）
kill -HUP PID                   # 发 SIGHUP（1），常用于服务重载配置
kill -15 PID                    # 同 kill PID
```

常用信号：

| 信号 | 编号 | 作用 |
| --- | --- | --- |
| SIGTERM | 15 | 优雅终止（默认） |
| SIGKILL | 9 | 强制终止，无法捕获 |
| SIGHUP | 1 | 重载配置或断开终端后保持运行 |
| SIGINT | 2 | Ctrl + C 发出的中断 |
| SIGSTOP | 19 | 暂停进程 |
| SIGCONT | 18 | 恢复暂停的进程 |

### 2.2 `killall` / `pkill`

```bash
killall nginx                   # 杀掉所有名为 nginx 的进程
pkill -f "python app.py"        # 按完整命令行匹配并杀掉
pkill -u alice                  # 杀掉 alice 的所有进程
```

> 坑：`pkill -f` 匹配范围大，写错 pattern 会误杀。先用 `pgrep -f` 确认匹配到的是哪些 PID。

---

## 3. systemd 服务管理

现代 Linux 发行版几乎都使用 **systemd** 作为 init 系统。服务管理的核心命令是 `systemctl`。

### 3.1 服务生命周期

```bash
systemctl start nginx           # 启动服务
systemctl stop nginx            # 停止服务
systemctl restart nginx         # 重启服务
systemctl reload nginx          # 重载配置（不中断连接）
systemctl status nginx          # 查看状态 + 最近日志
systemctl enable nginx          # 开机自启
systemctl disable nginx         # 取消开机自启
systemctl is-enabled nginx      # 检查是否开机自启
```

### 3.2 查看所有服务

```bash
systemctl list-units --type=service --state=running    # 正在运行的服务
systemctl list-unit-files --type=service               # 所有服务单元（含是否 enable）
systemctl --failed                                      # 启动失败的服务
```

### 3.3 服务单元文件位置

| 路径 | 说明 |
| --- | --- |
| `/usr/lib/systemd/system/` | 包管理器安装的单元文件（不要改这里） |
| `/etc/systemd/system/` | 管理员自定义 / 覆盖的单元文件 |
| `/run/systemd/system/` | 运行时生成的单元文件 |

自定义服务示例 `/etc/systemd/system/myapp.service`：

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/start.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

加载并启动：

```bash
systemctl daemon-reload         # 修改单元文件后必须重载
systemctl start myapp
systemctl enable myapp
```

### 3.4 日志查看 `journalctl`

```bash
journalctl -u nginx             # 看 nginx 服务日志
journalctl -u nginx -f          # 实时追踪
journalctl -u nginx --since "1 hour ago"    # 最近 1 小时
journalctl -u nginx --since today --until "2 hours ago"
journalctl -xe                  # 看所有日志 + 错误高亮 + 尾页
journalctl -b                   # 本次启动以来的日志
journalctl -p err               # 只看 error 级别以上
```

> 注意：`journalctl` 日志默认可能不持久化，重启后丢失。需要修改 `/etc/systemd/journald.conf` 开启 `Storage=persistent`。

---

## 4. 兼容旧系统：service / chkconfig

老 CentOS 6 / RHEL 6 使用 SysV init。虽然现在用得少，但阅读老文档时会遇到。

```bash
service nginx start             # 启动
service nginx stop              # 停止
service nginx restart           # 重启
service nginx status            # 状态

chkconfig nginx on              # 开机自启
chkconfig nginx off             # 取消开机自启
chkconfig --list nginx          # 查看各运行级别是否自启
```

---

## 5. 防火墙

Linux 防火墙经历了 `iptables` → `firewalld` / `ufw` → `nftables` 的演进。

### 5.1 firewalld（RHEL/CentOS/Fedora）

```bash
systemctl status firewalld

firewall-cmd --state                         # 查看是否运行
firewall-cmd --get-active-zones              # 看当前生效区域
firewall-cmd --list-all                      # 看当前区域所有规则
firewall-cmd --add-port=8080/tcp             # 临时开放 8080
firewall-cmd --add-port=8080/tcp --permanent # 永久开放
firewall-cmd --reload                        # 重载配置
firewall-cmd --remove-port=8080/tcp          # 关闭端口
firewall-cmd --add-service=http              # 开放服务（按名）
```

### 5.2 ufw（Ubuntu/Debian 简易防火墙）

```bash
sudo ufw status                 # 查看状态
sudo ufw allow 22/tcp           # 允许 SSH
sudo ufw allow 80/tcp           # 允许 HTTP
sudo ufw allow 8080             # 允许 8080（tcp+udp 默认）
sudo ufw deny 3306              # 拒绝 3306
sudo ufw enable                 # 启用
sudo ufw disable                # 禁用
sudo ufw delete allow 8080      # 删除规则
```

### 5.3 iptables（底层）

```bash
iptables -L -n                  # 列出规则
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT   # 允许 8080
iptables -A INPUT -p tcp --dport 3306 -j DROP     # 丢弃 3306
iptables -D INPUT ...           # 删除规则
```

> 坑：firewalld 和 iptables 不要混用，容易冲突。选一个统一管理。

---

## 6. 网络监控

### 6.1 `ss`（现代替代 netstat）

```bash
ss -tlnp                        # 查看监听中的 TCP 端口及进程
ss -tunap                       # 看所有 TCP/UDP 连接
ss -s                           # 统计连接状态
```

选项含义：

| 选项 | 含义 |
| --- | --- |
| `-t` | TCP |
| `-u` | UDP |
| `-l` | 监听（listening） |
| `-n` | 显示数字端口，不解析服务名 |
| `-p` | 显示进程名/PID |
| `-a` | 所有连接 |

### 6.2 `lsof`（查看打开的文件/端口）

```bash
lsof -i :8080                   # 看占用 8080 端口的进程
lsof -p 1234                    # 看 PID 1234 打开的文件
lsof /var/log/nginx/access.log  # 看谁在访问这个文件
```

### 6.3 `netstat`（老但常见）

```bash
netstat -tlnp                   # 监听端口
netstat -anp | grep ESTABLISHED # 已建立连接
```

> 现代发行版默认可能没装 netstat（属于 net-tools），推荐优先学 `ss`。

---

## 7. 系统运行级别

旧概念：

| 运行级别 | 含义 |
| --- | --- |
| 0 | 关机 |
| 1 | 单用户模式（救援模式） |
| 2 | 多用户无网络 |
| 3 | 多用户命令行 |
| 4 | 保留 |
| 5 | 图形界面 |
| 6 | 重启 |

systemd 对应 target：

```bash
systemctl get-default           # 看默认 target
systemctl set-default multi-user.target   # 默认命令行
systemctl set-default graphical.target    # 默认图形界面
systemctl isolate rescue.target           # 进入救援模式
```

---

## 8. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| `kill -9` 直接干 | 优先用 `kill`（SIGTERM），给进程清理机会；`-9` 是最后手段 |
| 改了 service 文件没 `daemon-reload` | systemd 不会自动感知修改，必须重载 |
| `systemctl start` 成功但 `enable` 没开 | 服务只手动启动，重启机器后不自动启动 |
| `journalctl -f` 看不到日志 | 服务可能把日志写到文件里了（如 `/var/log/`），或日志级别被过滤 |
| `firewall-cmd` 规则没加 `--permanent` | 临时规则，重启后失效 |
| `ss -tlnp` 没有输出 PID | 权限不够，需要用 sudo |
| 服务启动失败 | 先看 `systemctl status xxx` 里最后 10 行，再看 `journalctl -u xxx -xe` |