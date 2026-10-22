# 01_tokenization_and_generation · Tokenizer + 自回归生成 demo

演示 [[I_大语言模型笔记]] 中**推理相关**章节的核心内容：

- **Tokenizer**：BPE 切分粒度可视化、encode/decode、特殊 token、词表大小
- **Next token prediction**：手动 forward 一次看 logits 分布
- **自回归生成循环**：每步生成一个 token 的循环实现
- **KV cache**：`use_cache=True` vs `False` 的速度对比
- **Sampling 策略**：greedy / temperature / top_k / top_p 对生成结果的影响

## 涵盖知识点

- `AutoTokenizer.from_pretrained()` 加载 GPT-2 的 BPE tokenizer
- `tokenizer.encode()` 把文本变成 token id 序列
- `tokenizer.convert_ids_to_tokens()` 看每个 id 对应的字符串（BPE 子词）
- `model(input_ids).logits` 取最后一个位置的预测分布
- 自回归循环：forward → argmax → 拼接 → 重复
- `model.generate()` 的 `use_cache` 参数控制是否启用 KV cache
- Sampling 参数：`temperature`、`top_k`、`top_p`、`do_sample`

## 运行

```bash
# 装依赖
uv pip install --python .venv/bin/python -r example/llm-demo/01_tokenization_and_generation/requirements.txt

# 跑（首次会从 HuggingFace 下载 GPT-2 模型 + tokenizer，约 500MB）
.venv/bin/python example/llm-demo/01_tokenization_and_generation/main.py
```

## 关键观察点

1. **Tokenizer 切分粒度**：
   - 英文单词可能被切成多个子词（如 `programming` → `program` + `ming`）
   - 中文每个汉字通常对应 2-3 个 token（GPT-2 词表对中文不友好）
   - 标点、空格是独立的 token

2. **Next token prediction**：
   - prompt `"The capital of France is"` 后，概率最高的 token 应该是 `" Paris"`
   - 这是 next token prediction 的核心能力：模型通过 pretraining 学到的语言统计分布

3. **KV cache 加速效果**：
   - CPU 上加速比通常 2-5x
   - GPU 上加速比更明显（GPU 算力强，重计算的浪费更突出）
   - 序列越长加速比越大（O(T²) → O(T)）

4. **采样策略对多样性的影响**：
   - **greedy**：每次选概率最高的，确定性，可能陷入重复
   - **temperature<1**：概率分布更尖锐，更确定
   - **temperature>1**：概率分布更平，更随机，可能输出不合理
   - **top_k / top_p**：截断长尾，避免采样到极低概率 token

## 输出示例（节选）

```text
=== 1. Tokenizer ===
原文: 'Hello, my name is Limber. I love programming in Python.'
token 数: 17
前 15 个 token: ['Hello', ',', ' my', ' name', ' is', ' Lim', 'ber', '.', ' I', ' love', ' program', 'ming', ' in', ' Python', '.']

前 8 个 token 单独 decode（看 BPE 切分粒度）:
  id=15496, token='Hello',         decode='Hello'
  id=11,    token=',',             decode=','
  id=616,   token=' my',           decode=' my'
  id=1438,  token=' name',         decode=' name'
  id=318,   token=' is',           decode=' is'
  id=1757,  token=' Lim',          decode=' Lim'
  id=293,   token='ber',           decode='ber'
  id=13,    token='.',             decode='.'

vocab 大小: 50257

中文 '今天天气真好' 切成了 9 个 token:
  tokens: ['åä', 'ºä', '¸å¤©', 'æ°', 'å¤©', 'æ°', '£çœ', 'Ÿå', '¥']

=== 4. KV cache 效果对比 ===
生成 80 个 token (prompt 长度 8):
  use_cache=True:  2.34s
  use_cache=False: 8.91s
  加速比: 3.8x
  （序列越长，加速比越明显；CPU 上差距更显著）

=== 5. 采样策略对比 ===
[greedy (do_sample=False)]:
  ...' the one that you use to write your code in. It is a language that is easy to learn and'

[temperature=0.3 (低温度)]:
  ...' the one that you can use to create your own applications and websites. It is a'

[temperature=1.0 (默认温度)]:
  ...' the one for doing everything. We are going to talk about what makes them different, what'

[top_k=10]:
  ...' the same thing. There are many reasons for this. The first reason is that it is a very'
```

## 对应笔记

- [[I_大语言模型笔记]] — LLM 架构、训练流程、推理部署
  - §2 Tokenization
  - §7.1 自回归推理循环
  - §7.2 KV cache 原理
  - §7.3 Sampling 策略
- [[02_PyTorch笔记]] — 底层 tensor / autograd