## docker 概念
[Docker 基础概念 | 菜鸟教程](https://www.runoob.com/docker/docker-intro.html)
[Docker 官方文档](https://www.docker.com/)
[Docker镜像仓库](https://hub.docker.com/)

### docker 的核心概念
- 镜像
- 容器
- 仓库
	- 公有仓库 (docker hub)
	- 私有仓库
### docker 与虚拟机进行对比
![[image-1.png]]
### docker 整体架构图
![[image-2.png]]

### docker的几个核心组件
#### docker client
- 用户与docker交互的主要方式
- -接收用户命令并发送给Docker Daemon
- 可以与远程Docker Daemon通信

	**常用命令**：
	
	- `docker run` - 运行容器
	- `docker build` - 构建镜像
	- `docker pull` - 拉取镜像
	- `docker ps` - 查看容器状态
#### docker daemon
**功能**：

- Docker的核心服务进程
- 管理镜像、容器、网络和存储卷
- 监听Docker API请求并处理

**主要职责**：

- 镜像管理（构建、存储、分发）
- 容器生命周期管理
- 网络管理
- 数据卷管理
- 与Registry通信

#### Docker Engine

**组成**：

- Docker Client + Docker Daemon + REST API
- 是Docker的核心组件

**工作流程**：

1. Client发送命令到Daemon
2. Daemon解析并执行命令
3. 与Registry交互（如需要）
4. 管理本地镜像和容器
5. 返回结果给Client

#### Docker Registry

**作用**：

- 存储和分发Docker镜像
- 提供镜像的版本管理
- 支持公有和私有仓库

**Docker Hub特点**：

- 官方公共Registry
- 包含大量预构建镜像
- 支持自动构建功能
- 免费和付费服务

## Docker架构
[Docker 架构 | 菜鸟教程](https://www.runoob.com/docker/docker-architecture.html)

## Docker容器的使用
[Docker 容器使用 | 菜鸟教程](https://www.runoob.com/docker/docker-container-usage.html)
官方Docker CLI命令指南: [Docker CLI document](https://docs.docker.com/reference/)

