"""01_tokenization_and_generation · Tokenizer + 自回归生成 + KV cache + 采样策略演示

涵盖：
- Tokenizer：encode / decode / BPE 切分粒度 / 特殊 token / 词表大小
- Next token prediction：手动 forward 一次看 logits 分布
- 自回归生成循环：每步生成一个 token
- KV cache：use_cache=True vs False 速度对比
- 采样策略：greedy / temperature / top_k / top_p 对生成结果的影响

对应笔记：Hub/01_大语言模型笔记.md（§2 Tokenization、§7.1 推理循环、§7.2 KV cache、§7.3 Sampling）

运行：
    uv pip install --python example/.venv/bin/python -r example/llm-demo/01_tokenization_and_generation/requirements.txt
    example/.venv/bin/python example/llm-demo/01_tokenization_and_generation/main.py

首次运行会从 HuggingFace 下载 GPT-2 (~500MB)，请确保网络可用。
"""

import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def pick_device() -> torch.device:
    """自动选择可用设备，优先级 cuda > mps > cpu"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ============================================================
# 1. Tokenizer：encode / decode / BPE 切分粒度
# ============================================================

def demo_tokenizer() -> None:
    """Tokenizer：文本 ↔ token id 转换"""
    print("\n=== 1. Tokenizer：encode / decode ===")

    tok = AutoTokenizer.from_pretrained("gpt2")
    text = "Hello, my name is Limber. I love programming in Python. 你好世界。"

    # encode
    ids = tok.encode(text)
    print(f"原文: {text!r}")
    print(f"token 数: {len(ids)}")
    print(f"前 10 个 token id: {ids[:10]}")

    # 每个 id 对应的 token 字符串（BPE 切分粒度）
    tokens = tok.convert_ids_to_tokens(ids)
    print(f"前 15 个 token: {tokens[:15]}")

    # 单 token decode：看每个 token 实际对应的字符
    print("\n前 8 个 token 单独 decode（看 BPE 切分粒度）:")
    for tid in ids[:8]:
        tok_str = tok.convert_ids_to_tokens([tid])[0]
        decoded = tok.decode([tid])
        print(f"  id={tid:6d}, token={tok_str:15s}, decode={decoded!r}")

    # decode 整段
    print(f"\ndecode 整段: {tok.decode(ids)!r}")

    # 特殊 token
    print(f"\nbos_token: {tok.bos_token} (id={tok.bos_token_id})")
    print(f"eos_token: {tok.eos_token} (id={tok.eos_token_id})")
    print(f"pad_token: {tok.pad_token}")
    print(f"vocab 大小: {tok.vocab_size}")

    # 中英对比：GPT-2 中文效率低（中文按 byte 切，每个汉字 2-3 token）
    chinese_text = "今天天气真好"
    zh_ids = tok.encode(chinese_text)
    print(f"\n中文 '今天天气真好' 切成了 {len(zh_ids)} 个 token:")
    print(f"  tokens: {tok.convert_ids_to_tokens(zh_ids)}")


# ============================================================
# 2. Next token prediction：手动看 logits
# ============================================================

def demo_next_token_prediction() -> None:
    """演示前向一次后，最后一个位置的 logits 分布"""
    print("\n=== 2. Next token prediction（前向 + logits） ===")

    device = pick_device()
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2").to(device)
    model.eval()

    prompt = "The capital of France is"
    input_ids = tok.encode(prompt, return_tensors="pt").to(device)
    print(f"prompt: {prompt!r}")
    print(f"input_ids shape: {tuple(input_ids.shape)}")

    with torch.no_grad():
        out = model(input_ids)
        logits = out.logits                      # (1, T, vocab_size)
        last_logits = logits[0, -1, :]          # 最后一个位置的 logits
        probs = torch.softmax(last_logits, dim=-1)
        top5 = torch.topk(probs, 5)

    print("\n下一个 token 概率 top-5:")
    for prob, tid in zip(top5.values.tolist(), top5.indices.tolist()):
        tok_str = tok.convert_ids_to_tokens([tid])[0]
        print(f"  {tok_str:15s} (id={tid:6d}): {prob:.4f}")

    # 注意：这是没有采样策略时的原始概率，greedy 会选概率最高的


# ============================================================
# 3. 自回归生成循环（手动实现 vs model.generate）
# ============================================================

def demo_autoregressive_loop() -> None:
    """手动写自回归循环，对比 model.generate"""
    print("\n=== 3. 自回归生成循环（手动实现） ===")

    device = pick_device()
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2").to(device)
    model.eval()

    prompt = "Once upon a time"
    input_ids = tok.encode(prompt, return_tensors="pt").to(device)
    n_new = 20

    # 手动循环：每步前向 → 取最后位置 logits → argmax → 拼接
    print(f"prompt: {prompt!r}, 生成 {n_new} 个 token (greedy)")
    generated = input_ids.clone()
    with torch.no_grad():
        for step in range(n_new):
            out = model(generated)
            next_token = out.logits[0, -1, :].argmax()  # greedy
            generated = torch.cat([generated, next_token.unsqueeze(0).unsqueeze(0)], dim=1)

    new_tokens = generated[0, input_ids.shape[1]:].tolist()
    new_text = tok.decode(new_tokens, skip_special_tokens=True)
    print(f"手动循环生成: {prompt + new_text!r}")
    print(f"生成的 token ids: {new_tokens}")
    print(f"每个 token 对应的文本:")
    for tid in new_tokens[:10]:
        print(f"  id={tid}, token={tok.convert_ids_to_tokens([tid])[0]!r}, decode={tok.decode([tid])!r}")


# ============================================================
# 4. KV cache 效果对比
# ============================================================

def demo_kv_cache() -> None:
    """对比 use_cache=True 和 use_cache=False 的生成速度"""
    print("\n=== 4. KV cache 效果对比 ===")

    device = pick_device()
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2").to(device)
    model.eval()

    prompt = "The history of artificial intelligence began in"
    input_ids = tok.encode(prompt, return_tensors="pt").to(device)
    n_generate = 80

    # 用 KV cache
    t0 = time.time()
    with torch.no_grad():
        out_cache = model.generate(
            input_ids,
            max_new_tokens=n_generate,
            use_cache=True,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
    t_cache = time.time() - t0

    # 不用 KV cache
    t0 = time.time()
    with torch.no_grad():
        out_no_cache = model.generate(
            input_ids,
            max_new_tokens=n_generate,
            use_cache=False,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
    t_no_cache = time.time() - t0

    print(f"生成 {n_generate} 个 token (prompt 长度 {input_ids.shape[1]}):")
    print(f"  use_cache=True:  {t_cache:.2f}s")
    print(f"  use_cache=False: {t_no_cache:.2f}s")
    print(f"  加速比: {t_no_cache / t_cache:.1f}x")
    print(f"  （序列越长，加速比越明显；CPU 上差距更显著）")

    # 验证两种方式输出相同
    same = torch.equal(out_cache, out_no_cache)
    print(f"  两种方式输出相同: {same}")

    print(f"\n生成结果（use_cache=True）:")
    print(f"  {tok.decode(out_cache[0], skip_special_tokens=True)!r}")


# ============================================================
# 5. 采样策略对比
# ============================================================

def demo_sampling_strategies() -> None:
    """greedy / temperature / top_k / top_p 的输出对比"""
    print("\n=== 5. 采样策略对比 ===")

    device = pick_device()
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2").to(device)
    model.eval()

    prompt = "The best programming language is"
    input_ids = tok.encode(prompt, return_tensors="pt").to(device)
    n_generate = 30

    configs = [
        {"label": "greedy (do_sample=False)",      "do_sample": False},
        {"label": "temperature=0.3 (低温度)",       "do_sample": True, "temperature": 0.3},
        {"label": "temperature=1.0 (默认温度)",     "do_sample": True, "temperature": 1.0},
        {"label": "temperature=2.0 (高温度)",       "do_sample": True, "temperature": 2.0},
        {"label": "top_k=10",                       "do_sample": True, "top_k": 10, "temperature": 1.0},
        {"label": "top_p=0.9 + temperature=0.7",    "do_sample": True, "top_p": 0.9, "temperature": 0.7},
    ]

    for cfg in configs:
        label = cfg.pop("label")
        torch.manual_seed(42)  # 保证 sampling 路径结果可复现（greedy 不受 seed 影响）
        with torch.no_grad():
            out = model.generate(
                input_ids,
                max_new_tokens=n_generate,
                pad_token_id=tok.eos_token_id,
                **cfg,
            )
        new_text = tok.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
        print(f"\n[{label}]:")
        print(f"  ...{new_text!r}")


def main() -> None:
    print("=" * 60)
    print("01_tokenization_and_generation demo")
    print("=" * 60)

    device = pick_device()
    print(f"\n自动选设备: {device}")
    print(f"PyTorch: {torch.__version__}")

    demo_tokenizer()
    demo_next_token_prediction()
    demo_autoregressive_loop()
    demo_kv_cache()
    demo_sampling_strategies()

    print("\n" + "=" * 60)
    print("demo 跑完，参考 example/llm-demo/01_tokenization_and_generation/README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()