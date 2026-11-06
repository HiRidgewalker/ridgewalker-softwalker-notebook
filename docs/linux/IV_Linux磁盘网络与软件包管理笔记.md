---
title: "Linux 磁盘网络与软件包管理笔记"
sidebar_position: 4
---

# Linux 磁盘网络与软件包管理笔记

> 来自 旧稿 linux命令 的"硬盘分区挂载 / 网络配置 / rpm 和 yum"章节。旧稿目录已清理，当前以本文为准。
> 同系列：[I_Linux基础与文件管理笔记](./I_Linux基础与文件管理笔记.md)、[II_Linux用户权限与组管理笔记](./II_Linux用户权限与组管理笔记.md)、[III_Linux进程服务与系统管理笔记](./III_Linux进程服务与系统管理笔记.md)、[V_Linux定时任务笔记](./V_Linux定时任务笔记.md)。

磁盘、网络、软件包是系统管理的三座大山。不会这三样，服务器维护就无从谈起。

---

## 1. 磁盘管理

### 1.1 查看磁盘使用情况

```bash
df -h                           # 查看所有挂载点的磁盘使用（人类可读）
df -h /                         # 只看根分区
df -hT                          # 显示文件系统类型（ext4/xfs/tmpfs 等）
```

`df` 关键列：

| 列 | 含义 |
| --- | --- |
| Filesystem | 文件系统设备或挂载源 |
| Size | 总容量 |
| Used | 已用 |
| Available | 可用 |
| Use% | 使用率 |
| Mounted on | 挂载点 |

### 1.2 查看目录/文件占用

```bash
du -h file.txt                  # 看单个文件大小
du -sh /var/log                 # 看目录总大小（summary + human）
du -h --max-depth=1 /var        # 看 /var 下各一级子目录大小
du -ah --max-depth=1 /var/log | sort -hr | head  # 找出最大的文件/目录
```

`du` 选项：

| 选项 | 含义 |
| --- | --- |
| `-s` | 汇总，不显示子目录 |
| `-h` | 人类可读 |
| `-a` | 含文件 |
| `--max-depth=N` | 显示到第 N 层子目录 |
| `-c` | 最后加一个总计 |

### 1.3 挂载与卸载

```bash
mount                           # 列出当前所有挂载
mount /dev/sdb1 /mnt/data       # 手动挂载分区
umount /mnt/data                # 卸载
umount /dev/sdb1                # 按设备卸载（也可）
```

`/etc/fstab` 开机自动挂载示例：

```fstab
# <file system> <dir> <type> <options> <dump> <pass>
UUID=xxxxx   /mnt/data   ext4    defaults,noatime   0   2
```

> 警告：改 `/etc/fstab` 后先用 `mount -a` 测试，确认没有报错再重启。否则系统可能起不来。

### 1.4 分区工具 `fdisk` / `parted`

```bash
lsblk                           # 查看块设备和挂载点（最常用，无破坏风险）
fdisk -l                        # 列出所有磁盘分区
fdisk /dev/sdb                  # 对 /dev/sdb 进行分区（交互式）
parted /dev/sdb                 # 更大容量磁盘（GPT 分区表）
mkfs.ext4 /dev/sdb1             # 格式化分区为 ext4
mkfs.xfs /dev/sdb1              # 格式化为 xfs
```

---

## 2. 网络配置

### 2.1 基本连通性测试

```bash
ping baidu.com                  # 测试网络连通
ping -c 4 8.8.8.8               # 发 4 个包就停
traceroute baidu.com            # 看经过的每一跳（跟踪路由）
mtr baidu.com                   # ping + traceroute 结合版
```

### 2.2 查看网络配置

```bash
ip addr                         # 查看 IP 地址（现代推荐）
ip link                         # 查看网卡状态
ip route                        # 查看路由表
ip neigh                        # 查看 ARP 缓存
hostname -I                     # 快速看本机 IP
hostnamectl                     # 看主机名信息
```

老命令（仍可用，但建议学 ip）：

```bash
ifconfig                        # 看 IP（net-tools）
ifconfig eth0 up                # 启用网卡
route -n                        # 看路由表
arp -a                          # 看 ARP 缓存
```

### 2.3 DNS 与 hosts

```bash
cat /etc/resolv.conf            # 看 DNS 配置
cat /etc/hosts                  # 本地 hosts 映射
hostnamectl set-hostname myserver    # 修改主机名
```

`/etc/hosts` 示例：

```
127.0.0.1       localhost
192.168.1.100   db01.internal
192.168.1.101   app01.internal
```

### 2.4 下载与请求

```bash
curl -I https://example.com     # 看响应头
curl -L https://t.cn/xxx        # 跟随重定向
curl -o file.zip https://...    # 下载保存为 file.zip
curl -X POST -d 'a=1&b=2' https://api...    # POST 请求

wget https://example.com/file.tar.gz        # 下载
wget -c https://example.com/file.tar.gz     # 断点续传
wget -O myfile https://example.com/file     # 指定保存名
```

### 2.5 网络抓包与诊断

```bash
ss -tlnp                        # 看监听端口
lsof -i :8080                   # 看端口被谁占用
nc -zv 192.168.1.100 3306       # 测试某主机某端口是否通
nmap -p 1-1000 192.168.1.100    # 端口扫描（需安装 nmap）
dig baidu.com                   # DNS 查询
tcpdump -i any port 80          # 抓 80 端口包
```

---

## 3. 软件包管理

Linux 发行版分两大流派：**RPM 系**（RHEL/CentOS/Fedora/openSUSE）和 **Debian 系**（Ubuntu/Debian）。

### 3.1 RPM 系：rpm / yum / dnf

#### `rpm`（底层）

```bash
rpm -qa                         # 列出所有已安装包
rpm -qa | grep nginx            # 查是否装了 nginx
rpm -qi nginx                   # 看包详细信息
rpm -ql nginx                   # 看包安装了哪些文件
rpm -qf /usr/bin/nginx          # 查某个文件属于哪个包
rpm -e nginx                    # 卸载
rpm -ivh nginx-xxx.rpm          # 安装本地 rpm 包
```

#### `yum`（CentOS 7 / RHEL 7）

```bash
yum search nginx                # 搜索包
yum install nginx               # 安装
yum remove nginx                # 卸载
yum update                      # 更新所有包
yum update nginx                # 更新指定包
yum info nginx                  # 看包信息
yum clean all                   # 清缓存
yum makecache                   # 重建缓存
yum list installed              # 列出已安装
```

#### `dnf`（CentOS 8+ / RHEL 8+ / Fedora）

```bash
dnf install nginx
dnf remove nginx
dnf update
dnf search nginx
dnf repolist                    # 看已启用仓库
```

### 3.2 Debian 系：dpkg / apt

#### `dpkg`（底层）

```bash
dpkg -l                         # 列出已安装包
dpkg -l | grep nginx
dpkg -L nginx                   # 看包装了哪些文件
dpkg -S /usr/bin/nginx          # 查文件归属
dpkg -i nginx.deb               # 安装本地 deb 包
dpkg -r nginx                   # 卸载保留配置
dpkg -P nginx                   # 彻底卸载（含配置）
```

#### `apt`（推荐）

```bash
apt update                      # 更新包索引（不是升级包！）
apt upgrade                     # 升级所有可升级包
apt install nginx               # 安装
apt remove nginx                # 卸载保留配置
apt purge nginx                 # 彻底卸载
apt autoremove                  # 删除不再需要的依赖
apt search nginx                # 搜索
apt show nginx                  # 看包详情
apt list --installed            # 列出已安装
```

**`apt` vs `apt-get`**：`apt` 更友好（带进度条），`apt-get` 更底层、脚本里更稳定。

### 3.3 国内镜像源

国内访问官方源慢，通常换成阿里云、清华、中科大镜像：

- Ubuntu：`/etc/apt/sources.list`
- CentOS：`/etc/yum.repos.d/CentOS-Base.repo`

改完记得：

```bash
apt update                       # Debian/Ubuntu
yum makecache                    # CentOS 7
dnf makecache                    # CentOS 8+
```

---

## 4. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| `df` 看到空间满了但 `du` 找不到大文件 | 可能是删除中的文件仍被进程占用（日志未释放）。用 `lsof +L1` 找 |
| `/etc/fstab` 写错导致启动失败 | 改完务必 `mount -a` 测试，再重启 |
| `apt update` 报错证书问题 | 系统时间不对，或镜像源 HTTPS 证书过期。先 `date` 检查 |
| `yum install` 慢 | 换国内镜像源，或检查 DNS |
| 网络通了但 DNS 解析不了 | `/etc/resolv.conf` 里没配 DNS，或 `systemd-resolved` 冲突 |
| `ping` 通但 `curl` 不通 | 对方可能禁了 ICMP，或目标端口没开 / 防火墙拦截 |
| `ip addr` 看不到 IP | 网卡没启动、DHCP 没拿到、或 NetworkManager 没启用 |