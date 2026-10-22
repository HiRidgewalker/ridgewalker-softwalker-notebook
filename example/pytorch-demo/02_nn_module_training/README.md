# 02_nn_module_training · nn.Module 与训练范式 demo

演示 [[02_PyTorch笔记]] 中**训练相关**章节的核心内容：
- `nn.Module` 子类写法、`__init__`、`forward`
- `model(x)` 与 `model.forward(x)` 的差异（前者触发 hooks）
- `nn.Linear`、`nn.ReLU`、`nn.MSELoss` 等常用模块
- 优化器 `torch.optim.SGD`、学习率
- 完整的训练 5 步：`zero_grad` → `forward` → `loss` → `backward` → `step`
- `model.train()` / `model.eval()` 模式切换
- `torch.no_grad()` 在推理时的用法

## 涵盖知识点

- 继承 `nn.Module` 定义自己的网络
- 在 `__init__` 里搭子模块，在 `forward` 里定义计算
- 用 `nn.Sequential` 快速搭一个 MLP
- `loss.backward()` 反向传播后 `.grad` 自动填充
- `optimizer.step()` 用梯度更新参数
- `optimizer.zero_grad()` 清零梯度的必要性
- 模型参数移动到 GPU：`model.to(device)`
- 一个最小可跑的训练任务：学 `y = 2x + 1`

## 运行

```bash
# 装 torch（CPU 版即可）
uv pip install --python .venv/bin/python -r example/pytorch-demo/02_nn_module_training/requirements.txt

# 跑
.venv/bin/python example/pytorch-demo/02_nn_module_training/main.py
```

## 关键观察点

1. **数据**：人造数据 `y = 2x + 1 + 噪声`，简单线性回归任务。
2. **模型**：单层 `nn.Linear(1, 1)`，理论最优解 `weight=2, bias=1`。
3. **训练过程**：每 200 步打印一次 loss，应该看到 loss 持续下降。
4. **最终权重**：训练完成后打印学到的 weight 和 bias，应非常接近 2.0 和 1.0。
5. **`__call__` vs `forward`**：演示中只在 main 训练循环里用 `model(x)`，不直接调 `model.forward(x)`（hooks 完整性）。
6. **忘记 `zero_grad`**：临时注释掉 `optimizer.zero_grad()` 再跑一次，对比 loss 行为（会震荡）。

## 输出示例（节选）

```text
=== nn.Module + 训练范式 demo ===
设备: cpu  PyTorch: 2.x.x

--- 1. 两种写法：手写 forward vs nn.Sequential ---
手写 forward 模型: MLP(in=10, hidden=20, out=3) 参数量: 263
Sequential 模型:   MLP(in=10, hidden=20, out=3) 参数量: 263
两种写法结果一致 ✓

--- 2. 训练最小例子：学 y = 2x + 1 ---
初始权重: weight=0.1234, bias=0.5678
Step   0 | loss=4.5123
Step 200 | loss=0.0987
Step 400 | loss=0.0245
Step 600 | loss=0.0098
Step 800 | loss=0.0042
Step 999 | loss=0.0021
训练后权重: weight=1.9876, bias=0.9890   (理论: 2.0, 1.0)

--- 3. model(x) vs model.forward(x) ---
model(x)        -> OK（含 hooks）
model.forward(x)-> OK（跳过 hooks，不推荐）

--- 4. optimizer.zero_grad() 的必要性 ---
忘记清零: 梯度累加 → 步长异常大 → loss 震荡
正常清零: 梯度每步独立 → 平稳收敛
```

## 对应笔记

- [[02_PyTorch笔记]] — nn.Module、优化器、训练范式
- [[I_ML与DL基础概念笔记]] — 标准训练流程、Backbone/Neck/Head