# 03_eval_frameworks · OpenCompass + EvalScope 双框架 Mock 演示

演示 [[OpenCompass笔记]] / [[EvalScope笔记]] / [[LLM评测框架对比笔记]] 中**评测流程侧**的可执行部分，**全程不联网、不需要 GPU、不需要真实模型或 API**。

## Demo 列表

| Demo | 内容 | 是否需要真实服务 |
|---|---|---|
| 1. `custom_dataset` | 自定义 JSONL 数据集（5 条数学应用题）；OpenCompass BaseDataset 风格 + EvalScope general_qa 风格的字段校验 | 不需要 |
| 2. `local_eval` | 本地模型评测：mock HF 模型 + mock EvalScope `llm_ckpt`；输出每条样本的预测 + 准确率 + 延迟 | 不需要 |
| 3. `remote_eval` | 远程 API 模型评测：mock OpenAI / DashScope 兼容 API；模拟 `--max-num-workers` 并发 | 不需要 |
| 4. `dataset_selection` | 内置数据集选型决策树（基座 / Chat / 推理 / 代码 / 中文 / 长文本 / 多模态 / 安全 / Agent 九类） | 不需要 |
| 5. `metrics_report` | 评测报告解读：OpenCompass `summary_*.csv` + EvalScope `reports/*.json` 双格式对比，含子维度分桶 + 置信区间 + bad case 抽样 | 不需要 |

## 涵盖知识点

- **OpenCompass**：Config-driven 评测、`run.py` + `--max-num-workers`、HF / LMDeploy / vLLM backend、OpenAI API 模型
- **EvalScope**：`evalscope eval` 完整 CLI、4 种内置模板（`general_mcq` / `general_qa` / `general_fc` / `general_arena`）、CollectionSchema 权重采样、`--judge-strategy` 四种
- **生产评测流程**：7 步流水线（模型准备 → 数据集准备 → 评测执行 → 结果汇总 → 报告产出 → 对比分析 → 归档回溯）
- **报告指标**：总分、子维度分（category / difficulty 分桶）、置信区间、bad case 抽样、延迟、耗时
- **选型决策树**：按场景给推荐（学术榜单用 OpenCompass、生产一体化用 EvalScope）

## 安装与运行

```bash
# 装依赖（标准库为主，无需第三方包）
# 如需数据校验 pydantic 可选：uv pip install --python .venv/bin/python pydantic

# 跑全部 demo（mock 模式，无需任何外部服务）
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py

# 跑单个 demo
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py --demo custom_dataset
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py --demo local_eval
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py --demo remote_eval
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py --demo dataset_selection
.venv/bin/python example/llm-demo/03_eval_frameworks/main.py --demo metrics_report

# 仅跑 OpenCompass 视角
EVAL_BACKEND=opencompass .venv/bin/python example/llm-demo/03_eval_frameworks/main.py

# 仅跑 EvalScope 视角
EVAL_BACKEND=evalscope .venv/bin/python example/llm-demo/03_eval_frameworks/main.py
```

环境变量：

| 变量 | 默认 | 说明 |
|---|---|---|
| `EVAL_BACKEND` | `both` | 取值 `opencompass` / `evalscope` / `both`，控制哪些 demo 跑 |
| `OPENAI_API_KEY` | `mock` | mock 模式下不影响行为 |
| `EVAL_WORK_DIR` | `/tmp/evalscope_demo` | 写 JSONL 数据集的目录 |

## 输出示例（节选）

```text
# OpenCompass + EvalScope 双框架 Mock 演示
# EVAL_BACKEND=both
# WORK_DIR=/tmp/evalscope_demo

=== 1. 自定义 JSONL 数据集 ===
数据集路径：/tmp/evalscope_demo/custom_math.jsonl
样本数：5
类别分布：{'arithmetic': 3, 'geometry': 1, 'combinatorics': 1}

--- OpenCompass 风格加载（BaseDataset）---
  加载 5 条；字段映射 query → question
  [OK] 全部 5 条通过 OpenCompass schema 校验

--- EvalScope 风格加载（general_qa 模板）---
  [OK] 全部 5 条通过 EvalScope general_qa schema 校验
  示例字段：['id', 'system', 'query', 'response', 'answer', 'category', 'difficulty']

=== 2. 本地模型评测（Mock HF / EvalScope mock_llm）===
[OpenCompass HF backend] 样本数=5, accuracy=80.00%, avg_latency=12.3ms, total=63.2ms
[EvalScope llm_ckpt] 样本数=5, accuracy=80.00%, avg_latency=11.8ms, total=59.5ms

=== 3. 远程 API 模型评测（Mock OpenAI 兼容 API）===
[OpenCompass openai_gpt_4o] 样本数=5, accuracy=100.00%, avg_latency=98.4ms, total=512.3ms
[EvalScope openai_api] 样本数=5, accuracy=100.00%, avg_latency=102.7ms, total=525.1ms
[EvalScope dashscope_qwen_plus] 样本数=5, accuracy=100.00%, avg_latency=88.5ms, total=449.2ms

=== 5. 评测报告解读 ===
[关键指标解读]
  总分（overall accuracy）：80.00%
  平均延迟：12.3 ms/样本
  端到端耗时：63.2 ms

[子维度分数 — 按 category 分桶]
  arithmetic: 100.00% (3/3)
  geometry: 0.00% (0/1)
  combinatorics: 100.00% (1/1)

[置信区间 — 模拟 3 次跑]
  95% CI: [0.6500, 0.9500]

--- OpenCompass summary_*.csv (单一表格) ---
dataset,model,accuracy,avg_latency_ms,total_duration_ms,sample_count
custom_math,report-mock-gpt-4o,0.8000,12.30,63.20,5

--- EvalScope reports/*.json (多维度 JSON) ---
{
  "model": "report-mock-gpt-4o",
  "dataset": "custom_math",
  "overall_accuracy": 0.8,
  ...
  "category_breakdown": {
    "arithmetic": {"acc": 1.0, "count": 3},
    "geometry": {"acc": 0.0, "count": 1},
    "combinatorics": {"acc": 1.0, "count": 1}
  },
  ...
  "confidence_interval_95": [0.65, 0.95],
  "bad_cases_sample": [...]
}
```

## 关键观察点

1. **OpenCompass vs EvalScope 的定位差异**：OpenCompass 是 Config-driven（yaml/python 配置驱动），适合学术榜单（C-Eval / SuperBench）；EvalScope 是 TaskConfig 对象 + 4 种 eval-backend，适合生产一体化（评测 + 压测 + Arena + 可视化）。
2. **OpenAI 兼容是事实标准**：OpenCompass 的 `type='openai'` 和 EvalScope 的 `--eval-type openai_api` 都能接 vLLM / SGLang / DashScope 起的服务。同一份 mock API 代码可同时被两份框架调用。
3. **报告格式互补**：OpenCompass `summary_*.csv` 是单一表格（适合 CI 解析），EvalScope `reports/*.json` 是多维度 JSON（自带子指标分桶 + 置信区间 + bad case）。生产建议**两套都跑**：OpenCompass 跑学术对齐，EvalScope 跑工程对比。
4. **置信区间需要多次跑**：单次评测不可信。生产报告应包含 N=3 次跑的标准差 / 95% CI（参考 LMSYS Chatbot Arena 的 BT 模型风格）。
5. **子指标分桶是定位 bug 的关键**：本次 demo 中 geometry 类目 0% 准确率，立即定位模型在几何推理上的弱项；按 difficulty 分桶可定位简单/难题上的表现差异。
6. **Bad case 抽样是回归测试的输入**：每数据集抽 5~10 条失败样本，固化到内部回归集，下次发版必跑。
7. **数据集选型按场景决策**：基座 vs Chat vs 推理 vs 代码 vs 中文 vs 长文本 vs 多模态 vs 安全 vs Agent 九类，每类对应不同的数据集 + 评测方式（gen / ppl / LLM-as-Judge）。**不要全跑，按场景选 5~8 个数据集组合**。
8. **EvalScope 的 CollectionSchema 是核心创新**：通过 `WeightedSampler` 把多数据集按业务权重混合成单一 JSONL，一次评测出多维分数；OpenCompass 没有这个能力，需手动配多个数据集。

## 对应笔记

- [[OpenCompass笔记]] — 完整 OpenCompass v0.5.3 笔记（架构 / 本地 / 远程 / 60+ 数据集 / 自定义 / 指标 / 生产特性）
- [[EvalScope笔记]] — 完整 EvalScope v1.8.1 笔记（四大后端 / 本地 / 远程 / 191 benchmark / CollectionSchema / Arena / 压测 / service）
- [[LLM评测框架对比笔记]] — 选型决策树 + 10 维度差异表 + 7 步标准生产流程 + 8 项报告指标 + 6 类踩坑 + 业界实践