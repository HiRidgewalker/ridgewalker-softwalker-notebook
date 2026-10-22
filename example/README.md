# example

本目录存放知识库笔记中涉及的可运行演示代码。每个子目录是一个独立项目，各自维护依赖声明，可单独运行；对应说明见 `hub/` 下的总览笔记，笔记中通过 git 远程链接引用。

## 目录结构

| 目录 | 内容 |
|---|---|
| `agent/` | mini-agent 抽象基类演示 |
| `ai-assistant/` | HuggingFace pipeline 推理 |
| `cicd/` | Jenkinsfile、K8s manifest、Harbor、Helm values |
| `css/` | 盒模型 / Flex / 单位演示 |
| `db/` | SQLite + MySQL + PostgreSQL + MongoDB + Redis |
| `db-design/` | 慢查询埋点、Alembic 索引、Redis key 模板 |
| `devops/` | 分支策略、GitOps、Terraform 骨架 |
| `docker/` | Dockerfile、Compose、数据卷 |
| `gateway/` | FastAPI 网关 + JWT 鉴权 + Casbin 权限 |
| `go/` | Go 五个基础 demo，各自独立 `go.mod` |
| `go-sdk/` | Go 安装脚本 |
| `js-demo/` | JavaScript 六级演示 |
| `llm-demo/` | tokenization、推理服务、评测、RAG |
| `mq/` | RabbitMQ + Kafka |
| `nextjs-demo/` | Next.js 四例 |
| `python/` | Python 语法、模块、框架、异步演示 |
| `pytorch-demo/` | Tensor 与 nn.Module 训练 |
| `react/` | hooks / router / zustand |
| `typescript-types/` | TS 类型标注 |
| `vector-db/` | Milvus / Qdrant / zvec |
| `ws/` | WebSocket 服务端与三种客户端 |

## 约定

- 每个子目录是独立项目，依赖声明（`requirements.txt` / `package.json` / `go.mod`）跟随项目
- 虚拟环境与构建产物（`.venv/`、`node_modules/`、`.next/`、`__pycache__/`）不入库
- demo 顶部 docstring 说明知识点与运行方式
