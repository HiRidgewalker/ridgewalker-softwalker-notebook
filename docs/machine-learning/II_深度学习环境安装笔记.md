---
title: "深度学习环境安装笔记"
sidebar_position: 2
---

# 深度学习环境安装笔记

> 旧稿中所有安装相关内容的系统化整理。补充了 CUDA Toolkit / Runtime / Driver 区别、版本对应关系、常见错误排错清单。旧稿目录已清理，当前以本文为准。
>
> 相关笔记：[I_ML与DL基础概念笔记](./I_ML与DL基础概念笔记.md) · [02_PyTorch笔记](../pytorch/02_PyTorch笔记.md)

## 目录

1. [必须先搞清的三层关系](#1-必须先搞清的三层关系)
2. [安装顺序](#2-安装顺序)
3. [查看命令](#3-查看命令)
4. [NVIDIA 驱动安装](#4-nvidia-驱动安装)
5. [CUDA Toolkit 安装](#5-cuda-toolkit-安装)
6. [cuDNN 安装](#6-cudnn-安装)
7. [PyTorch 安装](#7-pytorch-安装)
8. [版本对应关系速查](#8-版本对应关系速查)
9. [常见安装错误与排错](#9-常见安装错误与排错)
10. [Windows / Linux 差异](#10-windows--linux-差异)
11. [CPU-only 安装](#11-cpu-only-安装)

---

## 1. 必须先搞清的三层关系

> 原笔记关键澄清：「`nvidia-smi` 看到的 CUDA 版本是驱动支持的最高版本，不代表已安装」。

很多人第一次装环境都被这三层关系搞晕过。先把它们区分清楚：

| 概念 | 全称 | 是什么 | 谁依赖谁 |
|------|------|--------|----------|
| **NVIDIA Driver** | NVIDIA 显卡驱动 | 让操作系统能使用 GPU | 不依赖任何东西，最底层 |
| **CUDA Toolkit** | CUDA 开发工具包 | nvcc 编译器 + 库 + headers，给程序调用 | 依赖对应版本范围的 Driver |
| **CUDA Runtime** | CUDA 运行时 | 程序实际跑起来时的 CUDA 库 | 包含在 Toolkit 中，但版本受 Driver 限制 |

### 1.1 一个常见误解

```text
nvidia-smi 显示 CUDA Version: 12.6   ← 这是驱动支持的最高 Runtime 版本
nvcc --version 显示 release 11.8     ← 这是你安装的 Toolkit 版本

两者可以不同！
- Driver 高于 Toolkit 是 OK 的（向下兼容）
- Driver 低于 Toolkit 就会运行失败
```

**类比：**

| 层级 | 类比 | 例子 |
|------|------|------|
| Driver | 操作系统的语言包 | Windows 11 自带的中文语言包 |
| CUDA Toolkit | 开发 SDK | VS 编译器 + 文档 + 示例 |
| CUDA Runtime | 程序运行时依赖 | 应用程序需要的运行时 DLL |

### 1.2 PyTorch 的 CUDA 版本

PyTorch 安装时绑定的是一个**特定的 CUDA Runtime 版本**（编译时用哪个就绑哪个）。

```python
import torch
print(torch.version.cuda)   # 12.1  ← PyTorch 编译时用的 CUDA
print(torch.cuda.is_available())  # True 才能跑 GPU
```

**PyTorch 编译时 CUDA ≥ 系统 Driver 支持的 CUDA** 即可运行（Driver 向上兼容）。

---

## 2. 安装顺序

```text
① NVIDIA Driver        ← 必需先装，最底层
        ↓
② CUDA Toolkit         ← 第二层，nvcc 编译器 + 库
        ↓
③ cuDNN                ← 第三层，深度学习专用加速库（拷贝文件即可）
        ↓
④ PyTorch (torch)      ← 最上层，通过 pip/conda 安装
```

**反过来装会导致版本错配问题。**

---

## 3. 查看命令

### 3.1 显卡与驱动

```bash
# Linux / WSL
nvidia-smi

# 输出示例：
# +─────────────────────────────────────────────+
# | NVIDIA-SMI 550.54.15    Driver Version: 550.54.15  |
# |              CUDA Version: 12.4                    |
# |─────────────────────────────────────────────|
# | GPU Name         Persistence-M | Bus-Id        |
# | 0  NVIDIA GeForce RTX 4090   On  | 00000000:01:00.0 |
# +─────────────────────────────────────────────+
```

### 3.2 CUDA Toolkit 版本

```bash
nvcc --version
# nvcc: NVIDIA (R) Cuda compiler driver
# Cuda compilation tools, release 12.1, V12.1.105

# 或者
nvcc -V
```

### 3.3 PyTorch 的 CUDA 版本

```python
import torch
print(torch.__version__)            # 2.1.0+cu121
print(torch.version.cuda)           # 12.1
print(torch.backends.cudnn.version())  # 8902 (cuDNN 8.9.2)
```

### 3.4 完整验证脚本

```bash
# 保存为 check_gpu.sh，跑一下确认环境正确
python -c "
import torch
print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('Device:', torch.cuda.get_device_name(0))
    print('Device count:', torch.cuda.device_count())
    x = torch.randn(3, 3).cuda()
    y = (x @ x.T)
    print('GPU compute test OK, shape:', y.shape)
"
```

---

## 4. NVIDIA 驱动安装

### 4.1 Windows

1. 去 [NVIDIA 驱动下载页](https://www.nvidia.com/Download/index.aspx) 选显卡型号
2. 下载 .exe 安装包，双击安装
3. 重启

### 4.2 Linux / WSL

**方式 A：Ubuntu 官方包（推荐）**

```bash
# 查看推荐驱动
ubuntu-drivers devices

# 自动安装推荐版本
sudo ubuntu-drivers autoinstall

# 重启
sudo reboot
```

**方式 B：NVIDIA 官方 .run 文件**

```bash
# 1. 禁用 nouveau
sudo bash -c "echo 'blacklist nouveau' >> /etc/modprobe.d/blacklist.conf"
sudo update-initramfs -u
sudo reboot

# 2. 安装
chmod +x NVIDIA-Linux-x86_64-*.run
sudo ./NVIDIA-Linux-x86_64-*.run

# 3. 验证
nvidia-smi
```

### 4.3 WSL 特别注意

WSL2 安装 NVIDIA 驱动有两种方式：

- **方式 A（推荐）**：Windows 上装 NVIDIA 驱动 + 在 WSL2 内 `nvidia-smi` 直接可用，**不需要在 WSL2 内重复装驱动**
- **方式 B**：WSL2 内独立装 CUDA Toolkit（不需要 Driver，Driver 由 Windows 提供）

参考：[CUDA on WSL 官方文档](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

---

## 5. CUDA Toolkit 安装

> 原笔记链接保留：[CUDA Toolkit 下载页](https://developer.nvidia.com/cuda-toolkit)

### 5.1 选择版本

- 去 [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive) 选你要的版本（11.8 / 12.1 / 12.4 等）
- **必须先看 PyTorch 官方支持哪些 CUDA 版本**：[pytorch.org/get-started](https://pytorch.org/get-started/locally/) 上有「Compute Platform」选项

### 5.2 Linux 安装（runfile）

```bash
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# 安装时取消勾选 Driver（如果已装）
# 安装完配置环境变量
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 验证
nvcc --version
```

### 5.3 Linux 安装（deb / apt）

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-12-1
```

### 5.4 Windows 安装

下载 .exe，双击安装。会自动配 PATH。

---

## 6. cuDNN 安装

> 原笔记链接保留：[Windows 安装 CUDA 和 cuDNN 保姆级教程](https://blog.csdn.net/m0_66434421/article/details/147337716)

cuDNN 是 NVIDIA 为深度学习优化的库（卷积、池化、归一化等加速），PyTorch 内部依赖。

**cuDNN 不需要编译，解压拷贝即可：**

### 6.1 安装步骤

1. 去 [cuDNN 下载页](https://developer.nvidia.com/cudnn)（需要注册 NVIDIA 账号）
2. 下载对应 CUDA 版本的 cuDNN（如 `cudnn-linux-x86_64-8.9.5.30_cuda12-archive.tar.xz`）
3. 解压，把文件复制到 CUDA Toolkit 目录：

```bash
# Linux 示例
tar -xvf cudnn-linux-x86_64-8.9.5.30_cuda12-archive.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

```powershell
# Windows：把 bin/include/lib 三个文件夹的内容复制到
# C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\
```

### 6.2 版本对应

| CUDA 版本 | 推荐 cuDNN 版本 |
|-----------|-----------------|
| CUDA 12.x | cuDNN 8.9 / 9.0 |
| CUDA 11.8 | cuDNN 8.6 / 8.7 / 8.9 |
| CUDA 11.7 | cuDNN 8.4 / 8.5 |
| CUDA 11.6 | cuDNN 8.3 / 8.4 |

---

## 7. PyTorch 安装

### 7.1 在线安装（推荐）

去 [pytorch.org/get-started](https://pytorch.org/get-started/locally/) 选系统 / 包管理器 / Python / CUDA，会生成命令。

**示例（CUDA 12.1，pip）：**

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**示例（CUDA 11.8，pip）：**

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**示例（conda）：**

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### 7.2 离线安装（whl）

> 原笔记链接保留：[torch whl 离线下载页](https://download.pytorch.org/whl/torch_stable.html)

适用场景：内网机器、离线服务器、conda/pip 装不上需要兜底。

**步骤：**

1. 在有网络的机器上打开 [torch_stable.html](https://download.pytorch.org/whl/torch_stable.html)
2. 找匹配 Python 版本、操作系统、CUDA 版本的 whl 文件，例如：
   ```
   torch-2.1.0+cu121-cp311-cp311-win_amd64.whl
   ```
   - `cp311` = Python 3.11
   - `win_amd64` = Windows 64 位
   - `cu121` = CUDA 12.1
3. 下载 + 同目录下其他依赖的 whl（torchvision、torchaudio 等）
4. 拷贝到目标机器，`pip install xxx.whl` 安装

**参考：** [超详细教程 - 2025 最新 PyTorch 安装](https://blog.csdn.net/Mr_Chp/article/details/146641434)（原笔记链接保留）

### 7.3 安装后必须验证

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

输出 `True` 才算装成功。`False` 表示 CUDA Runtime 与 Driver 不匹配。

---

## 8. 版本对应关系速查

### 8.1 NVIDIA Driver 与 CUDA 最高支持版本

| Driver 版本 | 支持的最高 CUDA |
|------------|----------------|
| 470.x | CUDA 11.4 |
| 515.x | CUDA 11.7 |
| 525.x | CUDA 12.0 |
| 530.x | CUDA 12.1 |
| 535.x | CUDA 12.2 |
| 545.x | CUDA 12.3 |
| 550.x | CUDA 12.4 |
| 555.x | CUDA 12.5 |

> 表格来自 [CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html)。Driver 向上兼容（高版本 Driver 支持所有低版本 CUDA）。

### 8.2 PyTorch 与 CUDA

| PyTorch 版本 | 编译时 CUDA |
|-------------|-------------|
| 2.4.x | 12.1 / 11.8 |
| 2.3.x | 12.1 / 11.8 |
| 2.2.x | 12.1 / 11.8 |
| 2.1.x | 12.1 / 11.8 |
| 2.0.x | 11.8 / 11.7 |
| 1.13.x | 11.7 / 11.6 |

去 [PyTorch 官网](https://pytorch.org/get-started/locally/) 看实时支持的 CUDA 列表。

### 8.3 一张图速查

```text
┌─────────────────────────────────────────────────────────────┐
│  你的环境                                                    │
│                                                             │
│  NVIDIA Driver (如 550.x)                                    │
│       ↑ 支持所有 ≤ CUDA 12.4 的 Runtime                      │
│       │                                                     │
│       ├─── CUDA Toolkit 12.1 (可选安装)                       │
│       │      ↑                                               │
│       │      └── cuDNN 8.9 (可选安装)                         │
│       │                                                     │
│       └─── PyTorch 2.4 (pip install 即可)                     │
│              编译时 CUDA = 12.1                              │
│              ↓                                               │
│         检查 torch.version.cuda == '12.1'                    │
│         检查 torch.cuda.is_available() == True               │
└─────────────────────────────────────────────────────────────┘
```

**最简原则：**
1. 装最新的稳定版 NVIDIA Driver
2. 去 PyTorch 官网选 CUDA 版本（一般 11.8 或 12.1）
3. `pip install` 对应 wheel
4. 验证 `torch.cuda.is_available() == True`

如果只需要 Python 层训练、不写 CUDA C++，**可以不装 CUDA Toolkit 和 cuDNN**，pip 装 PyTorch 自带必要的库。

---

## 9. 常见安装错误与排错

### 9.1 `torch.cuda.is_available()` 返回 False

**原因排查顺序：**

1. **NVIDIA Driver 没装或太旧**：`nvidia-smi` 报错或版本 < 470
   ```bash
   nvidia-smi
   # 报错 → 装驱动
   # 版本太低 → 升级驱动
   ```

2. **PyTorch 是 CPU 版**：装错了 wheel
   ```bash
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

3. **WSL2 没启用 GPU 直通**：确认 Windows NVIDIA 驱动版本 ≥ 525
   - 旧 WSL2 kernel 不支持，升级 `wsl --update`

4. **多 GPU 机器环境变量错乱**：`CUDA_VISIBLE_DEVICES` 设错了

### 9.2 `undefined symbol: cublasLtGetStatusString` 等链接错误

**原因：** cuDNN / CUDA 与 PyTorch 编译时版本不匹配

**解决：** 重装匹配的版本（按官网 wheel 装最稳）

### 9.3 `CUDA error: no kernel image is available for execution on the device`

**原因：** GPU 算力太新（如 RTX 4090 早期），PyTorch / CUDA 版本太老不支持

**解决：** 升级 PyTorch 到 ≥ 2.1（支持 sm_89 / sm_90）

### 9.4 `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver`

**原因：** Driver 与 kernel 不匹配（多见于 Linux）

**解决：**
```bash
sudo apt-get install --reinstall linux-headers-$(uname -r)
sudo reboot
```

### 9.5 离线安装 whl 时报 `torchvision` / `torchaudio` 版本找不到

**原因：** torchvision / torchaudio 必须严格匹配 torch 版本

**解决：** 用同一个 whl 源、同一个 CUDA tag 装：
```bash
pip install torch-2.1.0+cu121-cp311-cp311-linux_x86_64.whl
pip install torchvision-0.16.0+cu121-cp311-cp311-linux_x86_64.whl
pip install torchaudio-2.1.0+cu121-cp311-cp311-linux_x86_64.whl
```

### 9.6 pip install 速度慢 / 超时

**解决：** 换国内源
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple torch
```

PyTorch 官方源可换：
```bash
# 阿里云
pip install torch -i https://mirrors.aliyun.com/pytorch-wheels/cu121/
```

### 9.7 OOM（CUDA Out of Memory）

```text
RuntimeError: CUDA out of memory. Tried to allocate 1.50 GiB.
GPU 0 has a total capacity of 7.79 GiB of which 1.14 GiB is free.
```

**排查：**
- 减小 `batch_size`
- 启用混合精度：`with torch.cuda.amp.autocast():`
- 释放不用的中间变量：`del xxx; torch.cuda.empty_cache()`
- 检查有没有遗留的张量（Python 引用没断，显存不释放）

### 9.8 `RuntimeError: NCCL error in: ...`

**原因：** 多卡通信（NCCL）出问题

**排查：**
- 确认 `NCCL_DEBUG=INFO` 启动看详细日志
- 单卡测试能否跑通，多卡再试
- 容器/集群环境确认网络互通

---

## 10. Windows / Linux 差异

| 项 | Windows | Linux |
|----|---------|-------|
| 驱动安装 | .exe 图形化 | apt / .run 命令行 |
| 默认 shell | PowerShell / CMD | bash / zsh |
| WSL 支持 | 需要 WSL2 | 原生 |
| 路径分隔 | `\ ` | `/` |
| 多卡 NCCL | 经常有问题 | 正常 |
| 常用包管理器 | pip + conda | pip + conda + 系统包 |
| Docker 部署 | 麻烦 | 主流 |

**生产环境强烈推荐 Linux + Docker**。本地开发 Windows 够用，建议装 WSL2 跑实验。

---

## 11. CPU-only 安装

没显卡 / 不想折腾 CUDA / 只是学习小模型 → 装 CPU 版就够。

```bash
# 默认就是 CPU 版（不带 +cu 后缀）
pip install torch torchvision torchaudio

# 或用官网 CPU 选项
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**CPU 也能跑通所有 demo**，只是训练速度慢 10~100 倍。学习 PyTorch API 完全可以。

```python
import torch
print(torch.cuda.is_available())  # False
# 模型照样能跑，只是不在 GPU 上
model = torch.nn.Linear(3, 3)
y = model(torch.randn(2, 3))
```

**适用场景：**
- 学习 API / 调试代码
- 小模型（如逻辑回归、MLP、小 CNN）
- 数据集小（MNIST / CIFAR-10）
- 无 GPU 的机器

---

## 速查卡片

```text
安装顺序：Driver → CUDA Toolkit → cuDNN → PyTorch
验证命令：nvidia-smi / nvcc --version / torch.cuda.is_available()
只看 PyTorch 训练：装 Driver + pip 装 PyTorch wheel 即可
PyTorch 离线 whl：https://download.pytorch.org/whl/torch_stable.html
nvidia-smi 看到的 CUDA ≠ 已安装的 CUDA Toolkit
Driver 高于 Toolkit → OK，向下兼容
Driver 低于 Toolkit → 运行失败
CPU-only：pip install torch 即可
```

---

## 对应笔记

- [I_ML与DL基础概念笔记](./I_ML与DL基础概念笔记.md) — ML/DL 基础概念
- [02_PyTorch笔记](../pytorch/02_PyTorch笔记.md) — PyTorch 核心 API
- [example/pytorch-demo/](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/pytorch-demo/README.md) — PyTorch 可运行 demo

## 历史笔记

- 旧稿 AI、DeepLearning、MachineLearning零碎知识 — 原零碎笔记，所有安装相关内容已并入本篇