# Mac 使用笔记

> 整合自 `文档/mac磁盘修复.md`、`文档/macos快捷键.md`、`文档/MACOS常用命令.md`、`文档/logi.md`。原笔记保留在原位置供回溯。
>
> 原则：只整理现有内容，不延伸、不扩展。

## 一、系统维护：磁盘修复

> 来源：[bilibili 文章](https://www.bilibili.com/opus/583456626963920387)

### 1.1 核心命令

| 命令 | 作用 |
| --- | --- |
| `diskutil list` | 查看所有接入设备的磁盘 |
| `diskutil mount disk4s1` | 挂载指定硬盘 |
| `diskutil verifyVolume disk4s1` | 验证硬盘（急救前先验证） |
| `diskutil repairVolume disk4s1` | 修复硬盘 |

### 1.2 完整流程

当硬盘无法识别时：

1. `diskutil list` —— 查看所有磁盘
2. `diskutil mount disk4s1` —— 挂载指定硬盘
3. 如果挂载超时：
   - `ps aux | grep fsck` —— 查看进程
   - `sudo pkill -f fsck` —— 终止进程
4. `diskutil verifyVolume disk4s1` 或 `diskutil repairVolume disk4s1` —— 修复硬盘

> 注意：`disk4s1` 中的数字需要根据实际情况替换成你的硬盘编号。

## 二、常用命令

### 2.1 `which`

`which 软件名称`：查看软件安装位置。

### 2.2 `source`

`source 文件名称`：在当前 shell 环境中执行某个脚本文件里的内容。

- 它会：读取文件 → 按行执行 → 结果直接影响当前终端环境。

## 三、系统快捷键

> 来源：[快捷键文章](https://blog.ninc.top/posts/cheat-sheet/mac-quickKeys)

| 快捷键 | 功能 |
| --- | --- |
| `option + 点击绿色最大化按钮` | 应用铺满窗口但不全屏 |

## 四、应用快捷键

### 4.1 PyCharm

| 快捷键 | 功能 |
| --- | --- |
| `command + shift + f` | 全局搜索 |
| `command + option + 左/右方向键` | 从当前位置切换到上一个位置 / 下一个位置 |
| `command + shift + + / -` | 展开 / 折叠所有代码 |
| `command + + / -` | 展开 / 折叠当前块 |

### 4.2 VSCode

| 快捷键 | 功能 |
| --- | --- |
| `command + 触控板单击` | 进入源代码内部 |
| `control + -` | 返回上一个代码位置 |
| `control + shift + -` | 返回下一个代码位置 |

## 五、外设：Logi MX Keys Mini

### 5.1 系统切换

| 快捷键 | 功能 |
| --- | --- |
| `fn + o`（长按 3 秒） | 切换成 OS 系统 |
| `fn + p`（长按 3 秒） | 切换成 WIN 系统 |