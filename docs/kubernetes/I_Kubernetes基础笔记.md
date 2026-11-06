---
title: "Kubernetes 基础笔记"
sidebar_position: 1
---

# Kubernetes 基础笔记

> 由旧稿重新整理版本。K8s 系列新笔记共 8 篇：本文是**基础与速查**；[II_Kubernetes部署特性笔记](./II_Kubernetes部署特性笔记.md) 是**部署相关对象**（Deployment/StatefulSet/Ingress/PV/HPA/RBAC 等）；[III_K3s笔记](./III_K3s笔记.md) 是**K3s 实战**；[IV_Rancher笔记](./IV_Rancher笔记.md) 是**集群管理 UI**；[Harbor笔记](../harbor/Harbor笔记.md) 是**镜像仓库**；[I_Jenkins基础笔记](../jenkins/I_Jenkins基础笔记.md) 是**CI 引擎基础**；[II_Jenkins_CICD实战笔记](../jenkins/II_Jenkins_CICD实战笔记.md) 是**全链路流水线**；[小企业运维生产方案总览](/blog/小企业运维生产方案总览) 是**架构师视角总览**。旧稿目录已清理，当前以本文为准。

---

## 1. Kubernetes 是什么

Kubernetes（K8s）是 Google 开源的**容器编排平台**，用于自动化部署、扩缩、运维容器化应用。

核心能力：

- **自动调度**：把容器调度到合适节点
- **自我修复**：挂了自动重启、跨节点迁移
- **滚动升级**：无停机发版
- **弹性扩缩**：流量高峰自动扩容
- **配置管理**：ConfigMap / Secret 与镜像解耦
- **服务发现 / 负载均衡**：内置 DNS + Service
- **密钥与证书管理**：secret + cert-manager

---

## 2. 整体架构

```text
┌───────────────────── 控制平面（Control Plane）─────────────────────┐
│                                                                   │
│  kube-apiserver          ◀─── 所有交互的统一入口（REST API）       │
│       │                                                          │
│  ┌────┼────┬──────────────┬─────────────────┐                    │
│  │    │    │              │                 │                    │
│  scheduler  controller-manager   cloud-controller-manager         │
│  (调度)    (副本/节点/端点控制器)  (云厂商对接)                    │
│       │                                                          │
│       etcd  ◀─── 集群所有状态（KV 存储）                          │
└───────────────────────────────────────────────────────────────────┘
                            ▲                      ▲
                            │ 监听                 │
┌───────────────────── 工作节点（Worker Node）──────────────────────┐
│  kubelet   kube-proxy      容器运行时（containerd / CRI-O）         │
│  (节点代理) (网络代理)        ┌─────────────────────┐             │
│                              │ Pod / Container     │             │
│                              └─────────────────────┘             │
└───────────────────────────────────────────────────────────────────┘
```

### 2.1 控制平面（Control Plane）

| 组件 | 作用 |
| --- | --- |
| **kube-apiserver** | API 网关，所有组件（kubectl、kubelet、controller、scheduler）通过它读写集群状态 |
| **etcd** | 强一致 KV 存储，保存集群所有数据；etcd 挂了 = 集群脑裂 |
| **kube-scheduler** | 监听新创建的 Pod，决定它跑在哪个节点（资源、亲和性、污点等） |
| **kube-controller-manager** | 内嵌多个控制器：Deployment、StatefulSet、Node、Service 等 |

### 2.2 工作节点（Worker Node）

| 组件 | 作用 |
| --- | --- |
| **kubelet** | 节点代理，向 API Server 注册、接收 PodSpec、用 CRI 创建容器 |
| **kube-proxy** | 维护节点上的 iptables / IPVS 规则，实现 Service 转发 |
| **容器运行时** | containerd / CRI-O / Docker（已 deprecated），实际跑容器 |

### 2.3 K8s 与 Docker 的关系

- K8s 最初是 Docker 生态的"上层编排"，但 K8s v1.24+ 已不再直接支持 Docker（dockershim 移除）
- 现代 K8s 通过 **CRI（Container Runtime Interface）** 接入 containerd / CRI-O
- Docker 镜像格式 OCI 仍通用，Dockerfile 仍可继续写

---

## 3. 核心对象（Everything is an Object）

| 对象 | 作用 |
| --- | --- |
| **Pod** | 最小调度单元，可包含 1~N 个紧密耦合的容器（共享网络/卷） |
| **Deployment** | 管理 Pod 的副本和滚动升级 |
| **Service** | 为一组 Pod 提供稳定 IP + DNS 名 |
| **Namespace** | 逻辑分区（default / kube-system / 自定义） |
| **ConfigMap** | 非密配置 |
| **Secret** | 敏感配置（base64 编码，**非加密**） |
| **Ingress** | 7 层路由（HTTP/HTTPS） |
| **PersistentVolume / Claim** | 持久化存储 |
| **ServiceAccount** | Pod 用的身份 |
| **RBAC（Role / ClusterRole / Binding）** | 权限控制 |

> 详细对象在 [II_Kubernetes部署特性笔记](./II_Kubernetes部署特性笔记.md)。

---

## 4. YAML 基础

K8s 资源全部用 YAML 声明。所有字段可由 `kubectl explain <resource>.<field>` 查询。

```yaml
# 最低限度：apiVersion / kind / metadata / spec
apiVersion: apps/v1             # 哪一组 API
kind: Deployment                # 哪种对象
metadata:
  name: myapp
  namespace: default
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: nginx:1.27
          ports:
            - containerPort: 80
```

字段速记：

- `apiVersion`：见 `kubectl api-versions`
- `kind`：见 `kubectl api-resources`
- `metadata.name`：资源名（同一 namespace 内唯一）
- `metadata.labels`：任意 kv 标签，用于选择器 / 监控
- `metadata.annotations`：任意 kv 注解（接 ingress、cert 等）

---

## 5. kubectl 速查

### 5.1 上下文配置

```bash
# kubeconfig 位置
~/.kube/config           # 默认

# 多集群切换
kubectl config get-contexts
kubectl config use-context my-cluster

# 当前上下文信息
kubectl config current-context
```

### 5.2 看资源

```bash
kubectl get pods                                # 当前 ns
kubectl get pods -A                             # 所有 ns
kubectl get pods -n kube-system
kubectl get pods -o wide                       # 含节点 + IP
kubectl get pods -l app=nginx                   # 按 label 过滤
kubectl get pod mypod -o yaml                   # 看完整定义
kubectl get pod mypod -o jsonpath='{.status.podIP}'

kubectl get deploy,svc,ing -n demo              # 多种一起看
```

### 5.3 查详情与日志

```bash
kubectl describe pod mypod                      # 含事件
kubectl describe node mynode                    # 节点资源/状态
kubectl logs mypod                              # 当前容器日志
kubectl logs mypod -c mycontainer               # 多容器 pod 指定容器
kubectl logs mypod --previous                   # 上一个实例（崩溃后）
kubectl logs -f mypod                           # 实时跟随
kubectl logs -l app=nginx --tail=100            # 按 label 看日志

kubectl exec -it mypod -- bash                  # 进 pod 的第一个容器
kubectl exec -it mypod -c mycontainer -- sh    # 指定容器
```

### 5.4 创建 / 修改 / 删除

```bash
kubectl apply -f deployment.yaml                # 声明式（推荐）
kubectl apply -f ./dir/                         # 整个目录
kubectl apply -f - <<EOF                        # 从 stdin
apiVersion: v1
kind: ConfigMap
metadata:
  name: hello
data:
  world: hi
EOF

kubectl create -f deployment.yaml               # 命令式创建（已存在报错）
kubectl create deployment nginx --image=nginx   # 命令式快捷创建

kubectl edit deploy myapp                       # 临时改（存不住）
kubectl patch deploy myapp -p '{"spec":{"replicas":5}}'

kubectl delete -f deployment.yaml
kubectl delete pod mypod
kubectl delete pod -l app=nginx                 # 按 label 删
kubectl delete ns myns                          # 删 namespace
```

### 5.5 扩缩与回滚

```bash
kubectl scale deploy myapp --replicas=5
kubectl autoscale deploy myapp --min=2 --max=10 --cpu-percent=80   # HPA
kubectl rollout status deploy myapp
kubectl rollout history deploy myapp
kubectl rollout undo deploy myapp               # 回滚到上一版
kubectl rollout undo deploy myapp --to-revision=2

kubectl set image deploy/myapp myapp=myapp:v2  # 强写 image
```

### 5.6 调试与排错

```bash
kubectl get events --sort-by=.metadata.creationTimestamp -A    # 集群事件
kubectl get pods -A -o wide
kubectl top nodes                                              # 节点资源
kubectl top pods                                               # pod 资源

# 临时进调试容器（需要集群启用 ephemeral containers）
kubectl debug mypod -it --image=busybox --target=mycontainer

# 把本地端口转给 Pod / Service
kubectl port-forward svc/myapp 8080:80                        # localhost:8080 → service:80
kubectl port-forward pod/mypod 8080:80
```

### 5.7 其他

```bash
kubectl explain deployment.spec.template
kubectl api-resources
kubectl api-versions
kubectl cluster-info
kubectl version
```

---

## 6. 资源对象命名与 selector 机制

```yaml
spec:
  selector:
    matchLabels:
      app: nginx
```

- Deployment 用 `selector.matchLabels` 选定自己的 Pod
- Service 用 `selector` 选定要转发到的 Pod
- **改 label 后 selector 不匹配 = 旧 Pod 不被管理**（Deployment 会"丢失"副本）

```bash
# 看 Deployment 实际管理哪些 Pod
kubectl get deploy nginx -o jsonpath='{.spec.selector.matchLabels}{"\n"}'
# 然后
kubectl get pods -l app=nginx
```

---

## 7. K8s 部署形态对比

| 形态 | 适用 | 上手难度 |
| --- | --- | --- |
| **minikube** | 本地学 | 最低 |
| **kind** | 本地学，K8s in Docker | 低 |
| **k3d** | 本地/小型，K3s in Docker | 低 |
| **K3s** | 边缘 / 小型企业生产 | 低（见 [III_K3s笔记](./III_K3s笔记.md)） |
| **kubeadm** | 自建集群 | 中 |
| **RKE / RKE2** | Rancher 出品 | 中 |
| **EKS / AKS / GKE** | 公有云托管 | 中 |
| **OpenShift** | 企业级发行版 | 高（含 cert-operator 等） |

> 小企业首选 K3s（见后续笔记）。

---

## 8. 入门练习：本地 k3d

```bash
# 安装 k3d + kubectl
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
brew install kubectl

# 起一个 3 节点 k3d 集群
k3d cluster create mycluster --agents 2

# kubectl 已自动配置好
kubectl get nodes
```

```bash
# 跑个 nginx
kubectl create deploy nginx --image=nginx:1.27
kubectl expose deploy nginx --port=80
kubectl port-forward svc/nginx 8080:80
# 浏览器打开 localhost:8080

# 清理
k3d cluster delete mycluster
```

---

## 9. 常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| `kubectl` 报 `Unable to connect to the server` | kubeconfig 错误 / apiserver 不通 | 检查 `kubectl config view`、网络 |
| Pod pending | 节点资源不够 / PVC 没绑 / 镜像拉不下 | `kubectl describe pod` 看 Events |
| Pod CrashLoopBackOff | 容器启动错 | `kubectl logs mypod --previous` |
| Service IP 不通 | selector 没匹配上 Pod | 检查 label 是否一致 |
| Ingress 不生效 | 没装 ingress-controller | 装 Nginx Ingress 或 K3s 默认带 Traefik |
| 镜像拉不下来（ErrImagePull） | imagePullSecrets 不对 / 私有仓库未授权 | `kubectl create secret docker-registry` + `imagePullSecrets` |
| `apply` 后状态没更新 | 字段太多 diff 困难 | 先 `delete` 再 `create`，或用 `kubectl diff -f` 预览 |

---

## 10. 一句话总结

- K8s = 「容器编排」，不是「容器」本身（容器是 containerd/Docker 的事）
- 控制平面（apiserver + etcd + scheduler + controller）做决策；节点（kubelet + 容器运行时）执行
- 一切皆对象（Pod/Deployment/Service/…），YAML 是第一公民
- 调试核心命令：`get / describe / logs / exec / events`