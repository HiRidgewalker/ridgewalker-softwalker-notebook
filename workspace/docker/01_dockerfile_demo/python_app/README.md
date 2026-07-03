# Python 应用 Dockerfile Demo

对应：[[04_Dockerfile笔记]] 中的完整 Python 示例。

## 文件

- `Dockerfile`：两阶段。`builder` 阶段用 pip 装依赖到 `/root/.local`；最终镜像仅基于 `python:3.12-slim` + 已装好的依赖。
- `app.py`：Flask 应用，带 `/`（返回 JSON）和 `/health` 健康检查。
- `requirements.txt`：依赖（这里只是 Flask）。

## 运行

```bash
cd 01_dockerfile_demo/python_app

docker build -t myapp-py:1.0 .
docker images myapp-py:1.0           # 对比 python:3.12 的大小

docker run -d --name pyapp -p 5000:5000 -e TZ=Asia/Shanghai myapp-py:1.0
curl http://localhost:5000/
curl http://localhost:5000/health    # 输出 ok
docker logs pyapp                    # 看启动日志

# 看健康状态
docker inspect --format '{{.State.Health.Status}}' pyapp
# → "healthy"（若干秒后）

docker rm -f pyapp
docker rmi myapp-py:1.0
```

## 关键点

- 多阶段：**编译期镜像** → **`pip install`** 在 builder → 只拷 `/root/.local` 到 runtime
- `USER appuser`：非 root 运行
- `HEALTHCHECK`：`docker ps` 显示 `(healthy)`
- `PYTHONUNBUFFERED=1`：避免 `docker logs` 看不到输出
