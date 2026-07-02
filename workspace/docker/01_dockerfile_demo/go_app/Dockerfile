# syntax=docker/dockerfile:1.7
# 演示：Go 多阶段构建 + scratch/alpine 最小化镜像
# 对应 Hub/04_Dockerfile笔记.md 中的"多阶段构建"小节

# ========== 阶段 1：编译 ==========
FROM golang:1.22-alpine AS builder
WORKDIR /src

# 先拷依赖锁文件，最大化构建缓存命中
COPY go.mod go.sum ./
RUN go mod download

# 再拷代码
COPY . .

# 编译：静态二进制、不带调试信息
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/app .

# ========== 阶段 2：运行时 ==========
FROM alpine:3.20

# 装 CA 证书（Go 拉 HTTPS 必备）+ 设置时区
RUN apk add --no-cache ca-certificates tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

# 用非 root 运行
RUN addgroup -S app && adduser -S app -G app
USER app

COPY --from=builder /out/app /usr/local/bin/app

EXPOSE 8080
ENTRYPOINT ["app"]
