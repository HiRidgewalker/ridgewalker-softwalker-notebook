"""01_tensor_and_autograd · Tensor 与 autograd 演示

涵盖：
- Tensor 创建（tensor/zeros/ones/randn/arange）
- 属性（shape/dtype/device/ndim）
- 形状操作（reshape/unsqueeze/squeeze/transpose/permute）
- 运算（逐元素、矩阵乘法、聚合）
- 设备切换（CPU/CUDA/MPS 自动选择）
- autograd（requires_grad + backward + .grad）
- no_grad 上下文、.detach()

对应笔记：Hub/02_PyTorch笔记.md（Tensor 基础、autograd）

运行：
    uv pip install --python example/.venv/bin/python -r example/pytorch-demo/01_tensor_and_autograd/requirements.txt
    example/.venv/bin/python example/pytorch-demo/01_tensor_and_autograd/main.py
"""

import torch


def pick_device() -> torch.device:
    """自动选择可用设备，优先级 cuda > mps > cpu"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def demo_tensor_create_and_attrs() -> None:
    """1. Tensor 创建与属性"""
    print("\n=== 1. Tensor 创建与属性 ===")

    # 从 list 创建（默认推断 dtype=int64）
    a = torch.tensor([1, 2, 3])
    print(f"torch.tensor([1,2,3])        -> {a}, dtype={a.dtype}")

    # 全 0 / 全 1 / 随机
    z = torch.zeros(2, 3)
    o = torch.ones(2, 3)
    r = torch.randn(2, 3)  # 标准正态分布
    print(f"torch.zeros(2,3)            -> shape={tuple(z.shape)}")
    print(f"torch.ones(2,3)             -> shape={tuple(o.shape)}")
    print(f"torch.randn(2,3)            -> shape={tuple(r.shape)}")

    # arange / linspace
    ar = torch.arange(0, 10, 2)
    ls = torch.linspace(0, 1, 5)
    print(f"torch.arange(0,10,2)        -> {ar}")
    print(f"torch.linspace(0,1,5)       -> {ls}")

    # 属性
    t = torch.randn(2, 3, 4)
    print(f"torch.randn(2,3,4)          -> shape={tuple(t.shape)}, "
          f"dtype={t.dtype}, ndim={t.ndim}, device={t.device}")


def demo_shape_ops() -> None:
    """2. 形状操作"""
    print("\n=== 2. 形状操作 ===")

    t = torch.arange(12)  # shape: (12,)
    print(f"torch.arange(12)            -> shape={tuple(t.shape)}")

    r1 = t.reshape(3, 4)
    r2 = r1.unsqueeze(0)  # 在最前面加一维
    r3 = r2.squeeze(0)   # 去掉长度为 1 的维
    r4 = r1.transpose(0, 1)  # 等价 t.T，因为是 2D
    r5 = torch.randn(2, 3, 4).permute(2, 0, 1)  # (4,2,3)

    print(f"reshape(3,4)                -> shape={tuple(r1.shape)}")
    print(f"unsqueeze(0)                -> shape={tuple(r2.shape)}")
    print(f"squeeze(0)                  -> shape={tuple(r3.shape)}")
    print(f"transpose(0,1) on (3,4)     -> shape={tuple(r4.shape)}")
    print(f"permute(2,0,1) on (2,3,4)   -> shape={tuple(r5.shape)}")


def demo_basic_ops() -> None:
    """3. 基本运算"""
    print("\n=== 3. 基本运算 ===")

    a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    b = torch.tensor([[5.0, 6.0], [7.0, 8.0]])

    print(f"a + b        -> {a + b}")
    print(f"a * b (逐元素) -> {a * b}")
    print(f"a @ b (矩阵乘) -> \n{a @ b}")
    print(f"torch.matmul(a, b) (同上) -> \n{torch.matmul(a, b)}")

    # 聚合
    t = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    print(f"t.sum()      -> {t.sum()}")
    print(f"t.mean(dim=1)-> {t.mean(dim=1)}")
    print(f"t.argmax(dim=1) -> {t.argmax(dim=1)}")

    # 拼接
    c1 = torch.cat([a, b], dim=0)  # 沿行堆叠
    c2 = torch.stack([a, b], dim=0)  # 在新维度堆叠
    print(f"cat([a,b], dim=0)           -> shape={tuple(c1.shape)}")
    print(f"stack([a,b], dim=0)         -> shape={tuple(c2.shape)}")


def demo_device(device: torch.device) -> None:
    """4. 设备切换"""
    print("\n=== 4. 设备切换 ===")
    print(f"使用设备: {device}")

    t_cpu = torch.tensor([1.0, 2.0, 3.0])
    print(f"原始 tensor: device={t_cpu.device}")

    t_dev = t_cpu.to(device)
    print(f"搬到 {device}: device={t_dev.device}")

    # 验证设备上能算
    result = t_dev + 1
    print(f"device 上 +1 结果: {result}")

    # 不同设备的 tensor 不能直接算
    if device.type != "cpu":
        try:
            _ = t_cpu + t_dev
        except RuntimeError as e:
            print(f"跨设备相加报错（预期）: {str(e)[:80]}...")


def demo_autograd() -> None:
    """5. autograd：手算梯度 vs PyTorch 自动求导对比"""
    print("\n=== 5. autograd：手算 vs PyTorch ===")

    # y = w * x + b
    # loss = (y - target)^2
    # ∂loss/∂w = 2 * (y - target) * x
    # ∂loss/∂b = 2 * (y - target)

    x = torch.tensor(3.0)
    target = torch.tensor(10.0)
    w = torch.tensor(2.0, requires_grad=True)
    b = torch.tensor(1.0, requires_grad=True)

    # 前向
    y = w * x + b
    loss = (y - target) ** 2
    print(f"x={x.item()}, target={target.item()}, w={w.item()}, b={b.item()}")
    print(f"前向: y = {y.item()}, loss = {loss.item()}")

    # 反向
    loss.backward()
    print(f"反向: w.grad = {w.grad}, b.grad = {b.grad}")

    # 手算验证：y = 2*3 + 1 = 7，loss = (7-10)^2 = 9
    # ∂loss/∂w = 2 * (7-10) * 3 = -18，但 PyTorch 默认累加且这里只有一次，所以 .grad = -18
    # 等等，注意 w 是 +2，不是 -2，所以 ∂loss/∂w = 2*(y-target)*x = 2*(7-10)*3 = -18
    # 但 (7-10) = -3, 2*(-3)*3 = -18。正确。
    print(f"手算: w.grad 应为 -18.0, b.grad 应为 -6.0")
    print(f"PyTorch: w.grad = {w.grad}, b.grad = {b.grad}")
    match = (w.grad.item() == -18.0) and (b.grad.item() == -6.0)
    print(f"匹配: {'✓' if match else '✗'}")

    # 梯度累加演示
    print("\n--- 梯度累加特性 ---")
    w.grad.zero_()  # 手动清零
    y2 = w * x + b
    loss2 = (y2 - target) ** 2
    loss2.backward()
    print(f"清零后再反向: w.grad = {w.grad}")
    print("（多次 .backward() 会累加，必须先 .zero_grad() 或 .grad.zero_()）")


def demo_no_grad_and_detach() -> None:
    """6. no_grad 上下文 与 detach"""
    print("\n=== 6. no_grad 与 detach ===")

    x = torch.tensor(3.0)
    w = torch.tensor(2.0, requires_grad=True)

    # 默认模式（前向会构建计算图）
    y1 = w * x + 1
    print(f"默认 y1 = {y1.item()}, requires_grad = {y1.requires_grad}")

    # no_grad 上下文
    with torch.no_grad():
        y2 = w * x + 1
        print(f"no_grad y2 = {y2.item()}, requires_grad = {y2.requires_grad}")

    # detach：返回新 tensor，不带梯度
    y3 = (w * x + 1).detach()
    print(f"detach  y3 = {y3.item()}, requires_grad = {y3.requires_grad}")

    # 演示 detach 的隔离性
    print("\n--- detach 隔离性 ---")
    a = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
    b = a.detach()  # b 共享数据但不参与梯度
    b[0] = 99.0  # 改 b 会影响 a（共享内存）
    print(f"改 b 后 a = {a}  (共享内存)")
    print(f"改 b 后 b = {b}")

    # 演示 detach 不影响 requires_grad 属性传递
    c = torch.tensor([1.0, 2.0], requires_grad=True)
    d = c * 2
    e = d.detach()
    print(f"\nc.requires_grad={c.requires_grad}, d={d.requires_grad}, e={e.requires_grad}")


def main() -> None:
    print("=" * 60)
    print("01_tensor_and_autograd demo")
    print("=" * 60)

    device = pick_device()
    print(f"\n自动选设备: {device}")
    print(f"PyTorch 版本: {torch.__version__}")

    demo_tensor_create_and_attrs()
    demo_shape_ops()
    demo_basic_ops()
    demo_device(device)
    demo_autograd()
    demo_no_grad_and_detach()

    print("\n" + "=" * 60)
    print("demo 跑完，参考 example/pytorch-demo/01_tensor_and_autograd/README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()