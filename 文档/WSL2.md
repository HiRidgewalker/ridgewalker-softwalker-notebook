## 使用的基本条件
+ cpu虚拟化
+ 下载hyperv，并开启虚拟化

> [https://www.bilibili.com/video/BV1tW42197za/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2](https://www.bilibili.com/video/BV1tW42197za/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)
>

wsl2文档：[https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands](https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands)

## 基本命令
下载ubantu默认发行版

```shell
wsl --install --web-download
```

展示所有可以安装的发行版

```shell
wsl --list --online
```

下载指定的linux发行版

```shell
wsl --install linux版本名称 --web-download
```

显示机器上安装的linux子系统的列表

```shell
wsl --list -v
```

设置默认的linux子系统发行版

```shell
wsl --set-default linux版本名称

- 将指定的 Linux 发行版 设置为 默认的 WSL 发行版。
- 当你在命令行中输入 wsl 或 wsl.exe 而 没有指定发行版名称时，就会自动启动这个默认的发行版。
```

命令启动linux子系统

```shell
wsl -d linux系统版本名称
```

退出 （linux子系统会自动停止运行）

```shell
exit
```

卸载linux子系统

```shell
wsl --unregister linux系统版本名称
```

wsl导出linux子系统

```shell
wsl --export linux系统版本名称 压缩文件名称.tar(可以包含文件路径)
```

导入linux子系统

```shell
wsl --import 自定义的linux系统名称 解压子系统的文件路径 压缩包路径
```

关闭所有的wsl服务

```shell
wsl --shutdown
```

暂停某一个linux系统

```shell
wsl --terminate <Distribution Name>
```

