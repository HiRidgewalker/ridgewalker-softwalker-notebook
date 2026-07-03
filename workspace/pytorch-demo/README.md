# workspace/pytorch-demo · PyTorch 演示项目集合

> 这里放着与 [[02_PyTorch笔记]] 配套的 **2 个独立可运行的 PyTorch demo**。
> 每个 demo 都是单文件 Python 脚本，可直接 `python main.py` 跑起来（CPU 即可）。
> 对应说明见 `Hub/` 下的总览笔记，笔记中通过本 README 链接引用 demo。

## 子项目列表

| 子项目 | 演示主题 | 入口 |
|--------|----------|------|
| `01_tensor_and_autograd` | Tensor 创建/形状/运算、设备切换、`requires_grad` + `backward()`、`.detach()`、`no_grad()` | [01_tensor_and_autograd/README.md](./01_tensor_and_autograd/README.md) |
| `02_nn_module_training` | `nn.Module` 子类写法、`forward`、`__call__` 包装、loss/optimizer、训练几步并打印 loss | [02_nn_module_training/README.md](./02_nn_module_training/README.md) |

## 每个 demo 都包含

- `main.py` —— 单文件可运行脚本
- `requirements.txt` —— 第三方依赖（仅 `torch`）
- `README.md` —— 涵盖知识点、观察点、运行方式

## 统一运行方式

按 `rules/04-python虚拟环境.md`，使用 `workspace/.venv/` 内的 Python 解释器：

```bash
# 一次性：把 torch 装到统一 venv（CPU 版即可，体积约 200MB）
uv pip install --python workspace/.venv/bin/python -r workspace/pytorch-demo/01_tensor_and_autograd/requirements.txt

# 运行
workspace/.venv/bin/python workspace/pytorch-demo/01_tensor_and_autograd/main.py
workspace/.venv/bin/python workspace/pytorch-demo/02_nn_module_training/main.py
```

> **CPU-only 即可**：所有 demo 不依赖 GPU，只是用来观察 API 行为、打印张量形状与梯度值。
> 如需 GPU 版，把 `requirements.txt` 中的 `torch` 换成对应 CUDA wheel：
> `torch --index-url https://download.pytorch.org/whl/cu121`

## 设计与命名约定

- **每个 demo 一个子目录**：子目录名带数字前缀（如 `01_xxx`），便于扩展
- **`main.py` 作为入口**：标准 Python 文件名，不依赖包结构
- **可独立运行**：每个 demo 不依赖其他 demo 的代码
- **打印友好**：demo 会把所有关键张量形状 / 数值打印到 stdout，方便观察

## 对应笔记

- [[01_ML与DL基础概念笔记]] — ML/DL 基础概念
- [[02_PyTorch笔记]] — PyTorch 核心 API
- [[03_深度学习环境安装笔记]] — CUDA / cuDNN / PyTorch 安装