相关文章：[文章链接](https://www.bilibili.com/opus/583456626963920387)
文章命令总结：
你好！我已经仔细阅读了这篇文章，发现有几处命令缺失。根据上下文，我帮你补充完整的命令：
####  缺失的命令补充：

##### 1. **查看所有接入设备的磁盘**

文章位置：「在终端中输入命令：」之后

```bash
diskutil list
```

##### 2. **执行挂载硬盘**

文章位置：「接下来你可以在终端中输入：」之后

```bash
diskutil mount disk4s1
```

##### 3. **在终端中执行急救命令**

文章位置：「你也可以在终端中输入」之后

```bash
diskutil verifyVolume disk4s1
```

或者用修复命令：

```bash
diskutil repairVolume disk4s1
```

---

### 完整流程总结：

**当硬盘无法识别时：**

1. `diskutil list` - 查看所有磁盘
2. `diskutil mount disk4s1` - 挂载指定硬盘
3. 如果挂载超时：
    - `ps aux | grep fsck` - 查看进程
    - `sudo pkill -f fsck` - 终止进程
4. `diskutil verifyVolume disk4s1` 或 `diskutil repairVolume disk4s1` - 修复硬盘

注意：`disk4s1` 中的数字需要根据实际情况替换成你的硬盘编号。

希望这些补充能帮到你！如果还有其他问题，欢迎继续提问。