"""02_nn_module_training · nn.Module 与训练范式演示

涵盖：
- nn.Module 子类写法（__init__ + forward）
- nn.Sequential 容器快速搭模型
- 训练 5 步：zero_grad → forward → loss → backward → step
- model.train() / model.eval() 切换
- torch.no_grad() 在推理时的用法
- model(x) vs model.forward(x)：hooks 行为
- 忘记 optimizer.zero_grad() 的后果演示

对应笔记：Hub/02_PyTorch笔记.md（nn.Module、优化器、完整训练范式）

运行：
    uv pip install --python example/.venv/bin/python -r example/pytorch-demo/02_nn_module_training/requirements.txt
    example/.venv/bin/python example/pytorch-demo/02_nn_module_training/main.py
"""

import torch
import torch.nn as nn
import torch.optim as optim


def pick_device() -> torch.device:
    """自动选择可用设备，优先级 cuda > mps > cpu"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ============================================================
# 1. 两种写法：手写 forward vs nn.Sequential
# ============================================================

class MLPManual(nn.Module):
    """手写 forward 的 MLP"""

    def __init__(self, in_features: int, hidden: int, out_features: int) -> None:
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


def make_mlp_sequential(in_features: int, hidden: int, out_features: int) -> nn.Sequential:
    """用 nn.Sequential 搭同样的 MLP"""
    return nn.Sequential(
        nn.Linear(in_features, hidden),
        nn.ReLU(),
        nn.Linear(hidden, out_features),
    )


def demo_two_ways_to_define_model() -> None:
    """演示 nn.Module 的两种写法，结果应一致"""
    print("\n=== 1. 两种写法：手写 forward vs nn.Sequential ===")

    in_features, hidden, out_features = 10, 20, 3
    torch.manual_seed(42)  # 保证两种写法初始权重一致
    model_manual = MLPManual(in_features, hidden, out_features)
    model_seq = make_mlp_sequential(in_features, hidden, out_features)
    # 把 sequential 的权重复制到 manual，保证一致
    model_seq.load_state_dict(model_manual.state_dict())

    # 参数量
    n_manual = sum(p.numel() for p in model_manual.parameters())
    n_seq = sum(p.numel() for p in model_seq.parameters())
    print(f"手写 forward 模型: 参数量={n_manual}")
    print(f"Sequential 模型:   参数量={n_seq}")

    # 同样输入，对比输出
    x = torch.randn(4, in_features)
    with torch.no_grad():
        out_manual = model_manual(x)
        out_seq = model_seq(x)
    same = torch.allclose(out_manual, out_seq)
    print(f"两种写法结果一致: {'✓' if same else '✗'}")
    print(f"  输出 shape: {tuple(out_manual.shape)}")


# ============================================================
# 2. 模型参数自动注册（named_parameters）
# ============================================================

def demo_named_parameters() -> None:
    """演示子模块自动注册到 parameters()"""
    print("\n=== 2. nn.Module 自动注册子模块 ===")

    model = MLPManual(10, 20, 3)
    print("named_parameters():")
    for name, p in model.named_parameters():
        print(f"  {name:10s} -> shape={tuple(p.shape)}, requires_grad={p.requires_grad}")

    # 嵌套 nn.Module
    class BigModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.block = MLPManual(10, 20, 3)  # 整个 MLP 当子模块

        def forward(self, x):
            return self.block(x)

    big = BigModel()
    n_total = sum(p.numel() for p in big.parameters())
    print(f"\n嵌套模型总参数量: {n_total}")
    print("（子模块的参数会被外层自动收集）")


# ============================================================
# 3. 最小训练例子：学 y = 2x + 1
# ============================================================

def make_linear_data(n: int = 100, noise_std: float = 0.1) -> tuple[torch.Tensor, torch.Tensor]:
    """生成 y = 2x + 1 + 噪声 的数据"""
    torch.manual_seed(0)
    x = torch.randn(n, 1)
    y = 2.0 * x + 1.0 + torch.randn(n, 1) * noise_std
    return x, y


def demo_train_minimal() -> None:
    """用 nn.Linear 学 y = 2x + 1，看训练 5 步范式"""
    print("\n=== 3. 训练最小例子：学 y = 2x + 1 ===")

    device = pick_device()
    x, y = make_linear_data(n=200, noise_std=0.1)
    x, y = x.to(device), y.to(device)

    # 模型 / 损失 / 优化器
    model = nn.Linear(1, 1).to(device)
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    # 初始权重
    w0, b0 = model.weight.item(), model.bias.item()
    print(f"初始权重: weight={w0:.4f}, bias={b0:.4f}")

    # 训练
    num_steps = 1000
    for step in range(num_steps):
        # 训练 5 步（顺序不可乱）
        optimizer.zero_grad()   # ① 清零梯度
        pred = model(x)          # ② 前向
        loss = loss_fn(pred, y)  # ③ 计算损失
        loss.backward()          # ④ 反向传播
        optimizer.step()         # ⑤ 更新参数

        if step % 200 == 0 or step == num_steps - 1:
            print(f"Step {step:4d} | loss={loss.item():.4f}")

    # 最终结果
    w_final, b_final = model.weight.item(), model.bias.item()
    print(f"\n训练后权重: weight={w_final:.4f}, bias={b_final:.4f}")
    print(f"理论最优:  weight=2.0000, bias=1.0000")
    print(f"误差:      dw={abs(w_final - 2.0):.4f}, db={abs(b_final - 1.0):.4f}")


# ============================================================
# 4. model(x) vs model.forward(x)
# ============================================================

def demo_call_vs_forward() -> None:
    """演示 model(x) 触发 hooks，model.forward(x) 不会"""
    print("\n=== 4. model(x) vs model.forward(x) ===")

    call_count_pre = {"n": 0}
    call_count_post = {"n": 0}

    def pre_hook(module, inputs):
        call_count_pre["n"] += 1

    def post_hook(module, inputs, outputs):
        call_count_post["n"] += 1

    model = nn.Linear(3, 3)
    handle_pre = model.register_forward_pre_hook(pre_hook)
    handle_post = model.register_forward_hook(post_hook)

    x = torch.randn(2, 3)

    # 用 model(x)：hooks 被触发
    model(x)
    print(f"model(x) 调用一次后: pre_hook 触发 {call_count_pre['n']} 次, "
          f"post_hook 触发 {call_count_post['n']} 次")

    # 重置计数
    call_count_pre["n"] = 0
    call_count_post["n"] = 0

    # 用 model.forward(x)：hooks 不会被触发
    model.forward(x)
    print(f"model.forward(x) 调用一次后: pre_hook 触发 {call_count_pre['n']} 次, "
          f"post_hook 触发 {call_count_post['n']} 次")

    handle_pre.remove()
    handle_post.remove()
    print("结论：永远用 model(x)，不要用 model.forward(x)，否则 hooks 会失效")


# ============================================================
# 5. 忘记 zero_grad 的后果
# ============================================================

def demo_zero_grad_importance() -> None:
    """演示忘记 optimizer.zero_grad() 会导致梯度累加、训练震荡"""
    print("\n=== 5. optimizer.zero_grad() 的必要性 ===")

    x, y = make_linear_data(n=100, noise_std=0.1)

    # 正常训练（每次 step 前清零）
    print("--- 正常训练（每次 zero_grad） ---")
    torch.manual_seed(1)
    model_ok = nn.Linear(1, 1)
    opt_ok = optim.SGD(model_ok.parameters(), lr=0.05)
    for step in range(200):
        opt_ok.zero_grad()       # ← 关键
        loss = ((model_ok(x) - y) ** 2).mean()
        loss.backward()
        opt_ok.step()
        if step % 50 == 0:
            print(f"  Step {step:3d} | loss={loss.item():.4f} | "
                  f"w={model_ok.weight.item():.3f}, b={model_ok.bias.item():.3f}")

    # 错误训练（不调用 zero_grad）
    print("\n--- 错误训练（忘记 zero_grad，梯度累加） ---")
    torch.manual_seed(1)
    model_bad = nn.Linear(1, 1)
    opt_bad = optim.SGD(model_bad.parameters(), lr=0.05)
    for step in range(200):
        # 注意：没有调用 opt_bad.zero_grad()
        loss = ((model_bad(x) - y) ** 2).mean()
        loss.backward()
        opt_bad.step()
        if step % 50 == 0:
            print(f"  Step {step:3d} | loss={loss.item():.4f} | "
                  f"w={model_bad.weight.item():.3f}, b={model_bad.bias.item():.3f}")
    print("\n（梯度累加 → 步长越来越大 → 权重在最优解附近震荡）")


# ============================================================
# 6. train / eval 模式切换
# ============================================================

def demo_train_eval_mode() -> None:
    """演示 model.train() / model.eval() 对 Dropout / BN 的影响"""
    print("\n=== 6. model.train() / model.eval() 切换 ===")

    model = nn.Sequential(
        nn.Linear(4, 4),
        nn.BatchNorm1d(4),
        nn.ReLU(),
        nn.Dropout(p=0.5),
        nn.Linear(4, 2),
    )

    x = torch.randn(8, 4)

    # 训练模式
    model.train()
    out_train1 = model(x)
    out_train2 = model(x)
    same_train = torch.allclose(out_train1, out_train2)
    print(f"train 模式: 两次 forward 输出相同? {same_train} "
          f"（Dropout 随机，应不同）")

    # eval 模式
    model.eval()
    with torch.no_grad():
        out_eval1 = model(x)
        out_eval2 = model(x)
    same_eval = torch.allclose(out_eval1, out_eval2)
    print(f"eval 模式: 两次 forward 输出相同? {same_eval} "
          f"（Dropout 关闭，应相同）")
    print("结论: 验证/测试时必须 model.eval() + no_grad()")


def main() -> None:
    print("=" * 60)
    print("02_nn_module_training demo")
    print("=" * 60)

    device = pick_device()
    print(f"\n自动选设备: {device}")
    print(f"PyTorch 版本: {torch.__version__}")

    demo_two_ways_to_define_model()
    demo_named_parameters()
    demo_train_minimal()
    demo_call_vs_forward()
    demo_zero_grad_importance()
    demo_train_eval_mode()

    print("\n" + "=" * 60)
    print("demo 跑完，参考 example/pytorch-demo/02_nn_module_training/README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()