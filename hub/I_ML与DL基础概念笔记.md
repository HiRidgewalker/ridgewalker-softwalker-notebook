# 机器学习与深度学习基础概念笔记

> 原 旧稿 与 旧稿 的重新整理版本，补充大量基础概念内容。旧稿目录已清理，当前以本文为准。
>
> 配套 demo：[example/pytorch-demo/](../example/pytorch-demo/)
> 相关笔记：[[02_PyTorch笔记]] · [[II_深度学习环境安装笔记]]

## 目录

1. [AI / ML / DL 三者关系](#1-ai--ml--dl-三者关系)
2. [机器学习三大范式](#2-机器学习三大范式)
3. [标准训练流程](#3-标准训练流程)
4. [神经网络基础](#4-神经网络基础)
5. [CNN 卷积神经网络](#5-cnn-卷积神经网络)
6. [网络模型结构：Backbone / Neck / Head](#6-网络模型结构backbone--neck--head)
7. [训练常用名词](#7-训练常用名词)
8. [评估指标简表](#8-评估指标简表)
9. [优化器简介](#9-优化器简介)
10. [常见任务类型](#10-常见任务类型)
11. [数学背景补充](#11-数学背景补充)

---

## 1. AI / ML / DL 三者关系

**AI（Artificial Intelligence，人工智能）** 是最宽泛的概念：让机器表现出类人智能行为的任何技术。

**ML（Machine Learning，机器学习）** 是 AI 的一个子集：不写显式规则，而是让模型从数据中学习规律。

**DL（Deep Learning，深度学习）** 是 ML 的一个子集：使用深层神经网络（通常有多个隐藏层）来学习表示。

```
┌─────────────────────────────────────────┐
│              AI（人工智能）                │
│  ┌───────────────────────────────────┐   │
│  │       ML（机器学习）                │   │
│  │  ┌─────────────────────────────┐  │   │
│  │  │   DL（深度学习，多层神经网络） │  │   │
│  │  └─────────────────────────────┘  │   │
│  └───────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

| 名称 | 典型方法 | 数据需求 | 代表场景 |
|------|----------|----------|----------|
| AI（早期） | 规则系统、专家系统、搜索 | 无需数据 | 国际象棋、逻辑推理 |
| ML | 决策树、SVM、线性回归、KNN | 中等 | 信用评分、推荐系统 |
| DL | CNN、RNN、Transformer | 大 | 图像识别、语音、NLP |

---

## 2. 机器学习三大范式

### 2.1 监督学习（Supervised Learning）

**定义：** 给定「输入 - 输出」标注对，训练模型学习从输入到输出的映射。

```text
输入 X          标签 y          模型          预测 ŷ
─────→ ─────→   f(X)   ─────→   与 y 比较 → 损失
```

**典型任务：**
- **分类（Classification）**：标签是离散类别（猫 / 狗 / 鸟）
- **回归（Regression）**：标签是连续数值（房价、温度）

**代表算法：** 线性回归、逻辑回归、SVM、决策树、随机森林、神经网络

### 2.2 无监督学习（Unsupervised Learning）

**定义：** 数据只有输入，没有标签，让模型自己发现数据中的结构。

**典型任务：**
- **聚类（Clustering）**：把相似样本归类（K-Means、DBSCAN）
- **降维（Dimensionality Reduction）**：把高维数据压到低维（PCA、t-SNE）
- **密度估计 / 生成**：学习数据分布（GAN、VAE、自回归模型）

### 2.3 强化学习（Reinforcement Learning, RL）

**定义：** 智能体（Agent）在环境（Environment）中通过试错学习，根据奖励（Reward）调整策略（Policy）。

```text
Agent ─action─→ Environment ─state, reward─→ Agent
```

**代表算法：** Q-Learning、Policy Gradient、PPO、DQN

### 2.4 半监督 & 自监督

- **半监督**：少量标注 + 大量未标注
- **自监督**：从数据本身构造伪标签（如 BERT 的 MLM、GPT 的下一 token 预测）—— 大模型预训练的典型范式

---

## 3. 标准训练流程

一个完整的监督学习训练循环如下：

```text
┌──────────────────────────────────────────────────┐
│  1. 准备数据（Dataset / DataLoader）               │
│  2. 选择模型（nn.Module）                          │
│  3. 选择损失函数（Loss）                            │
│  4. 选择优化器（Optimizer）                         │
│  5. 训练循环：                                      │
│     for epoch in epochs:                           │
│       for batch in dataloader:                     │
│         ① 清零梯度  optimizer.zero_grad()           │
│         ② 前向传播  pred = model(x)                │
│         ③ 计算损失  loss = loss_fn(pred, y)         │
│         ④ 反向传播  loss.backward()                │
│         ⑤ 更新参数  optimizer.step()               │
│  6. 验证 / 测试（Eval 模式，不更新梯度）              │
│  7. 保存模型（state_dict）                          │
└──────────────────────────────────────────────────┘
```

**关键点：**
- 训练时模型是 `train()` 模式（Dropout / BatchNorm 行为不同）
- 验证 / 测试时切换 `eval()`，并用 `torch.no_grad()` 关闭梯度节省显存
- 训练 step 的固定 5 步顺序不能乱（尤其 `zero_grad` 必须在 `backward` 之前）

---

## 4. 神经网络基础

### 4.1 神经元（Neuron）

模拟生物神经元：接受多个输入，加权求和后通过激活函数输出。

```text
      x1 ─w1─┐
      x2 ─w2─┤
      x3 ─w3─┤── Σ ── activation ── y
      ...     │
      xn ─wn─┘
```

数学表达：`y = activation(w·x + b)`

### 4.2 层（Layer）

- **输入层（Input Layer）**：接收原始特征
- **隐藏层（Hidden Layer）**：特征变换
- **输出层（Output Layer）**：产出最终预测

"深度学习"中的"深度"指隐藏层数量多（一般 ≥ 3 层就算深）。

### 4.3 激活函数（Activation）

引入非线性，让网络能拟合复杂函数。

| 名称 | 公式 | 输出范围 | 用途 |
|------|------|----------|------|
| Sigmoid | `1/(1+e^-x)` | (0, 1) | 二分类输出 |
| Tanh | `(e^x-e^-x)/(e^x+e^-x)` | (-1, 1) | 隐藏层（已被 ReLU 替代） |
| ReLU | `max(0, x)` | [0, +∞) | 隐藏层（最常用） |
| Softmax | `e^xi / Σe^xj` | (0, 1)，和为 1 | 多分类输出 |
| GELU / Swish | 略 | (-, +) | Transformer 隐藏层 |

### 4.4 前向传播（Forward）

输入 → 层层变换 → 输出。本质就是矩阵乘法 + 激活函数的反复嵌套。

---

## 5. CNN 卷积神经网络

> 原笔记已有「CNN（卷积）、卷积核、池化」词条，这里系统展开。

CNN 是处理**图像**类网格数据的主流架构（现在也被用于 1D 信号、2D 频谱等）。

### 5.1 卷积核（Kernel / Filter）

一个小的权重矩阵（如 3×3），在输入上滑动做点积，提取局部特征。

```text
输入（5×5）             卷积核（3×3）         输出（3×3）
┌───────────┐          ┌─────────┐         ┌─────┐
│ 1 2 3 4 5 │          │ 1 0 1   │         │ ... │
│ 6 7 8 9 1 │   *      │ 0 1 0   │   =     │ ... │
│ 2 3 4 5 6 │          │ 1 0 1   │         │ ... │
│ 7 8 9 1 2 │          └─────────┘         └─────┘
│ 3 4 5 6 7 │
└───────────┘
```

### 5.2 卷积运算的关键参数

- **步长（Stride）**：卷积核每次滑动的步数。步长越大，输出越小
- **填充（Padding）**：在输入边缘补 0（或其他值），控制输出尺寸
- **输出尺寸公式**：`O = (I - K + 2P) / S + 1`
  - `I` 输入尺寸，`K` 卷积核尺寸，`P` 填充，`S` 步长

### 5.3 池化（Pooling）

下采样，减少特征图尺寸、扩大感受野、减少计算量。

| 类型 | 做法 | 特点 |
|------|------|------|
| 最大池化（Max Pooling） | 取窗口内最大值 | 保留最强特征，最常用 |
| 平均池化（Average Pooling） | 取窗口内平均值 | 平滑、保留整体信息 |
| 全局平均池化（Global Avg Pool） | 整张图取一个均值 | 替代全连接层，减少参数 |

### 5.4 一个典型 CNN 结构

```text
Input → [Conv → ReLU → Pool] × N → Flatten → FC → Output
         ↑ 重复堆叠
```

代表网络：LeNet、AlexNet、VGG、ResNet、EfficientNet

---

## 6. 网络模型结构：Backbone / Neck / Head

> 承接原笔记「网络模型分为主干网络，颈部网络和头部网络」。

这个三段式划分是目标检测 / 分割 / 识别等任务的标准架构。

```text
┌──────────────┐    ┌──────────┐    ┌──────────┐
│   Backbone   │ →  │   Neck   │ →  │   Head   │ →  最终输出
│   主干网络    │    │  颈部网络 │    │  头部网络  │
└──────────────┘    └──────────┘    └──────────┘
```

| 部分 | 作用 | 典型实现 |
|------|------|----------|
| **Backbone** | 提取基础特征（边缘、纹理、形状） | ResNet、ViT、Swin Transformer |
| **Neck** | 多尺度特征融合、上下文增强 | FPN、PANet、BiFPN |
| **Head** | 针对具体任务输出预测 | 检测头（YOLO Head）、分割头（Mask Head）、分类头（FC） |

**示例：YOLOv5/v8 的结构**

```text
Input
  ↓ Backbone (CSPDarknet / YOLOv8 Backbone)
[P3, P4, P5] 多尺度特征
  ↓ Neck (FPN + PAN)
融合后的多尺度特征
  ↓ Head (Detect Head)
[boxes, scores, classes]
```

---

## 7. 训练常用名词

| 名词 | 定义 |
|------|------|
| **Epoch** | 把整个训练集过一遍 |
| **Batch** | 一次前向 + 反向更新所用的样本集合 |
| **Iteration / Step** | 处理一个 batch 算一次 iteration |
| **Learning Rate (lr)** | 优化器每次更新的步长 |
| **Momentum** | 优化器的惯性项（SGD 中常用 0.9） |
| **Weight Decay** | 权重衰减（一种正则化，等价于 L2 正则） |
| **Gradient Descent** | 沿损失函数负梯度方向更新参数 |
| **Backpropagation** | 用链式法则从输出层往回算梯度 |
| **Overfitting** | 训练集表现好但测试集差 |
| **Underfitting** | 训练集都没学好 |
| **Regularization** | 抑制过拟合（Dropout、Weight Decay、数据增强） |

**Epoch / Batch / Iteration 关系：**

```text
1 Epoch = 整个数据集过一遍 = N 个 Iteration
N = 总样本数 / Batch Size
例：1000 张图，batch=32，则 1 epoch ≈ 32 次 iteration
```

---

## 8. 评估指标简表

### 8.1 分类任务

| 指标 | 公式 | 含义 |
|------|------|------|
| Accuracy | `(TP+TN) / Total` | 整体正确率 |
| Precision | `TP / (TP+FP)` | 预测为正的里面多少真为正 |
| Recall | `TP / (TP+FN)` | 真实为正的里面多少被召回 |
| F1 | `2·P·R / (P+R)` | P 和 R 的调和均值 |
| AUC | ROC 曲线下面积 | 衡量排序能力，对阈值不敏感 |
| mAP | mean Average Precision | 多类别 / 多 IoU 阈值平均精度（检测任务） |

**混淆矩阵：**

```text
            预测正    预测负
实际正       TP        FN
实际负       FP        TN
```

### 8.2 回归任务

| 指标 | 说明 |
|------|------|
| MAE | 平均绝对误差 |
| MSE | 平均平方误差（对异常值敏感） |
| RMSE | MSE 的平方根 |
| R² | 决定系数，越接近 1 越好 |

---

## 9. 优化器简介

| 优化器 | 核心思想 | 适用 |
|--------|----------|------|
| **SGD** | 沿负梯度方向更新 | 简单任务、可解释、需要精细调参 |
| **SGD + Momentum** | 加惯性 | 通用，最常用基线 |
| **Adam** | 自适应学习率 + 动量 | 几乎所有深度学习任务默认选择 |
| **AdamW** | Adam + 解耦的权重衰减 | Transformer 训练标配 |
| **RMSProp** | 自适应学习率 | RNN |

**学习率调度（LR Scheduler）：**

- `StepLR`：每隔 N 个 epoch 衰减
- `CosineAnnealing`：余弦曲线衰减
- `ReduceLROnPlateau`：指标不再下降时衰减
- **Warmup**：训练初期 lr 从小到大（Transformer 训练必要）

---

## 10. 常见任务类型

| 任务 | 输入 | 输出 | 代表模型 |
|------|------|------|----------|
| 图像分类 | 单张图 | 类别 | ResNet、ViT |
| 目标检测 | 单张图 | 框 + 类别 + 置信度 | YOLO、Faster R-CNN、DETR |
| 语义分割 | 单张图 | 每个像素的类别 | U-Net、DeepLab、SegFormer |
| 实例分割 | 单张图 | 每个物体的 mask | Mask R-CNN、SAM |
| 文本分类 | 文本 | 类别 | BERT、RoBERTa |
| 命名实体识别 | 文本 | 序列标签 | BERT + CRF |
| 机器翻译 | 文本 | 文本 | Transformer、T5、mBART |
| 文本生成 | 文本 / 提示 | 文本 | GPT、LLaMA |
| 语音识别 | 音频 | 文本 | Whisper、Conformer |
| 语音合成 | 文本 | 音频 | Tacotron、VITS |
| 多模态 | 图 + 文 | 文本 | CLIP、LLaVA、GPT-4V |
| 强化学习 | 环境状态 | 动作 | PPO、SAC |

---

## 11. 数学背景补充

### 雅各比矩阵（Jacobian Matrix）

向量函数对向量的偏导数矩阵。深度学习里主要用于：

- **输入是向量、输出是向量** 的函数的局部线性化
- 链式法则的高维形式（`∂y/∂x = ∂y/∂u · ∂u/∂x`，矩阵乘法）

```text
若 f: Rⁿ → Rᵐ，则雅各比矩阵 J ∈ Rᵐˣⁿ：
J[i,j] = ∂f_i / ∂x_j
```

反向传播就是反复应用雅各比矩阵的链式乘法。PyTorch 的 autograd 自动帮你做了。

**参考：** [基本初等函数导数推导 - 知乎](https://zhuanlan.zhihu.com/p/89843248)（原笔记外链保留）

### 链式法则（Chain Rule）

反向传播的理论基础。

```text
Loss = f(g(h(x)))
∂Loss/∂x = (∂f/∂g) · (∂g/∂h) · (∂h/∂x)
           ← 反向逐层相乘
```

### 其他常用数学名词

| 名词 | 含义 |
|------|------|
| 矩阵乘法 | 神经网络前向传播的本质 |
| Softmax 函数 | 多分类概率归一化 |
| 交叉熵（Cross Entropy） | 分类任务最常用损失 |
| L2 范数 | 权重衰减、梯度裁剪 |
| 梯度消失 / 爆炸 | 深层网络训练的经典问题 |

---

## 速查卡片

```text
训练 5 步（顺序不可乱）：
  ① optimizer.zero_grad()
  ② pred = model(x)
  ③ loss = loss_fn(pred, y)
  ④ loss.backward()
  ⑤ optimizer.step()

模型三段式：Backbone → Neck → Head
CNN 三件套：Conv → Activation → Pool
优化器默认：Adam / AdamW
LR 调度：Warmup + Cosine
```

---

## 对应笔记

- [[02_PyTorch笔记]] — PyTorch 核心 API 实战
- [[II_深度学习环境安装笔记]] — CUDA / cuDNN / PyTorch 安装
- [example/pytorch-demo/01_tensor_and_autograd/](../example/pytorch-demo/01_tensor_and_autograd/README.md) — Tensor / autograd 可运行 demo
- [example/pytorch-demo/02_nn_module_training/](../example/pytorch-demo/02_nn_module_training/README.md) — nn.Module 训练可运行 demo

## 历史笔记

- 旧稿 AI、DeepLearning、MachineLearning零碎知识 — 原零碎笔记，已被本篇替代
- 旧稿 Pytorch学习笔记 — 原 PyTorch 占位笔记，已被 [[02_PyTorch笔记]] 替代