# Rancher 笔记

> 来自 [[Hub/12_K3s笔记]] 的延伸：「K3s 跑起来了，怎么可视化管起来」——Rancher 是答案。

---

## 1. Rancher 是什么

**Rancher** 是 SUSE 出品的**多 Kubernetes 集群管理平台**。一个 Rancher 实例可以纳管：

- 本地 K3s / RKE2 / k8s 集群
- 公有云 EKS / AKS / GKE
- 导入已有的任何 K8s 集群（v1.x 全版本）

提供 UI、CLI（`rancher`）、API 调用多种管理方式。

### 1.1 核心能力

| 能力 | 作用 |
| --- | --- |
| **多集群 UI** | 统一面板看所有集群状态、节点、工作负载 |
| **集群生命周期** | 创建 / 删除 / 备份集群（RKE / K3s） |
| **用户/项目 RBAC** | 跨集群统一用户、角色、权限 |
| **应用商店（Charts）** | 一键装 Longhorn / Prometheus / Grafana / cert-manager 等 |
| **集成认证** | AD / LDAP / SAML / OIDC / Keycloak |
| **Fleet** | GitOps 跨集群部署 |
| **监控告警** | 内置 Prometheus + Grafana（社区版可用） |

### 1.2 Rancher 版本

- **v2.x**：当前主线（社区版从 GitHub releases 装 Apache 2.0）
- 不区分"社区/商业"——同一个安装，区别在 license：Community/Enterprise/Enterprise with Rancher Prime

---

## 2. 安装方式对比

| 方式 | 命令 | 适用 |
| --- | --- | --- |
| **Docker 单容器** | `docker run -d --name rancher rancher/rancher` | 演示、学习（**< 50 节点不推荐生产**） |
| **Helm on K3s/RKE2** | Helm 装到已有 K8s | **生产推荐**（高可用靠底层 K8s） |
| **RKE/RKE2 自建集群再装** | RKE 拉起一个 K3s/RKE2 cluster 再装 Rancher | **企业生产**，完整 HA |

### 2.1 生产推荐拓扑

```text
                ┌──────────────────────────┐
                │  Rancher Cluster（K3s）   │  1 套
                │  管理控制台                │
                └────────────┬─────────────┘
                             │ (import)
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼─────────┐  ┌───────▼─────────┐  ┌───────▼─────────┐
│  Workload A     │  │  Workload B     │  │  Workload C     │
│  (K3s cluster)  │  │  (K3s cluster)  │  │  (K3s cluster)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
   dev / test / prod
```

---

## 3. Helm 安装到 K3s（生产推荐）

### 3.1 准备一个 K3s 作为 Rancher 集群

```bash
# 在一台（或 HA 多台）机器上起 K3s，专门跑 Rancher
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable=traefik \
  --disable=servicelb
```

> Rancher 集群不需要 Ingress（用 NodePort + 外部 LB 转发即可），所以 disable traefik。

### 3.2 安装 Rancher Helm Chart

```bash
# 加 Helm repo
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add jetstack https://charts.jetstack.io
helm repo update

# 创建 namespace
kubectl create namespace cattle-system

# 安装 cert-manager（Rancher 依赖）
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.1/cert-manager.yaml

# 装 Rancher
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set bootstrapPassword=admin \
  --set ingress.ingressClassName=nginx
```

或者用 `ingressClassName=traefik`，取决于你要不要同时装 Nginx Ingress。

### 3.3 访问入口

```bash
kubectl -n cattle-system get svc rancher
# 类型 ClusterIP? 不对，应该是 ingress 把 hostname 暴露出去
# 因为这里没装 ingress，所以 Rancher 自己用 NodePort 暴露
```

> 一般做法：在 Rancher 集群前面挂一个**外部负载均衡**（F5 / HAProxy / Nginx），转发到 K3s 节点端口。

```bash
# Rancher 集群入口
https://rancher.example.com
# 首登：admin / <bootstrapPassword>
```

### 3.4 入口证书

- **Let's Encrypt 自动**：配上 cert-manager + DNS-01 挑战即可
- **自带证书**：

```bash
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set ingress.tls.source=secret \
  --set ingress.tls.secretName=tls-rancher-ingress
```

- **私有 CA 证书**：传 `ingress.tls.ca` 等参数

---

## 4. 纳管已存在的 K3s 集群

Rancher 不强制管理 K8s 生命周期，**也可以纳管现有集群**（imported）。

### 4.1 在 Rancher UI 操作

1. `Cluster Management` → `Clusters` → `Import Existing`
2. 选择 `Generic`（K3s 选这个）
3. 把 Rancher 给出的 manifest 粘到 K3s 里 apply

```bash
# 在 K3s 节点跑
curl -sfL https://get.k3s.io | K3S_URL=https://k3s.example.com:6443 K3S_TOKEN=... sh -

# 在 Rancher UI 拿到：
curl --insecure -sfL https://rancher.example.com/v3/.../import | kubectl apply -f -
```

> 完成后，这个 K3s 集群就出现在 Rancher UI 里，可以 web 化管理。

### 4.2 拓扑优势

- Rancher 集群（1 套 K3s）专门跑 Rancher 控制台 + 数据库
- 业务集群（多个 K3s）跑工作负载
- 业务集群挂了不影响 Rancher 控制台

---

## 5. 用户/项目 RBAC

Rancher 内置两种类型用户：

| 类型 | 适用于 |
| --- | --- |
| **Local User** | 内部测试 |
| **External User（OIDC/SAML/LDAP）** | 生产 |

### 5.1 三层权限模型

```text
Global
  └── Cluster
        └── Project（Namespace 组）
              └── Namespace
                    └── Workload
```

- **Global Permission**：管理员 / 普通用户（影响所有集群）
- **Cluster Role**：集群级权限（如查看节点）
- **Project Role**：项目级权限（覆盖多个 namespace）

### 5.2 集成 Keycloak / OIDC

`Cluster Management → Settings → Authentication → Keycloak`（也支持 GitHub / Google / LDAP / SAML）。

详细参数见 Rancher 官方 Auth 文档。

---

## 6. 应用商店（Charts）

Rancher 内置 Helm Catalog，**一键装组件**：

```bash
# UI 路径：Apps → Charts
# 或 CLI：
kubectl create namespace cattle-system
# Charts 列表：Apps → Repositories
```

常见装包：

| Chart | 用途 |
| --- | --- |
| **Longhorn** | 块存储（推荐装） |
| **Rancher Monitoring** | Prometheus + Grafana |
| **Rancher Logging** | Loki + Promtail |
| **cert-manager** | 证书管理 |
| **MetalLB** | LoadBalancer |
| **Nginx Ingress Controller** | Ingress |
| **ArgoCD / Fleet** | GitOps |

> 装好的应用跟 `helm install` 等价，可随时 `helm history` 看。

---

## 7. 内置监控 + 告警（社区版）

装 `Rancher Monitoring` chart 后：

```text
Grafana → Explore
  ├── Prometheus 抓取 cluster node-exporter
  ├── kube-state-metrics 抓 K8s 对象状态
  └── Rancher 自己导出集群信息
```

访问：

```bash
# UI: Apps → Installed Apps → rancher-monitoring
# Grafana:
# https://<rancher-host>/api/v1/namespaces/cattle-monitoring-system/services/http:rancher-monitoring-grafana:80/proxy
# 默认用户 admin / <生成的密码>
kubectl get secret -n cattle-monitoring-system rancher-monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d
```

告警：`Alerts → Alertmanager`，配 webhook / 邮件。

---

## 8. 备份与恢复

### 8.1 Rancher 配置备份

Rancher 把所有配置存到 **cattle-system namespace** 的一个 secret + 集群里的几个对象里。**最简单**：把整个 `cattle-system` ns + `local` 集群定义备份。

### 8.2 Rancher 部署的集群备份

每个被纳管的 K3s 集群用 [[Hub/12_K3s笔记]] 的 `k3s etcd-snapshot` 机制备份（自身配置）。

### 8.3 Rancher 服务器自身的备份（Rancher Backup Operator）

```bash
# 在 Rancher 集群
kubectl apply -f https://github.com/rancher/backup-restore-operator/releases/download/v3.1.2/rancher-backup.yaml

# 创建备份
rancher-backup create --type s3 --bucket my-restore --endpoint s3.example.com --access-key xxx --secret-key xxx
```

恢复时：

```bash
rancher-backup restore --filename backup-xxx.tar.gz
```

---

## 9. Fleet（GitOps）

Rancher 自带的 GitOps 引擎，可以**把 git 仓库里的 manifest 推到一组目标集群**。

```yaml
# Repo: myrepo/k8s-fleet/web.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
...
```

```bash
# 在 Rancher：Continuous Delivery → Git Repos
# 添加 git repo → 选 cluster → 自动同步
```

Rancher Fleet 适合「一个 git 仓库管多个集群」场景。进阶可单用 ArgoCD。

---

## 10. 升级 Rancher

```bash
# 升级到新版本
helm repo update
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --reuse-values \
  --set rancherImageTag=v2.9.2
```

> 跨大版本（2.8 → 2.9）注意看 release notes，特别是 K8s 版本依赖与已弃用字段。

---

## 11. 常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| Rancher 域名访问不通 | 外部 LB 转发到 NodePort 失败 | 检查 LB → 节点端口 → K3s → cattle-system |
| 证书报错 | 证书链不全 / hostname 不匹配 | 用 cert-manager 自动签发 |
| 导入集群后节点 NotReady | 集群内缺镜像 / cilium/flannel 没通 | `kubectl describe node` 看事件 |
| 装的应用 pods pending | 资源不够 / StorageClass 缺 PV | 加节点、装 Longhorn |
| Local 用户登不上 | 没设置密码 | 第一次用 admin/bootstrapPassword 登，然后创建 |
| 备份文件损坏 | 跨版本备份恢复兼容差 | 同大版本内恢复 |

---

## 12. 一句话总结

- **Rancher = K8s 集群的统一管理 UI**，能纳管 已有 K3s / RKE2 / EKS / 自建
- 生产用 Helm 安装到独立 K3s（隔离基础环境与被管集群）
- 用 Keycloak/OIDC 做统一登录，用 Cluster Role + Project Role 限权
- 监控/告警、Helm 应用商店、Fleet GitOps 都内置，能省很多组件搭建工作