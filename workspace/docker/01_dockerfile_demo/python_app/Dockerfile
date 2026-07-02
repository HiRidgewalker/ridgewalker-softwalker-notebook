# syntax=docker/dockerfile:1.7
# 演示：Python 多阶段构建 + 非 root 用户
# 对应 Hub/04_Dockerfile笔记.md 中的"实战：Python 应用"

# ========== 阶段 1：装依赖到用户目录 ==========
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
# --user 把依赖装到 /root/.local，后续拷走
RUN pip install --user -r requirements.txt

# ========== 阶段 2：运行镜像 ==========
FROM python:3.12-slim

# 用 TZ 变量 + 装 tzdata，简单实现时区（镜像小巧的话可去掉）
ENV PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# 建非 root 用户
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app.py .

USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]
