# 个人知识库目录

> 本知识库的统一总导航。
> 一级模块按"知识域"划分，二级按"子领域/工具栈"划分，三级按"具体技术/笔记"划分。

## 添加新模块的方法

- **一级模块**：当一个主题无法被现有模块合理收纳，且预计会持续增加笔记时新建。命名用实体名词或概念，不用"其他/杂项"等模糊词。
- **二级模块**：当一级模块下笔记超过 8~10 个且能聚成清晰子主题时新建。命名要求具体。
- **三级模块**：仅在二级模块内笔记明显需要再细分时使用，命名直接对应具体技术或笔记名。

---
# 常用



---
## 1. 编程语言

### Python

基础语法：

- [[Python基础]]
- [[Python异步编程（asyncio）]]
- [[Jupyter笔记]]

虚拟环境：

- [[UV笔记]]
- [[Anaconda笔记]]

Web 框架：

- [[FastAPI笔记]]
- [[Django笔记]]

类型校验：

- [[Pydantic笔记]]

异步任务：

- [[Celery笔记]]

项目实战：

- [[Django+FastAPI秒杀系统课程]]

### Golang

- [[01_Go笔记]]
- [[02_Go基础语法笔记]]
- [[03_Go复合类型笔记]]
- [[04_Go函数笔记]]
- [[05_Go面向对象笔记]]
- [[06_Go包与工程笔记]]
- [[07_Go常见问题笔记]]

---

## 2. 前端开发

### 基础三件套

CSS：

- [[01_CSS笔记]]
- [[02_CSS选择器与继承笔记]]
- [[03_CSS盒模型笔记]]
- [[04_CSS布局笔记]]
- [[05_CSS单位与值笔记]]
- [[06_CSS常见问题笔记]]
- 配套 demo：[workspace/css/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/css)（01_box_model / 02_flex / 03_units）

前端工程：

- [[前端工程笔记]]（静态资源放 public 还是 src/assets 等）


JavaScript：

- [[01_JavaScript笔记]] — 基础与 ES6+（语法 / 数据类型 / 运算符 / 数组方法 / 解构 / 模板字符串 / Set Map）
- [[02_JavaScript进阶笔记]] — 作用域 / 闭包 / this / 构造函数 / 原型链 / class
- [[03_JavaScript异步与模块笔记]] — 回调函数 / Promise / async-await / 事件循环 + ES Module
- 配套 demo：[workspace/js-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/js-demo)（01_basics / 02_es6 / 03_scope_closure / 04_oop / 05_async / 06_module）

### TypeScript

- [[TypeScript类型标注与React类型笔记]]

### React 生态

- [[01_React笔记]]
- [[02_React Hooks笔记]]
- [[03_Zustand状态管理笔记]]
- [[04_React Router笔记]]

### Next.js

总览与基础：

- [[01_Next.js 笔记]]
- [[02_Next.js 路由笔记]]
- [[03_Next.js Server与Client组件笔记]]

数据与渲染：

- [[04_Next.js 数据获取与Server Actions笔记]]
- [[05_Next.js 渲染模式笔记]]

速查与 FAQ：

- [[06_Next.js 常见问题笔记]]

配套 demo：

- [workspace/nextjs-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/nextjs-demo)（01_routing_basic / 02_server_client_components / 03_data_fetching / 04_server_actions）

---

## 3. 后端开发与中间件

### 数据库

关系型：

- [[01_MySQL笔记]]
- [[02_PostgreSQL笔记]]
- [[03_SQLite笔记]]
- [[04_关系型数据库对比与选型笔记]]
- 配套 demo：[workspace/db/sql-tools-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/db/sql-tools-demo)（sqlite3 + pymysql + psycopg 三种驱动最小示例）

NoSQL：

- [[01_MongoDB笔记]]
- [[02_Redis笔记]]
- 配套 demo：[workspace/db/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/db)（含 sql-tools-demo + mongodb_demo + redis_demo）

向量数据库：

- [[01_Milvus笔记]]
- [[02_Qdrant笔记]]
- [[03_zvec笔记]]
- 配套 demo：[workspace/vector-db/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/vector-db)（含 docker-compose.yml + milvus_demo + qdrant_demo + zvec_demo）

设计相关：

- [[01_数据库设计相关笔记]]
- 配套 demo：[workspace/db-design/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/db-design)（慢查询埋点 + Alembic 加索引 + Redis key 模板）

### 消息队列

- [[01_RabbitMQ笔记]]
- [[02_Kafka笔记]]
- [[03_消息队列对比与选型笔记]]
- 配套 demo：[workspace/mq/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/mq)（dev/prod 双 profile docker-compose + RabbitMQ + Kafka 生产配置示例）

### 进程与服务管理

- [[01_进程与服务管理笔记]]

---

## 4. AI 与机器学习

### 机器学习基础

概念与原理：

- [[01_ML与DL基础概念笔记]]

PyTorch：

- [[02_PyTorch笔记]]

环境安装：

- [[03_深度学习环境安装笔记]]

配套 demo：

- [workspace/pytorch-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/pytorch-demo)（01_tensor_and_autograd / 02_nn_module_training）
### 大语言模型

模型本身：

- [[01_大语言模型笔记]]
- 配套 demo：[workspace/llm-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/llm-demo)（01_tokenization_and_generation · GPT-2 演示 tokenizer / KV cache / 采样策略）

推理与部署：

- [[02_推理部署笔记]]（vLLM + SGLang 显存/并发/Prometheus 指标/Grafana/日志全套生产调优）
- 配套 demo：[workspace/llm-demo/02_inference_serving](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/llm-demo/02_inference_serving)（OpenAI 客户端 + Prometheus 解析，无需 GPU）

评测：

- [[OpenCompass笔记]]（上海 AI Lab / 书生·浦语，学术榜单权威，60+ 内置数据集）
- [[EvalScope笔记]]（阿里魔搭，一站式：评测 + 压测 + Arena + 可视化 + 训练集成，191 个内置 benchmark）
- [[评测框架对比笔记]]（场景化选型 + 标准生产评测流程 + 自定义数据集流程 + 报告指标清单）
- 配套 demo：[workspace/llm-demo/03_eval_frameworks](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/llm-demo/03_eval_frameworks)（双框架 mock，无需 GPU / 模型服务）

### 提示词与上下文工程

- [[RAG工业方案笔记]]（2026 最新 RAG 框架、文档解析、Embedding、向量库、评测体系）
- [[Prompt工程笔记]]（Anthropic 官方原则 + DSPy 编译器范式 + 结构化输出 + 模板管理）
- [[Rerank笔记]]（Cross-encoder / LLM-based 重排序 + BGE v2/v3 + Cohere / Jina / Qwen3-Reranker）
- [[上下文工程与Agent笔记]]（Context Engineering 四大策略 + Manus 经验 + Agent 框架 + 记忆系统 + MCP）
- 配套 demo：[workspace/llm-demo/04_rag_evaluation](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/llm-demo/04_rag_evaluation)（mock RAG + RAGAS 4 大指标，无需 GPU / 模型服务）


### Agent 与 Skills

Agent 设计：

- [[Agent总览笔记]]
- [[Agent开源项目笔记]]

协议与扩展：

- [[Skills笔记]]
- [[MCP笔记]]

实战案例：

- [[mini-agent学习笔记]]
- 配套 demo：[workspace/agent/abstract-base-class/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/agent/abstract-base-class)（mini-agent 源码中的 ABC 抽象基类演示）

### AI 工具与平台

AI 编程助手：

- [[ClaudeCode笔记]]
- [[Codex笔记]]
- [[OpenCode笔记]]
- [[Openclaw笔记]]

模型平台：

- [[HuggingFaceTransformers笔记]]
- [[Ollama笔记]]
- 配套 demo：[workspace/ai-assistant/huggingface-pipeline-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/ai-assistant/huggingface-pipeline-demo)（HF Transformers pipeline 最小推理示例）

---

## 5. 运维与基础设施

### Docker

- [[01_Docker笔记]] — 总览与 CLI 速查
- [[02_Docker镜像与容器笔记]] — 镜像/容器/网络命令详解
- [[03_Docker数据卷与挂载笔记]] — bind / volume / tmpfs 挂载专题
- [[04_Dockerfile笔记]] — Dockerfile 编写
- [[05_Docker Compose笔记]] — Compose 多服务编排
- 配套 demo：[workspace/docker/](workspace/docker/)（01_dockerfile_demo / 02_compose_demo / 03_volume_demo）

### 容器编排与 CI/CD

- [[01_Kubernetes基础笔记]] — 概念、角色、kubectl 速查
- [[02_Kubernetes部署特性笔记]] — Deployment/StatefulSet/Ingress/PV/HPA/RBAC/NetworkPolicy
- [[03_K3s笔记]] — K3s 单节点/HA 集群、内置组件
- [[04_Rancher笔记]] — Rancher 部署与多集群管理
- [[05_Harbor笔记]] — 企业级镜像仓库
- [[06_Jenkins基础笔记]] — Jenkins 声明式 Pipeline
- [[07_Jenkins_CICD实战笔记]] — Git+Jenkins+Harbor+K3s 全链路
- [[08_运维生产方案总览]] — 组件选型与整体拓扑
- 配套模板：[workspace/cicd/](workspace/cicd/)（Jenkinsfile + K8s manifest + Harbor compose + Jenkins Helm values）

### DevOps

- [[01_DevOps基础与文化笔记]] — DevOps 概念、CALMS、与 SRE/平台工程区别
- [[02_小企业DevOps方案笔记]] — 50~500 人企业主流开源栈与商业栈
- [[03_DevOps工具链对比笔记]] — Git/CI/CD/IaC/可观测/安全/制品 选型参考
- 配套 demo：[workspace/devops/](workspace/devops/)（branch strategy / GitOps / Terraform）

### Linux 与 WSL

- [[01_Linux基础与文件管理笔记]] — 目录约定、文件操作、vim、帮助命令
- [[02_Linux用户权限与组管理笔记]] — user/group、rwx、chmod/chown/chgrp
- [[03_Linux进程服务与系统管理笔记]] — 进程、systemd、防火墙、网络监控
- [[04_Linux磁盘网络与软件包管理笔记]] — 磁盘挂载、网络配置、rpm/yum/apt
- [[05_Linux定时任务笔记]] — crontab / at / systemd timer
- [[WSL笔记]] — WSL1 vs WSL2、wsl CLI、wsl.conf/.wslconfig、systemd

---

## 6. 计算机基础与软件工程

### 网络与协议

- [[websocket笔记]]
- [[TCP_IP四层网络模型笔记]]
- 配套 demo：[workspace/ws/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/ws)（FastAPI WebSocket 完整示例：服务端 + 浏览器 / Python / Node.js 三种客户端 + REST 触发推送）

### 安全与鉴权

- [[鉴权与登录笔记]]
- [[权限模型笔记]]
- 配套 demo：[workspace/gateway/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/gateway)（FastAPI 网关 + JWT 鉴权 + Casbin 权限 + 扫码登录）

### 网关

- [[API网关笔记]]

### 系统架构

- （权限模型已并入「安全与鉴权」板块，见 [[权限模型笔记]]）

### 代码规范、技巧与杂项知识

- [[代码规范与开发技巧笔记]]

---


## 7. 工具与效率

### 快捷键速查

- [[工具快捷键]]

### 命令行与 Shell

- [[常用命令&快捷指令]]
- [[快捷指令]]

### Markdown 与写作

- [[markdown latex语法大全]]

### 名词速查

- [[技术名词&专有名词]]

---


## 8. 版本管理与协作

### Git 与平台

- [[01_Git笔记]]
- [[02_Git命令速查笔记]]
- [[03_Git回滚决策笔记]]
- [[Git Worktree 笔记]]

---


## 9. 产品与设计

### Figma 与 UI

- [[Figma笔记]]
- [[UI术语与设计风格笔记]]

### 独立开发

- [[穷鬼出海套餐笔记]]

---

## 10. Mac 与桌面环境

- [[Mac使用笔记]]（系统维护 / 常用命令 / 快捷键 / 外设 集中整理）

---

## 12. 加密和股票

### 投机感悟

- [[投资心得与方法论笔记]]

### Crypto 与 Web3

- [[Crypto与Web3笔记]]

### 量化交易

- [[量化交易笔记]]

### 投研与新闻

- [[金融资讯源笔记]]

---

## 13. 个人成长

### 计划与目标

- [[30天快速成长计划]]
- [[每日四象限计划表]]
- [[用7天，真正“认识你自己”]]

### 复盘

- [[日复盘模版]]
- [[周复盘模版]]

### 框架与方法

- [[建立“人生把控感”的核心框架]]

### 感悟

- [[有感]]

---

## 16. 健康与生活

### 中医与传统

- [[天纪—倪海厦笔记]]

---

## 17. 杂项 / 收件箱

- 临时收纳未归类条目，待整理后迁移到合适模块
