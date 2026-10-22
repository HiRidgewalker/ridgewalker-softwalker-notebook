# Go 应用 Dockerfile Demo

对应：[[IV_Dockerfile笔记]] 的「多阶段构建」小节。

## 文件

- `Dockerfile`：两阶段构建。第一阶段在 `golang:1.22-alpine` 编译；最终镜像仅基于 `alpine:3.20` + 静态二进制。

## 运行

```bash
# 在本目录中
cd 01_dockerfile_demo/go_app

# 1) 准备 go.mod
go mod init example.com/myapp
go mod tidy

# 2) 构建
docker build -t myapp-go:1.0 .

# 3) 看镜像体积（对比 alpine:3.20 的 6MB vs golang:1.22 的几百 MB）
docker images myapp-go:1.0

# 4) 跑
docker run -d --name myapp -p 8080:8080 myapp-go:1.0
curl http://localhost:8080/
curl http://localhost:8080/health

# 5) 清理
docker rm -f myapp
docker rmi myapp-go:1.0
```

## 期望

最终镜像通常 < 20MB，包含：alpine 基础 + tzdata + ca-certificates + 一个 Go 静态二进制。
