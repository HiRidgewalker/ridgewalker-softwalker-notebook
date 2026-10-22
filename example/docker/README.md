# example/docker

Docker 相关的可运行 demo 集合，对应笔记见 `Hub/04_Dockerfile笔记`、`Hub/05_Docker Compose笔记`、`Hub/03_Docker数据卷与挂载笔记`。

## 目录结构

```
example/docker/
├── README.md                       ← 本文件
├── 01_dockerfile_demo/             ← Dockerfile 编写（含多阶段）
│   ├── go_app/
│   │   ├── Dockerfile
│   │   ├── main.go
│   │   └── README.md
│   └── python_app/
│       ├── Dockerfile
│       ├── app.py
│       ├── requirements.txt
│       └── README.md
├── 02_compose_demo/                ← Compose 多服务编排
│   ├── flask_pg_redis/
│   │   ├── compose.yml
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── README.md
└── 03_volume_demo/                 ← bind / volume / tmpfs 三种挂载对比
    ├── compose.yml
    ├── bind-data/                  ← bind mount 测试用数据
    └── README.md
```

## 运行约定

- 需要本机已安装 Docker（v24+ 推荐，Compose v2 用 `docker compose` 空格命令）
- 所有 demo 跑前 `cd` 到对应子目录
- 跑完用 `docker compose down -v` 一键清理（包括卷）
