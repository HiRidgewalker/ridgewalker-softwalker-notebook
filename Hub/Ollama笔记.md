# Ollama 笔记

> 由旧稿重新整理版本，从零补充了 Ollama 的定位、特性、命令速查、API 接入、Modelfile。旧稿目录已清理，当前以本文为准。

## 一、定位

**Ollama** 是一个开源的**本地大模型运行工具**，主打"一条命令跑起开源 LLM"。无需自己处理 Python 环境、CUDA、模型权重转换，跨 macOS / Linux / Windows 提供一致体验。

与 [[HuggingFaceTransformers笔记]] 的区别：

- Transformers：库级别，偏开发 / 微调 / 研究
- Ollama：CLI + 服务级别，偏本地快速体验 / 个人开发 / 小规模部署

## 二、核心特性

- **极简命令**：`ollama run llama3` 直接对话
- **模型自动管理**：下载、缓存、删除一体化
- **自动 GPU 加速**：检测到 NVIDIA / Apple Silicon / ROCm 自动启用
- **REST API**：本地起 `http://localhost:11434`，可被任意应用调用
- **OpenAI 兼容端点**：可直接替换 OpenAI SDK 的 `base_url`
- **Modelfile**：自定义模型配置（系统提示词、参数、模板）
- **模型库丰富**：Llama / Qwen / Mistral / Gemma / DeepSeek / Phi 等

## 三、常用命令速查

| 命令 | 功能 |
| --- | --- |
| `ollama pull <model>` | 下载模型（如 `ollama pull llama3`） |
| `ollama run <model>` | 进入对话模式；带 prompt 可一次性问（如 `ollama run llama3 "hello"`） |
| `ollama list` | 列出本地已有模型 |
| `ollama ps` | 列出当前加载到内存的模型 |
| `ollama show <model>` | 查看模型详情（参数、大小、模板等） |
| `ollama rm <model>` | 删除本地模型 |
| `ollama cp <src> <dst>` | 复制模型到新名字 |
| `ollama serve` | 启动 API 服务（默认 `127.0.0.1:11434`） |

## 四、快速开始

```shell
# 1. 安装（macOS 一行；Linux 见官方安装脚本）
brew install ollama

# 2. 拉取并运行一个模型
ollama run llama3

# 3. 一次性提问
ollama run qwen2 "用一句话解释什么是 MCP"

# 4. 启动服务（默认前台运行；生产用 systemd / launchd）
ollama serve
```

## 五、API 接入

### 5.1 REST API

```shell
# 生成
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?"
}'

# 对话（多轮）
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}'
```

### 5.2 OpenAI 兼容端点

Ollama 提供 `/v1/chat/completions` 等端点，可以直接替换 OpenAI SDK 的 base URL：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # 占位即可
)

resp = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "hello"}],
)
print(resp.choices[0].message.content)
```

> 这让本地模型可以**零成本替换 OpenAI**，配合 LangChain / LlamaIndex / AutoGen 等框架无感切换。

## 六、Modelfile 简介

通过 `Modelfile` 自定义模型：

```dockerfile
FROM llama3

# 设置系统提示词
SYSTEM """
你是一个严谨的中文技术助手，回答时引用具体来源。
"""

# 调整推理参数
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
```

构建并运行：

```shell
ollama create my-assistant -f Modelfile
ollama run my-assistant
```

## 七、典型使用场景

| 场景 | 适合度 |
| --- | --- |
| 本地快速体验开源模型 | ⭐⭐⭐⭐⭐ |
| 个人开发 / 隐私数据处理 | ⭐⭐⭐⭐⭐ |
| 配合 OpenAI 兼容 SDK 替代线上 API | ⭐⭐⭐⭐⭐ |
| 小规模生产部署（个人 / 小团队） | ⭐⭐⭐⭐ |
| 大规模高并发生产推理 | ⭐⭐（建议用 VLLM） |
| 模型微调 / 训练 | ❌（用 Transformers） |

## 八、资源

- [官方模型搜索](https://ollama.com/search)
- [datawhale 动手学 Ollama（中文教程）](https://datawhalechina.github.io/handy-ollama/)
- [GitHub 仓库](https://github.com/ollama/ollama)
- [官方文档](https://github.com/ollama/ollama/tree/main/docs)

## 九、相关笔记

- 模型库 / 训练库：[[HuggingFaceTransformers笔记]]
- 高吞吐推理：[[02_推理部署笔记]]
- LLM 基础：[[01_大语言模型笔记]]
- Agent 系统结构：[[Agent总览笔记]]