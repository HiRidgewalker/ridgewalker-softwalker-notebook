"""02_inference_serving · OpenAI 兼容客户端 + Prometheus 指标解析 + benchmark 模拟

涵盖（对应 Hub/02_推理部署笔记）：

- 1. OpenAI 兼容客户端：用 openai SDK 打本地/远程 vLLM / SGLang 服务（两者均兼容
     /v1/chat/completions），流式响应中统计 TTFT / TPOT / 端到端吞吐；
     无服务时自动降级为 mock。
- 2. Prometheus /metrics 解析：从服务端 /metrics 端点抓文本，按 Counter / Gauge /
     Histogram 三类分组打印关键指标（vllm:、sglang:）；无服务时输出 mock 文本。
- 3. Benchmark 模拟：用本地 mock server 模拟 N 个并发请求，统计 P50 / P99 延迟，
     输出 vllm bench serve 风格的 JSON 报告（无需真实 GPU）。
- 4. vllm bench serve 调用说明：演示关键参数与输出 JSON schema（不真跑，
     subprocess 调用 --help 并展示）。

环境变量：
- INFERENCE_BASE_URL  默认 http://localhost:8000/v1（vLLM 默认；SGLang 默认 30000）
- INFERENCE_MODEL    默认 "my-model"
- INFERENCE_API_KEY  默认 "EMPTY"（vLLM / SGLang 默认不校验）

对应笔记：Hub/02_推理部署笔记.md（§2 / §5.3 / §8 / §11）

运行：
    example/.venv/bin/python example/llm-demo/02_inference_serving/main.py
    # 或带环境变量指定 vLLM：
    INFERENCE_BASE_URL=http://localhost:8000/v1 example/.venv/bin/python \
      example/llm-demo/02_inference_serving/main.py
    # 或带环境变量指定 SGLang：
    INFERENCE_BASE_URL=http://localhost:30000/v1 example/.venv/bin/python \
      example/llm-demo/02_inference_serving/main.py
"""

from __future__ import annotations

import json
import os
import random
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

import requests

# ============================================================
# 配置
# ============================================================

BASE_URL = os.environ.get("INFERENCE_BASE_URL", "http://localhost:8000/v1").rstrip("/")
if not BASE_URL.endswith(("/v1",)):
    # 兜底：用户可能传了根地址，自动补 /v1
    BASE_URL = BASE_URL + "/v1"
MODEL = os.environ.get("INFERENCE_MODEL", "my-model")
API_KEY = os.environ.get("INFERENCE_API_KEY", "EMPTY")
METRICS_URL = os.environ.get("INFERENCE_METRICS_URL", BASE_URL.rstrip("/v1") + "/metrics")
TIMEOUT_SEC = 3.0


def _is_service_up(url: str) -> bool:
    """探测服务是否在跑（HEAD 或 GET /，3s 超时）"""
    try:
        r = requests.get(url.replace("/v1", "/"), timeout=TIMEOUT_SEC)
        return r.status_code < 500
    except Exception:
        return False


# ============================================================
# 1. OpenAI 兼容客户端：发 chat 请求测 TTFT / TPOT / 吞吐
# ============================================================

@dataclass
class ChatResult:
    ttft_ms: float            # time to first token
    tpot_ms: float            # 平均 token 间延迟
    duration_ms: float        # 端到端耗时
    output_tokens: int        # 生成的 token 数
    output_text: str          # 完整回复
    throughput_tok_s: float   # output_tokens / duration


def _call_chat_stream(prompt: str, max_tokens: int = 64) -> ChatResult:
    """调用 OpenAI 兼容服务的流式 chat（vLLM / SGLang 通用）"""
    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    t_start = time.perf_counter()
    ttft: float | None = None
    chunk_times: list[float] = []
    text_parts: list[str] = []
    completion_tokens = 0

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True,
        temperature=0.0,
    )

    for chunk in stream:
        now = time.perf_counter()
        if ttft is None and chunk.choices and chunk.choices[0].delta.content:
            ttft = (now - t_start) * 1000.0
            chunk_times.append(now)
        elif chunk.choices and chunk.choices[0].delta.content:
            chunk_times.append(now)
        # 累加文本与 token 数（usage 在最后一个 chunk）
        if chunk.choices and chunk.choices[0].delta.content:
            text_parts.append(chunk.choices[0].delta.content)
            completion_tokens += 1

    t_end = time.perf_counter()
    duration_ms = (t_end - t_start) * 1000.0
    if ttft is None:
        ttft = duration_ms  # 没收到 token 时退化为端到端

    # 计算 TPOT（除第一个 token 之外的平均间隔）
    if len(chunk_times) > 1:
        tpot_ms = statistics.mean(
            (chunk_times[i] - chunk_times[i - 1]) * 1000.0
            for i in range(1, len(chunk_times))
        )
    else:
        tpot_ms = duration_ms

    output_tokens = completion_tokens if completion_tokens > 0 else max_tokens

    return ChatResult(
        ttft_ms=ttft,
        tpot_ms=tpot_ms,
        duration_ms=duration_ms,
        output_tokens=output_tokens,
        output_text="".join(text_parts),
        throughput_tok_s=output_tokens / (duration_ms / 1000.0) if duration_ms > 0 else 0.0,
    )


def _mock_chat_stream(prompt: str, max_tokens: int = 64) -> ChatResult:
    """无真实服务时的 mock 流式响应"""
    print(f"  [mock] prompt={prompt!r}, max_tokens={max_tokens}")
    t_start = time.perf_counter()
    time.sleep(0.05)  # 模拟 TTFT
    ttft = (time.perf_counter() - t_start) * 1000.0
    # 模拟逐 token 输出
    chunk_times = [time.perf_counter()]
    text_parts = [f"[mock response to: {prompt[:30]}...] "]
    for i in range(min(max_tokens - 1, 30)):
        time.sleep(random.uniform(0.01, 0.03))
        chunk_times.append(time.perf_counter())
        text_parts.append(f"tok{i} ")
    duration_ms = (chunk_times[-1] - t_start) * 1000.0
    tpot_ms = statistics.mean(
        (chunk_times[i] - chunk_times[i - 1]) * 1000.0
        for i in range(1, len(chunk_times))
    )
    output_tokens = len(chunk_times)
    output_text = "".join(text_parts)
    return ChatResult(
        ttft_ms=ttft,
        tpot_ms=tpot_ms,
        duration_ms=duration_ms,
        output_tokens=output_tokens,
        output_text=output_text,
        throughput_tok_s=output_tokens / (duration_ms / 1000.0),
    )


def demo_openai_compatible_client() -> None:
    """演示 OpenAI 兼容客户端测延迟与吞吐"""
    print("\n=== 1. OpenAI 兼容客户端（vLLM / SGLang 通用） ===")
    print(f"BASE_URL = {BASE_URL}")
    print(f"MODEL    = {MODEL}")

    if _is_service_up(BASE_URL):
        print("[live] 探测到本地服务，走真实路径")
        result = _call_chat_stream("用一句话解释 KV cache。", max_tokens=64)
    else:
        print("[mock] 未探测到本地服务，使用 mock 流式响应演示指标计算")
        print("       启动 vLLM: vllm serve <model>")
        print("       启动 SGLang: python3 -m sglang.launch_server --model-path <model>")
        result = _mock_chat_stream("用一句话解释 KV cache。", max_tokens=64)

    print(f"\n  TTFT           = {result.ttft_ms:.1f} ms")
    print(f"  TPOT（平均）   = {result.tpot_ms:.1f} ms")
    print(f"  端到端耗时     = {result.duration_ms:.1f} ms")
    print(f"  生成 token 数  = {result.output_tokens}")
    print(f"  生成吞吐       = {result.throughput_tok_s:.2f} tok/s")
    print(f"  回复预览       = {result.output_text[:100]!r}")


# ============================================================
# 2. Prometheus /metrics 解析
# ============================================================

def _parse_prometheus_text(text: str) -> dict[str, list[tuple[dict[str, str], float]]]:
    """解析 Prometheus 文本格式，按指标名分组为 {labels: value} 列表"""
    families: dict[str, list[tuple[dict[str, str], float]]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # 形如 metric_name{label="val",label2="val2"} 1.23
        if "{" in line:
            head, rest = line.split("{", 1)
            name = head.strip()
            label_str, val_str = rest.split("}", 1)
            labels = {}
            for pair in label_str.split(","):
                if "=" not in pair:
                    continue
                k, v = pair.split("=", 1)
                labels[k.strip()] = v.strip().strip('"')
            try:
                value = float(val_str.strip())
            except ValueError:
                continue
            families.setdefault(name, []).append((labels, value))
        else:
            parts = line.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            name, val_str = parts
            try:
                value = float(val_str.strip())
            except ValueError:
                continue
            families.setdefault(name.strip(), []).append(({}, value))
    return families


def _classify_prometheus(metric_name: str) -> str:
    """基于 Prometheus / vLLM / SGLang 命名习惯的简单分类

    V0 命名以 _total 结尾识别 Counter；V1（vLLM 0.7+）改用裸名（如
    vllm:request_success），需要按已知集合识别。"""
    if "_bucket" in metric_name or "_sum" in metric_name or "_count" in metric_name:
        return "Histogram"
    if metric_name.endswith("_total") or metric_name.endswith("_created"):
        return "Counter"
    # vLLM V1 已知 Counter（裸名）—— 与 Hub/02_推理部署笔记 §5.1 保持一致
    _V1_COUNTERS = {
        "vllm:request_success", "vllm:corrupted_requests",
        "vllm:prompt_tokens", "vllm:prompt_tokens_cached",
        "vllm:prompt_tokens_by_source", "vllm:generation_tokens",
        "vllm:prefix_cache_queries", "vllm:prefix_cache_hits",
        "vllm:external_prefix_cache_queries", "vllm:external_prefix_cache_hits",
        "vllm:mm_cache_queries", "vllm:mm_cache_hits",
        "vllm:num_preemptions",
        "vllm:spec_decode_num_accepted_tokens_per_pos",
        "vllm:nixl_num_failed_notifications",
        "vllm:nixl_num_failed_transfers",
        "vllm:nixl_num_kv_expired_reqs",
    }
    if metric_name in _V1_COUNTERS:
        return "Counter"
    return "Gauge"


_MOCK_VLLM_METRICS = """\
# HELP vllm:request_success Total number of successfully finished requests.
# TYPE vllm:request_success counter
vllm:request_success{model_name="my-model"} 1024.0
# HELP vllm:prompt_tokens Total number of prefill tokens processed.
# TYPE vllm:prompt_tokens counter
vllm:prompt_tokens{model_name="my-model"} 524288.0
# HELP vllm:generation_tokens Total number of generation tokens processed.
# TYPE vllm:generation_tokens counter
vllm:generation_tokens{model_name="my-model"} 204800.0
# HELP vllm:num_requests_running Number of requests currently running on GPU.
# TYPE vllm:num_requests_running gauge
vllm:num_requests_running{model_name="my-model"} 32.0
# HELP vllm:num_requests_waiting Number of requests waiting to be processed.
# TYPE vllm:num_requests_waiting gauge
vllm:num_requests_waiting{model_name="my-model"} 4.0
# HELP vllm:kv_cache_usage_perc KV cache usage (0.0 - 1.0).
# TYPE vllm:kv_cache_usage_perc gauge
vllm:kv_cache_usage_perc{model_name="my-model"} 0.78
# HELP vllm:time_to_first_token_seconds Time to first token (TTFT) histogram.
# TYPE vllm:time_to_first_token_seconds histogram
vllm:time_to_first_token_seconds_bucket{model_name="my-model",le="0.1"} 800.0
vllm:time_to_first_token_seconds_bucket{model_name="my-model",le="0.5"} 1020.0
vllm:time_to_first_token_seconds_bucket{model_name="my-model",le="+Inf"} 1024.0
vllm:time_to_first_token_seconds_sum{model_name="my-model"} 65.4
vllm:time_to_first_token_seconds_count{model_name="my-model"} 1024.0
"""

_MOCK_SGLANG_METRICS = """\
# HELP sglang:request_success_total Total successfully finished requests.
# TYPE sglang:request_success_total counter
sglang:request_success_total{model_name="my-model"} 800.0
# HELP sglang:prompt_tokens_total Total prefill tokens.
# TYPE sglang:prompt_tokens_total counter
sglang:prompt_tokens_total{model_name="my-model"} 409600.0
# HELP sglang:generation_tokens_total Total generation tokens.
# TYPE sglang:generation_tokens_total counter
sglang:generation_tokens_total{model_name="my-model"} 163840.0
# HELP sglang:num_running_reqs Number of running requests.
# TYPE sglang:num_running_reqs gauge
sglang:num_running_reqs{model_name="my-model"} 24.0
# HELP sglang:token_usage KV token usage (0.0 - 1.0).
# TYPE sglang:token_usage gauge
sglang:token_usage{model_name="my-model"} 0.71
# HELP sglang:cache_hit_rate RadixAttention cache hit rate (0.0 - 1.0).
# TYPE sglang:cache_hit_rate gauge
sglang:cache_hit_rate{model_name="my-model"} 0.62
# HELP sglang:gen_throughput Generation throughput (tokens/sec).
# TYPE sglang:gen_throughput gauge
sglang:gen_throughput{model_name="my-model"} 12500.0
"""


def demo_prometheus_metrics_parsing() -> None:
    """从 /metrics 端点抓文本并按 Counter / Gauge / Histogram 分组打印"""
    print("\n=== 2. Prometheus /metrics 解析 ===")
    print(f"METRICS_URL = {METRICS_URL}")

    if _is_service_up(METRICS_URL):
        print("[live] 从真实 /metrics 拉取")
        try:
            text = requests.get(METRICS_URL, timeout=TIMEOUT_SEC).text
        except Exception as e:
            print(f"[mock] /metrics 拉取失败: {e}，改用 mock 数据")
            text = _MOCK_VLLM_METRICS if "vllm" in METRICS_URL or ":8000" in METRICS_URL else _MOCK_SGLANG_METRICS
    else:
        # 看不到任何服务，按地址规则选 mock
        if "30000" in METRICS_URL:
            text = _MOCK_SGLANG_METRICS
            print("[mock] SGLang /metrics 端口 (30000)，使用 mock SGLang 指标")
        else:
            text = _MOCK_VLLM_METRICS
            print("[mock] 未探测到本地服务，使用 mock vLLM 指标")

    families = _parse_prometheus_text(text)
    by_class: dict[str, list[str]] = {"Counter": [], "Gauge": [], "Histogram": []}
    for name, samples in families.items():
        if not samples:
            continue
        cls = _classify_prometheus(name)
        first_labels, first_value = samples[0]
        label_str = ",".join(f'{k}="{v}"' for k, v in first_labels.items() if k != "model_name")
        if label_str:
            label_str = "{" + label_str + "}"
        if cls == "Histogram":
            base = name.removesuffix("_bucket").removesuffix("_sum").removesuffix("_count")
            line = f"  {base}{label_str}: ... ({len(samples)} samples)"
        else:
            line = f"  {name}{label_str} = {first_value:g}"
        # 去重（histogram 多个 bucket 只显示一次）
        if line not in by_class[cls]:
            by_class[cls].append(line)

    for cls in ("Counter", "Gauge", "Histogram"):
        items = by_class[cls]
        if not items:
            continue
        print(f"\n  [{cls}] ({len(items)} metrics)")
        for line in items[:15]:
            print(line)
        if len(items) > 15:
            print(f"  ...（还有 {len(items) - 15} 个，省略）")

    print("\n  [观察点]")
    print("  - vLLM 指标前缀 'vllm:'，SGLang 指标前缀 'sglang:'，二者不互通")
    print("  - vllm:kv_cache_usage_perc 应当 >0.75 表明显存利用充分")
    print("  - vllm:num_requests_waiting > 0 持续增长 = 排队")
    print("  - sglang:cache_hit_rate >0.5 通常意味着多轮/RAG 场景有效复用 KV")


# ============================================================
# 3. Benchmark 模拟：本地 mock + 并发请求，输出 vllm bench serve 风格 JSON
# ============================================================

def _simulate_one_request(i: int) -> dict[str, float]:
    """模拟一次请求：返回 TTFT / E2E / output_tokens"""
    # 故意让数据有差异，方便看 P50 / P99
    ttft_ms = random.uniform(50, 200) + (i % 7) * 5
    output_tokens = random.randint(50, 300)
    tpot_ms = random.uniform(20, 60)
    e2e_ms = ttft_ms + output_tokens * tpot_ms
    return {
        "ttft_ms": ttft_ms,
        "e2e_ms": e2e_ms,
        "output_tokens": float(output_tokens),
    }


def demo_benchmark_simulation() -> None:
    """模拟并发请求并打印 benchmark JSON 报告（无需任何服务）"""
    print("\n=== 3. Benchmark 模拟（无需 GPU） ===")
    n = 50
    concurrency = 8
    print(f"[mock] 模拟 {n} 个请求 / 并发 {concurrency}")

    # 串行模拟（demo 不演示真并发，只演示统计逻辑）
    samples = [_simulate_one_request(i) for i in range(n)]
    ttft_list = sorted(s["ttft_ms"] for s in samples)
    e2e_list = sorted(s["e2e_ms"] for s in samples)
    tpot_list = sorted(s["e2e_ms"] / max(s["output_tokens"], 1) for s in samples)

    def pct(arr: list[float], p: float) -> float:
        if not arr:
            return 0.0
        idx = min(int(len(arr) * p), len(arr) - 1)
        return arr[idx]

    total_output_tokens = int(sum(s["output_tokens"] for s in samples))
    wall_time_s = sum(s["e2e_ms"] for s in samples) / 1000.0 / concurrency

    report = {
        "successful_requests": n,
        "total_input_tokens": n * 256,                # 假设 prompt 256 tokens
        "total_output_tokens": total_output_tokens,
        "request_throughput": n / wall_time_s,
        "output_token_throughput": total_output_tokens / wall_time_s,
        "total_token_throughput": (n * 256 + total_output_tokens) / wall_time_s,
        "mean_ttft_ms": statistics.mean(ttft_list),
        "median_ttft_ms": statistics.median(ttft_list),
        "p99_ttft_ms": pct(ttft_list, 0.99),
        "mean_tpot_ms": statistics.mean(tpot_list),
        "median_tpot_ms": statistics.median(tpot_list),
        "p99_tpot_ms": pct(tpot_list, 0.99),
        "mean_e2e_ms": statistics.mean(e2e_list),
        "median_e2e_ms": statistics.median(e2e_list),
        "p99_e2e_ms": pct(e2e_list, 0.99),
    }

    print("\n[vllm bench serve 风格 JSON 输出]:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n  [观察点]")
    print(f"  - request_throughput ≈ {report['request_throughput']:.2f} req/s")
    print(f"  - output_token_throughput ≈ {report['output_token_throughput']:.0f} tok/s")
    print(f"  - P99 TTFT / TPOT 决定用户感知延迟")


# ============================================================
# 4. vllm bench serve 调用说明
# ============================================================

def demo_bench_serve_runner() -> None:
    """演示 vllm bench serve 关键参数（不真跑，subprocess --help）"""
    print("\n=== 4. vllm bench serve 关键参数说明 ===")
    try:
        r = subprocess.run(
            ["vllm", "bench", "serve", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            # 截取关键参数说明
            lines = r.stdout.splitlines()
            # 输出几个最常用的开关
            keywords = {"--model", "--dataset", "--num-prompts", "--request-rate",
                        "--max-concurrency", "--burstiness", "--backend",
                        "--save-result", "--save-detailed", "--plot-timeline",
                        "--result-dir", "--result-filename"}
            print("  [关键参数（从 --help 抽取）]")
            for line in lines:
                if any(k in line for k in keywords):
                    print(f"    {line.strip()}")
        else:
            print(f"  [skip] 'vllm bench serve --help' 调用失败（vLLM 未装）。")
            print("         安装：uv pip install vllm")
            print("\n  [关键参数说明（手写）]")
            print("    --model             模型 ID，如 meta-llama/Meta-Llama-3-8B-Instruct")
            print("    --dataset           ShareGPT / BurstGPT / Random / Prefix Repetition / 自定义 JSON")
            print("    --num-prompts       总请求数")
            print("    --request-rate      inf 表示打满最大吞吐；数字表示 QPS")
            print("    --max-concurrency   最大并发请求数")
            print("    --burstiness        Gamma 分布形状参数，默认 1.0（Poisson）")
            print("    --backend           vllm / openai-chat / openai-embeddings / vllm-rerank")
            print("    --save-result       保存聚合 JSON 到 --result-dir")
            print("    --save-detailed     增加 per-request 数据")
            print("    --plot-timeline     输出交互式 HTML 时间线")
    except FileNotFoundError:
        print("  [skip] 'vllm' 命令不在 PATH 中（vLLM 未装）")
        print("         参考 Hub/02_推理部署笔记 §5.3 关键参数说明")


# ============================================================
# main
# ============================================================

def main() -> None:
    print("=" * 60)
    print("02_inference_serving demo")
    print("=" * 60)
    print(f"\n配置：BASE_URL={BASE_URL}, MODEL={MODEL}")
    print(f"提示：启动 vLLM 后重跑本 demo 可切到 [live] 路径")

    demo_openai_compatible_client()
    demo_prometheus_metrics_parsing()
    demo_benchmark_simulation()
    demo_bench_serve_runner()

    print("\n" + "=" * 60)
    print("demo 跑完，参考 example/llm-demo/02_inference_serving/README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
