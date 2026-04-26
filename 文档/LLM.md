# llm知识点
## 1. Zero-shot Learning（零样本学习）

**定义：**  
不给模型任何示例，只通过**任务描述（instruction）**让模型完成任务。

**特点：**

- 不提供输入→输出的样例
    
- 完全依赖模型预训练中学到的泛化能力
    
- prompt 通常只有「任务说明 + 输入」
    

**示例：**

```text
任务：判断情感（正面 / 负面）
文本：这个产品真的很好用

输出：
```

模型直接推断：

```text
正面
```

**本质：**

> 模型基于语义理解 + 已有知识进行“直接推理”

## 2. Few-shot Learning（少样本学习）

**定义：**  
在 prompt 中提供**少量示例（input → output）**，再让模型对新输入进行推理。

**特点：**

- 提供 1~K 个示例（通常 1~10 个）
    
- 模型通过“上下文学习（in-context learning）”模仿模式
    
- prompt = 示例 + 新输入
    

**示例：**

```text
任务：判断情感

文本：这个产品很好用 → 正面
文本：体验很差 → 负面
文本：质量不错 → 正面

文本：物流太慢 →
```

模型输出：

```text
负面
```

**本质：**

> 模型通过上下文中的“示范”，学习任务格式和决策边界

---

## 核心对比

|维度|Zero-shot|Few-shot|
|---|---|---|
|是否给示例|❌ 不给|✅ 给少量|
|依赖能力|预训练泛化能力|上下文学习能力|
|prompt复杂度|低|较高|
|稳定性|较不稳定|更稳定|
|可控性|弱|强|

---

## 关键补充（你这个背景建议重点理解）

### 1. 为什么 few-shot 有用？

因为 LLM 本质是：

> **next token prediction + 模式拟合器**

few-shot 等于在 prompt 里“临时训练”模型，让它：

- 学任务格式
    
- 学 decision boundary
    
- 学输出风格
    

---

### 2. 和 Fine-tuning 的区别

|方式|是否改模型参数|成本|场景|
|---|---|---|---|
|Zero-shot|❌|低|简单任务|
|Few-shot|❌|低|提升效果|
|Fine-tune|✅|高|专用能力|

# LLM本地部署所需显存估算
- [估算大模型所需显存_人工智能平台 PAI(PAI)-阿里云帮助中心](https://help.aliyun.com/zh/pai/getting-started/estimation-of-the-required-video-memory-for-the-model#7a013a3d617zj)
