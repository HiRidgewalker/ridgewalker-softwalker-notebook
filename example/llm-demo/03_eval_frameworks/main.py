"""03_eval_frameworks · OpenCompass + EvalScope 双框架 Mock 演示

涵盖（对应 Hub/OpenCompass笔记 / Hub/EvalScope笔记 / Hub/评测框架对比笔记）：

- 1. 自定义 JSONL 数据集：5 条数学应用题，含 system / query / response / answer
     字段；展示 OpenCompass 风格（BaseDataset 加载）+ EvalScope 风格
     （general_qa 模板）的读取与字段校验。
- 2. 本地模型评测：模拟 OpenCompass 加载 HF 模型 + 跑 JSONL；模拟 EvalScope
     run_task 用 mock_llm；输出每条样本的预测和分项得分。
- 3. 远程 API 模型评测：模拟 OpenCompass --models gpt_3_5_turbo 配置 + 远程
     API 调用；模拟 EvalScope --eval-type openai_api + --api-url 配置 +
     远程 API 调用。
- 4. 内置数据集选型：演示「按场景选数据集」决策树（基座 / Chat / 推理 /
     代码 / 中文 / 长文本 / 多模态 / 安全 / Agent 九类），每类给出
     OpenCompass 和 EvalScope 各自的数据集名。
- 5. 评测报告解读：模拟跑完后的报告输出（总分、子维度分、bad case 抽样、
     置信区间），展示 OpenCompass summary_*.csv + EvalScope reports/*.json
     两套格式的解读。

环境变量：
- EVAL_BACKEND     默认 both（opencompass / evalscope / both）
- OPENAI_API_KEY   默认 mock（远程 API mock 模式自动降级）

对应笔记：
- Hub/OpenCompass笔记.md
- Hub/EvalScope笔记.md
- Hub/评测框架对比笔记.md

运行：
    workspace/.venv/bin/python workspace/llm-demo/03_eval_frameworks/main.py
    # 或指定 demo：
    workspace/.venv/bin/python workspace/llm-demo/03_eval_frameworks/main.py --demo custom_dataset
    # 或指定 backend：
    EVAL_BACKEND=evalscope workspace/.venv/bin/python workspace/llm-demo/03_eval_frameworks/main.py

特点：全程不联网、不需要 GPU、不需要真实模型 / API。
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ============================================================
# 配置
# ============================================================

EVAL_BACKEND = __import__("os").environ.get("EVAL_BACKEND", "both").lower()
OPENAI_API_KEY = __import__("os").environ.get("OPENAI_API_KEY", "mock")
WORK_DIR = Path(__import__("os").environ.get("EVAL_WORK_DIR", str(Path(__file__).resolve().parent / "_outputs")))
WORK_DIR.mkdir(parents=True, exist_ok=True)

VALID_BACKENDS = {"opencompass", "evalscope", "both"}


def _should_run(backend: str) -> bool:
    """是否运行指定 backend 的 demo"""
    if EVAL_BACKEND == "both":
        return True
    return EVAL_BACKEND == backend


# ============================================================
# 自定义 JSONL 数据集：5 条数学应用题
# ============================================================

CUSTOM_DATASET_JSONL = [
    {
        "id": 1,
        "system": "你是一个数学解题助手。",
        "query": "小明有 5 个苹果，吃了 2 个，还剩几个？",
        "response": "3",
        "answer": "3",
        "category": "arithmetic",
        "difficulty": "easy",
    },
    {
        "id": 2,
        "system": "你是一个数学解题助手。",
        "query": "一本书 200 页，第一天看了 25%，第二天看了 1/4，剩多少页？",
        "response": "第一天看了 200 * 25% = 50 页，第二天看了 200 * 1/4 = 50 页，剩 200 - 50 - 50 = 100 页。",
        "answer": "100",
        "category": "arithmetic",
        "difficulty": "medium",
    },
    {
        "id": 3,
        "system": "你是一个数学解题助手。",
        "query": "一个长方形周长 36cm，长是宽的 2 倍，面积多少？",
        "response": "设宽为 x，则长为 2x，周长 2(x + 2x) = 6x = 36，得 x = 6，宽 6 长 12，面积 72。",
        "answer": "72",
        "category": "geometry",
        "difficulty": "medium",
    },
    {
        "id": 4,
        "system": "你是一个数学解题助手。",
        "query": "鸡兔同笼，共 35 头 94 脚，问鸡几只？",
        "response": "设鸡 x 只，兔 35-x 只，2x + 4(35-x) = 94，2x + 140 - 4x = 94，-2x = -46，x = 23。",
        "answer": "23",
        "category": "combinatorics",
        "difficulty": "hard",
    },
    {
        "id": 5,
        "system": "你是一个数学解题助手。",
        "query": "火车 3 小时行 240km，每小时行多少km？",
        "response": "240 / 3 = 80 km/h。",
        "answer": "80",
        "category": "arithmetic",
        "difficulty": "easy",
    },
]


def _write_dataset_jsonl(path: Path) -> None:
    """把内存数据写为标准 JSONL 文件"""
    with open(path, "w", encoding="utf-8") as f:
        for item in CUSTOM_DATASET_JSONL:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# ============================================================
# Mock 模型 / API
# ============================================================

class MockLocalHFModel:
    """模拟 OpenCompass HF backend 的本地模型：简单 hash + 模板匹配。

    EvalScope 的 mock_llm 走相同路径。
    """

    def __init__(self, name: str = "mock-qwen2-0.5b"):
        self.name = name
        self._call_count = 0

    def chat(self, system: str, query: str) -> str:
        self._call_count += 1
        # 模拟推理：80% 概率给正确答案，20% 给错误答案（模拟模型能力有限）
        time.sleep(random.uniform(0.005, 0.02))  # 模拟推理延迟
        # 找到当前 query 对应的 ground truth
        gt = next((item["answer"] for item in CUSTOM_DATASET_JSONL if item["query"] == query), "0")
        if random.random() < 0.8:
            return f"\\boxed{{{gt}}}"
        else:
            wrong = str(int(gt) + random.choice([-2, -1, 1, 2]))
            return f"\\boxed{{{wrong}}}"


class MockRemoteAPI:
    """模拟 OpenAI 兼容远程 API（vLLM / SGLang / DashScope 通用）"""

    def __init__(self, name: str = "mock-gpt-4o", base_url: str = "https://api.openai.com/v1"):
        self.name = name
        self.base_url = base_url
        self._call_count = 0

    def chat(self, system: str, query: str) -> str:
        self._call_count += 1
        time.sleep(random.uniform(0.05, 0.15))  # 远程 API 慢
        gt = next((item["answer"] for item in CUSTOM_DATASET_JSONL if item["query"] == query), "0")
        # 远程强模型：95% 正确
        if random.random() < 0.95:
            return f"\\boxed{{{gt}}}"
        else:
            return f"\\boxed{{{int(gt) + 1}}}"


def _extract_boxed(text: str) -> str | None:
    """从 \boxed{...} 抽取答案"""
    import re
    m = re.search(r"\\boxed\{([^}]+)\}", text)
    return m.group(1) if m else None


def _normalize(s: str) -> str:
    """归一化答案字符串便于比较"""
    return s.strip().rstrip("。. ").lower()


# ============================================================
# 1. 自定义 JSONL 数据集
# ============================================================

def _validate_opencompass_schema(item: dict[str, Any]) -> list[str]:
    """OpenCompass 风格字段校验（强制 question + answer）"""
    errors = []
    if "query" not in item and "question" not in item:
        errors.append("missing 'query' or 'question'")
    if "answer" not in item:
        errors.append("missing 'answer'")
    return errors


def _validate_evalscope_schema(item: dict[str, Any]) -> list[str]:
    """EvalScope general_qa 模板字段校验（query + response 必填）"""
    errors = []
    if "query" not in item:
        errors.append("missing 'query' (general_qa 模板必填)")
    if "response" not in item:
        errors.append("missing 'response' (用于评测 ground truth)")
    return errors


def demo_custom_dataset_jsonl() -> None:
    """演示自定义 JSONL 数据集：OpenCompass + EvalScope 双风格字段校验"""
    print("=" * 60)
    print("=== 1. 自定义 JSONL 数据集 ===")
    print("=" * 60)
    print(f"数据集路径：{WORK_DIR}/custom_math.jsonl")
    print(f"样本数：{len(CUSTOM_DATASET_JSONL)}")
    print(f"类别分布：{dict((c, sum(1 for x in CUSTOM_DATASET_JSONL if x['category']==c)) for c in set(x['category'] for x in CUSTOM_DATASET_JSONL))}")
    print()

    # 写文件
    path = WORK_DIR / "custom_math.jsonl"
    _write_dataset_jsonl(path)
    print(f"[写入] {path}")
    print()

    # OpenCompass 风格加载（BaseDataset.load 返回 list[dict]）
    print("--- OpenCompass 风格加载（BaseDataset）---")
    if _should_run("opencompass"):
        oc_data = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    oc_data.append(json.loads(line))
        # 字段映射：query -> question，answer 不变
        oc_mapped = [{"question": item["query"], "answer": item["answer"]} for item in oc_data]
        print(f"  加载 {len(oc_mapped)} 条；字段映射 query → question")
        # 校验
        all_ok = True
        for i, item in enumerate(oc_mapped):
            errors = _validate_opencompass_schema(item)
            if errors:
                print(f"  [FAIL] sample {i}: {errors}")
                all_ok = False
        if all_ok:
            print(f"  [OK] 全部 {len(oc_mapped)} 条通过 OpenCompass schema 校验")
        print()

    # EvalScope 风格加载（general_qa 模板：query + response）
    print("--- EvalScope 风格加载（general_qa 模板）---")
    if _should_run("evalscope"):
        es_data = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    es_data.append(json.loads(line))
        # general_qa 直接用 query + response 字段（无需映射）
        all_ok = True
        for i, item in enumerate(es_data):
            errors = _validate_evalscope_schema(item)
            if errors:
                print(f"  [FAIL] sample {i}: {errors}")
                all_ok = False
        if all_ok:
            print(f"  [OK] 全部 {len(es_data)} 条通过 EvalScope general_qa schema 校验")
        # 字段预览
        print(f"  示例字段：{list(es_data[0].keys())}")
        print()

    # 数据集分类汇总
    print("--- 数据集分类汇总 ---")
    by_diff = {}
    for item in CUSTOM_DATASET_JSONL:
        by_diff.setdefault(item["difficulty"], []).append(item["id"])
    for diff, ids in by_diff.items():
        print(f"  {diff}: ids={ids}")
    print()


# ============================================================
# 2. 本地模型评测
# ============================================================

@dataclass
class EvalSample:
    id: int
    question: str
    ground_truth: str
    prediction: str
    extracted: str | None
    correct: bool
    latency_ms: float


@dataclass
class EvalResult:
    backend: str
    model_name: str
    samples: list[EvalSample] = field(default_factory=list)
    accuracy: float = 0.0
    avg_latency_ms: float = 0.0
    total_duration_ms: float = 0.0


def _run_local_eval(model: MockLocalHFModel, dataset: list[dict]) -> EvalResult:
    """本地模型评测（OpenCompass / EvalScope 走相同路径）"""
    result = EvalResult(backend="local", model_name=model.name)
    start = time.time()
    for item in dataset:
        t0 = time.time()
        prediction = model.chat(item["system"], item["query"])
        latency = (time.time() - t0) * 1000
        extracted = _extract_boxed(prediction)
        correct = extracted is not None and _normalize(extracted) == _normalize(item["answer"])
        result.samples.append(EvalSample(
            id=item["id"],
            question=item["query"],
            ground_truth=item["answer"],
            prediction=prediction,
            extracted=extracted,
            correct=correct,
            latency_ms=latency,
        ))
    result.total_duration_ms = (time.time() - start) * 1000
    result.accuracy = sum(1 for s in result.samples if s.correct) / len(result.samples) if result.samples else 0
    result.avg_latency_ms = statistics.mean([s.latency_ms for s in result.samples]) if result.samples else 0
    return result


def demo_local_model_evaluation() -> None:
    """演示本地模型评测：mock HF 模型走 JSONL"""
    print("=" * 60)
    print("=== 2. 本地模型评测（Mock HF / EvalScope mock_llm）===")
    print("=" * 60)
    print()

    # 模拟 OpenCompass HF backend
    if _should_run("opencompass"):
        print("--- OpenCompass HF backend ---")
        # 等价配置（实际用 yaml / python 配置）：
        #   models = [dict(type='hf', abbr='qwen2-0.5b',
        #                  model_path='Qwen/Qwen2-0.5B-Instruct',
        #                  generation_kwargs=dict(max_new_tokens=512))]
        #   datasets = [dict(type='MyCustomDataset', path='data/my_custom.jsonl', ...)]
        #   python run.py configs/eval.py -w outputs/qwen2_hf --max-num-workers 1
        print("  模拟 config：models=[hf_qwen2_0.5b] datasets=[MyCustomDataset]")
        model = MockLocalHFModel(name="hf-mock-qwen2-0.5b")
        result = _run_local_eval(model, CUSTOM_DATASET_JSONL)
        _print_eval_result(result, backend_label="OpenCompass [HF]")
        print()

    # 模拟 EvalScope mock_llm
    if _should_run("evalscope"):
        print("--- EvalScope mock_llm / llm_ckpt ---")
        # 等价配置：
        #   from evalscope import TaskConfig, run_task
        #   run_task(TaskConfig(model='Qwen/Qwen2-0.5B-Instruct',
        #                       datasets=['general_qa'],
        #                       dataset_args={'general_qa': {'local_path': 'custom_eval/math'}}))
        print("  模拟 TaskConfig: model=Qwen/Qwen2-0.5B-Instruct, datasets=[general_qa]")
        model = MockLocalHFModel(name="evalscope-mock-qwen2-0.5b")
        result = _run_local_eval(model, CUSTOM_DATASET_JSONL)
        _print_eval_result(result, backend_label="EvalScope [llm_ckpt]")
        print()


# ============================================================
# 3. 远程 API 模型评测
# ============================================================

def demo_remote_api_evaluation() -> None:
    """演示远程 API 模型评测：mock OpenAI 兼容 API"""
    print("=" * 60)
    print("=== 3. 远程 API 模型评测（Mock OpenAI 兼容 API）===")
    print("=" * 60)
    print()

    # 模拟 OpenCompass OpenAI backend
    if _should_run("opencompass"):
        print("--- OpenCompass OpenAI backend ---")
        # 等价配置（实际用 yaml）：
        #   models = [dict(type='openai', abbr='gpt-4o',
        #                  model='gpt-4o', key=os.environ['OPENAI_API_KEY'],
        #                  api_base='https://api.openai.com/v1')]
        #   python run.py configs/eval_gpt4.py -w outputs/gpt4 --max-num-workers 8
        print("  模拟 config：models=[openai_gpt_4o] --max-num-workers 8")
        api = MockRemoteAPI(name="openai-mock-gpt-4o", base_url="https://api.openai.com/v1")
        result = _run_local_eval(api, CUSTOM_DATASET_JSONL)
        _print_eval_result(result, backend_label="OpenCompass [openai_gpt_4o]")
        print()

    # 模拟 EvalScope openai_api / DashScope / ModelScope Inference
    if _should_run("evalscope"):
        print("--- EvalScope openai_api（vLLM / SGLang / DashScope 通用）---")
        # 等价配置：
        #   evalscope eval --model gpt-4o \
        #     --api-url https://api.openai.com/v1 \
        #     --api-key $OPENAI_API_KEY \
        #     --eval-type openai_api \
        #     --datasets general_qa
        print("  模拟 CLI：--eval-type openai_api --api-url https://api.openai.com/v1")
        api = MockRemoteAPI(name="evalscope-mock-gpt-4o", base_url="https://api.openai.com/v1")
        result = _run_local_eval(api, CUSTOM_DATASET_JSONL)
        _print_eval_result(result, backend_label="EvalScope [openai_api]")
        print()

        print("--- EvalScope openai_api（DashScope 远程）---")
        print("  模拟 CLI：--api-url https://dashscope.aliyuncs.com/compatible-mode/v1")
        api_dash = MockRemoteAPI(name="evalscope-mock-qwen-plus", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        result = _run_local_eval(api_dash, CUSTOM_DATASET_JSONL)
        _print_eval_result(result, backend_label="EvalScope [dashscope_qwen_plus]")
        print()


# ============================================================
# 4. 内置数据集选型（按场景）
# ============================================================

DATASET_SELECTION_TREE = {
    "基座语言理解": {
        "OpenCompass": ["mmlu", "c-eval", "cmmlu", "agieval", "arc", "hellaswag"],
        "EvalScope": ["mmlu", "mmlu_pro", "ceval", "cmmlu", "arc", "hellaswag", "gpqa_diamond", "super_gpqa"],
        "指标": "Accuracy（5-shot ppl 或 0-shot）",
        "样本量建议": "200~2000",
    },
    "Chat / Instruct": {
        "OpenCompass": ["mt_bench", "alpaca_eval", "ifeval"],
        "EvalScope": ["ifeval", "ifbench", "multi_if", "alpaca_eval", "arena_hard", "general_arena"],
        "指标": "LLM-as-Judge WinRate / IF 通过率",
        "样本量建议": "500~800",
    },
    "推理（数学 / 逻辑）": {
        "OpenCompass": ["gsm8k", "math", "bbh", "theoremqa", "cmath"],
        "EvalScope": ["gsm8k", "gsm8k_v", "math_500", "competition_math", "bbh", "drop", "aime24", "aime25"],
        "指标": "Acc（CoT 提取答案后比对）",
        "样本量建议": "全量或 500",
    },
    "代码": {
        "OpenCompass": ["humaneval", "mbpp", "humaneval_plus"],
        "EvalScope": ["humaneval", "humaneval_plus", "mbpp", "mbpp_plus", "live_code_bench", "bigcodebench", "scicode", "swe_bench_verified"],
        "指标": "pass@1 / pass@k（无偏估计器）",
        "样本量建议": "全量（数据集小）",
    },
    "中文能力": {
        "OpenCompass": ["ceval", "cmmlu", "clue_afqmc", "clue_cmrc", "clue_c3", "clue_chid"],
        "EvalScope": ["ceval", "cmmlu", "iquiz", "maritime_bench", "chinese_simpleqa", "gaokao", "maritime_ocr_bench"],
        "指标": "Accuracy",
        "样本量建议": "全量",
    },
    "长文本": {
        "OpenCompass": ["longbench", "l_eval", "leval"],
        "EvalScope": ["longbench_v2", "needle_haystack", "aa_lcr", "docmath", "locomo", "longmemeval"],
        "指标": "子任务 Acc / NIAH 热力图",
        "样本量建议": "长度梯度 + 深度梯度",
    },
    "多模态（VLM）": {
        "OpenCompass": "❌ 纯文本（需配合 VLMEvalKit）",
        "EvalScope": ["mmmu", "mm_bench", "math_vista", "ocr_bench", "ai2d", "hallusion_bench", "mm_star", "chartqa", "docvqa", "mvbench"],
        "指标": "Accuracy（选择题）",
        "样本量建议": "全量或 500",
    },
    "Function Calling / Agent": {
        "OpenCompass": ["toolbench", "agentbench"],
        "EvalScope": ["bfcl_v3", "bfcl_v4", "acebench", "tau_bench", "tau2_bench", "tir_bench", "gaia", "terminal_bench_v2", "mcp_atlas", "general_fc"],
        "指标": "Acc / 任务成功率（Docker 沙箱）",
        "样本量建议": "全量",
    },
    "安全 / 对齐": {
        "OpenCompass": "通过自定义数据集接入（ToxiGen / BeaverTails）",
        "EvalScope": ["halueval", "bfcl_v4"],  # EvalScope 安全数据集较少，需自定义
        "指标": "Toxicity Rate / 攻击成功率",
        "样本量建议": "全量",
    },
}


def demo_built_in_dataset_selection() -> None:
    """演示「按场景选数据集」决策树"""
    print("=" * 60)
    print("=== 4. 内置数据集选型（按场景）===")
    print("=" * 60)
    print()
    print("决策树：场景 → 推荐框架 + 数据集 + 指标 + 样本量")
    print()
    for scene, info in DATASET_SELECTION_TREE.items():
        print(f"### {scene}")
        oc = info["OpenCompass"]
        es = info["EvalScope"]
        oc_str = oc if isinstance(oc, str) else ", ".join(oc)
        es_str = es if isinstance(es, str) else ", ".join(es)
        print(f"  OpenCompass: {oc_str}")
        print(f"  EvalScope:   {es_str}")
        print(f"  指标：{info['指标']}")
        print(f"  样本量建议：{info['样本量建议']}")
        print()

    # 最小可用组合建议
    print("--- 最小可用组合（个人 / 中小团队发版）---")
    print("  基座快筛：MMLU + HellaSwag + ARC + GSM8K")
    print("  Instruct 评测：IFEval + MT-Bench（自动化 + LLM-as-Judge）+ 内部 Badcase 人工抽检 ~50 条")
    print("  代码：HumanEval pass@1 + LiveCodeBench 最近 release")
    print("  中文：C-Eval + C-MMLU")
    print()


# ============================================================
# 5. 评测报告解读
# ============================================================

def _gen_summary_csv(result: EvalResult) -> str:
    """模拟 OpenCompass summary_*.csv 输出"""
    lines = ["dataset,model,accuracy,avg_latency_ms,total_duration_ms,sample_count"]
    lines.append(
        f"custom_math,{result.model_name},{result.accuracy:.4f},{result.avg_latency_ms:.2f},{result.total_duration_ms:.2f},{len(result.samples)}"
    )
    return "\n".join(lines)


def _gen_reports_json(result: EvalResult) -> str:
    """模拟 EvalScope reports/*.json 输出"""
    # 子指标细分（按 category）
    by_cat_correct = {}
    by_cat_total = {}
    by_difficulty_correct = {}
    by_difficulty_total = {}
    bad_cases = []
    for item, sample in zip(CUSTOM_DATASET_JSONL, result.samples):
        cat = item["category"]
        diff = item["difficulty"]
        by_cat_total[cat] = by_cat_total.get(cat, 0) + 1
        by_difficulty_total[diff] = by_difficulty_total.get(diff, 0) + 1
        if sample.correct:
            by_cat_correct[cat] = by_cat_correct.get(cat, 0) + 1
            by_difficulty_correct[diff] = by_difficulty_correct.get(diff, 0) + 1
        else:
            bad_cases.append({
                "id": sample.id,
                "question": sample.question,
                "ground_truth": sample.ground_truth,
                "extracted_answer": sample.extracted,
                "prediction": sample.prediction,
            })
    # 模拟 3 次跑求置信区间
    ci_scores = [result.accuracy + random.uniform(-0.05, 0.05) for _ in range(3)]
    ci_scores = [max(0, min(1, s)) for s in ci_scores]
    return json.dumps({
        "model": result.model_name,
        "dataset": "custom_math",
        "overall_accuracy": round(result.accuracy, 4),
        "avg_latency_ms": round(result.avg_latency_ms, 2),
        "total_duration_ms": round(result.total_duration_ms, 2),
        "sample_count": len(result.samples),
        "category_breakdown": {
            cat: {"acc": round(by_cat_correct.get(cat, 0) / by_cat_total[cat], 4), "count": by_cat_total[cat]}
            for cat in by_cat_total
        },
        "difficulty_breakdown": {
            diff: {"acc": round(by_difficulty_correct.get(diff, 0) / by_difficulty_total[diff], 4), "count": by_difficulty_total[diff]}
            for diff in by_difficulty_total
        },
        "confidence_interval_95": [
            round(statistics.mean(ci_scores) - 1.96 * statistics.stdev(ci_scores), 4),
            round(statistics.mean(ci_scores) + 1.96 * statistics.stdev(ci_scores), 4),
        ],
        "bad_cases_sample": bad_cases[:3],
    }, ensure_ascii=False, indent=2)


def _print_eval_result(result: EvalResult, backend_label: str) -> None:
    """统一打印评测结果 + 双框架报告格式"""
    print(f"  [{backend_label}] 样本数={len(result.samples)}, accuracy={result.accuracy:.2%}, "
          f"avg_latency={result.avg_latency_ms:.1f}ms, total={result.total_duration_ms:.1f}ms")
    print()
    print(f"  --- OpenCompass 风格 summary_*.csv ---")
    print(_gen_summary_csv(result))
    print()
    print(f"  --- EvalScope 风格 reports/*.json ---")
    print(_gen_reports_json(result))


def demo_metrics_report_reading() -> None:
    """演示评测报告解读：OpenCompass csv + EvalScope json 双格式"""
    print("=" * 60)
    print("=== 5. 评测报告解读（OpenCompass csv + EvalScope json）===")
    print("=" * 60)
    print()

    # 跑一次评测生成报告
    api = MockRemoteAPI(name="report-mock-gpt-4o")
    result = _run_local_eval(api, CUSTOM_DATASET_JSONL)

    print("[关键指标解读]")
    print(f"  总分（overall accuracy）：{result.accuracy:.2%}")
    print(f"  平均延迟：{result.avg_latency_ms:.1f} ms/样本")
    print(f"  端到端耗时：{result.total_duration_ms:.1f} ms")
    print()

    # 按 category / difficulty 分桶
    print("[子维度分数 — 按 category 分桶]")
    by_cat = {}
    for item, sample in zip(CUSTOM_DATASET_JSONL, result.samples):
        cat = item["category"]
        by_cat.setdefault(cat, []).append(sample.correct)
    for cat, results in by_cat.items():
        acc = sum(results) / len(results)
        print(f"  {cat}: {acc:.2%} ({sum(results)}/{len(results)})")
    print()

    print("[子维度分数 — 按 difficulty 分桶]")
    by_diff = {}
    for item, sample in zip(CUSTOM_DATASET_JSONL, result.samples):
        diff = item["difficulty"]
        by_diff.setdefault(diff, []).append(sample.correct)
    for diff, results in by_diff.items():
        acc = sum(results) / len(results)
        print(f"  {diff}: {acc:.2%} ({sum(results)}/{len(results)})")
    print()

    # 置信区间
    print("[置信区间 — 模拟 3 次跑]")
    ci_scores = [result.accuracy + random.uniform(-0.05, 0.05) for _ in range(3)]
    ci_scores = [max(0, min(1, s)) for s in ci_scores]
    ci_low = statistics.mean(ci_scores) - 1.96 * statistics.stdev(ci_scores)
    ci_high = statistics.mean(ci_scores) + 1.96 * statistics.stdev(ci_scores)
    print(f"  95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
    print()

    # Bad case 抽样
    print("[Bad Case 抽样 — 失败样本前 3 条]")
    bad = [s for s in result.samples if not s.correct]
    for s in bad[:3]:
        print(f"  id={s.id}: Q={s.question[:30]}... | GT={s.ground_truth} | pred={s.prediction}")
    if not bad:
        print("  （本次随机跑无 bad case）")
    print()

    # 完整报告格式
    print("[完整报告格式对比]")
    print()
    print(f"--- OpenCompass summary_*.csv (单一表格) ---")
    print(_gen_summary_csv(result))
    print()
    print(f"--- EvalScope reports/*.json (多维度 JSON) ---")
    print(_gen_reports_json(result))
    print()


# ============================================================
# 入口
# ============================================================

DEMOS = {
    "custom_dataset": ("自定义 JSONL 数据集（OpenCompass + EvalScope 双风格字段校验）", demo_custom_dataset_jsonl),
    "local_eval": ("本地模型评测（mock HF / EvalScope mock_llm）", demo_local_model_evaluation),
    "remote_eval": ("远程 API 模型评测（mock OpenAI 兼容 API）", demo_remote_api_evaluation),
    "dataset_selection": ("内置数据集选型（按场景决策树）", demo_built_in_dataset_selection),
    "metrics_report": ("评测报告解读（OpenCompass csv + EvalScope json）", demo_metrics_report_reading),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenCompass + EvalScope 双框架 Mock 演示")
    parser.add_argument("--demo", choices=list(DEMOS.keys()) + ["all"], default="all",
                        help="指定 demo（默认 all 跑全部）")
    args = parser.parse_args()

    if EVAL_BACKEND not in VALID_BACKENDS:
        print(f"[WARN] EVAL_BACKEND={EVAL_BACKEND} 无效，应为 {VALID_BACKENDS}；fallback 到 both", file=sys.stderr)
        global_eval_backend = "both"
    else:
        global_eval_backend = EVAL_BACKEND

    print(f"# OpenCompass + EvalScope 双框架 Mock 演示")
    print(f"# EVAL_BACKEND={global_eval_backend}")
    print(f"# WORK_DIR={WORK_DIR}")
    print(f"# 5 个 demo：自定义 JSONL / 本地模型 / 远程 API / 数据集选型 / 报告解读")
    print()

    if args.demo == "all":
        for name in DEMOS:
            DEMOS[name][1]()
    else:
        DEMOS[args.demo][1]()
    return 0

    print(f"# OpenCompass + EvalScope 双框架 Mock 演示")
    print(f"# EVAL_BACKEND={EVAL_BACKEND}")
    print(f"# WORK_DIR={WORK_DIR}")
    print(f"# 5 个 demo：自定义 JSONL / 本地模型 / 远程 API / 数据集选型 / 报告解读")
    print()

    if args.demo == "all":
        for name in DEMOS:
            DEMOS[name][1]()
    else:
        DEMOS[args.demo][1]()
    return 0


if __name__ == "__main__":
    sys.exit(main())