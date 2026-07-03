# 01_tensor_and_autograd · Tensor 与自动求导 demo

演示 [[02_PyTorch笔记]] 中**前两章**的核心内容：
- Tensor 的创建、属性、形状操作、运算
- 设备切换（CPU / CUDA / MPS）
- autograd：`requires_grad` + `backward()` + `.grad`
- 上下文管理：`torch.no_grad()`、`.detach()`

## 涵盖知识点

- `torch.tensor()` / `torch.zeros/ones/randn/arange`
- `.shape` / `.dtype` / `.device` / `.ndim`
- `view` / `reshape` / `unsqueeze` / `squeeze` / `transpose` / `permute`
- 逐元素运算、矩阵乘法（`@` / `matmul`）、聚合（`sum` / `mean` / `argmax`）
- `.to(device)` 切换设备
- `requires_grad=True` + `loss.backward()` 自动求梯度
- `torch.no_grad()` 上下文：推理时不构建计算图
- `.detach()`：把 tensor 从计算图剥离

## 运行

```bash
# 装 torch（CPU 版即可）
uv pip install --python workspace/.venv/bin/python -r workspace/pytorch-demo/01_tensor_and_autograd/requirements.txt

# 跑
workspace/.venv/bin/python workspace/pytorch-demo/01_tensor_and_autograd/main.py
```

## 关键观察点

1. **设备自动判断**：脚本会优先用 `cuda`，没有就 `mps`，最后 `cpu`。
2. **梯度计算**：手算 `y = w*x + b`，`loss = (y - 10)^2`，对 w、b 求导并打印，对照 `loss.backward()` 输出的 `.grad`。
3. **`no_grad` vs 默认模式**：同一段推理代码分别在 `no_grad` 上下文内外跑，对比显存和速度（差异在小张量上不明显，看输出说明即可）。
4. **`.detach()`**：把中间 tensor 剥离后再做修改，原 tensor 不会受影响（反之亦然）。

## 输出示例（节选）

```text
=== 1. Tensor 创建与属性 ===
shape=torch.Size([2, 3])  dtype=torch.float32  device=cpu  ndim=2

=== 2. 形状操作 ===
reshape  -> torch.Size([3, 4])
unsqueeze(0) -> torch.Size([1, 12])

=== 3. 设备切换 ===
使用设备: cpu
tensor([[1., 2., 3.]]) on cpu

=== 4. autograd：手算与自动求导对比 ===
手动计算: w.grad=18.0  b.grad=-6.0
PyTorch:   w.grad=18.0  b.grad=-6.0
一致 ✓

=== 5. no_grad 与 detach ===
no_grad 下计算: tensor(7.)  requires_grad=False
.detach() 后:  tensor(7.)  requires_grad=False
```

## 对应笔记

- [[02_PyTorch笔记]] — Tensor 基础、autograd
- [[03_深度学习环境安装笔记]] — torch 安装（CPU 版够用）