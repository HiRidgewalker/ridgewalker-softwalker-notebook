# Linux 用户权限与组管理笔记

> 来自 [[linux命令]] 的"用户管理 / 用户组 / 组管理和权限管理"章节。原笔记保留在 `文档/linux命令.md` 供回溯。
> 同系列：[[01_Linux基础与文件管理笔记]]、[[03_Linux进程服务与系统管理笔记]]、[[04_Linux磁盘网络与软件包管理笔记]]、[[05_Linux定时任务笔记]]。

Linux 是**多用户多任务**操作系统。理解用户、组、权限，是避免"服务器被别人误操作"和"为什么脚本跑不通"的基础。

---

## 1. 核心概念

### 1.1 用户（User）

每个登录 Linux 的人都对应一个用户账号：

- `root`：超级管理员，UID 固定为 `0`，拥有系统最高权限
- 普通用户：日常工作使用，UID 通常从 `1000` 开始
- 系统用户：运行服务用（如 `nginx`、`mysql`、`www-data`），UID 通常 `< 1000`，默认不能登录

### 1.2 组（Group）

每个用户至少属于一个**主组**，可加入多个**附加组**。组存在的意义是**批量授权**。

```
用户 dev_a  ──┬── 主组：developers
用户 dev_b  ──┤   附加组：sudo、docker
用户 dev_c  ──┘

把目录 /app 的所有组设为 developers，整个组自然都能访问。
```

### 1.3 三个身份

每个文件/目录都有三类访问者：

| 身份 | 英文 | 说明 |
| --- | --- | --- |
| 所有者 | user / owner | 文件创建者 |
| 所在组 | group | 文件创建者所在的主组 |
| 其他人 | others | 既不是所有者、也不在所在组的用户 |

---

## 2. 用户管理命令

### 2.1 增删改用户

```bash
useradd alice                              # 创建用户 alice（默认创建家目录 /home/alice）
useradd -m alice                           # 显式创建家目录（某些系统默认不建）
useradd -d /data/alice alice               # 指定家目录
useradd -s /bin/bash alice                 # 指定登录 shell
useradd -g developers -G sudo,docker alice # 指定主组 + 附加组

passwd alice                               # 设置/修改 alice 的密码
passwd                                     # root 可直接改自己密码

userdel alice                              # 删除用户（保留家目录）
userdel -r alice                           # 删除用户 + 家目录 + 邮件池（彻底）
```

### 2.2 查询与切换

```bash
id alice                                   # 查看用户 UID/GID/所属组
whoami                                     # 当前用户名
who am i                                   # 当前登录用户（含终端和时间）
su - alice                                 # 完全切换到 alice 环境（加载她的环境变量）
su alice                                   # 切换身份，但保留当前 shell 环境变量
exit                                       # 退回原来的用户
sudo -u alice cmd                          # 以 alice 身份执行单次命令
```

> 坑：`su` 和 `su -` 区别很大。`-` 会加载目标用户的完整环境，常用于运维切换；不加 `-` 容易残留当前用户的 PATH，导致命令找不到。

### 2.3 修改用户属性

```bash
usermod -g developers alice                # 修改主组
usermod -G sudo,docker alice               # 修改附加组（会覆盖原有附加组！）
usermod -aG docker alice                   # 追加到 docker 组（推荐用 -aG）
usermod -s /bin/zsh alice                  # 修改登录 shell
usermod -L alice                           # 锁定用户
usermod -U alice                           # 解锁用户
```

---

## 3. 用户组管理命令

```bash
groupadd developers                        # 创建组
groupdel developers                        # 删除组（组内不能有用户作为其主组）
groups                                     # 查看当前用户所属组
groups alice                               # 查看 alice 所属组
```

**添加用户到组**：

```bash
gpasswd -a alice docker                    # 把 alice 加入 docker 组
gpasswd -d alice docker                    # 从 docker 组移除 alice
```

---

## 4. 文件权限详解

### 4.1 `ls -l` 的权限字符串

```
-rw-r--r-- 1 alice developers 1213 Feb 2 09:39 abc
```

| 位 | 含义 |
| --- | --- |
| 第 0 位 | 文件类型：`-` 普通文件、`d` 目录、`l` 软链、`c/b` 设备文件 |
| 第 1-3 位 | 所有者权限（rw-） |
| 第 4-6 位 | 所在组权限（r--） |
| 第 7-9 位 | 其他人权限（r--） |

### 4.2 `rwx` 在文件上的含义

| 权限 | 对文件的作用 |
| --- | --- |
| `r`（读） | 可读内容，如 `cat`、`less` |
| `w`（写） | 可修改、删除、覆盖内容 |
| `x`（执行） | 可作为程序/脚本运行，如 `./script.sh` |

### 4.3 `rwx` 在目录上的含义（经常被误解）

| 权限 | 对目录的作用 |
| --- | --- |
| `r` | 可列出目录里的文件名（`ls` 能看列表） |
| `w` | 可在目录下创建、删除、重命名文件 |
| `x` | 可进入目录（`cd`），可访问目录下已知的文件路径 |

> 重要：目录没有 `x` 权限，即使有 `r` 也读不到文件内容；目录有 `w` 就能删里面的文件（不管文件本身是不是你的）。

### 4.4 特殊权限位

| 符号 | 名称 | 作用 |
| --- | --- | --- |
| `s`（所有者位） | SUID | 执行该文件时以文件所有者身份运行 |
| `s`（组位） | SGID | 执行文件时以文件所在组身份运行；对目录：新文件继承目录所在组 |
| `t`（其他位） | Sticky Bit | 对目录：只有文件所有者或 root 能删除自己的文件（如 `/tmp`） |

示例：

```bash
ls -ld /tmp                 # drwxrwxrwt
ls -l /usr/bin/passwd       # -rwsr-xr-x（SUID，普通用户改自己的密码需要 root 权限写 /etc/shadow）
```

---

## 5. 修改权限 `chmod`

### 5.1 符号法（直观）

```bash
chmod u+x script.sh              # 给所有者加执行权限
chmod g-w file.txt               # 给组去掉写权限
chmod o=r file.txt               # 把其他人设为只读
chmod a+r file.txt               # 给所有人加读权限
chmod u=rwx,g=rx,o=x script.sh   # 组合写法
```

角色：

| 字母 | 含义 |
| --- | --- |
| `u` | user（所有者） |
| `g` | group（所在组） |
| `o` | others（其他人） |
| `a` | all（全部） |

操作：

| 符号 | 含义 |
| --- | --- |
| `+` | 增加权限 |
| `-` | 减少权限 |
| `=` | 设置成指定权限 |

### 5.2 数字法（快速）

| 数字 | 二进制 | 权限 |
| --- | --- | --- |
| 0 | 000 | `---` |
| 1 | 001 | `--x` |
| 2 | 010 | `-w-` |
| 3 | 011 | `-wx` |
| 4 | 100 | `r--` |
| 5 | 101 | `r-x` |
| 6 | 110 | `rw-` |
| 7 | 111 | `rwx` |

```bash
chmod 644 file.txt               # rw-r--r--（普通文件默认）
chmod 755 script.sh              # rwxr-xr-x（可执行脚本/目录）
chmod 700 private.key            # rwx------（私钥等敏感文件）
chmod 2770 /data/shared          # rwxrws---（SGID，共享目录组继承）
```

### 5.3 递归修改

```bash
chmod -R 755 /app                # 递归修改 /app 下所有文件和目录
chmod -R u+rwX /app              # 大写 X：只给目录和已有执行权限的文件加 x
```

> 坑：`chmod -R 777 /` 会把整个系统权限搞乱，永远不要执行。

---

## 6. 修改所有者 `chown` 与 修改组 `chgrp`

### 6.1 `chown`

```bash
chown alice file.txt             # 改所有者为 alice
chown alice:developers file.txt  # 同时改所有者和所在组
chown :developers file.txt       # 只改组（等价 chgrp）
chown -R alice:alice /home/alice/project  # 递归
```

### 6.2 `chgrp`

```bash
chgrp developers file.txt        # 改组
groupmod -n newdev developers    # 重命名组
```

---

## 7. 默认权限 `umask`

新文件/目录创建时，权限不是 777，而是：

```
文件默认最大权限：666
目录默认最大权限：777
实际权限 = 最大权限 - umask
```

常见 `umask`：

| umask | 文件权限 | 目录权限 | 适用场景 |
| --- | --- | --- | --- |
| 022 | 644 | 755 | 普通用户（大多数发行版默认） |
| 002 | 664 | 775 | 共享开发环境 |
| 077 | 600 | 700 | 高安全场景 |

```bash
umask                 # 查看当前 umask
umask 002             # 临时设置（退出 shell 失效）
echo "umask 002" >> ~/.bashrc  # 持久化
```

---

## 8. ACL（访问控制列表）速查

当"所有者 + 组 + 其他人"还不够细时，用 ACL 给**特定用户或组**单独授权。

```bash
getfacl file.txt                 # 查看 ACL
setfacl -m u:bob:rwx file.txt    # 给用户 bob 加 rwx
setfacl -m g:developers:rw file.txt  # 给组 developers 加 rw
setfacl -x u:bob file.txt        # 移除 bob 的 ACL
setfacl -b file.txt              # 清空所有 ACL
setfacl -R -m u:bob:rx /dir      # 递归
```

---

## 9. sudo 基础

```bash
sudo cmd                          # 以 root 身份执行 cmd
sudo -i                           # 切换到 root 交互 shell
sudo -u www-data cmd              # 以 www-data 身份执行
sudo -l                           # 查看当前用户被允许执行的 sudo 命令
```

sudo 授权由 `/etc/sudoers` 控制，**不要直接编辑**，用：

```bash
visudo
```

让普通用户拥有全部 sudo 权限：

```bash
alice  ALL=(ALL:ALL) ALL
```

让普通用户免密执行 docker 命令：

```bash
%docker ALL=(ALL) NOPASSWD: /usr/bin/docker
```

---

## 10. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| 普通用户加入 `docker` 组后没生效 | 需要**退出重新登录**或 `newgrp docker`，不是立即生效 |
| 加了 `r` 但读不到文件 | 目录没有 `x` 权限，无法进入目录访问文件内容 |
| 文件所有者不是自己却删不掉 | 如果所在目录的组/其他人有 `w` 权限，别人也能删 |
| `chmod -R` 太粗 | 644 给目录会导致无法进入，755 给私钥会暴露。敏感文件应 600 |
| `sudo` 找不到命令 | sudo 默认使用 root 的 PATH，可能跟当前用户的 PATH 不同。用绝对路径或修改 secure_path |
| 脚本提示 Permission denied | 没有 `x` 权限。chmod +x 后执行，或 `bash script.sh`  bypass |
| SUID/SGID 滥用 | 随便给可执行文件 SUID 等于给别人 root 后门，能不用就不用 |