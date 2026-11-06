---
title: "Linux 基础与文件管理笔记"
sidebar_position: 1
---

# Linux 基础与文件管理笔记

> 来自 旧稿 linux命令 的"文件目录类 / 综合知识便捷操作 / vi 与 vim / 帮助指令"章节。旧稿目录已清理，当前以本文为准。
> 同系列：[II_Linux用户权限与组管理笔记](./II_Linux用户权限与组管理笔记.md)、[III_Linux进程服务与系统管理笔记](./III_Linux进程服务与系统管理笔记.md)、[IV_Linux磁盘网络与软件包管理笔记](./IV_Linux磁盘网络与软件包管理笔记.md)、[V_Linux定时任务笔记](./V_Linux定时任务笔记.md)。

本文聚焦 Linux 最常用的**目录约定、文件操作、文本查看、重定向、vim、帮助命令**。

---

## 1. 目录约定（重要）

Linux 没有"安装位置强制规定"，但有一套被广泛遵循的目录惯例。知道这套约定能让你快速判断一个文件/可执行文件属于谁。

| 路径 | 用途 | 典型内容 |
| --- | --- | --- |
| `/opt` | 第三方大型软件（手动安装） | 自己下载的 JDK、IDEA、数据库 tar 包 |
| `/usr/local` | 编译/脚本方式安装的本地软件 | `nginx`、`python` 源码编译结果 |
| `/usr/bin` | 系统分发的可执行文件（包管理器装的） | `git`、`curl`、`vim` |
| `/etc` | 全部配置文件 | `/etc/profile`、`/etc/nginx/`、`/etc/ssh/` |
| `/var/log` | 日志文件 | `/var/log/syslog`、`/var/log/nginx/` |
| `/home/<user>` | 普通用户家目录 | 用户数据、`.bashrc`、`.ssh/` |
| `/root` | root 家目录 | root 的配置 |
| `/tmp` | 临时文件（重启可能清空） | 进程间临时数据 |
| `/proc`、`/sys` | 内核与进程虚拟文件系统 | `/proc/<pid>/`、`/proc/cpuinfo` |

### 环境变量

- `/etc/profile`：**全局**登录 shell 加载（对所有用户生效）
- `~/.bashrc` / `~/.zshrc`：**当前用户**交互式非登录 shell 加载
- `~/.bash_profile` / `~/.profile`：**当前用户**登录 shell 加载

修改后立即生效：

```bash
source /etc/profile        # 让全局生效
source ~/.bashrc           # 让当前用户生效
```

---

## 2. 帮助命令

| 命令 | 用途 |
| --- | --- |
| `man <cmd>` | 完整手册（最权威），按 `q` 退出 |
| `<cmd> --help` | 简明帮助（常用选项速查） |
| `<cmd> -h` | 同上（部分命令短选项） |
| `help <cmd>` | bash 内置命令的帮助 |
| `type <cmd>` | 判断命令是外部程序、别名还是 shell 内置 |
| `which <cmd>` | 查找外部命令的可执行文件路径 |
| `info <cmd>` | 更详细的 GNU 文档（较少用） |

```bash
man ls                # 看 ls 完整手册
ls --help             # 简明帮助
type cd               # 输出 "cd is a shell builtin"
type ls               # 输出 "ls is /usr/bin/ls"（或别名）
which python3         # 输出 python3 路径
```

**man 的章节编号**（如 `man 1 passwd` vs `man 5 passwd`）：

| 章节 | 内容 |
| --- | --- |
| 1 | 用户命令 |
| 2 | 系统调用 |
| 3 | C 库函数 |
| 4 | 设备文件 |
| 5 | 配置文件格式 |
| 8 | 系统管理命令 |

---

## 3. 文件与目录操作

### 3.1 路径与切换

```bash
pwd                 # 显示当前绝对路径
cd                  # 等价 cd ~，回到当前用户的家目录
cd ~                # 同上
cd -                # 回到上一次所在目录（两个目录间反复横跳时很爽）
cd ..               # 上一级
cd ../..            # 上两级
cd /etc/nginx       # 用绝对路径
cd ./conf.d         # 用相对路径
```

### 3.2 查看目录内容 `ls`

```bash
ls                  # 列出当前目录（不含隐藏）
ls -a               # 含隐藏文件（. 开头的）
ls -l               # 详细列表（权限/所有者/大小/时间）
ls -lh              # -l + 文件大小带单位（K/M/G）
ls -lt              # 按修改时间倒序（最新的在前）
ls -ltr             # 按修改时间正序（最旧在前）
ls -R               # 递归列出子目录
ls -ld /etc         # 看目录本身的属性（不加 d 会列出目录里所有内容）
ls -F               # 文件类型标识（/=目录 *=可执行 @=软链）
ls --color=auto     # 着色（默认一般是开的）
```

`ls -l` 输出逐列含义：

```
-rw-r--r-- 1 root root 1213 Feb  2 09:39 abc
│└┬┘└┬┘└┬┘ │   │   │     │        │      └ 文件名
│ │   │   │  │   │   │     │        └ 修改时间
│ │   │   │  │   │   │     └ 大小（字节）
│ │   │   │  │   │   └ 所在组
│ │   │   │  │   └ 所有者
│ │   │   │  └ 硬链接数 / 子目录数
│ │   │   └ 其他用户权限（r--）
│ │   └ 所在组权限（r--）
│ └ 所有者权限（rw-）
└ 文件类型（- 普通文件 / d 目录 / l 软链）
```

### 3.3 创建与删除

```bash
mkdir dir1                       # 创建单级目录
mkdir -p a/b/c                   # 递归创建多级目录（父目录不存在会自动建）

touch file.txt                   # 创建空文件 / 刷新已有文件的时间戳

rmdir dir1                       # 删除空目录（目录里有内容就报错）
rm file.txt                      # 删除文件
rm -f file.txt                   # 强制删除不提示
rm -rf dir1                      # 递归强制删除目录（慎用，没有回收站）
rm -ri dir1                      # 递归删除但每一步都确认（更安全）
```

> 坑：**`rm -rf` 没有回收站**，误删重要目录恢复成本极高。生产环境可以装 `trash-cli`，或者用 `mv` 先移到 `/tmp/garbage/` 临时区，过几天再清。

### 3.4 复制与移动

```bash
cp src.txt dst.txt               # 复制文件
cp src.txt /tmp/                 # 复制到目录
cp -r dir1/ dir2/                # 递归复制目录
cp -p src.txt dst.txt            # 保留权限、时间戳
cp -a dir1/ dir2/                # 归档模式（保留所有属性 + 递归，等于 -dR --preserve=all）

mv old.txt new.txt               # 重命名（同目录下）
mv file.txt /tmp/                # 移动（跨目录）
mv dir1/ /opt/                   # 移动目录
```

> 坑：`mv` 是**原地操作**，跨磁盘分区的 `mv` 实际是 cp + rm。如果目录很大、跨分区、不可中断，**优先用 `rsync`**（支持断点续传 + 进度条）。

### 3.5 查看文件内容

| 命令 | 用途 | 特点 |
| --- | --- | --- |
| `cat file` | 一次性输出全部 | 文件大会刷屏 |
| `less file` | 分页浏览（推荐） | 支持搜索 `/`、翻页 `b`/`space`、`q` 退出 |
| `more file` | 分页浏览（老） | 只能往下翻 |
| `head file` | 看头部（默认 10 行） | `head -n 20` |
| `tail file` | 看尾部（默认 10 行） | `tail -n 20`、`tail -f` 实时追踪 |
| `tac file` | 倒序输出（cat 反过来） | 较少用 |
| `nl file` | 输出带行号 | 类似 `cat -n` |

**`less` 的常用快捷键**：

| 键 | 作用 |
| --- | --- |
| `j` / `k` | 下 / 上移动一行 |
| `space` / `b` | 下 / 上翻一页 |
| `g` / `G` | 跳到首 / 尾 |
| `/pattern` | 向下搜索 |
| `?pattern` | 向上搜索 |
| `n` / `N` | 跳到下一个 / 上一个匹配 |
| `q` | 退出 |

**`tail -f` 的进阶用法**（排查问题时非常常用）：

```bash
tail -f /var/log/nginx/access.log       # 实时追踪
tail -F /var/log/nginx/access.log       # 文件被 rotate 后重新打开（更稳）
tail -n 100 -f app.log | grep ERROR     # 实时只看错误
```

### 3.6 输出与重定向

```bash
echo "hello"                        # 输出到屏幕
echo $PATH                          # 输出环境变量
echo -e "a\nb"                      # 解析转义

> file                              # 清空文件（创建或截断）
>> file                             # 追加
echo "hello" > file.txt             # 覆盖写入
echo "world" >> file.txt            # 追加写入

cmd > out.log 2>&1                  # 标准输出 + 标准错误都重定向到文件
cmd > /dev/null 2>&1                # 完全丢弃所有输出（"黑洞"）
cmd >> out.log 2>&1                 # 追加（不覆盖）
```

**三种流**：

| 流 | 文件描述符 | 默认目标 | 丢弃 |
| --- | --- | --- | --- |
| stdin | 0 | 键盘 | `< /dev/null` |
| stdout | 1 | 屏幕 | `> /dev/null` |
| stderr | 2 | 屏幕 | `2> /dev/null` |

### 3.7 管道 `|`

把前一个命令的 **stdout** 当作后一个命令的 **stdin**：

```bash
cat /etc/group | grep wudang        # 等价 grep wudang /etc/group
ps -ef | grep nginx                 # 查 nginx 进程
cat access.log | grep 404 | head     # 多级过滤
```

> 坑：`|` 默认不传递 `stderr`。要也传：`cmd1 2>&1 | cmd2`。

### 3.8 软链接 `ln`

```bash
ln -s /root /home/myroot            # 给 /root 在 /home 下建个软链 myroot
ln -sf /new/path /home/myroot       # 强制覆盖已有软链
```

软链 ≈ Windows 快捷方式，**删软链不影响源**，删源会让软链变"悬空"（dangling，红色闪烁）。

### 3.9 历史命令 `history`

```bash
history                            # 列出所有历史
history 20                         # 最近 20 条
!123                               # 执行历史编号 123 的命令
!!                                 # 重复上一条
!$                                 # 上一条命令的最后一个参数
sudo !!                            # 上一条命令加 sudo（最常用）
Ctrl + R                           # 反向搜索历史（输关键字回车）
```

`history` 默认存在 `~/.bash_history`，由 `HISTSIZE` / `HISTFILESIZE` 控制条数。

---

## 4. vim / vi 速查

vi 是几乎所有 Linux 发行版默认安装的编辑器。vim 是 vi 的增强版。掌握最少 10 个键就能干活。

### 4.1 三种模式

```
       ┌──────────┐  i/a/o    ┌──────────┐  Esc    ┌──────────┐
       │ Normal   │ ────────► │ Insert   │ ─────► │ Normal   │
       │ (默认)   │ ◄──────── │ (编辑)   │ ◄───── │          │
       └──────────┘  Esc      └──────────┘         └──────────┘
            │                                          ▲
            │ :                                        │
            ▼                                          │
       ┌──────────┐                                    │
       │ Command  │ ──── :w / :q / :wq ────────────────┘
       │ (命令行) │
       └──────────┘
```

### 4.2 进入与退出

```bash
vim file.txt                       # 打开文件（不存在则创建）
vim +20 file.txt                   # 打开并跳到第 20 行
vim -O2 a.txt b.txt                # 水平分屏同时打开两个文件
```

| 命令 | 作用 |
| --- | --- |
| `:w` | 保存 |
| `:q` | 退出（未修改才可） |
| `:wq` 或 `ZZ` | 保存并退出 |
| `:q!` | 强制退出（丢弃修改） |
| `:w file2.txt` | 另存为 |

### 4.3 模式切换

| 键 | 作用 |
| --- | --- |
| `i` | 在光标前进入插入模式 |
| `a` | 在光标后进入插入模式 |
| `o` | 在下方新开一行进入插入模式 |
| `O` | 在上方新开一行进入插入模式 |
| `I` | 在行首进入插入模式 |
| `A` | 在行尾进入插入模式 |
| `Esc` | 回到普通模式（任何时候按一下都安全） |

### 4.4 普通模式下的移动

| 键 | 作用 |
| --- | --- |
| `h j k l` | 左 下 上 右 |
| `w / b` | 跳到下一个 / 上一个单词开头 |
| `0 / $` | 跳到行首 / 行尾 |
| `gg / G` | 跳到文件首 / 尾 |
| `<n>G` | 跳到第 n 行 |
| `Ctrl + f / b` | 向下 / 上翻页 |

### 4.5 编辑命令

| 键 | 作用 |
| --- | --- |
| `x` | 删除当前字符 |
| `dd` | 删除当前行 |
| `dw` | 删除一个单词 |
| `d$` | 删除到行尾 |
| `yy` | 复制当前行 |
| `yw` | 复制一个单词 |
| `p / P` | 在下方 / 上方粘贴 |
| `u` | 撤销 |
| `Ctrl + r` | 重做 |
| `.` | 重复上一次操作 |

### 4.6 搜索与替换

```vim
/text              " 向下搜索 text
?text              " 向上搜索 text
n / N              " 跳到下一个 / 上一个匹配
:set hlsearch      " 高亮搜索结果
:nohlsearch        " 临时关闭高亮（:noh）

:%s/old/new/g      " 全文替换
:%s/old/new/gc     " 全文替换但每次询问
:10,20s/old/new/g  " 只在第 10~20 行替换
```

### 4.7 进阶：批量操作

```vim
dd                                 " 删一行
3dd                                " 删三行
yyp                                " 复制当前行并在下方粘贴（快速复制一行）
Ctrl + v → jjj → I → // → Esc      " 批量给多行加注释
:%!sort                            " 对全文按行排序（用 sort 命令）
```

> 实用场景：服务器上没装图形界面、SSH 远程、Docker 容器里改配置 —— 学会 vim 是生存技能。

---

## 5. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| `rm -rf /` 或 `rm -rf /*` | 删除根目录或全部内容，**绝对不要执行**。现代系统有些加了 `--preserve-root` 保护 |
| `> file` 写错路径 | `>` 是覆盖，文件名打错就静默创建了新空文件，原内容不会丢但容易误判 |
| `mv` 跨分区 | 大目录跨分区时实际是 cp + rm，半途中断可能造成一边的残留。**大文件迁移用 `rsync`** |
| 中文文件名乱码 | 终端和文件编码不一致（UTF-8 vs GBK）。统一设置 `LANG=en_US.UTF-8` 或 `zh_CN.UTF-8` |
| `Ctrl + S` 锁屏终端 | 终端里按 Ctrl+S 会"冻结"显示，按 `Ctrl + Q` 解锁 |
| `exit` 与 `logout` | `logout` 仅在文本登录（runlevel 3）下生效，图形界面下用 `exit` 退出当前 shell |