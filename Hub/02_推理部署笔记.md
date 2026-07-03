---
title: 推理部署（vLLM + SGLang）生产笔记
description: vLLM 与 SGLang 在生产环境的完整使用方法：显存优化参数、并发机制、Prometheus 指标、token 吞吐率量化、Grafana 面板、日志配置；附 vLLM vs SGLang 选型对比。所有结论来自公开文档与官方博客。
type: hub
---

# 推理部署（vLLM + SGLang）生产笔记

> **本文目的**：补全 [[01_大语言模型笔记]] §7 推理部署的"原理 → 生产"缺口。**原理**（自回归循环、KV cache 结构、PagedAttention 思想）已在 `Hub/01_大语言模型笔记` §7.1-§7.7 覆盖；本文专注于：**怎么把模型启动成一个生产可观测、可调优的服务**。
> 由旧稿重构而来；旧稿仅是外部链接清单，当前以本文为准。

## 阅读地图

| § | 主题 | 一句话定位 |
|---|---|---|
| 1 | vLLM 概述 | 项目背景与生态 |
| 2 | vLLM 启动命令 | `vllm serve` 典型用法与 OpenAI 兼容 API |
| 3 | vLLM 显存优化 | PagedAttention / prefix caching / chunked prefill / 量化 / 多卡并行 + 关键参数 |
| 4 | vLLM 并发与吞吐 | continuous batching / speculative decoding / 调度参数 |
| 5 | vLLM 可观测性 | Prometheus 指标完整清单 / Grafana / bench / 日志 / V0 vs V1 |
| 6 | vLLM 调优 checklist | 显存、吞吐、监控三组定位清单 |
| 7 | SGLang 概述 | LMSYS 出品、RadixAttention、与 vLLM 的关系 |
| 8 | SGLang 启动命令 | `python3 -m sglang.launch_server` 完整 ServerArgs |
| 9 | SGLang 显存与吞吐 | mem-fraction-static / radix cache / 多卡 / 量化 |
| 10 | SGLang 并发与吞吐 | zero-overhead 调度 / cache-aware 路由 / speculative |
| 11 | SGLang 可观测性 | sglang: 前缀指标 / 官方 Grafana / 日志 |
| 12 | vLLM vs SGLang 横向对比 | 共同点 / 差异表 / 选型建议 / 互操作 |
| 13 | 来源链接 | 全部参考链接按章节分组 |

---

## 1. vLLM 概述

[vLLM](https://github.com/vllm-project/vllm) 是 UC Berkeley RISELab 2023 年开源的高吞吐 LLM serving 系统，论文 [PagedAttention (arXiv:2309.06180)](https://arxiv.org/abs/2309.06180) 与 [vLLM 发布博客](https://vllm.ai/blog/2023-06-20-vllm) 把 KV cache 的显存浪费从传统系统的 60-80% 降到 <4%，单卡吞吐最高相对 HF Transformers **24×**、相对 HF TGI **3.5×**。

当前主要使用方：

- **LMSYS Chatbot Arena**：vLLM 部署服务 Chatbot Arena 部分模型（与 SGLang、ORT 并行承担），原报告单卡吞吐提升 30×、GPU 数量 -50%。
- **Anyscale（vLLM 商业运营方）**：在 [Anyscale × Google GKE 联合博客](https://www.anyscale.com/blog/high-performance-distributed-inference-with-ray-serve-llm) 披露 Llama-3-70B 上开 prefix caching + FP8 KV cache 后吞吐 **+2.1×**、P99 TTFT **-40%**。
- **Modal / BentoML / AWS Neuron / 阿里云 PAI**：均有官方生产案例。

---

## 2. vLLM 启动命令

**最小启动**（OpenAI 兼容服务）：

```bash
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --gpu-memory-utilization 0.92 \
  --max-model-len 8192
```

启动后默认监听 `http://0.0.0.0:8000`，同时提供：

- **OpenAI 兼容端点**：`/v1/chat/completions`、`/v1/completions`、`/v1/embeddings`（可直接用 OpenAI SDK / `curl`）
- **Prometheus 指标**：`/metrics`（V0 在启动日志中提示，V1 默认开启）
- **健康检查**：`/health`

**典型生产命令**（融合 prefix caching + chunked prefill + KV cache 量化）：

```bash
vllm serve meta-llama/Meta-Llama-3-70B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 8 \
  --gpu-memory-utilization 0.95 \
  --max-model-len 16384 \
  --max-num-seqs 256 \
  --max-num-batched-tokens 8192 \
  --kv-cache-dtype fp8_e4m3 \
  --quantization awq \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-log-requests
```

来源：[Engine Args 官方文档](https://docs.vllm.ai/en/latest/configuration/engine_args.html)。

---

## 3. vLLM 显存优化

### 3.1 PagedAttention 原理回顾（与 G1 的关联）

把 KV cache 切成固定 token 数的 block（如 16 tokens），用 block table 做逻辑块到物理块的映射，借鉴 OS 虚拟内存：

- **block table** 维护 `(请求 → 物理 block 序列)` 映射
- **copy-on-write + 引用计数** 让 parallel sampling / beam search 共享前缀 KV cache
- **效果**：浪费从 60-80% 降到 **<4%**（仅每序列最后一个 block 浪费），吞吐相对原系统 **最高 2.2×**

### 3.2 版本演进的关键特性

| 版本 | 特性 | 价值 |
|---|---|---|
| **v0.4 (2024-01)** | Automatic Prefix Caching (APC)，按 block hash 复用 KV | 多轮对话 / 长上下文 QA 显存与延迟双降 |
| **v0.6 (2024-09)** | 默认开启 Chunked Prefill，长 prompt 切块与 decode 共 batch | TTFT 与吞吐同步改善，长 prompt 不再独占 GPU |
| **v0.7+** | V1 引擎默认，多进程 Prometheus、OpenTelemetry tracing | 监控与分布式追踪原生集成 |

来源：[vLLM v0.6 博客](https://vllm.ai/blog/2024-10-23-vllm-v06)、[Automatic Prefix Caching 文档](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)。

### 3.3 显存相关关键参数（v0.6 / v0.7）

| 参数 | 默认 | 含义 | 生产推荐 |
|---|---|---|---|
| `--gpu-memory-utilization` | 0.92 | 模型权重+KV 池占总显存比例 | 单实例 0.9-0.95；同卡多实例按比例拆 |
| `--max-model-len` | 模型 config | 最大上下文 | 设为业务 P99（不要按 max_position_embeddings） |
| `--max-num-seqs` | 256 | 单步并发序列数 | 受 KV 容量限制，配合监控 `vllm:num_requests_running` |
| `--max-num-batched-tokens` | 2048 | 单步总 token 上限 | 长 prompt 提到 4096-8192 提高 chunked prefill 利用率 |
| `--block-size` | 16 | 每 block token 数 | 长上下文可试 32；与 prefix cache 粒度权衡 |
| `--cpu-offload-gb` | 0 | 每 GPU CPU offload（GiB） | 0.5-4 GiB，装下大模型但拖慢 forward，需 NVLink |
| `--num-gpu-blocks-override` | None | 强制 block 数 | 仅调优 / 测试用 |
| `--enable-prefix-caching` | v0.6+ True | 启用 APC | 多轮 / RAG 必开 |
| `--kv-cache-dtype` | auto | KV 精度：`fp8_e5m2` / `fp8_e4m3` / `nvfp4` | FP8 KV → 等效并发翻倍，精度几乎无损 |

来源：[Engine Args 官方文档](https://docs.vllm.ai/en/latest/configuration/engine_args.html)、[Metrics Design](https://docs.vllm.ai/en/latest/design/metrics/)。

### 3.4 量化对显存的影响

加载方式统一：`LLM(model=..., quantization="awq"/"gptqmodel"/"bitsandbytes"/"fp8")` 或 CLI `--quantization <method>`。

| 格式 | 位宽 | 相对 FP16 显存 | 说明 |
|---|---|---|---|
| **AWQ** | INT4 | ~25% | Marlin kernel，Ampere+ 加速 |
| **GPTQ / GPTQModel** | INT4 | ~25% | Marlin / Machete kernel |
| **bitsandbytes NF4** | 4-bit | ~25% | `bitsandbytes>=0.49.2`，在线量化 |
| **FP8 (W8A8)** | FP8 | ~50% | Hopper (H100/H200) 最佳 |

**典型收益**：70B 模型 FP16 ~140GB → AWQ INT4 **~35GB**，可装进单张 A100-80G；FP8 再砍半。

来源：[Quantization 总览](https://docs.vllm.ai/en/latest/features/quantization.html)。

### 3.5 多卡相关

| 维度 | 切分方式 | 显存效果 |
|---|---|---|
| `--tensor-parallel-size`（TP） | 单层切多卡（attn head / FFN 维度） | 权重 ≈ 1/N，KV ≈ 1/N，NVLink 效率高 |
| `--pipeline-parallel-size`（PP） | 按层切多卡 | 权重 1/N 但 KV 不切，气泡大，跨节点大模型用 |
| `--enable-expert-parallel`（EP） | MoE 专家切多卡 | 专家权重 1/N，其他部分走 TP |

**建议**：单节点 70B+ Dense → TP；跨节点或 70B+ MoE → TP × EP。

来源：[vLLM MoE 支持 Issue](https://github.com/vllm-project/vllm/issues/4650)。

---

## 4. vLLM 并发与吞吐

### 4.1 Continuous Batching

每个 token 生成步后重新调度，新请求可立即插入。GPU 利用率从静态 batching 的 ~30% 提升到 **80%+**，吞吐提升 **10×+**。

实现位于 vLLM 的 scheduler（`vllm/v1/engine_core.py`），与 prefix caching / chunked prefill 深度集成。

### 4.2 Chunked Prefill（v0.6+ 默认）

把长 prompt 切成小块（`--max-num-batched-tokens / 2` 之类）与 decode 共 batch，降低 prefill 阶段对 KV 的瞬时占用，避免长请求独占 GPU。

实际效果（Anyscale × GKE 联合案例）：长 prompt 场景 decode batch 翻 **1.8×**。

### 4.3 Prefix Caching

按 block hash 自动匹配 KV cache 块，多轮对话 / RAG 场景命中率常 >60%。

LMSYS 接入 vLLM 后单卡吞吐 **30×**，GPU 数量 **-50%**。

### 4.4 Speculative Decoding

用一个小 draft model 一次猜 k 个 token，大模型一次 verify k 个，**保真输出分布**（接受/拒绝规则保证与原模型一致），典型加速 **2-3×**。

启动方式：`--speculative-model <draft-model> --num-speculative-tokens 5`。

### 4.5 调度相关参数

| 参数 | 推荐范围 | 说明 |
|---|---|---|
| `--max-num-seqs` | 128 - 512 | 受 KV 池容量限制，超过会被抢占 |
| `--max-num-batched-tokens` | 4096 - 16384 | 长 prompt 场景提到 4096+ |
| `--scheduler-delay-factor` | 0 - 10 | 控制调度延迟因子（生产一般不动） |
| `--num-lookahead-slots` | 0 | speculative 时的预分配槽位 |

监控 `vllm:num_preemptions`，出现频繁抢占时调小 `max-num-seqs` 或 `max-model-len`。

来源：[vLLM blog](https://vllm.ai/blog/2023-06-20-vllm)、[LMSYS SGLang blog 2024-01](https://lmsys.org/blog/2024-01-17-sglang/)。

---

## 5. vLLM 可观测性

### 5.1 Prometheus 指标完整清单

来源：[Production Metrics 文档](https://docs.vllm.ai/en/latest/usage/metrics/) 与 [Metrics Design](https://docs.vllm.ai/en/latest/design/metrics/)。所有指标带 `model_name` 标签。

#### Counter（单调递增）

| 指标 | 说明 |
|---|---|
| `vllm:request_success`（V1；V0 为 `vllm:request_success_total`） | 成功请求数 |
| `vllm:corrupted_requests` | 损坏请求数 |
| `vllm:prompt_tokens` | prompt token 总数 |
| `vllm:prompt_tokens_cached` | prefix cache 命中 token 数 |
| `vllm:prompt_tokens_by_source` | 按数据源拆分（OpenAI / HTTP / engine 等） |
| `vllm:generation_tokens` | 生成 token 总数 |
| `vllm:prefix_cache_queries` / `vllm:prefix_cache_hits` | prefix cache 查询 / 命中次数 |
| `vllm:external_prefix_cache_queries` / `vllm:external_prefix_cache_hits` | 外部 prefix cache（多实例共享） |
| `vllm:mm_cache_queries` / `vllm:mm_cache_hits` | 多模态 cache |
| `vllm:num_preemptions` | 请求抢占次数 |
| `vllm:spec_decode_num_accepted_tokens_per_pos` | speculative accepted token 数 |
| `vllm:nixl_num_failed_notifications` / `vllm:nixl_num_failed_transfers` / `vllm:nixl_num_kv_expired_reqs` | NIXL KV connector |
| `vllm:estimated_flops_per_gpu_total` 等 MFU 系列 | 需 `--enable-mfu-metrics` |

#### Gauge（实时状态）

| 指标 | 说明 |
|---|---|
| `vllm:num_requests_running` | 正在处理的请求数 |
| `vllm:num_requests_waiting` / `vllm:num_requests_waiting_by_reason` | 排队请求数（可按原因拆分） |
| `vllm:kv_cache_usage_perc`（V0 为 `vllm:gpu_cache_usage_perc`） | KV 缓存利用率，0-1 |
| `vllm:lora_requests_info` | 当前活跃 LoRA（值 = wall-clock） |
| `vllm:engine_sleep_state` | 引擎睡眠状态 |

#### Histogram（分布）

| 指标 | 说明 |
|---|---|
| `vllm:time_to_first_token_seconds`（TTFT） | 首个 token 延迟 |
| `vllm:inter_token_latency_seconds`（TPOT / ITL） | token 间延迟 |
| `vllm:e2e_request_latency_seconds` | 端到端延迟 |
| `vllm:request_queue_time_seconds` | 排队时间 |
| `vllm:request_prefill_time_seconds` / `vllm:request_decode_time_seconds` / `vllm:request_inference_time_seconds` | prefill / decode / 推理总时间 |
| `vllm:request_time_per_output_token_seconds` | 旧 `time_per_output_token_seconds` 的规范化名 |
| `vllm:request_prompt_tokens` / `vllm:request_generation_tokens` | 请求级 token 数 |
| `vllm:request_max_num_generation_tokens` / `vllm:request_params_n` / `vllm:request_params_max_tokens` | 请求级参数 |
| `vllm:request_prefill_kv_computed_tokens` / `vllm:iteration_tokens_total` | prefill 计算的 KV token |
| `vllm:kv_block_lifetime_seconds` / `vllm:kv_block_idle_before_evict_seconds` / `vllm:kv_block_reuse_gap_seconds` | KV block 生命周期 |
| `vllm:model_forward_time_milliseconds` / `vllm:model_execute_time_milliseconds` | OpenTelemetry + `--collect-detailed-traces` |

### 5.2 Grafana / Prometheus 集成

vLLM 仓库自带可一键启动的监控栈：

```
examples/observability/prometheus_grafana/
├── docker-compose.yaml
├── prometheus.yaml
├── grafana.json            # 单端口 vLLM dashboard
└── README.md
```

官方提供更多 dashboard JSON：

- `examples/observability/dashboards/grafana/performance_statistics.json` —— 延迟 / 吞吐 / 性能
- `examples/observability/dashboards/grafana/query_statistics.json` —— 请求量 / KPI
- `examples/observability/dashboards/perses/` —— Perses 模板
- `examples/observability/opentelemetry/` —— OTel 集成示例

启动后端口：

- vLLM `8000/metrics`
- Prometheus `9090`
- Grafana `3000`（`admin/admin`）

来源：[examples/observability/README](https://github.com/vllm-project/vllm/blob/main/examples/observability/prometheus_grafana/README.md)。

### 5.3 vllm bench CLI

来源：[Benchmark CLI 文档](https://docs.vllm.ai/en/latest/benchmarking/cli.html)。

| 子命令 | 用途 | 关键参数 |
|---|---|---|
| `vllm bench serve` | 在线压测 | `--model` `--dataset` `--num-prompts` `--request-rate`（`inf` = 最大吞吐） `--max-concurrency` `--burstiness` `--ramp-up-strategy {linear,exponential}` `--backend {vllm,openai-chat,...}` `--plot-timeline` `--save-result` |
| `vllm bench throughput` | 离线吞吐 | `--model` `--dataset` `--num-prompts` `--max-num-seqs` |

输出 JSON schema：

```json
{
  "successful_requests": 200,
  "total_input_tokens": 50000,
  "total_output_tokens": 80000,
  "request_throughput": 12.5,
  "output_token_throughput": 5000.0,
  "total_token_throughput": 8125.0,
  "mean_ttft_ms": 120, "median_ttft_ms": 95, "p99_ttft_ms": 380,
  "mean_tpot_ms": 35, "median_tpot_ms": 30, "p99_tpot_ms": 110,
  "mean_itl_ms": 35, "median_itl_ms": 30, "p99_itl_ms": 110
}
```

来源：[Benchmark 文档](https://docs.vllm.ai/en/latest/benchmarking/cli.html)。

### 5.4 日志配置

| 参数 / 环境变量 | 默认 | 说明 |
|---|---|---|
| `--enable-log-requests` | False | 记录 Request ID / 参数 / LoRA（`VLLM_LOGGING_LEVEL=INFO`） |
| `--enable-log-outputs` | False | 记录生成内容（注意 PII） |
| `--enable-log-deltas` | True | 增量式输出日志 |
| `--disable-log-stats` | False | 关闭统计日志 |
| `--uvicorn-log-level` | info | 仅控制 uvicorn 访问日志 |
| `VLLM_LOGGING_LEVEL` 环境变量 | INFO | 决定 `--enable-log-requests` 详细级别 |

来源：[vllm serve CLI 文档](https://docs.vllm.ai/en/latest/cli/serve.html)。

### 5.5 V0 vs V1 引擎可观测性差异

V1（v0.7+ 默认开启，`VLLM_USE_V1=1`）对指标体系有较大改造：

- **命名规范化**：`vllm:gpu_cache_usage_perc` → `vllm:kv_cache_usage_perc`，移除 V0 中未实现的 `vllm:avg_prompt_throughput_toks_per_s` / `vllm:tokens_total`
- **更细 Histogram**：`request_params_n` / `request_max_num_generation_tokens` / `request_prefill_kv_computed_tokens` / `num_requests_waiting_by_reason`
- **新增 NIXL KV connector 指标**（`vllm:nixl_*`）与可选 MFU 指标（`--enable-mfu-metrics`）
- **Multiprocess Prometheus**：V1 重写注册代码（`vllm/v1/metrics/prometheus.py`），贴近官方 multiprocess mode

V0 中未在 V1 继续支持的：阶段时间 `request_forward_time_seconds` / `request_execute_time_seconds`，已统一收敛到 `request_prefill_time_seconds` / `request_decode_time_seconds` / `request_inference_time_seconds`。

---

## 6. vLLM 调优 checklist

**显存定位**：

1. 业务监控 `vllm:kv_cache_usage_perc` —— 目标 **>75%**
2. 长 prompt 开启 chunked prefill（v0.6+ 默认）
3. KV cache 可试 `--kv-cache-dtype fp8_e4m3`（等效并发翻倍，精度几乎无损）
4. 多实例同卡：每个实例 `--gpu-memory-utilization` 按比例拆

**吞吐定位**：

1. 监控 `rate(vllm:prompt_tokens_total[1m])` 与 `rate(vllm:generation_tokens_total[1m])` 算 token/s
2. `vllm:num_requests_waiting_by_reason` 拆分队列延迟原因
3. `vllm:num_preemptions` 接近 0；不为 0 时调小 `--max-num-seqs`
4. 多轮 / RAG 必开 prefix caching，命中率 >60% 收益明显

**监控面板建议**：四组面板

1. **吞吐**：token/s、RPS、output token throughput
2. **延迟**：P50 / P99 TTFT、TPOT、ITL、E2E（用 `histogram_quantile`）
3. **队列 / 调度**：`num_requests_running` / `num_requests_waiting{by_reason}` / `num_preemptions`
4. **KV 与内存**：`kv_cache_usage_perc`、prefix cache hit rate、KV block 生命周期

---

## 7. SGLang 概述

[SGLang](https://github.com/sgl-project/sglang) 是 LMSYS 团队（也是 Chatbot Arena 运营方）开发的高性能 LLM serving 框架，论文 [arXiv:2312.07104](https://arxiv.org/abs/2312.07104)，v0.4+ 官方宣称**全球 40 万+ GPU、每日数万亿 token** 的生产规模。

**核心创新：RadixAttention**

- 用 radix tree（前缀树的紧凑紧凑形式）维护"prompt → KV cache tensor"映射
- KV cache 不立即释放，跨请求自动复用
- 树存在 CPU、tensor 以 paged layout 存 GPU，LRU 递归驱逐叶子
- frontend 始终发全量 prompt，runtime 自动匹配，**手动配置成本为 0**

**与 vLLM PagedAttention 的区别**：

- PagedAttention 只解决显存碎片（KV 在 block 内连续物理布局）
- RadixAttention 在此之上加"跨请求自动前缀复用"，多轮对话 / 长 system prompt 场景命中率显著更高

来源：[LMSYS RadixAttention blog](https://lmsys.org/blog/2024-01-17-sglang/)、[arXiv:2312.07104](https://arxiv.org/abs/2312.07104)。

其他独创点：

| 特性 | 价值 |
|---|---|
| **Compressed FSM / XGrammar**（v0.4+） | 把 regex/grammar 编译为 FSM，JSON 解码延迟降 2×、吞吐升 2.5× |
| **Zero-Overhead Batch Scheduler**（v0.4） | CPU 调度与 GPU 计算重叠，吞吐 +1.1× |
| **Cache-Aware Load Balancer**（v0.4） | Rust router，缓存命中率 20% → 75%，路由命中后吞吐最高 1.9× |
| **DP Attention**（≥v0.4） | DeepSeek MLA 单 KV head，避免 TP 重复 |
| **PD Disaggregation**（v0.5+） | prefill/decode 拆节点，GB200 NVL72 解码 **2.7×/GPU** |

来源：[Compressed FSM blog 2024-02](https://lmsys.org/blog/2024-02-05-compressed-fsm/)、[v0.4 blog 2024-12](https://lmsys.org/blog/2024-12-04-sglang-v0-4/)、[GB200 PD Part I](https://lmsys.org/blog/2025-06-16-gb200-part-1/)。

---

## 8. SGLang 启动命令

**最小启动**：

```bash
python3 -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 --port 30000
```

启动后默认监听 `http://0.0.0.0:30000`：

- OpenAI 兼容：`/v1/chat/completions`、`/v1/completions`、`/v1/embeddings`、`/v1/.../vision`
- 原生：`/generate`、`/parse_function_call`
- 离线：`sgl.Engine(...).generate(...)`

**典型生产命令**：

```bash
python3 -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 --port 30000 \
  --mem-fraction-static 0.85 \
  --max-running-requests 256 \
  --chunked-prefill-size 8192 \
  --tp-size 2 --dp-size 4 \
  --attention-backend flashinfer \
  --quantization awq \
  --enable-metrics --enable-mfu-metrics \
  --tool-call-parser qwen25 \
  --log-level info
```

**踩坑提醒**：社区博客常见 `--enable-prefix-caching` / `--chunked-context`，但当前 ServerArgs 用 `--chunked-prefill-size` + `--disable-radix-cache=False` 等价；二者混用会触发报错。

来源：[ServerArgs 源码](https://raw.githubusercontent.com/sgl-project/sglang/main/python/sglang/srt/server_args.py)、[SGLang send_request 文档](https://docs.sglang.io/basic_usage/send_request.html)。

---

## 9. SGLang 显存与吞吐

### 9.1 关键 ServerArgs

| 参数 | 默认 | 说明 |
|---|---|---|
| `--mem-fraction-static` | None（自动算）| 模型权重 + KV cache pool 占总显存；OOM 时下调 |
| `--max-running-requests` | None（无上限）| 并发请求上限 |
| `--chunked-prefill-size` | None / `-1` 禁用 | 每块 prefill token 数（≥v0.2）|
| `--disable-radix-cache` | False（默认开 Radix）| 关闭前缀缓存 |
| `--tp-size` / `--dp-size` | 1 | 张量并行 / 节点内数据并行 |
| `--attention-backend` | 自动 | `flashinfer` / `fa3` / `fa4` / `triton` / `cutlass_mla` / `flashmla` 等 |
| `--prefill-attention-backend` / `--decode-attention-backend` | 自动 | 拆分 prefill / decode 阶段 backend |
| `--quantization` | None | `awq` / `gptq` / `marlin` / `bitsandbytes` / `gguf` / `fp8` / `mxfp8` / `w8a8_int8` 等 ≥30 种 |
| `--page-size` | 默认 | KV paged layout page size |

### 9.2 显存切分逻辑

GPU 显存按 `mem-fraction-static` **一次性预留**「**权重 + KV cache pool**」；KV pool 内部按 `page_size` 分页；TP / DP / EP 三种并行可叠加。

### 9.3 多卡组合

| 维度 | 切分方式 |
|---|---|
| `--tp-size` | 张量并行，单层切多卡 |
| `--dp-size` | 单节点多副本（独立 KV / 独立调度），靠 prefix cache 命中提升 |
| `--enable-dp-attention` | DP 时 attention 维度通信（DeepSeek MLA 用）|

来源：[SGLang DP Attention 文档](https://docs.sglang.io/)。

### 9.4 量化

≥30 种选项，覆盖 INT4 / FP8 / GGUF / AWQ / GPTQ / Marlin / bitsandbytes 等。命令行 `--quantization awq_marlin` 直接加载预量化模型。

---

## 10. SGLang 并发与吞吐

### 10.1 Zero-Overhead Continuous Batching

调度实现于 `python/sglang/srt/managers/scheduler.py`。v0.4 改造为 zero-overhead：CPU 调度与 GPU 计算重叠，吞吐 +1.1×。

### 10.2 Cache-Aware Load Balancer（v0.4+）

纯 Rust 实现的 router，多副本场景下基于 KV cache 命中路由请求。在 v0.4 博客的真实负载数据：

- 缓存命中率 **20% → 75%**
- 路由命中文本后路由吞吐最高 **1.9×**

### 10.3 Speculative Decoding

支持算法：EAGLE / EAGLE-2 / EAGLE-3 / MTP / DFLASH / NGRAM / STANDALONE / NEXTN（≥0.3 起 EAGLE 默认 ON）。

关键参数：`--speculative-algorithm` / `--speculative-draft-model-path` / `--speculative-num-steps` / `--speculative-eagle-topk` / `--speculative-num-draft-tokens` / `--speculative-attention-mode {prefill,decode}`。

benchmark 数据（LLaMA-3.1-8B，1×H100 MT bench）：无 spec **158 tok/s** → EAGLE-2 **244** → **EAGLE-3 373**。

来源：[SGLang spec 文档](https://docs.sglang.io/advanced_features/speculative_decoding.html)。

### 10.4 PD Disaggregation（v0.5+）

把 prefill 和 decode 拆到不同节点，专用于超大规模推理。GB200 NVL72 解码 **2.7×/GPU**。

来源：[GB200 PD blog 2025-06](https://lmsys.org/blog/2025-06-16-gb200-part-1/)。

### 10.5 vLLM 与 SGLang 公开 benchmark 对比

来源：[LMSYS Llama3 bench blog 2024-07](https://lmsys.org/blog/2024-07-25-sglang-llama3/)。

| 场景 | 结果 |
|---|---|
| Llama-70B 离线 | SGLang **3.1× vLLM** |
| Llama-8B 单卡 A100（短输入）| SGLang 与 TRT-LLM 同档（≈5000 tok/s），均优于 vLLM |
| Online RPS>10 | SGLang 延迟稳定，vLLM 激增 |
| 前缀缓存测试 | **关闭** prefix cache 的公平对比，确保差异来自引擎本身 |

注意：上述结果发布于 2024-07，vLLM 与 SGLang 都在持续演进；当代 benchmark 请自行 `vllm bench serve` + sglang 等价物对比。

---

## 11. SGLang 可观测性

### 11.1 Prometheus 指标（`sglang:` 前缀）

启动参数：`--enable-metrics --enable-mfu-metrics`。访问 `http://localhost:30000/metrics`。

**Counter**：

| 指标 | 说明 |
|---|---|
| `sglang:prompt_tokens_total` | prompt token 总数 |
| `sglang:generation_tokens_total` | 生成 token 总数 |
| `sglang:request_success_total` | 成功请求总数 |

**Gauge**：

| 指标 | 说明 |
|---|---|
| `sglang:token_usage` | KV token 使用率 |
| `sglang:cache_hit_rate` | radix cache 命中率 |
| `sglang:num_running_reqs` | 运行中请求数 |
| `sglang:num_used_tokens` | 已用 token 数 |
| `sglang:gen_throughput` | 生成吞吐（tok/s） |
| `sglang:num_queue_reqs` | 队列请求数 |

**Histogram**：

| 指标 | 说明 |
|---|---|
| `sglang:time_to_first_token_seconds` | TTFT |
| `sglang:e2e_request_latency_seconds` | E2E 延迟 |
| `sglang:time_per_output_token_seconds` | TPOT |
| `sglang:func_latency_seconds{label=""}` | 按 label 拆分延迟 |

**MFU（需 `--enable-mfu-metrics`）**：

| 指标 | 说明 |
|---|---|
| `sglang:estimated_flops_per_gpu_total` | 估算的 GPU FLOPs |

> **命名注意**：SGLang 指标以 `sglang:` 前缀，与 vLLM 的 `vllm:` **不自动映射**；采集 / 告警需要分别配置。

来源：[production_metrics](https://github.com/sgl-project/sglang/blob/main/docs/references/production_metrics.md)。

### 11.2 官方 Grafana Dashboard

仓库自带：

```
examples/monitoring/
├── docker-compose.yaml    # 一键起 Prometheus + Grafana
├── grafana/dashboards/json/sglang-dashboard.json
└── prometheus/prometheus.yaml
```

### 11.3 日志配置

| 参数 | 默认 | 说明 |
|---|---|---|
| `--log-level` | info | `warning` / `info` / `debug` |
| `--log-requests` | False | 记录请求轨迹 |
| `--request-timeout` | None | 请求超时 |

日志默认输出 JSON 行，便于对接 Loki / ELK。

---

## 12. vLLM vs SGLang 横向对比

### 12.1 共同点（都已具备）

- OpenAI 兼容 API (`/v1/chat/completions` 等)
- Continuous batching（vLLM 早期提出，SGLang v0.4 后 zero-overhead 重叠）
- KV cache 分页（PagedAttention 系）
- Tensor / Pipeline / Expert parallel 多卡并行
- 量化：FP8 / INT8 / INT4 / GPTQ / AWQ / GGUF
- Speculative decoding（EAGLE 系列 / n-gram 等）
- 多模态（vLLM-Omni 演进 / SGLang VLM 原生）

### 12.2 差异表

| 维度 | vLLM | SGLang | 倾向 |
|---|---|---|---|
| **KV cache 管理** | PagedAttention（block 分页） | PagedAttention + RadixAttention（前缀树自动复用） | 多轮对话 / 长 system prompt 共享 → SGLang 优 |
| **通用 LLM serving** | 非常成熟，PMC 级 | 成熟，LMSYS 主理 | 大体相当 |
| **Agent / structured output** | xgrammar / guidance / outlines 后端 | DSL 原生（`gen` / `select` / `function`）；XGrammar compressed FSM 10× JSON | SGLang 略优 |
| **显存调优粒度** | 细粒度参数（几十个） | 相对简洁，ServerArgs 自动调优 | vLLM 参数多 |
| **吞吐量 baseline** | 长期领先 | 共享前缀场景反超，部分场景接近 / 超过 vLLM | 看场景 |
| **工具生态** | HF 生态整合深（PEFT / TRL / LM Eval）| 独立生态，已集成 DSPy / LangChain | 看已有栈 |
| **多模态** | vLLM-Omni 演进，原生支持 LLaVA/Qwen2-VL | 原生支持 LLaVA/Qwen2-VL | 大体相当 |
| **K8s / 部署工具** | Anyscale / BentoML / 社区 Helm 齐全 | 主要靠社区，官方 Helm 较薄 | vLLM 更成熟 |
| **监控** | Prometheus + Grafana 模板齐全，V1 引擎内置 OTel | Prometheus 逐步补齐，官方 docker-compose + Grafana JSON | vLLM 更成熟 |
| **社区** | 2000+ 贡献者，PMC | LMSYS 主导，活跃 | vLLM 用户更多 |
| **生产规模披露** | Anyscale / AWS / 阿里云大规模使用 | 「全球 40 万+ GPU、每日数万亿 token」 | 都有大用户 |

### 12.3 选型建议

1. **纯文本 LLM serving**（chat / completion）：默认 vLLM，生态、K8s 模板、社区最大。
2. **多轮对话 / agent / tool use 密集**：SGLang 值得一试，RadixAttention 自动复用 system prompt 与历史 prefix，TTFT 与吞吐改善明显。
3. **HF Transformers 生态深度集成**（HF Hub / PEFT / TRL）：vLLM 集成成本更低。
4. **已有 K8s + Prometheus + Grafana 体系**：vLLM 集成模板成熟（`examples/observability/` 一键启）。
5. **结构化输出（JSON / Regex / EBNF）密集**：SGLang 的 XGrammar 后端更快。
6. **超大规模部署**：两者都有大规模生产案例，按团队熟悉度选。

### 12.4 互操作 / 共存

- **同集群双引擎**：用 OpenAI 兼容 API 解耦——文本 chat 走 vLLM，agent / tool use 走 SGLang，客户端调用方式一致，迁移成本低。
- **DSPy 集成**：SGLang 已作为 backend 集成至 [DSPy PR #263](https://github.com/stanfordnlp/dspy/pull/263)，同一份程序可在两引擎间切换。
- **混合 KV cache 思路**：vLLM 0.6+ 引入了 prefix caching（`--enable-prefix-caching`），业务若有大量共享前缀但想用 vLLM 生态，可开启。
- **LLaVA 在线 demo**：[https://llava.hliu.cc/](https://llava.hliu.cc/) 由 SGLang 提供服务。

> **注意事项**：两者 KV cache 物理布局不兼容，prefix cache **不能跨引擎共享**；同集群部署注意端口与 GPU 资源隔离。

---

## 13. 来源链接汇总

### vLLM

- [PagedAttention 论文 arXiv:2309.06180](https://arxiv.org/abs/2309.06180)
- [vLLM 发布博客 2023-06](https://vllm.ai/blog/2023-06-20-vllm)
- [vLLM v0.6 博客 2024-10](https://vllm.ai/blog/2024-10-23-vllm-v06)
- [vLLM 官方文档](https://docs.vllm.ai/en/latest/)
- [Engine Args 文档](https://docs.vllm.ai/en/latest/configuration/engine_args.html)
- [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
- [Quantization 总览](https://docs.vllm.ai/en/latest/features/quantization.html)
- [AWQ 文档](https://docs.vllm.ai/en/latest/quantization/auto_awq.html)
- [GPTQModel 文档](https://docs.vllm.ai/en/latest/quantization/gptqmodel.html)
- [BitsAndBytes 文档](https://docs.vllm.ai/en/latest/quantization/bnb.html)
- [Production Metrics 文档](https://docs.vllm.ai/en/latest/usage/metrics/)
- [Metrics Design](https://docs.vllm.ai/en/latest/design/metrics/)
- [vLLM V1 Prometheus 源码](https://github.com/vllm-project/vllm/blob/main/vllm/v1/metrics/prometheus.py)
- [Benchmark CLI](https://docs.vllm.ai/en/latest/benchmarking/cli.html)
- [vllm serve CLI](https://docs.vllm.ai/en/latest/cli/serve.html)
- [Structured Outputs](https://docs.vllm.ai/en/latest/features/structured_outputs.html)
- [examples/observability README](https://github.com/vllm-project/vllm/blob/main/examples/observability/prometheus_grafana/README.md)
- [Anyscale × Google GKE 案例](https://www.anyscale.com/blog/high-performance-distributed-inference-with-ray-serve-llm)
- [vLLM MoE Issue #4650](https://github.com/vllm-project/vllm/issues/4650)

### SGLang

- [SGLang GitHub](https://github.com/sgl-project/sglang)
- [SGLang 官方文档](https://docs.sglang.io/)
- [SGLang send_request](https://docs.sglang.io/basic_usage/send_request.html)
- [SGLang OpenAI Completions](https://docs.sglang.io/basic_usage/openai_api_completions.html)
- [SGLang OpenAI Vision](https://docs.sglang.io/basic_usage/openai_api_vision.html)
- [SGLang Structured Outputs](https://docs.sglang.io/advanced_features/structured_outputs.html)
- [SGLang Speculative Decoding](https://docs.sglang.io/advanced_features/speculative_decoding.html)
- [SGLang Tool Parser](https://docs.sglang.io/advanced_features/tool_parser.html)
- [production_metrics 文档](https://github.com/sgl-project/sglang/blob/main/docs/references/production_metrics.md)
- [ServerArgs 源码](https://raw.githubusercontent.com/sgl-project/sglang/main/python/sglang/srt/server_args.py)
- [arXiv:2312.07104 RadixAttention 论文](https://arxiv.org/abs/2312.07104)
- [LMSYS RadixAttention blog 2024-01](https://lmsys.org/blog/2024-01-17-sglang/)
- [LMSYS Compressed FSM blog 2024-02](https://lmsys.org/blog/2024-02-05-compressed-fsm/)
- [LMSYS Llama3 bench blog 2024-07](https://lmsys.org/blog/2024-07-25-sglang-llama3/)
- [LMSYS v0.3 blog 2024-09](https://lmsys.org/blog/2024-09-04-sglang-v0-3/)
- [LMSYS v0.4 blog 2024-12](https://lmsys.org/blog/2024-12-04-sglang-v0-4/)
- [LMSYS GB200 PD Part I blog 2025-06](https://lmsys.org/blog/2025-06-16-gb200-part-1/)
- [XGrammar 技术综述](https://blog.mlc.ai/2024/11/22/achieving-efficient-flexible-portable-structured-generation-with-xgrammar)

### 互操作

- [DSPy SGLang backend PR #263](https://github.com/stanfordnlp/dspy/pull/263)
- [LLaVA 在线 demo](https://llava.hliu.cc/)

---

## 配套 demo

- [[workspace/llm-demo/02_inference_serving/README]]：OpenAI SDK 打本地/远程 vLLM/SGLang 服务 + Prometheus 指标解析 + benchmark JSON 模拟（无需 GPU）。
- [[01_大语言模型笔记]] §7：原理（自回归循环 / KV cache / 连续 batching / PagedAttention 思想）。
