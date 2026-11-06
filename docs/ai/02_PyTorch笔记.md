---
title: "PyTorch 笔记"
sidebar_position: 2
---

# PyTorch 笔记

> 原 旧稿（仅 1 行占位符）与 旧稿 中 `__call__` 等 PyTorch 相关内容的重新整理版本，补充完整的 PyTorch 核心 API 与训练范式。旧稿目录已清理，当前以本文为准。
>
> 相关笔记：[I_ML与DL基础概念笔记](./I_ML与DL基础概念笔记.md) · [II_深度学习环境安装笔记](./II_深度学习环境安装笔记.md)
> 配套 demo：[example/pytorch-demo/](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/pytorch-demo/README.md)

## 目录

1. [PyTorch 是什么](#1-pytorch-是什么)
2. [Tensor 基础](#2-tensor-基础)
3. [设备切换：CPU / CUDA / MPS](#3-设备切换cpu--cuda--mps)
4. [autograd 自动求导](#4-autograd-自动求导)
5. [nn.Module 与 __call__](#5-nnmodule-与-__call__)
6. [优化器（torch.optim）](#6-优化器torchoptim)
7. [数据加载（Dataset / DataLoader）](#7-数据加载dataset--dataloader)
8. [损失函数（torch.nn.loss）](#8-损失函数torchnnloss)
9. [模型保存与加载](#9-模型保存与加载)
10. [完整训练范式](#10-完整训练范式)
11. [baseline 与 pipeline](#11-baseline-与-pipeline)

---

## 1. PyTorch 是什么

### 1.1 定位

由 Meta（原 Facebook）开源的深度学习框架，是学术界事实标准、工业界主流之一。

### 1.2 设计哲学

- **动态图（Define-by-Run）**：每次前向传播都会构建计算图，便于调试（与 TensorFlow 1.x 的静态图相对）
- **Pythonic**：API 设计贴近 NumPy 和 Python 习惯
- **三件套**：`Tensor` + `autograd` + `nn.Module`
- **GPU 加速**：`tensor.cuda()` 或 `tensor.to('cuda')` 一键切到 GPU

### 1.3 安装与版本

详见 [II_深度学习环境安装笔记](./II_深度学习环境安装笔记.md)。验证安装：

```python
import torch
print(torch.__version__)           # PyTorch 版本
print(torch.cuda.is_available())   # 是否有可用 GPU
print(torch.cuda.device_count())   # GPU 数量
```

---

## 2. Tensor 基础

### 2.1 什么是 Tensor

PyTorch 的核心数据结构，类似 NumPy 的 `ndarray`，但能跑在 GPU 上、并支持自动求导。

### 2.2 创建 Tensor

```python
import torch

# 从 list 创建
a = torch.tensor([1, 2, 3])

# 全 0 / 全 1 / 随机
torch.zeros(2, 3)             # 2x3 全 0
torch.ones(2, 3)              # 2x3 全 1
torch.rand(2, 3)              # 2x3 [0,1) 均匀分布
torch.randn(2, 3)             # 2x3 标准正态分布

# 特殊构造
torch.arange(0, 10, 2)        # [0, 2, 4, 6, 8]，类似 range
torch.linspace(0, 1, 5)       # [0, 0.25, 0.5, 0.75, 1]
torch.eye(3)                  # 3x3 单位矩阵

# 从 NumPy 互转
import numpy as np
arr = np.array([1, 2, 3])
t = torch.from_numpy(arr)     # numpy → tensor（共享内存）
back = t.numpy()              # tensor → numpy（共享内存）
```

### 2.3 常用属性

```python
t = torch.randn(2, 3, 4)
t.shape        # torch.Size([2, 3, 4])
t.dtype        # torch.float32
t.device       # device(type='cpu')
t.ndim         # 3
```

### 2.4 形状操作

```python
t = torch.arange(12)                # shape: (12,)
t.view(3, 4)                         # 变形为 (3, 4)，要求内存连续
t.reshape(3, 4)                      # 变形，必要时复制（推荐）
t.unsqueeze(0)                       # 在 dim=0 处加一维 → (1, 12)
t.squeeze()                          # 去掉所有长度为 1 的维
t.transpose(0, 1)                    # 交换两个维度
t.permute(2, 0, 1)                   # 任意重排维度
```

### 2.5 运算

```python
# 逐元素
a + b        a * b        a ** 2
torch.add(a, b)           # 等价 a + b

# 矩阵乘法
a @ b                     # 二维张量等价 torch.mm(a, b)
torch.matmul(a, b)        # 广播式的矩阵乘（支持 batch）

# 聚合
a.sum()                   # 全元素求和
a.mean()                  # 全元素均值
a.max() / a.min()         # 最大/最小
a.argmax(dim=1)           # 沿 dim=1 取最大值的下标

# 拼接
torch.cat([a, b], dim=0)        # 沿已有维度拼接
torch.stack([a, b], dim=0)      # 在新维度上堆叠
```

> 详细 demo 见 [example/pytorch-demo/01_tensor_and_autograd/](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/pytorch-demo/01_tensor_and_autograd/README.md)

---

## 3. 设备切换：CPU / CUDA / MPS

### 3.1 三种设备

| 设备 | 含义 | 适用 |
|------|------|------|
| `cpu` | 普通 CPU | 永远可用、慢 |
| `cuda` | NVIDIA GPU | 需要 NVIDIA 显卡 + CUDA |
| `mps` | Apple Silicon GPU | M1/M2/M3 Mac |

### 3.2 `.to(device)` 切换

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# 或者 Apple Silicon: torch.device('mps') if torch.backends.mps.is_available() else 'cpu'

t = torch.randn(2, 3)
t = t.to(device)        # 把 tensor 搬到 device

model = MyModel()
model = model.to(device)  # 把模型搬到 device
```

> **关键**：模型和它要处理的数据必须在**同一个设备**上，否则会报 `RuntimeError: expected device cuda but got device cpu`。

### 3.3 性能建议

- 能上 GPU 就上 GPU，吞吐可差 10~100 倍
- 数据加载用 `DataLoader(num_workers=...)` 多进程，喂到 GPU 的开销别太大
- `pin_memory=True` + 非阻塞传输（`non_blocking=True`）可加速 CPU→GPU

---

## 4. autograd 自动求导

### 4.1 核心思想

PyTorch 在每次前向传播时构建**动态计算图**，每个有 `requires_grad=True` 的 tensor 节点会自动记录产生它的运算。`.backward()` 沿图反向传播算梯度。

### 4.2 基础用法

```python
import torch

# 1. 准备参数（必须 requires_grad=True）
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(1.0, requires_grad=True)

# 2. 前向
x = torch.tensor(3.0)
y_pred = w * x + b       # y_pred = 2*3 + 1 = 7
loss = (y_pred - 10) ** 2  # loss = (7-10)^2 = 9

# 3. 反向
loss.backward()           # 自动算 w.grad 和 b.grad
print(w.grad)             # tensor(18.) = 2 * (7-10) * 3
print(b.grad)             # tensor(-6.) = 2 * (7-10) * 1
```

### 4.3 三个核心开关

| 开关 | 作用 |
|------|------|
| `requires_grad=True` | tensor 是否参与梯度计算（参数必须开） |
| `with torch.no_grad():` | 上下文内所有运算不构建计算图（推理 / 验证时用） |
| `.detach()` | 把 tensor 从当前图中剥离，返回的新 tensor `requires_grad=False` |

```python
# 推理时：不需要梯度，节省显存
with torch.no_grad():
    pred = model(x)

# 中间结果冻结（detach）
frozen_feature = feature.detach()
```

### 4.4 梯度累加 / 清零

默认每次 `.backward()` 是**累加**到 `.grad` 上的，所以训练时要手动清零：

```python
optimizer.zero_grad()   # 把所有参数的 .grad 清零
loss.backward()          # 反向传播，累加到 .grad
optimizer.step()         # 用 .grad 更新参数
```

### 4.5 梯度裁剪

防止梯度爆炸（RNN / Transformer 常见）：

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

---

## 5. nn.Module 与 `__call__`

> 原笔记 `AI、DeepLearning、MachineLearning零碎知识.md` 中提到的 `__call__` 在这里展开。

### 5.1 `nn.Module` 是什么

所有神经网络模块的**基类**。你可以继承它来定义自己的网络层或整个模型。

```python
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()              # 必须调用父类 init
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = MyModel()
y = model(x)                            # 像函数一样调用
```

### 5.2 `__call__` 的真相

当你写 `model(x)` 时：

1. 触发的是 `nn.Module.__call__(self, x)`（基类实现的 `__call__`）
2. 内部按顺序执行：
   - **前 hooks**：`register_forward_pre_hook` 注册的函数
   - **真正的 forward**：`self.forward(x)`（你重写的方法）
   - **后 hooks**：`register_forward_hook` 注册的函数
3. 所以 `model(x)` ≠ `model.forward(x)`，前者会触发 hooks，后者不会

> 这就是为什么「永远用 `model(x)` 而不是 `model.forward(x)`」——后者会跳过 hooks，行为不一致。

```python
# 等价但不等价
output1 = model(x)        # 推荐：会触发 hooks
output2 = model.forward(x) # 不推荐：跳过 hooks
```

### 5.3 子模块管理

```python
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3)
        self.bn1 = nn.BatchNorm2d(16)
        self.fc = nn.Linear(16 * 26 * 26, 10)
        # 所有 nn.Module 子对象会自动注册，model.parameters() 能找到

net = Net()
for name, p in net.named_parameters():
    print(name, p.shape)         # 自动遍历所有子模块的参数

# 嵌套：把别的 nn.Module 当子模块
class Big(nn.Module):
    def __init__(self):
        super().__init__()
        self.block = Net()      # 整个 Net 作为子模块
```

### 5.4 常用 `nn` 模块速查

| 模块 | 用途 |
|------|------|
| `nn.Linear(in, out)` | 全连接层 |
| `nn.Conv2d(in, out, k)` | 2D 卷积 |
| `nn.Conv1d / Conv3d` | 1D / 3D 卷积 |
| `nn.BatchNorm2d(n)` | 批归一化 |
| `nn.LayerNorm(d)` | 层归一化（Transformer 标配） |
| `nn.ReLU / GELU / SiLU` | 激活函数 |
| `nn.Dropout(p)` | Dropout 正则化 |
| `nn.Embedding(n, d)` | 词嵌入 |
| `nn.RNN / LSTM / GRU` | 循环层 |
| `nn.MultiheadAttention` | 多头注意力 |
| `nn.Transformer` | 完整 Transformer |
| `nn.Sequential(...)` | 按顺序串起来的容器 |

---

## 6. 优化器（torch.optim）

### 6.1 用法范式

```python
import torch.optim as optim

optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

for epoch in range(num_epochs):
    for x, y in dataloader:
        optimizer.zero_grad()           # ① 清零
        pred = model(x)                 # ② 前向
        loss = loss_fn(pred, y)         # ③ 计算损失
        loss.backward()                 # ④ 反向
        optimizer.step()                # ⑤ 更新参数
```

### 6.2 常用优化器

| 优化器 | 关键参数 | 适用 |
|--------|----------|------|
| `optim.SGD` | `lr`, `momentum`, `weight_decay` | 简单任务 / CV 基线 |
| `optim.Adam` | `lr`, `betas=(0.9, 0.999)` | 通用默认 |
| `optim.AdamW` | `lr`, `weight_decay` | Transformer 训练标配 |
| `optim.RMSprop` | `lr`, `alpha` | RNN |

### 6.3 学习率调度（LR Scheduler）

```python
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

for epoch in range(100):
    train_one_epoch()
    scheduler.step()       # 每个 epoch 末尾更新 lr
```

| 调度器 | 行为 |
|--------|------|
| `StepLR` | 每 N 个 epoch 衰减一次 |
| `MultiStepLR` | 在指定 epoch 衰减 |
| `ExponentialLR` | 每个 epoch 乘 gamma |
| `CosineAnnealingLR` | 余弦曲线从 lr 降到 0 |
| `ReduceLROnPlateau` | 指标不再下降时降 lr |
| `LinearLR + CosineAnnealingLR` | Warmup + Cosine（Transformer 标配） |

---

## 7. 数据加载（Dataset / DataLoader）

### 7.1 `Dataset`：定义「一个样本怎么读」

```python
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, data_list):
        self.data = data_list

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x, y = self.data[idx]
        # 可在此做 transform：归一化、随机裁剪、翻转...
        return x, y
```

### 7.2 `DataLoader`：定义「怎么批量喂给模型」

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,            # 训练时打乱
    num_workers=4,           # 多进程读数据
    pin_memory=True,         # 锁页内存，加速 CPU→GPU
    drop_last=True,          # 丢掉最后一个不完整的 batch
)

for batch in loader:
    x, y = batch             # x.shape: (32, ...)，y.shape: (32,)
    ...
```

### 7.3 torchvision 的内置数据集

```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

train_set = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_set  = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
```

---

## 8. 损失函数（torch.nn.loss）

| 损失 | 公式 | 场景 |
|------|------|------|
| `nn.CrossEntropyLoss` | 多分类 softmax + 交叉熵 | 分类任务（logits 输入，无需手动 softmax） |
| `nn.BCEWithLogitsLoss` | 二分类 sigmoid + 二元交叉熵 | 二分类 / 多标签 |
| `nn.MSELoss` | 均方误差 | 回归 |
| `nn.L1Loss` | 平均绝对误差 | 回归、对异常值更鲁棒 |
| `nn.SmoothL1Loss` | L1 + L2 平滑 | 检测任务回归框 |
| `nn.KLDivLoss` | KL 散度 | 蒸馏 |
| `nn.CosineEmbeddingLoss` | 余弦相似度 | 表示学习 |

```python
# 分类任务典型用法
loss_fn = nn.CrossEntropyLoss()
logits = model(x)             # 原始分数，不用过 softmax
loss = loss_fn(logits, target)  # target 是整数类别索引，不是 one-hot
```

---

## 9. 模型保存与加载

### 9.1 推荐方式：只存参数（state_dict）

```python
# 保存
torch.save(model.state_dict(), 'model.pth')

# 加载
model = MyModel()                                  # 先实例化
model.load_state_dict(torch.load('model.pth'))     # 再加载参数
model.eval()                                       # 切到推理模式
```

### 9.2 整模型保存（含结构）

```python
torch.save(model, 'model_full.pth')       # 不推荐：依赖类路径
loaded = torch.load('model_full.pth')
```

### 9.3 断点续训：checkpoint

```python
# 保存
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, 'checkpoint.pth')

# 加载
ckpt = torch.load('checkpoint.pth')
model.load_state_dict(ckpt['model_state_dict'])
optimizer.load_state_dict(ckpt['optimizer_state_dict'])
start_epoch = ckpt['epoch'] + 1
```

### 9.4 跨设备加载

```python
# CPU 加载 GPU 训练的模型
model.load_state_dict(torch.load('model.pth', map_location='cpu'))

# GPU 加载 CPU 训练的模型
model.load_state_dict(torch.load('model.pth', map_location='cuda:0'))
```

---

## 10. 完整训练范式

一个工业级训练循环模板：

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# === 数据 ===
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader   = DataLoader(val_dataset,   batch_size=32, shuffle=False)

# === 模型 / 损失 / 优化器 ===
model     = MyModel().to(device)
loss_fn   = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

# === 训练循环 ===
for epoch in range(num_epochs):
    # ---- 训练 ----
    model.train()
    train_loss = 0
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)

        optimizer.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * x.size(0)

    scheduler.step()

    # ---- 验证 ----
    model.eval()
    val_loss, correct = 0, 0
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            val_loss += loss_fn(pred, y).item() * x.size(0)
            correct += (pred.argmax(dim=1) == y).sum().item()

    print(f'Epoch {epoch+1}/{num_epochs} | '
          f'train_loss={train_loss/len(train_dataset):.4f} | '
          f'val_acc={correct/len(val_dataset):.4f}')

# === 保存 ===
torch.save(model.state_dict(), 'model.pth')
```

**关键细节：**
- `model.train()` / `model.eval()` 切换 Dropout / BN 行为
- `torch.no_grad()` 节省显存、加速验证
- 验证时不调用 `optimizer.step()`
- `loss.item()` 把 0-d tensor 转成 Python 数字用于日志

---

## 11. baseline 与 pipeline

> 承接原笔记 `Pytorch学习笔记.md` 中的 `baseline` 和 `pipeline` 词条。

### 11.1 baseline（基线）

在解决一个新问题时，先用**最简单的可行方案**跑通完整流程，建立**性能下界**。

**为什么必须有 baseline：**
- 没有 baseline，无法判断后续优化的有效性
- 没有 baseline，无法判断模型是真的学到东西还是只是瞎猜

**常见的 baseline：**
- 任务：**分类** → 多数类猜测 / 随机猜
- 任务：**回归** → 输出均值 / 中位数
- 任务：**检测** → 用预训练模型先跑一遍
- 任务：**NLP** → TF-IDF + LR / SVM

**参考文章：** [CSDN - baseline和pipeline](https://blog.csdn.net/qq_38463737/article/details/120743532)

### 11.2 pipeline（流水线）

在 ML 项目中，pipeline 指**端到端的数据 → 模型 → 部署**完整流程。

```text
数据采集 → 数据清洗 → 特征工程 → 模型训练 → 模型评估 → 部署上线 → 监控迭代
   ↑                                                            ↓
   └────────────────── 反馈闭环 ←────────────────────────────────┘
```

**工程实现：**
- **数据 pipeline**：PyTorch `Dataset` / `DataLoader`、Airflow、Spark
- **训练 pipeline**：PyTorch Lightning、HuggingFace Accelerate、DeepSpeed
- **部署 pipeline**：TorchServe、Triton Inference Server、ONNX Runtime
- **编排**：MLflow、Kubeflow、Metaflow

### 11.3 baseline → pipeline → 优化 三步走

```text
Step 1: 跑通 baseline（确保全流程可执行）
        ↓
Step 2: 搭建 pipeline（模块化、可复现）
        ↓
Step 3: 逐步优化（数据 / 模型 / 训练策略）
```

不要一上来就堆叠最新技术 —— 先把 baseline 跑通。

---

## 速查卡片

```text
训练 5 步：zero_grad → forward → loss → backward → step
模型调用：model(x) 不要用 model.forward(x)
设备切换：.to(device)，模型和数据必须在同一设备
推理模式：with torch.no_grad(): + model.eval()
参数保存：state_dict() + load_state_dict()
优化器默认：Adam / AdamW
Loss 默认：分类用 CrossEntropyLoss
```

---

## 对应笔记

- [I_ML与DL基础概念笔记](./I_ML与DL基础概念笔记.md) — ML/DL 基础概念与训练流程
- [II_深度学习环境安装笔记](./II_深度学习环境安装笔记.md) — CUDA / cuDNN / PyTorch 安装
- [example/pytorch-demo/01_tensor_and_autograd/](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/pytorch-demo/01_tensor_and_autograd/README.md) — Tensor / autograd 可运行 demo
- [example/pytorch-demo/02_nn_module_training/](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/pytorch-demo/02_nn_module_training/README.md) — nn.Module 训练可运行 demo

## 历史笔记

- 旧稿 Pytorch学习笔记 — 原 PyTorch 占位笔记（基本为空），已被本篇替代
- 旧稿 AI、DeepLearning、MachineLearning零碎知识 — 原零碎笔记，`__call__` 等 PyTorch 相关内容已并入本篇
