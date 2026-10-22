---
title: 大语言模型（LLM）笔记
description: LLM 从原始世界知识到可对话服务的完整工业流程：数据工程 → 预训练 → 后训练（SFT + 偏好对齐）→ 推理部署 → 模型压缩。所有阶段用具体技术栈描述，避免抽象/比喻。
type: hub
---

# 大语言模型（LLM）笔记

> **本文目的**：从工业级流程视角，描述一个 LLM 如何从一堆原始世界知识（网页、书籍、代码、论文）经过多阶段训练，最终能理解用户输入并生成对话回复。
> 由旧稿重构而来；旧稿目录已清理，当前以本文为准。

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | LLM 架构基础 | 当前主流 decoder-only Transformer 的标准组件 |
| 2 | Tokenization | 文本 ↔ token id 转换，决定了模型能"看到"什么粒度 |
| 3 | 数据工程 | pretraining 前的语料处理 pipeline，决定数据质量 |
| 4 | 预训练 | next token prediction + 大规模分布式训练 |
| 5 | SFT 监督微调 | 让模型学会按 chat template 格式回复 |
| 6 | 偏好对齐 | RLHF / DPO / RLAIF 让模型回答符合人类偏好 |
| 7 | 推理部署 | 推理循环、KV cache、PagedAttention、vLLM 体系 |
| 8 | 模型压缩 | 量化 / 蒸馏 / 剪枝，降低推理成本 |
| 9 | 工具栈速查 | 各阶段工业级框架/工具的代表选型 |
| 10 | 端到端链路 | 把所有阶段串成一张图 |

---

## 1. LLM 架构基础

当前主流 LLM（LLaMA、Qwen、DeepSeek、Mistral 等）几乎都是 **decoder-only Transformer**，区别在于层内组件的选型。

### 1.1 标准组件清单

| 组件 | 当前主流选择 | 备注 |
|---|---|---|
| 位置编码 | **RoPE**（Rotary Position Embedding） | 外推性好，支持 context 长度扩展（YaRN、NTK-aware 缩放） |
| 归一化 | **RMSNorm**（pre-norm） | 比 LayerNorm 少一个均值中心化计算；pre-norm 训练更稳定 |
| 激活函数 | **SwiGLU** / GeGLU | 替代 ReLU，FFN 中使用三个投影矩阵 |
| 注意力变体 | **GQA**（Grouped-Query Attention） | 多个 query head 共享一组 KV，KV cache 显存随 group 数线性下降 |
| 注意力实现 | **Flash Attention** | IO-aware 算法，显存从 O(N²) 降到 O(N) |
| FFN 扩展比 | 通常 `hidden = 2.66 × dim`（SwiGLU 的 8/3） | 与 GQA 配合平衡参数和计算量 |

### 1.2 模型结构对比

| 类型 | 代表 | 特点 |
|---|---|---|
| Dense | LLaMA-3-70B, Qwen2.5-72B | 每层参数全激活，推理计算量 = 参数量 |
| MoE（Mixture of Experts） | Mixtral 8x7B, DeepSeek-V3 | 每层多个 expert，路由只激活 top-k（通常 2/8），参数量大但推理 FLOPs 小 |

### 1.3 与上一代结构的差异

- **encoder-decoder**（T5/FLAN-T5）：用得越来越少，因为同等参数下 decoder-only 在 scaling law 上表现更好
- **纯 encoder**（BERT 系）：只懂不理解，不能生成，已退出 LLM 主流
- **post-norm → pre-norm**：pre-norm 让深层网络训练更稳定，是当前标配

---

## 2. Tokenization

Tokenization 是文本进入模型的第一道工序，决定了模型能"看到"的最小语义单位。

### 2.1 主流算法

| 算法 | 代表实现 | 训练方式 |
|---|---|---|
| **BPE**（Byte Pair Encoding） | GPT-2、tiktoken（OpenAI） | 从字符集开始，迭代合并最高频字符对 |
| **WordPiece** | BERT | 类似 BPE，但选择合并对时基于似然增益 |
| **Unigram** | SentencePiece（默认） | 从大词表开始，反向迭代剪枝掉贡献小的 token |

### 2.2 关键工程细节

- **词表大小权衡**：
  - 太小（如 8K）：每个 token 平均字符少，序列变长，attention 计算量↑
  - 太大（如 200K）：embedding 表参数大，稀有 token 训练不充分
  - 当前主流：32K ~ 128K（LLaMA-3 = 128K，Qwen2.5 = 151K）
- **特殊 token**：
  - 基础：`<bos>`、`<eos>`、`<pad>`、`<unk>`
  - Chat 专用：`<|im_start|>`、`<|im_end|>`（Qwen 风格）、`<|user|>`、`<|assistant|>`（LLaMA-3 风格）
- **实现选型**：
  - `tiktoken`：OpenAI 高性能 BPE（GPT-4、o1 用）
  - `SentencePiece`：Google 库，语言无关，直接在 raw text 上训练（不需要预分词）
  - `transformers.AutoTokenizer`：统一接口，加载任何模型的 tokenizer

### 2.3 Tokenization 对下游任务的影响

- 多语言模型必须支持目标语言的 token；中英混合文本的 token 效率差异可达 5x
- 代码 token 通常单独训练（如 LLaMA-3 的 code-specific 词表）
- 数学公式 token 是数学推理模型的优化点（如 DeepSeek-Math）

---

## 3. 数据工程（pretraining 之前）

pretraining 的输入是**清洗过的 token 流**，不是原始网页。数据工程 pipeline 的每一步都直接影响模型质量。

### 3.1 数据源

| 来源 | 典型代表 | 特点 |
|---|---|---|
| 网页 | **Common Crawl**（PB 级） | 最大来源，质量参差，需要重度清洗 |
| 百科 | Wikipedia | 高质量，但量级小（~50GB） |
| 代码 | The Stack / GitHub | 代码能力的主要来源 |
| 书籍 | Books3 / Project Gutenberg | 长文本、文学性 |
| 论文 | ArXiv / S2ORC | 学术推理能力 |
| 问答 | StackExchange | 指令格式的天然样本 |

### 3.2 工业级清洗 pipeline

```
原始网页 → 1.抽取 → 2.语言识别 → 3.质量过滤 → 4.去重 → 5.PII 移除 → tokenizer → token 流
```

**步骤详解**：

1. **抽取**（Extraction）：HTML → 正文
   - 工具：`trafilatura`、`jusText`、`resiliparse`
   - 目标：去掉导航栏、广告、模板内容

2. **语言识别**（Language Identification）
   - 工具：`fastText` 语言分类器（CLD-2、langdetect 备选）
   - 目标：只保留目标语言（如英语为主、目标中文按比例）

3. **质量过滤**（Quality Filtering）
   - **启发式**：长度、标点比例、停用词比例、特殊字符比例
   - **模型打分**：用一个小 KenLM 算 perplexity，过滤掉 perplexity 极端的文档
   - **DSIR**（Data Selection via Importance Resampling）：用目标域数据训练分类器，按重要性重采样

4. **去重**（Deduplication）
   - **精确去重**：文档级/段落级别 hash（SHA-256）
   - **模糊去重**：MinHash + LSH（Locality-Sensitive Hashing），检测 90%+ 重叠的文档
   - **必要性**：LLaMA 论文显示去重可以提升 perplexity 和减少记忆化风险

5. **PII 移除**（Personally Identifiable Information）
   - 规则：邮箱、电话、身份证号正则
   - 模型：NER 模型识别姓名、地址
   - 合规：GDPR、个人隐私法规要求

### 3.3 公开 pretraining 数据集

| 数据集 | 提供方 | 规模 | 特点 |
|---|---|---|---|
| **The Pile** | EleutherAI | 825 GB | 多源混合，已被广泛使用 |
| **RedPajama** | Together | 1.2T tokens | LLaMA-1 论文的复现版本 |
| **Dolma** | AI2 | 3T tokens | 完整工具链开源 |
| **FineWeb** | HuggingFace | 15T tokens | 2024 年发布，目前质量最高的开源 web 数据集 |

---

## 4. 预训练（Pretraining）

预训练的目标是让模型学会**预测下一个 token**，即建模语言统计分布。这一步是 LLM 所有能力的根基。

### 4.1 训练目标：Causal Language Modeling (CLM)

给定 token 序列 `x_1, x_2, ..., x_T`：

$$
\mathcal{L} = -\frac{1}{T} \sum_{t=1}^{T} \log P(x_{t+1} \mid x_1, ..., x_t)
$$

- **本质**：teacher forcing，每个位置上预测下一个 token，标准 cross-entropy 损失
- **为什么有效**：能学到语法、事实、推理链（因为推理过程出现在训练语料中）
- **扩展形式**：
  - **FIM**（Fill-in-the-Middle）：允许模型在中间插入 token，用于代码补全
  - **CLM + FIM 联合训练**：Code LLM 常用

### 4.2 分布式训练（3D 并行）

单卡放不下 70B 模型，单机多卡算力不够，pretraining 必须用分布式。工业上有 3 个并行维度：

| 维度 | 切分方式 | 代表实现 |
|---|---|---|
| **TP**（Tensor Parallel） | 单层切到多 GPU（attention head、FFN 维度） | Megatron-LM |
| **PP**（Pipeline Parallel） | 按层切分到多 GPU（如 0-15 层在 GPU0） | GPipe, PipeDream |
| **DP**（Data Parallel） | 模型复制多份，各看不同 batch | PyTorch DDP |

**组合使用**：3D 并行 = TP × PP × DP，是 100B+ 模型训练的标准范式。

### 4.3 显存优化

| 技术 | 作用 | 库 |
|---|---|---|
| **ZeRO-1/2/3** | 把 optimizer state / gradient / parameter 分片到 DP 进程 | DeepSpeed |
| **FSDP** | PyTorch 原生等价于 ZeRO-3 | torch.distributed.fsdp |
| **混合精度（BF16 + FP32 master）** | 主计算用 BF16（速度↑、显存↓），优化器更新用 FP32（数值稳定） | torch.amp, DeepSpeed |
| **Flash Attention** | IO-aware attention，O(N) 显存 | flash-attn |
| **Gradient Checkpointing** | 不保存中间 activation，反向时重算 | torch.utils.checkpoint |
| **Activation Offloading** | GPU 显存不够时卸载到 CPU/NVMe | DeepSpeed |
| **CPU Offloading** | optimizer state 放 CPU（ZeRO-Offload） | DeepSpeed |

### 4.4 工业级框架

| 框架 | 提供方 | 定位 |
|---|---|---|
| **Megatron-LM** | NVIDIA | TP/PP 性能天花板 |
| **DeepSpeed** | Microsoft | ZeRO 系列，生态完善 |
| **FSDP** | PyTorch 原生 | 与 torch 生态无缝集成 |
| **Hugging Face Transformers + Accelerate** | HuggingFace | 入门友好，社区丰富 |

### 4.5 典型规模参考

| 模型 | 参数量 | 训练 token 数 | GPU | 时长 |
|---|---|---|---|---|
| GPT-3 | 175B | 300B | ~10K V100 | 数月 |
| LLaMA-1 65B | 65B | 1.4T | 2K A100 × 80GB | ~21 天 |
| LLaMA-3 70B | 70B | 15.6T | 16K H100 | 数月 |
| DeepSeek-V3 | 671B (MoE, 37B active) | 14.8T | 2K H800 | ~2 月 |

训练算力成本：单次完整 pretrain 成本可达 $1M ~ $100M+ 量级。

---

## 5. SFT（Supervised Fine-Tuning，监督微调）

Pretraining 完的模型是一个"next token predictor"，能续写但不会按指令回答。**SFT 让模型学会按 chat template 格式与用户对话**。

### 5.1 Chat Template

SFT 数据的标准格式是多轮对话：

```xml
<|im_start|>system
你是一个 helpful assistant<|im_end|>
<|im_start|>user
什么是 KV cache？<|im_end|>
<|im_start|>assistant
KV cache 是 Transformer 推理时缓存 K/V 张量的机制...<|im_end|>
<|im_start|>user
它和 PagedAttention 的关系？<|im_end|>
<|im_start|>assistant
PagedAttention 是 vLLM 对 KV cache 的分页管理...<|im_end|>
```

各模型的 template 风格不同：
- **ChatML**：Qwen 系列使用（`<|im_start|>` / `<|im_end|>`）
- **LLaMA-3 格式**：`<|begin_of_text|>` + `<|start_header_id|>user<|end_header_id|>`
- **OpenAI ChatML**：`{role, content}` JSON（API 层）

### 5.2 训练细节

- **损失 Mask**：**只对 assistant 的 token 计算 cross-entropy**，user 和 system 的 token 设为 `-100`（PyTorch ignore_index）
- **原因**：让模型学"怎么回答"，而不是学"怎么提问"
- **实现**：在数据预处理阶段用 tokenizer 的 `apply_chat_template()`，然后按 role 标记 loss

### 5.3 SFT 数据集

| 数据集 | 规模 | 来源 |
|---|---|---|
| **Alpaca** | 52K | self-instruct（GPT-3.5 生成） |
| **ShareGPT** | ~90K | ChatGPT 真实多轮对话 |
| **OpenHermes-2.5** | 1M | 多源混合 |
| **UltraChat** | 1.5M | 两阶段 self-instruct |
| **OpenOrca** | 4M | GPT-4 解释 + FLAN |

### 5.4 SFT 工具

| 工具 | 特点 |
|---|---|
| **TRL `SFTTrainer`** | HuggingFace 原生，与 transformers 无缝 |
| **LLaMA-Factory** | 配置式训练平台，支持 100+ 模型 |
| **Axolotl** | YAML 配置驱动，社区活跃 |
| **Unsloth** | 显存优化（2x↓），速度优化（5x↑） |

### 5.5 全参数微调 vs PEFT

| 方法 | 显存需求（7B） | 适用场景 |
|---|---|---|
| **全参数 SFT** | ~60GB+ | 数据足、需要深度定制 |
| **LoRA**（Low-Rank Adaptation） | ~20GB | 冻结原权重，注入低秩矩阵（rank=16~64） |
| **QLoRA** | ~10GB | 4-bit 量化 + LoRA，单卡 24GB 也能训 70B |

---

## 6. 偏好对齐

SFT 让模型学会了"按格式回答"，但回答质量不一定符合人类偏好。**偏好对齐阶段让模型变得更 helpful、harmless、honest（3H 原则）**。

### 6.1 RLHF（Reinforcement Learning from Human Feedback）

OpenAI 在 InstructGPT 论文中提出的三步法：

**Step 1：SFT**（已在第 5 步完成）

**Step 2：训练 Reward Model**
- 数据：人类对同一 prompt 的多个回答做排序（`(prompt, chosen, rejected)`）
- 模型：以 prompt 为输入，输出标量分数 `r(x, y)`
- 损失：pairwise ranking loss
$$
\mathcal{L}_{RM} = -\log \sigma(r(x, y_w) - r(x, y_l))
$$
- 通常 6B ~ 70B 的 RM，标量头

**Step 3：PPO（Proximal Policy Optimization）优化**
- 目标：在 RM 分数高的方向调模型，同时加 KL 惩罚防止偏离 SFT 模型太远
$$
\max_\pi \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi(y|x)} [r(x, y) - \beta \cdot \text{KL}(\pi \| \pi_{SFT})]
$$
- 难点：训练不稳定，需要 4 个模型同时在显存中（policy / reference / reward / value）

### 6.2 DPO（Direct Preference Optimization）

**简化版 RLHF**，无需训练 reward model，直接用偏好对优化：

$$
\mathcal{L}_{DPO} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)
$$

- **优势**：训练稳定、实现简单、显存占用小（2 个模型）
- **代价**：在分布外 prompt 上效果略逊于 RLHF

### 6.3 其他对齐变体

| 算法 | 特点 |
|---|---|
| **KTO**（Kahneman-Tversky） | 用单条标注（good/bad）而非成对 |
| **IPO** | 避免 DPO 的 overfitting |
| **ORPO** | SFT + 对齐一体化，无需 reference model |
| **RLAIF**（RL from AI Feedback） | 用 LLM 反馈替代人类反馈（Constitutional AI） |
| **Reinforcement Learning from Self-Feedback** | 模型自评 + 强化（Anthropic 风格） |

### 6.4 推理模型（Reasoning Models）

2024 年开始的新范式：模型在回答前先**长链思考**（long chain-of-thought）。

| 代表 | 方法 |
|---|---|
| OpenAI o1 / o3 | 内部 long-CoT + RL（细节未完全公开） |
| DeepSeek-R1 | RL 训练出 long-CoT 行为，蒸馏到小模型 |
| Qwen-QwQ | long-CoT SFT + RL |

**关键创新**：
- **Process Reward Model (PRM)**：对推理**步骤**打分（不是最终答案），奖励正确的推理过程
- **Test-time compute scaling**：推理时多次采样 + 搜索（best-of-N、MCTS）
- **长 CoT 蒸馏**：把大推理模型的能力蒸馏到小模型（DeepSeek-R1-Distill 系列）

---

## 7. 推理部署

训练完成的模型如何变成可调用的服务？这是工程化最复杂的环节。

### 7.1 自回归推理循环

```
tokens = tokenizer.encode(prompt)               # 1. 文本 → token ids
while not stop:                                  # 2. 自回归循环
    logits = model(tokens)                       #    forward（一次）
    next_logits = logits[:, -1, :]               #    取最后一个位置
    next_token = sample(next_logits, T, top_p, top_k)  # 3. 采样
    tokens = append(tokens, next_token)          # 4. 拼接到序列
    if next_token == eos_token: stop             # 5. 终止判断
return tokenizer.decode(tokens)                  # 6. token ids → 文本
```

每生成一个 token 要跑一次完整的 forward（对整个序列），所以**推理是 O(T²) FLOPs**（T 为序列长度）。

### 7.2 KV Cache 原理

每次生成新 token 时，attention 需要所有历史 token 的 K、V。如果每次重算：
- 第 1 步算 1 个 token 的 K、V
- 第 2 步算 2 个 token 的 K、V
- ...
- 第 T 步算 T 个 token 的 K、V
- **总计算量**：O(T²)

**KV cache 做法**：把每一步算过的 K、V 缓存起来，每步只算新 token 的 K、V：
- **总计算量**：O(T)
- **代价**：每层每头要存 T 个 K 向量 + T 个 V 向量，显存占用为 `2 × n_layers × n_heads × head_dim × T × bytes_per_elem`

### 7.3 Sampling 策略

| 策略 | 公式 / 行为 | 适用 |
|---|---|---|
| **Greedy** | `argmax` | 确定性场景（代码、数学） |
| **Temperature** | `softmax(logits / T)`，T<1 更确定，T>1 更随机 | 控制多样性 |
| **Top-k** | 只从概率 top-k 中采样 | 截断长尾 |
| **Top-p**（Nucleus） | 累积概率达 p 的最小集合中采样 | 自适应截断 |
| **Min-p** | 概率 ≥ p × max_prob 中采样 | Top-p 的改进版 |

实际工程中常组合：`temperature=0.7, top_p=0.9` 是常见的折中。

### 7.4 Batching 演进

LLM 推理的关键瓶颈是 **GPU 利用率低**（因为每个请求长度不同、生成时间不同）。

| 方案 | 做法 | 缺陷 |
|---|---|---|
| **Static Batching** | 等所有请求完成才返回 | 长请求拖累短请求（padding 浪费） |
| **Dynamic Batching** | 把同时到达的请求组 batch | 仍受最长请求限制 |
| **Continuous Batching**（vLLM） | 每个 token 生成步后重新调度，新请求可立即插入 | 实现复杂 |

Continuous batching 让 GPU 利用率从 ~30% 提升到 ~80%+，吞吐量提升 10x+。

### 7.5 PagedAttention（vLLM 核心创新）

KV cache 的传统做法是**预分配连续显存**，按最大序列长度分配，浪费严重。

**PagedAttention** 借鉴 OS 虚拟内存的**分页管理**：
- 把 KV cache 切成固定大小的 block（如每 block 16 tokens）
- 维护 block table（逻辑 → 物理 block 映射）
- 显存利用率从 ~20% 提升到 ~80%+

### 7.6 投机解码（Speculative Decoding）

用一个小 draft model 一次猜 k 个 token，大模型一次 verify k 个：

```
draft_model: 生成 [t1, t2, ..., tk]
main_model: 一次 forward，验证 [t1, t2, ..., tk]
接受其中前缀匹配的 m 个（m ≤ k）
```

- **加速**：2-3x（草稿模型便宜，大模型一次验证多个 token）
- **保真**：接受/拒绝规则保证输出分布与原模型**完全一致**

### 7.7 推理框架

| 框架 | 提供方 | 特点 |
|---|---|---|
| **vLLM** | UC Berkeley | PagedAttention + Continuous Batching，工业首选 |
| **TGI**（Text Generation Inference） | HuggingFace | 生产级 serving，多模型支持 |
| **SGLang** | LMSYS | RadixAttention，适合 agent / 复杂 prompt |
| **TensorRT-LLM** | NVIDIA | 极致性能，需要编译 |
| **llama.cpp** | 开源 | CPU/边缘设备，GGUF 格式 |
| **MLX** | Apple | Apple Silicon 优化 |
| **vLLM-Omni / SGLang** | 2025+ | 多模态推理 |

### 7.8 服务化

- **API 协议**：OpenAI-compatible（`/v1/chat/completions`），已成事实标准
- **流式响应**：SSE（Server-Sent Events）逐 token 返回
- **Autoscaling**：基于 GPU 利用率 / 队列长度的 K8s HPA
- **可观测性**：请求延迟、TTFT（Time To First Token）、TPS（Tokens Per Second）

> 上述为推理部署的**原理侧**。生产环境的部署调优——显存参数（`gpu-memory-utilization` / `kv-cache-dtype` / 量化）、并发机制（continuous batching / prefix caching / chunked prefill）、Prometheus 指标完整清单、Grafana 面板、`vllm bench serve` / 日志配置、以及 vLLM 与 SGLang 的横向对比与选型建议——详见 **[[02_推理部署笔记]]**。

---

## 8. 模型压缩

部署时显存和算力是主要瓶颈。**压缩在部署前进行**，目的是减小模型体积、提升推理速度、降低成本。

### 8.1 量化（Quantization）

把权重从高精度（FP16）转到低精度（INT8/INT4/FP8），减显存 + 加速计算。

#### 8.1.1 精度等级与显存占用（7B 模型）

| 精度 | 单参数字节 | 7B 模型总显存 | 适用 |
|---|---|---|---|
| FP32 | 4 | 28 GB | 训练 |
| FP16 / BF16 | 2 | 14 GB | 推理 / 训练 |
| INT8 | 1 | 7 GB | 推理 |
| FP8（E4M3） | 1 | 7 GB | H100 推理 |
| INT4 | 0.5 | 3.5 GB | 边缘部署 |
| INT2 | 0.25 | 1.75 GB | 极限压缩（质量损失大） |

#### 8.1.2 量化粒度

- **per-tensor**：整层一个 scale + zero point（粒度粗，质量损失大）
- **per-channel**：每个 channel 一个 scale + zero point
- **per-group**：每 group_size 个 weight 共享一个 scale（group_size=128 常见，质量最好）

#### 8.1.3 主流量化算法

| 算法 | 类型 | 原理 |
|---|---|---|
| **GPTQ** | PTQ | 逐层量化，基于二阶 Hessian（OBS 算法）补偿误差 |
| **AWQ** | PTQ | Activation-aware Weight Quantization，保护 1-3% salient weights 不量化 |
| **SmoothQuant** | PTQ | 等价变换把 activation 难度转移到 weight |
| **bitsandbytes** | PTQ | HuggingFace 集成，NF4 数据类型，4-bit 推理 |
| **QAT** | QAT | 训练时模拟量化，质量更好但成本高 |

### 8.2 蒸馏（Distillation）

用大模型（teacher）教小模型（student）。

| 蒸馏目标 | 损失 |
|---|---|
| **Logit 蒸馏** | `KL(softmax(z_T / T) || softmax(z_S / T))` |
| **Feature 蒸馏** | student 的 hidden state 拟合 teacher 的 hidden state |
| **Attention 蒸馏** | attention matrix 对齐 |

代表模型：
- **DistilBERT**：60% 大小，保留 97% 性能
- **TinyLLaMA**：1.1B，从 LLaMA-2 蒸馏
- **Qwen2.5 系列**：0.5B/1.5B/3B 是从大模型蒸馏

### 8.3 剪枝（Pruning）

| 类型 | 做法 | 代表 |
|---|---|---|
| **结构化剪枝** | 删整个 attention head / FFN 神经元 / layer | MobileBERT、MiniLM |
| **非结构化剪枝** | 单个 weight 置 0（需要稀疏计算支持） | SparseGPT、Wanda |

工业实践：结构化剪枝更常用，因为非结构化稀疏需要硬件/库支持。

### 8.4 工业级案例

- **Qwen2.5 系列**：0.5B / 1.5B / 3B 是从大模型蒸馏
- **DeepSeek-V3**：MoE + FP8 训练 + 多 token 预测
- **GPT-4 推测**：8x220B MoE（未官方确认）

---

## 9. 工具栈速查

| 类别 | 代表工具 / 框架 |
|---|---|
| **训练框架** | Megatron-LM, DeepSpeed, FSDP, Hugging Face Transformers + Accelerate |
| **SFT / 对齐** | TRL, LLaMA-Factory, Axolotl, DeepSpeed-Chat |
| **推理框架** | vLLM, TGI, SGLang, TensorRT-LLM, llama.cpp |
| **量化** | bitsandbytes, AutoGPTQ, AutoAWQ, SmoothQuant |
| **数据处理** | dolma (AI2), FineWeb (HF), RedPajama, The Pile |
| **评测** | lm-eval-harness, OpenCompass, MMLU, MT-Bench, LiveBench |
| **Tokenizer** | tiktoken, SentencePiece, HuggingFace tokenizers |
| **部署平台** | HuggingFace Endpoints, Modal, Together, Fireworks, Anyscale |

---

## 10. 端到端链路：世界知识 → 对话能力

把上述所有阶段串起来，看一个 LLM 是如何从一堆原始语料变成可对话的产品的：

```
原始世界知识（PB 级网页 / 书籍 / 代码）
    │
    ▼  [数据工程 pipeline：抽取 → 语言识别 → 质量过滤 → 去重 → PII]
    │
清洗后的 token 流（~10T tokens）
    │
    ▼  [预训练：next token prediction + 3D 并行 + BF16 + Flash Attention]
    │
Base LLM（如 LLaMA-3-70B）
    │  ┌─ 已具备：语言能力、事实知识、初步推理
    │  └─ 缺失：不会按指令回答、不知道自己的角色
    ▼  [SFT：chat template 数据 + mask user token + 全参/LoRA 微调]
    │
Instruct LLM（如 LLaMA-3-70B-Instruct）
    │  ┌─ 已具备：按格式回答、对话能力
    │  └─ 缺失：不一定符合人类偏好（可能冗长、可能有害）
    ▼  [偏好对齐：RLHF (Reward Model + PPO) 或 DPO]
    │
Aligned Chat Model（如 Claude、GPT-4、文心一言）
    │  ┌─ 已具备：helpful + harmless + honest
    │  └─ 可选：long-CoT 推理增强（o1、DeepSeek-R1）
    ▼  [可选：模型压缩：量化 / 蒸馏 / 剪枝]
    │
部署版本（FP16/INT8/INT4）
    │
    ▼  [推理部署：vLLM + KV cache + Continuous Batching]
    │
用户输入 → tokenizer → 模型 → next token 采样 → KV cache 加速 → 解码 → 流式返回
```

### 10.1 关键转换点

| 转换 | 作用 |
|---|---|
| 原始语料 → 清洗 token 流 | **质量过滤**决定了模型上限。数据质量比模型架构更影响最终效果（"garbage in, garbage out"） |
| Token 流 → Base LLM | pretraining 让模型**内化语言统计分布**，包含语法、事实、推理模式 |
| Base LLM → Instruct LLM | SFT 让模型学会**条件生成**（按指令回答） |
| Instruct LLM → Aligned Model | 对齐让模型回答**符合人类偏好**（更结构化、更安全、更有用） |
| Aligned Model → 部署版本 | 压缩让模型**适配目标硬件**（显存、延迟、吞吐量要求） |

### 10.2 当前 SOTA 趋势（2025）

- **推理模型崛起**：o1、o3、DeepSeek-R1 把长 CoT 变成新范式
- **Agent 化**：LLM 作为推理核心 + 工具调用 + 规划
- **小模型蒸馏**：用大推理模型的能力蒸馏到 7B / 1.5B 模型
- **MoE 普及**：推理时只激活部分参数，性价比高于 dense
- **长 context**：1M+ tokens 成为标配（Qwen2.5-1M, Gemini-1.5-Pro）
- **多模态原生**：GPT-4o、Gemini 2.0、Qwen2.5-VL 把视觉/音频原生融合进 LLM

---

## 配套 demo

- [[workspace/llm-demo/01_tokenization_and_generation/README]]：用 GPT-2 演示 tokenizer 切分、next token prediction 循环、KV cache 加速效果、采样策略对比。
- [[workspace/llm-demo/02_inference_serving/README]]：OpenAI SDK 打本地/远程 vLLM/SGLang 服务 + Prometheus 指标解析 + benchmark JSON 模拟（无需 GPU）。
- [[02_PyTorch笔记]]：底层 tensor / nn.Module / autograd 基础
- [[03_深度学习环境安装笔记]]：CUDA / cuDNN / PyTorch 版本对应
- [[02_推理部署笔记]]：vLLM / SGLang 生产环境的显存/并发/指标/日志/选型对比
