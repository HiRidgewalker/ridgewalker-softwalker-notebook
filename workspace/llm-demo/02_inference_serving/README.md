# 02_inference_serving · OpenAI 客户端 + Prometheus 解析 + benchmark 模拟

演示 [[Hub/02_推理部署笔记]] 中**生产调优侧**的可执行部分：

- **OpenAI 兼容客户端**：用 openai SDK（≥1.0）打本地/远程 vLLM / SGLang 服务（两者均暴露 `/v1/chat/completions`），流式响应中统计 TTFT / TPOT / 端到端吞吐
- **Prometheus `/metrics` 解析**：拉服务端指标文本，按 Counter / Gauge / Histogram 三类分组打印关键指标（`vllm:` / `sglang:` 前缀）
- **Benchmark 模拟**：本地 mock 服务 + 并发请求，输出 `vllm bench serve` 风格的 JSON 报告（无需真实 GPU）
- **`vllm bench serve` 调用说明**：列出关键参数和 JSON 输出 schema

> 整个 demo **不需要 GPU**，所有真实路径在服务不可达时自动降级为 mock。

## 涵盖知识点

- OpenAI SDK 客户端（`openai.OpenAI`）流式调用与时间戳采集
- Prometheus 文本格式解析（`metric{labels} value` / `metric_bucket{...} count`）
- vLLM 关键指标：`vllm:request_success` / `vllm:kv_cache_usage_perc` / `vllm:time_to_first_token_seconds_*` 等
- SGLang 关键指标：`sglang:cache_hit_rate` / `sglang:gen_throughput` / `sglang:num_running_reqs` 等
- `vllm bench serve --help` 关键参数
- benchmark JSON schema（`output_token_throughput` / `p99_ttft_ms` / `p99_tpot_ms` 等）

## 运行

```bash
# 装依赖
uv pip install --python workspace/.venv/bin/python -r workspace/llm-demo/02_inference_serving/requirements.txt

# 跑（mock 模式，无需启动 vLLM / SGLang）
workspace/.venv/bin/python workspace/llm-demo/02_inference_serving/main.py
```

### 切到 live 模式

```bash
# 启动 vLLM（另一终端）
vllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000

# 用环境变量指定，重跑 demo 即走 live 路径
INFERENCE_BASE_URL=http://localhost:8000/v1 \
INFERENCE_MODEL=meta-llama/Meta-Llama-3-8B-Instruct \
workspace/.venv/bin/python workspace/llm-demo/02_inference_serving/main.py
```

```bash
# 启动 SGLang
python3 -m sglang.launch_server --model-path meta-llama/Llama-3.1-8B-Instruct --port 30000

# 用环境变量切到 SGLang
INFERENCE_BASE_URL=http://localhost:30000/v1 \
INFERENCE_MODEL=meta-llama/Llama-3.1-8B-Instruct \
workspace/.venv/bin/python workspace/llm-demo/02_inference_serving/main.py
```

环境变量：

| 变量 | 默认 | 说明 |
|---|---|---|
| `INFERENCE_BASE_URL` | `http://localhost:8000/v1` | OpenAI 兼容服务地址（vLLM 默认 8000，SGLang 默认 30000） |
| `INFERENCE_MODEL` | `my-model` | 模型 ID（与服务启动时的模型一致） |
| `INFERENCE_API_KEY` | `EMPTY` | API key（vLLM / SGLang 默认不校验，给任意非空字符串） |
| `INFERENCE_METRICS_URL` | `<base>/metrics` | Prometheus 指标端点 |

## 输出示例（节选）

```text
=== 1. OpenAI 兼容客户端（vLLM / SGLang 通用） ===
BASE_URL = http://localhost:8000/v1
MODEL    = my-model
[mock] 未探测到本地服务，使用 mock 流式响应演示指标计算

  TTFT           = 51.3 ms
  TPOT（平均）   = 18.7 ms
  端到端耗时     = 632.4 ms
  生成 token 数  = 31
  生成吞吐       = 49.02 tok/s
  回复预览       = '[mock response to: 用一句话解释 KV cache。... ] tok0 tok1 ...'

=== 2. Prometheus /metrics 解析 ===
METRICS_URL = http://localhost:8000/metrics

  [Counter] (3 metrics)
    vllm:request_success = 1024
    vllm:prompt_tokens = 524288
    vllm:generation_tokens = 204800
  [Gauge] (3 metrics)
    vllm:num_requests_running = 32
    vllm:num_requests_waiting = 4
    vllm:kv_cache_usage_perc = 0.78
  [Histogram] (1 metrics)
    vllm:time_to_first_token_seconds: ... (15 samples)

  [观察点]
  - vLLM 指标前缀 'vllm:'，SGLang 指标前缀 'sglang:'，二者不互通
  - vllm:kv_cache_usage_perc 应当 >0.75 表明显存利用充分
  - vllm:num_requests_waiting > 0 持续增长 = 排队
  - sglang:cache_hit_rate >0.5 通常意味着多轮/RAG 场景有效复用 KV

=== 3. Benchmark 模拟（无需 GPU） ===
[mock] 模拟 50 个请求 / 并发 8

[vllm bench serve 风格 JSON 输出]:
{
  "successful_requests": 50,
  "total_input_tokens": 12800,
  "total_output_tokens": 8712,
  "request_throughput": 8.21,
  "output_token_throughput": 1431.7,
  "total_token_throughput": 3534.5,
  "mean_ttft_ms": 102.3,
  "median_ttft_ms": 96.7,
  "p99_ttft_ms": 215.4,
  "mean_tpot_ms": 38.5,
  "p99_tpot_ms": 57.8,
  ...
}
```

## 关键观察点

1. **OpenAI 兼容是事实标准**：vLLM、SGLang、TGI、TensorRT-LLM 都暴露 `/v1/chat/completions`，一份客户端代码可切换。
2. **指标前缀不可互通**：`vllm:` / `sglang:` 完全独立，采集 / 告警规则需分别配置；底层 KV cache 物理布局也不同，prefix cache 不能跨引擎共享。
3. **TTFT / TPOT / E2E 是生产核心指标**：对应 `time_to_first_token_seconds` / `time_per_output_token_seconds` / `e2e_request_latency_seconds` 三个 Histogram；告警阈值参考 P99（如 P99 TTFT < 500ms）。
4. **KV 缓存利用率是显存定位起点**：`vllm:kv_cache_usage_perc`（V0 名为 `gpu_cache_usage_perc`）应稳定 >0.75；<0.5 时考虑提高 `--max-num-seqs` 或缩小 `--max-model-len`。
5. **prefix cache 命中率**：`vllm:prefix_cache_hits / vllm:prefix_cache_queries` 在多轮 / RAG 场景常 >60%，命中率低时检查 system prompt 是否进 prefix cache。
6. **benchmark 报告字段**：`output_token_throughput`（tok/s）通常比 `request_throughput`（req/s）更能反映 GPU 利用率，因为不同请求生成 token 数差异巨大。

## 对应笔记

- [[Hub/02_推理部署笔记]]
  - §2 vLLM 启动命令
  - §3 vLLM 显存优化（关键参数表）
  - §4 vLLM 并发与吞吐
  - §5 vLLM 可观测性（完整 Prometheus 指标 / Grafana / 日志）
  - §8 SGLang 启动命令（注意 `chunked-prefill-size` vs `enable-chunked-prefill` 别名坑）
  - §9-§10 SGLang 显存 / 并发
  - §11 SGLang 可观测性
  - §12 vLLM vs SGLang 横向对比与选型
- [[Hub/01_大语言模型笔记]] §7 推理部署（原理基础）
