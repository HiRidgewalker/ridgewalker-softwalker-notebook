---
title: "Harbor 笔记"
---

# Harbor 笔记

> 来自 [IV_Rancher笔记](../kubernetes/IV_Rancher笔记.md) 的延伸：「CI/CD 的镜像要落到哪里」——Harbor 是企业级答案。

---

## 1. Harbor 是什么

**Harbor** 是 CNCF Graduated 项目，**企业级容器镜像仓库**。

Docker Registry 的基础上加：

- **项目管理**：租户隔离
- **RBAC**：用户/角色/权限
- **镜像复制**：跨 Harbor 实例同步（p2p / pull-based）
- **漏洞扫描**：Trivy 集成
- **镜像签名**：Cosign / Notary
- **镜像保留策略**：自动清理过期 tag
- **REST API + Webhook**：CI 集成
- **存储后端**：文件系统 / S3 / Azure Blob / GCS / OCI Object Storage

> Docker Hub 是公有 Hub 的运营实例；Harbor 是私有"Hub"，是企业内镜像仓库的事实标准。

---

## 2. 为什么不用 Docker Hub / 公有仓库

| | 公开 Hub（Docker Hub） | 私有 Harbor |
| --- | --- | --- |
| 镜像可被外部看到 | 默认是 | 内网部署 |
| 拉取速率限制 | yes（2020 起匿名 100/6h） | 无 |
| 漏洞扫描 | 收费（DSE） | 免费 Trivy |
| 数据合规 | 数据出企业 | 数据在企业内 |
| 商业机密 | 不安全 | 安全 |
| 内网访问 | 拉不动 | 可 |
| 多架构 | 公共镜像 OK | 内部镜像必须自己 |

**结论**：企业内部所有业务镜像都该推 Harbor（哪怕是 alpine 也要自存一份断网时用）。

---

## 3. 部署

### 3.1 三种部署方式对比

| 方式 | 适用 | 复杂度 | 推荐度 |
| --- | --- | --- | --- |
| **docker-compose 单机** | 演示 / 测试 | 最低 | ⭐⭐ |
| **offline 安装包（Helm chart → K8s）** | **生产推荐**，含全部组件 | 中 | ⭐⭐⭐⭐⭐ |
| **Helm chart 直接装** | 有公网的环境 | 低 | ⭐⭐⭐ |

### 3.2 docker-compose 单机部署（学习）

```bash
# 下载 release
curl -L https://github.com/goharbor/harbor/releases/download/v2.11.0/harbor-offline-installer-v2.11.0.tgz | tar xz
cd harbor

# 改配置
cp harbor.yml.tmpl harbor.yml
sed -i 's/hostname: reg.mydomain.com/hostname: harbor.example.com/' harbor.yml
sed -i 's/port: 80/port: 8080/' harbor.yml
sed -i 's|HTTPS:.*|# HTTPS off for test/' harbor.yml

# 自签证书（HTTPS 场景）
mkdir -p certs
openssl req -x509 -newkey rsa:4096 \
  -keyout certs/server.key -out certs/server.crt \
  -days 365 -nodes -subj '/CN=harbor.example.com'

./install.sh --with-trivy
```

进入：

```bash
docker compose ps
# 默认用户 admin / Harbor12345（首次登录强制改密码）
```

### 3.3 Helm chart 安装到 K8s/K3s（生产推荐）

```bash
# 加 chart repo
helm repo add harbor https://helm.goharbor.io
helm repo update

# 创建 namespace
kubectl create namespace harbor

# 安装
helm install harbor harbor/harbor \
  --namespace harbor \
  --set expose.ingress.hosts.core=harbor.example.com \
  --set externalURL=https://harbor.example.com \
  --set persistence.enabled=true \
  --set persistence.persistentVolumeClaim.registry.size=200Gi \
  --set persistence.persistentVolumeClaim.chartmuseum.size=20Gi \
  --set persistence.persistentVolumeClaim.jobservice.size=10Gi \
  --set persistence.persistentVolumeClaim.database.size=20Gi \
  --set persistence.persistentVolumeClaim.redis.size=5Gi \
  --set metrics.enabled=true \
  --set trivy.enabled=true
```

> 实际生产还应该：
> - 配置 `expose.tls.certificate` 用真证书（cert-manager）
> - 数据库改为外部 Postgres（避免单点）
> - 镜像复制到第二个 Harbor 实例做灾备

### 3.4 高可用（双 Harbor）

```text
┌──────────┐                     ┌──────────┐
│ Harbor A │ ──pull-based复制──▶ │ Harbor B │
└──────────┘                     └──────────┘
   写                                 读
```

Harbor 间通过 **Replication Rule** 同步：

```
Harbor UI → Administration → Replications
  Name:    primary-to-backup
  Source:  primary.harbor.com
  Dest:    backup.harbor.com
  Trigger: Scheduled / Manual / Event-based
```

---

## 4. 项目 / 成员 / 角色

### 4.1 项目

- 一个项目 = 一个团队 / 业务线
- 项目下可以建多个镜像仓库（按名称）
- 项目可见性：Public（匿名拉）/ Private

```bash
# 项目命名规范：team-app 或者 group/app
# 比如：backend/webapi、frontend/web、infra/postgres
```

### 4.2 角色

| 角色 | 权限 |
| --- | --- |
| **Project Admin** | 全权限 |
| **Developer** | 推/拉镜像 |
| **Guest** | 仅拉公开项目的镜像 |
| **Maintainer** | 项目内管理员 |

### 4.3 机器人账号（**CI 强烈推荐用机器人**）

```text
Projects → myproj → Robot Accounts → New Robot Account
  Name:       robot-ci
  Description: Used by Jenkins build agents
  Permissions: Push and Pull
```

机器人账号：

- 有独立用户名密码（`robot$myproj+robot-ci`）
- 不需要创建真实用户
- 比用一个真实用户密码安全（密码可以旋转、回滚）

---

## 5. 镜像推送

### 5.1 从 docker CLI 推送

```bash
# 登录
docker login harbor.example.com -u robot$myproj+robot-ci -p xxxx

# 标签 → 推送
docker tag myapp:v1 harbor.example.com/myproj/webapi:v1
docker push harbor.example.com/myproj/webapi:v1
```

### 5.2 从 buildx 推送（多架构）

```bash
# 多架构构建 + 推送
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t harbor.example.com/myproj/webapi:v1 \
  --push .
```

需要 `BUILDX_EXPERIMENTAL=1`，或者 `docker buildx create --use`。

### 5.3 在 K8s 里构建（Kaniko / Buildah）

```bash
# Kaniko 不需要特权，K8s 推荐
# 推送时用 service account 配置的 imagePullSecrets 不需要
# 直接 docker login + push 即可
```

> Jenkins Pipeline 用 Kaniko / buildx 都好，详见 [II_Jenkins_CICD实战笔记](../jenkins/II_Jenkins_CICD实战笔记.md)。

---

## 6. K8s 拉取 Harbor 镜像

### 6.1 配置 imagePullSecrets

```bash
kubectl create namespace myapp

kubectl create secret docker-registry harbor-pull \
  --docker-server=harbor.example.com \
  --docker-username=robot$myproj+robot-ci \
  --docker-password=xxxxx \
  --docker-email=ci@example.com \
  --namespace=myapp
```

### 6.2 Pod 使用

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
    - name: web
      image: harbor.example.com/myproj/webapi:v1
  imagePullSecrets:
    - name: harbor-pull
```

### 6.3 Service Account 默认使用（namespace 级）

```bash
# 让 default service account 自动有 imagePullSecrets
kubectl patch serviceaccount default -n myapp -p '{"imagePullSecrets":[{"name":"harbor-pull"}]}'
```

```bash
# 每个新 namespace 怎么自动用？用 rancher/projects + service account
# 或者自己写 controller（简单服务可以用初创脚本 kubectl patch）
```

---

## 7. 漏洞扫描（Trivy）

```bash
# Harbor UI：Project → Image → Scan → 看到 CRITICAL/HIGH/MEDIUM/LOW
```

CI/CD 流水线集成：

```groovy
// Jenkinsfile 示例
sh """
  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image \
    --exit-code 1 \
    --severity HIGH,CRITICAL \
    harbor.example.com/myproj/webapi:${TAG}
"""
```

> 详见 [II_Jenkins_CICD实战笔记](../jenkins/II_Jenkins_CICD实战笔记.md)。

---

## 8. 镜像复制策略

### 8.1 场景

| 场景 | 作用 |
| --- | --- |
| 主 Harbor → 备份 Harbor | 灾备 / 多活 |
| 国内 Harbor → 海外 Harbor | 跨国拉取加速 |
| 开发 Harbor → 测试 Harbor | 环境隔离推不同镜像 |
| Harbor → CI runner 内仓库 | CI 离线内网拉取 |

### 8.2 两种模式

- **Push-based（默认）**：源端配置触发条件，目标会被动拉取
- **Pull-based**：目标端主动定时拉源端（更通用，权限倒置；推荐用于灾备）

### 8.3 实战：跨 Harbor 同步

```text
Source Harbor:  harbor.example.com  (生产)
Backup Harbor:  harbor-dr.example.com (灾备)

Pull-based rule on backup:
  Source registry: harbor.example.com
  Source project:   myproj
  Filter:           *
  Trigger:          Every 1 hour
  Dest project:     myproj
```

---

## 9. 安全

| 措施 | 配置 |
| --- | --- |
| 容器镜像签名 | `cosign` 或 Notary v2，签名镜像防篡改 |
| 限制 pushed | Force 勾选"禁止覆盖"避免误覆盖 |
| 镜像保留策略 | Tag Retention：保留 30 天内 + 最近 50 个 tag |
| 防恶意镜像 | 漏洞扫描 + 自动拒绝 HIGH/CRITICAL 推送 |
| RBAC 最小权限 | 按项目分配 robot account；不同环境用不同 robot |
| 自签名 CA | 所有 K8s 节点 trust 私有 CA |

### 9.1 开启 Cosign 签名验证

```bash
# cosign 推镜像时签名
cosign sign --key cosign.key harbor.example.com/myproj/webapi:v1

# 拉取时验证（K8s + cert-manager + Kyverno）
```

简化方案：生产环境只在镜像扫描通过后才允许进生产仓库（Harbor 自动化策略 + RBAC）。

---

## 10. Webhook（CI 集成）

```text
Project → Webhooks → New Webhook
  URL:    http://jenkins.internal/job/pull-and-deploy/build?token=xxx
  Triggers: Push image, Delete image, Scan completed
```

Jenkins 侧接收触发：

```groovy
// 用 Generic Webhook Trigger 插件接收 + 解析 payload + 触发部署
```

> 这是"镜像推完自动部署"的常用做法。

---

## 11. 常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| docker login 失败 | HTTPS 自签证书未 trust | 把 ca.crt 放到 `/etc/docker/certs.d/harbor.example.com/ca.crt` |
| K8s 拉镜像 ErrImagePull | imagePullSecrets 没配 / 密码错 | `kubectl describe pod` + secret |
| 推镜像 413 | Nginx body 上限 | Harbor 反代 / Ingress 加 `client_max_body_size 500m` |
| 跨 Harbor 同步一直卡 | Pull-based 但目标 Harbor 没配置 source | 在目标 Harbor 添加 source endpoint |
| Trivy 扫描慢 | 镜像很大 / 数据库没缓存 | `--skip-db-update` + 持续运行的 trivy server |
| Harbor 重装数据丢 | 没挂载 / 没备份 PVC | 持久化卷必须挂；etcd snapshot 同样重要 |

---

## 12. 一句话总结

- **Harbor = 私有 Docker Hub + 漏洞扫描 + 复制策略 + RBAC**，是企业级 CI/CD 必备
- 生产部署选 Helm（offline 安装包）到 K3s，独立 namespace
- **机器人账号 + 镜像签名 + 漏洞门禁**是部署到生产前的强制流程
- K8s 用 `imagePullSecrets` 或 `service-account patch` 注入默认凭据