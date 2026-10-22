"""HuggingFace Transformers pipeline 最小推理演示

运行：workspace/.venv/bin/python pipeline_demo.py

涵盖的知识点：
1. pipeline 一行推理（情感分析、文本生成）
2. 显式指定模型
3. AutoTokenizer + AutoModel 的最简加载

注意：
- 首次运行会下载模型（情感分析约 250MB，文本生成 gpt2 约 500MB）
- 需要联网；如已下载会自动复用缓存
- 演示用最小模型（distilbert / gpt2），跑得快、内存占用小
"""

from transformers import pipeline


def demo_sentiment():
    """情感分析：默认模型 distilbert-base-uncased-finetuned-sst-2-english"""
    print("=" * 60)
    print("[1] 情感分析（pipeline('sentiment-analysis')）")
    print("=" * 60)
    classifier = pipeline("sentiment-analysis")
    texts = [
        "I love using HuggingFace Transformers!",
        "This is the worst experience I've ever had.",
    ]
    for t in texts:
        print(f"  text: {t}")
        print(f"  -> {classifier(t)}")


def demo_generation():
    """文本生成：默认模型 gpt2"""
    print("=" * 60)
    print("[2] 文本生成（pipeline('text-generation')）")
    print("=" * 60)
    generator = pipeline("text-generation", model="gpt2")
    out = generator(
        "Once upon a time in a small village",
        max_new_tokens=30,
        num_return_sequences=1,
        do_sample=True,
        top_k=50,
    )
    print(f"  -> {out[0]['generated_text']}")


def demo_explicit_load():
    """显式加载：AutoTokenizer + AutoModelForCausalLM"""
    print("=" * 60)
    print("[3] 显式加载（AutoTokenizer + AutoModelForCausalLM）")
    print("=" * 60)
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    inputs = tokenizer("Hello, my name is", return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=20, do_sample=False)
    print(f"  prompt: Hello, my name is")
    print(f"  -> {tokenizer.decode(outputs[0])}")


if __name__ == "__main__":
    demo_sentiment()
    demo_generation()
    demo_explicit_load()