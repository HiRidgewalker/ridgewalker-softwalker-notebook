# WSL 笔记

> 来自 [[WSL笔记]]。旧稿目录已清理，当前以本文为准。

WSL（Windows Subsystem for Linux）是 Windows 上运行 Linux 环境的子系统，不需要完整虚拟机，开发者最常用的 Windows + Linux 混合方案。

---

## 1. WSL 是什么

WSL 让你在 Windows 上原生运行 Linux 发行版：

- 不需要安装 VMware / VirtualBox 完整虚拟机
- 启动速度快（秒级）
- 与 Windows 共享文件系统、网络
- 可通过 Windows Terminal、PowerShell、VS Code Remote 使用

### 1.1 WSL1 vs WSL2

| 维度 | WSL1 | WSL2 |
| --- | --- | --- |
| 架构 | 系统调用翻译层 | 真正的轻量 Linux 内核虚拟机 |
| 启动速度 | 很快 | 很快 |
| 兼容性 | 部分系统调用不支持 | 几乎完整 Linux 兼容性 |
| 文件 IO 性能 | 访问 Windows 文件快 | 访问 Linux 文件极快，跨 `/mnt/c` 慢 |
| 网络 | 与 Windows 共享网络栈 | 独立虚拟网卡，NAT 模式 |
| 推荐 | 已不推荐 | 现在默认推荐 |

查看当前版本：

```powershell
wsl -l -v
```

设置某个发行版用 WSL2：

```powershell
wsl --set-version Ubuntu-22.04 2
```

---

## 2. 安装与发行版管理

### 2.1 前置条件

- Windows 10 版本 1903+（建议 2004+）或 Windows 11
- 启用虚拟化：BIOS 里开 VT-x/AMD-V
- Windows 功能：开启"适用于 Linux 的 Windows 子系统"和"虚拟机平台"

可以在 PowerShell（管理员）里一键开启：

```powershell
wsl --install
```

这会启用所需功能并安装默认发行版（Ubuntu）。

### 2.2 安装指定发行版

```powershell
wsl --install --web-download                  # 默认装 Ubuntu，并走网页下载
wsl --list --online                           # 列出可安装的发行版
wsl --install -d Debian --web-download        # 安装 Debian
wsl --install -d openSUSE-Leap-15.5
```

### 2.3 查看与管理发行版

```powershell
wsl --list                                    # 列出已安装
wsl --list --verbose                          # 详细（含 WSL 版本、运行状态）
wsl --set-default Ubuntu-22.04                # 设置默认发行版
wsl --terminate Ubuntu-22.04                  # 停止指定发行版
wsl --shutdown                                # 停止所有 WSL 发行版和虚拟机
wsl --unregister Ubuntu-22.04                 # 卸载指定发行版（数据全删）
```

### 2.4 导入/导出（备份与迁移）

```powershell
wsl --export Ubuntu-22.04 D:\backup\ubuntu.tar    # 导出为 tar
wsl --import MyUbuntu D:\wsl\MyUbuntu D:\backup\ubuntu.tar  # 导入到新位置
```

导入后默认用户是 root，需要手动改默认用户：

```powershell
ubuntu.exe config --default-user alice
```

> 坑：`wsl --import` 默认登录用户是 root，不会自动沿用之前的普通用户。

---

## 3. 日常使用

### 3.1 启动 Linux

```powershell
wsl                                           # 启动默认发行版
wsl -d Ubuntu-22.04                           # 启动指定发行版
wsl -d Ubuntu-22.04 -u root                   # 以 root 启动
wsl -e bash -c "ls ~"                         # 不进入交互 shell，执行命令后退出
```

### 3.2 Windows 与 Linux 文件互访

**Linux 里访问 Windows**：

```bash
cd /mnt/c/Users/Alice/Desktop
ls
```

**Windows 里访问 Linux**：

在资源管理器地址栏输入：

```
\\wsl$\Ubuntu-22.04
```

或：

```powershell
explorer.exe .
```

> 重要：在 Windows 里**不要直接修改 Linux 文件**（尤其是 `/home`、 `/etc` 下的），可能破坏文件权限或软链。推荐通过 WSL 内部操作。

### 3.3 退出

```bash
exit                                          # 退出当前 Linux shell
wsl --terminate Ubuntu-22.04                  # 在 Windows 侧停止
wsl --shutdown                                # 全部停止
```

---

## 4. WSL 配置文件

### 4.1 `/etc/wsl.conf`（发行版内配置）

控制单个 WSL 发行版的行为。

```ini
[user]
default = alice                               # 默认登录用户

[boot]
systemd = true                                # 启用 systemd（WSL2 支持）

[network]
generateHosts = true
generateResolvConf = true

[interop]
enabled = true                                # 允许调用 Windows 程序
appendWindowsPath = true                      # 把 Windows PATH 追加到 Linux PATH

[automount]
enabled = true
mountFsTab = true
root = /mnt/
options = "metadata,umask=22,fmask=11"        # 改进 Windows 盘挂载权限
```

修改后生效：

```powershell
wsl --shutdown
wsl
```

### 4.2 `%UserProfile%\.wslconfig`（Windows 全局配置）

控制 WSL2 虚拟机整体资源。

```ini
[wsl2]
memory=8GB                                    # 最大内存
processors=4                                  # CPU 核数
swap=2GB                                      # 交换文件大小
swapFile=C:\\temp\\wsl-swap.vhdx
localhostForwarding=true                      # localhost 端口转发
kernelCommandLine = "cgroup_no_v1=all"
```

修改后生效：

```powershell
wsl --shutdown
```

---

## 5. 网络互通

### 5.1 WSL2 访问 Windows

WSL2 里访问 Windows 本机，用：

```bash
curl http://host.docker.internal:8080         # 访问 Windows 上跑的 8080 服务
curl http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):8080
```

更简单的：Windows 侧服务监听 `0.0.0.0`，WSL2 直接用 Windows 本机 IP。

### 5.2 Windows 访问 WSL2

WSL2 里启动的服务：

```bash
python3 -m http.server 8080
```

Windows 侧直接用浏览器访问：

```
http://localhost:8080
```

WSL2 默认会把 Linux 的 localhost 端口转发到 Windows localhost。

### 5.3 WSL2 的 IP

WSL2 每次启动 IP 可能变。如果需要固定局域网访问，可用脚本或 WSL-vpnkit 等工具。

```bash
hostname -I                                   # 看 WSL2 当前 IP
```

---

## 6. systemd 支持

WSL2 从 0.67.6 版本开始支持 systemd。开启后可以在 WSL 里：

```bash
sudo systemctl status
sudo systemctl start nginx
sudo systemctl enable docker
```

开启方式：在 `/etc/wsl.conf` 里加：

```ini
[boot]
systemd = true
```

然后 `wsl --shutdown` 再重新进入。

---

## 7. VS Code Remote WSL

官方插件：`ms-vscode-remote.remote-wsl`

安装后：

1. 在 WSL 里进入项目目录
2. 执行 `code .`
3. 会自动打开 Windows 上的 VS Code，并远程连接到 WSL 环境

文件、终端、扩展都在 WSL 里运行，但 UI 在 Windows 上。

---

## 8. WSL 更新

```powershell
wsl --update                                  # 更新 WSL 内核
wsl --update --pre-release                    # 更新到预览版
wsl --version                                 # 看 WSL 版本
```

---

## 9. 常见坑汇总

| 坑 | 说明 |
| --- | --- |
| WSL2 `/mnt/c` 下文件 IO 很慢 | 项目代码尽量放在 Linux 文件系统（`/home/xxx`），不要放在 `/mnt/c` |
| DNS 解析失败 | 公司 VPN 可能覆盖 `/etc/resolv.conf`。可在 `wsl.conf` 关闭 `generateResolvConf` 后手动写 DNS |
| WSL2 占用内存不释放 | 在 `.wslconfig` 限制 memory，或用 `wsl --shutdown` 释放 |
| 导入发行版后默认用户是 root | 用发行版自身命令（如 `ubuntu.exe config --default-user alice`）改 |
| Docker Desktop 连不上 WSL | 在 Docker Desktop Settings → Resources → WSL Integration 里开启对应发行版 |
| WSL 提示 "占位程序接收到错误数据" | 通常是 Windows 防火墙/安全软件拦截，或 LxssManager 服务异常，重启可解 |
| 中文路径乱码 | 统一用 UTF-8，可在 `.wslconfig` 或终端设置里确认编码 |

---

## 10. 快速命令速查表

| 命令 | 作用 |
| --- | --- |
| `wsl --install` | 安装 WSL 和默认 Ubuntu |
| `wsl --install -d <发行版>` | 安装指定发行版 |
| `wsl --list --online` | 可安装发行版列表 |
| `wsl --list -v` | 已安装 + 版本 + 状态 |
| `wsl --set-default <发行版>` | 设置默认发行版 |
| `wsl -d <发行版>` | 启动指定发行版 |
| `wsl --shutdown` | 关闭所有 WSL |
| `wsl --terminate <发行版>` | 关闭指定发行版 |
| `wsl --export <发行版> file.tar` | 导出备份 |
| `wsl --import <名称> <目录> file.tar` | 导入 |
| `wsl --unregister <发行版>` | 卸载 |
| `wsl --update` | 更新 WSL 内核 |
| `wsl --version` | 查看版本 |