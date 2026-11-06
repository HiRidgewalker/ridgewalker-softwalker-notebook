# Catalog

> 平铺主题索引：每个技术主题独占一节，直接列出相关笔记；跨技术综合文章集中在 Cross-cutting Topics。

## Common Use

常用速查。

- [[markdown-latex-syntax]]
- [[common-cheatsheet]]

## Temporary Storage

暂存区，未完成的内容先放这里。

- [[speech-recognition]]

---

## Python

- [[python-basics]]
- [[python-async-asyncio]]

## uv

- [[uv]]

## Anaconda

- [[anaconda]]

## Jupyter

- [[jupyter]]

## Go

- [[01-go-overview]]
- [[02-go-basic-syntax]]
- [[03-go-composite-types]]
- [[04-go-functions]]
- [[05-go-oop]]
- [[06-go-packages-and-projects]]
- [[07-go-faq]]

## JavaScript

- [[01-javascript-basics]] — 基础与 ES6+（语法 / 数据类型 / 运算符 / 数组方法 / 解构 / 模板字符串 / Set Map）
- [[02-javascript-advanced]] — 作用域 / 闭包 / this / 构造函数 / 原型链 / class
- [[03-javascript-async-and-modules]] — 回调函数 / Promise / async-await / 事件循环 + ES Module

## TypeScript

- [[typescript-types-and-react-types]]

## CSS

- [[01-css-overview]]
- [[02-css-selectors-and-inheritance]]
- [[03-css-box-model]]
- [[04-css-layout]]
- [[05-css-units-and-values]]
- [[06-css-faq]]

## React

- [[01-react-overview]]
- [[02-react-hooks]]
- [[03-zustand-state-management]]
- [[04-react-router]]

## Next.js

- [[01-nextjs-overview]]
- [[02-nextjs-routing]]
- [[03-nextjs-server-and-client-components]]
- [[04-nextjs-data-fetching-and-server-actions]]
- [[05-nextjs-rendering-modes]]
- [[06-nextjs-faq]]

---

## FastAPI

- [[fastapi]]

## Django

- [[django]]

## Celery

- [[celery]]

## Pydantic

- [[pydantic]]

---

## Git

- [[01-git-overview]]
- [[02-git-command-cheatsheet]]
- [[03-git-rollback-decision]]
- [[04-git-worktree]]

---

## MySQL

- [[mysql]]

## PostgreSQL

- [[postgresql]]

## SQLite

- [[sqlite]]

## MongoDB

- [[mongodb]]

## Redis

- [[redis]]

---

## Milvus

- [[milvus]]

## Qdrant

- [[qdrant]]

## zvec

- [[zvec]]

---

## RabbitMQ

- [[rabbitmq]]

## Kafka

- [[kafka]]

---

## Docker

- [[01-docker-overview]] — 总览与 CLI 速查
- [[02-docker-images-and-containers]] — 镜像/容器/网络命令详解
- [[03-docker-volumes-and-mounts]] — bind / volume / tmpfs 挂载专题
- [[04-dockerfile]] — Dockerfile 编写
- [[05-docker-compose]] — Compose 多服务编排

## Kubernetes

- [[01-kubernetes-basics]] — 概念、角色、kubectl 速查
- [[02-kubernetes-deployment-features]] — Deployment/StatefulSet/Ingress/PV/HPA/RBAC/NetworkPolicy
- [[03-k3s]] — K3s 单节点/HA 集群、内置组件
- [[04-rancher]] — Rancher 部署与多集群管理

## Harbor

- [[harbor]] — 企业级镜像仓库

## Jenkins

- [[01-jenkins-basics]] — Jenkins 声明式 Pipeline
- [[02-jenkins-cicd-practice]] — Git+Jenkins+Harbor+K3s 全链路

## Linux

- [[01-linux-basics-and-file-management]] — 目录约定、文件操作、vim、帮助命令
- [[02-linux-users-permissions-and-groups]] — user/group、rwx、chmod/chown/chgrp
- [[03-linux-processes-services-and-system]] — 进程、systemd、防火墙、网络监控
- [[04-linux-disk-network-and-packages]] — 磁盘挂载、网络配置、rpm/yum/apt
- [[05-linux-scheduled-tasks]] — crontab / at / systemd timer

## WSL

- [[wsl]] — WSL1 vs WSL2、wsl CLI、wsl.conf/.wslconfig、systemd

## Process Management

- [[process-and-service-management]]

---

## Machine Learning

- [[01-ml-and-dl-basics]]
- [[02-deep-learning-environment-setup]]

## PyTorch

- [[pytorch]]

## Large Language Models

- [[01-large-language-models]]
- [[02-inference-deployment]] — vLLM + SGLang 显存/并发/Prometheus 指标/Grafana/日志全套生产调优

## LLM Evaluation

- [[opencompass]] — 上海 AI Lab / 书生·浦语，学术榜单权威，60+ 内置数据集
- [[evalscope]] — 阿里魔搭，一站式：评测 + 压测 + Arena + 可视化 + 训练集成，191 个内置 benchmark

## Prompt Engineering

- [[prompt-engineering]] — Anthropic 官方原则 + DSPy 编译器范式 + 结构化输出 + 模板管理

## RAG

- [[rag-industrial-solutions]] — 2026 最新 RAG 框架、文档解析、Embedding、向量库、评测体系
- [[rerank]] — Cross-encoder / LLM-based 重排序 + BGE v2/v3 + Cohere / Jina / Qwen3-Reranker

## Agent

- [[agent-overview]]
- [[agent-open-source-projects]]
- [[mini-agent-study-notes]]

## MCP

- [[mcp]]

## Skills

- [[skills]]

## AI Coding Assistants

- [[claude-code]]
- [[codex]]
- [[opencode]]
- [[openclaw]]

## Model & Inference Platform

- [[huggingface-transformers]]
- [[ollama]]

---

## Figma

- [[figma]]

## UI/UX Design

- [[ui-terms-and-design-styles]]

---

## Computer Networks

- [[websocket]]
- [[tcp-ip-four-layer-model]]

---

## Cross-cutting Topics

跨技术主题，条目后括号内为关联主题。

- [[数据库设计与索引优化笔记]]（MySQL / PostgreSQL / Redis）
- [[关系型数据库选型对比笔记]]（MySQL / PostgreSQL / SQLite / MongoDB）
- [[消息队列选型对比笔记]]（RabbitMQ / Kafka）
- [[LLM评测框架对比笔记]]（OpenCompass / EvalScope）
- [[Django+FastAPI秒杀系统课程]]（Django / FastAPI / Redis / Celery）
- [[小企业运维生产方案总览]]（Docker / Kubernetes / Harbor / Jenkins）
- [[DevOps基础与文化笔记]]（Docker / Kubernetes / Jenkins / Git）— DevOps 概念、CALMS、与 SRE/平台工程区别
- [[小企业DevOps方案笔记]]（Docker / Kubernetes / Jenkins）— 50~500 人企业主流开源栈与商业栈
- [[DevOps工具链选型对比笔记]]（Git / Docker / Kubernetes / Jenkins）— Git/CI/CD/IaC/可观测/安全/制品 选型参考
- [[鉴权与登录笔记]]（FastAPI / Redis）
- [[权限模型与Casbin实践笔记]]（FastAPI / 鉴权）
- [[API网关原理与选型笔记]]（FastAPI / Nginx）
- [[上下文工程与Agent笔记]]（Agent / MCP / Prompt Engineering）
- [[前端工程化笔记]]（JavaScript / CSS / Next.js）
- [[UI设计工具与灵感资源笔记]]（AI Coding Assistants / Model & Inference Platform）

