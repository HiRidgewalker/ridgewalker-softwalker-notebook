# K3s 笔记

> 来自 [[I_Kubernetes基础笔记]] 的延伸：「小企业选哪个 K8s 发行版」的答案。

---

## 1. K3s 是什么

**K3s** 是 Rancher Labs（已被 SUSE 收购）出品的**轻量级 Kubernetes 发行版**，把上游 K8s 打包成单个 < 100MB 的二进制，移除 alpha feature 和传统 in-tree cloud provider。

### 1.1 核心特点

- **单二进制**：一个文件包含 kubelet、kube-proxy、scheduler、controller-manager 等所有组件
- **低资源**：server 节点最低 512MB RAM 即可运行
- **SQLite 默认存储**：单节点用嵌入式 SQLite，HA 用嵌入式 etcd
- **内置组件**：默认装好 Traefik（Ingress）、servicelb（LB）、local-path（存储）、metrics-server
- **易部署**：一行命令启动
- **CNCF 一致性认证**：与上游 K8s API 完全兼容

### 1.2 与上游 K8s 的差异

| 项目 | K3s |
| --- | --- |
| 安装 | 单 curl + sh |
| 默认存储 | SQLite（HA 时 etcd） |
| 默认容器运行时 | containerd |
| 默认 Ingress | Traefik v2 |
| 默认 LoadBalancer | servicelb（轻量） |
| 默认存储类 | local-path |
| 默认 metrics | metrics-server |
| 二进制大小 | ~70MB |
| 兼容上游 YAML | 100% 兼容（大部分 manifest 可直接 apply） |
| API 差异 | 几乎无（少数 alpha 特性未实现） |

### 1.3 适用场景

✅ **适合**

- 边缘计算（IoT、零售店）
- 小/中型企业内部 K8s
- CI/CD runner 集群（Jenkins on K3s）
- 资源受限环境
- 不想维护 kubeadm 复杂度

❌ **不适合**

- 数百+ 节点的大规模集群（仍然用 EKS/RKE2/自建 kubeadm 更合适）
- 需要原生 cloud provider 集成（GCE/AWS/GCP K8s 原生功能）

---

## 2. K3s vs RKE2 vs k8s（kubeadm）

| | K3s | RKE2 | kubeadm |
| --- | --- | --- | --- |
| 二进制大小 | ~70MB | ~100MB | 多组件 |
| 资源需求 | 低 | 中 | 高 |
| 安全加固 | 基础 | 高级（CIS 合规默认开） | 需手动 |
| 数据库 | SQLite / 内置 etcd / 外部 SQL | 内置 etcd | 外部 etcd |
| 部署复杂度 | 最低 | 低 | 高 |
| 上游兼容性 | 100% API 兼容 | 100% | 100% |
| 推荐场景 | 边缘、中小规模 | 金融、政企合规场景 | K8s 工程师学习底层 |

> **小企业**：K3s 起步，规模起来或要安全合规再迁 RKE2。同一 Rancher 可纳管两者。

---

## 3. 安装

### 3.1 单节点（学习 / 测试）

```bash
curl -sfL https://get.k3s.io | sh -

# 自动 systemctl 启用 k3s 服务
# kubeconfig 位置：/etc/rancher/k3s/k3s.yaml

# 配置 kubectl
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 验证
kubectl get nodes
```

### 3.2 单节点（生产）

```bash
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable=traefik \
  --default-local-storage-path /var/lib/rancher/k3s/storage \
  --node-name server-01 \
  --node-external-ip 192.168.1.10
```

### 3.3 HA 集群（生产推荐）

至少 3 个 server 节点用**嵌入式 etcd**：

```bash
# 第 1 台 server
curl -sfL https://get.k3s.io | sh -s - \
  --cluster-init \
  --write-kubeconfig-mode 644 \
  --tls-san 192.168.1.10 \
  --tls-san k3s.example.com

# 拿到 token
cat /var/lib/rancher/k3s/server/node-token

# 第 2、3 台 server（用 K3S_URL + K3S_TOKEN 环境变量）
curl -sfL https://get.k3s.io | sh -s - \
  --server https://192.168.1.10:6443 \
  --token <node-token> \
  --tls-san k3s.example.com

# 添加 worker（agent 节点）
curl -sfL https://get.k3s.io | sh -s - \
  --server https://192.168.1.10:6443 \
  --token <node-token> \
  --node-name worker-01
```

- **server 节点**：跑 etcd + 控制平面，**奇数**台（1/3/5/7）
- **agent 节点**：跑工作负载

### 3.4 离线安装（无外网环境）

```bash
# 在有外网的机器上
mkdir -p /tmp/k3s-offline && cd /tmp/k3s-offline
wget https://github.com/k3s-io/k3s/releases/download/v1.30.4%2Bk3s1/k3s
wget https://github.com/k3s-io/k3s/releases/download/v1.30.4%2Bk3s1/k3s-airgap-images-amd64.tar
wget https://get.k3s.io/install.sh

# 复制到内网机器，scp 一个文件就够
# 在内网机器上
sudo mkdir -p /var/lib/rancher/k3s/agent/images/
sudo cp k3s-airgap-images-amd64.tar /var/lib/rancher/k3s/agent/images/
sudo cp k3s /usr/local/bin/
sudo chmod +x /usr/local/bin/k3s
sudo INSTALL_K3S_SKIP_ENABLE=true sh install.sh
sudo systemctl enable --now k3s
```

### 3.5 高可用外部数据库方案（SQL / MySQL / Postgres）

```bash
# 启动时启用外部数据库
curl -sfL https://get.k3s.io | sh -s - \
  --datastore-endpoint="mysql://root:pwd@tcp(mysql.example.com:3306)/k3s" \
  --datastore-cafile=/etc/ssl/ca.pem \
  --datastore-certfile=/etc/ssl/client-cert.pem \
  --datastore-keyfile=/etc/ssl/client-key.pem
```

> 外部 DB 适合：1）大集群；2）想保留运维团队熟悉的 DBA 工具。

---

## 4. K3s 内置组件

K3s 默认启用以下内置组件，生产环境建议评估是否替换：

| 组件 | 默认 | 替代方案 |
| --- | --- | --- |
| **Container Runtime** | containerd | - |
| **DNS** | CoreDNS | - |
| **Ingress** | Traefik v2（`--disable=traefik` 可关） | Nginx Ingress Controller |
| **LoadBalancer** | servicelb（`--disable=servicelb` 可关） | MetalLB |
| **Storage** | local-path（`--disable=local-storage` 可关） | Longhorn / NFS |
| **Metrics** | metrics-server | - |
| **Network** | Flannel（默认 VXLAN） | Calico / Cilium（要 NetworkPolicy） |

> ⚠️ Flannel 默认不支持 NetworkPolicy。要做命名空间隔离必须换 Calico 或 Cilium：

```bash
curl -sfL https://get.k3s.io | sh -s - \
  --flannel-backend=none \
  --disable-network-policy

# 然后装 Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27/manifests/calico.yaml
```

---

## 5. K3s 常用操作

### 5.1 服务管理

```bash
# 服务控制
sudo systemctl status k3s
sudo systemctl restart k3s
sudo journalctl -u k3s -f            # 日志

# 配置文件
sudo vim /etc/rancher/k3s/config.yaml

# 重启生效
sudo systemctl restart k3s
```

### 5.2 etcd snapshot（HA 必备）

```bash
# 手动
sudo k3s etcd-snapshot save

# 定时任务（默认 cron：每天 0:00, 8:00, 16:00）
# /etc/rancher/k3s/config.yaml
etcd-snapshot-schedule-cron: "0 */6 * * *"   # 每 6 小时
etcd-snapshot-retention: 10                   # 保留 10 个
etcd-snapshot-s3: true                        # 上传到 S3（需额外配置）
etcd-snapshot-s3-bucket: my-k3s-snapshots
etcd-snapshot-s3-folder: prod
```

恢复：

```bash
sudo systemctl stop k3s
sudo rm -rf /var/lib/rancher/k3s/server/db
sudo k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/<snapshot-name>
```

### 5.3 升级 K3s

```bash
# 服务端 + 节点一起升
curl -sfL https://get.k3s.io | sh -

# server 之间会自动升级，agent 由 server 推送
```

> 升级顺序：先 server，再 agent。

### 5.4 K3s 二进制直接调用

```bash
k3s server                  # 在前台启动 server
k3s agent                   # 在前台启动 agent
k3s kubectl get nodes       # 集群内置 kubectl

# 一些常用子命令
k3s crictl ps               # 容器运行时查看
k3s ctr -n k8s.io images ls # 镜像列表
```

---

## 6. K3s 上装 Helm

```bash
# 安装 Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 加 Rancher 仓库
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add jetstack https://charts.jetstack.io
helm repo add longhorn https://charts.longhorn.io
helm repo update
```

---

## 7. 备份恢复方案

| 数据 | 备份方式 |
| --- | --- |
| **集群状态（etcd）** | k3s etcd-snapshot → 本地 / S3 |
| **应用数据（DB 卷等）** | Longhorn Backup / Restic → NFS / S3 |
| **Helm / manifests 配置** | Git 仓库（GitOps 推荐） |
| **镜像** | Harbor 内置 replication 到备份仓库 |

---

## 8. 常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| kubectl 报 `connection refused` | K3s 没起来 | `systemctl status k3s` |
| `traefik` 默认占 80/443 | K3s 内置 | `--disable=traefik` 自己装 Nginx Ingress |
| LoadBalancer Service 一直 pending | servicelb 没启用 | `--disable=servicelb` 后需装 MetalLB |
| NetworkPolicy 不生效 | Flannel 不支持 | 换 Calico / Cilium |
| 高可用集群脑裂 | server 数 < 3 | 加 server 节点，奇数台 |
| 离线装失败 | 镜像包没放对路径 | 确认为 `/var/lib/rancher/k3s/agent/images/` |
| 升级后 API 不兼容 | 上游 K8s 删除 alpha | 看 K3s release notes |

---

## 9. 一句话总结

- **K3s = 上游 K8s 的精简版**，单二进制、低资源、易上手，对小企业**最实用**
- 默认 `traefik + servicelb + local-path + metrics-server`，生产按需替换
- HA 用 **3/5 台 server + 嵌入式 etcd**，配置 `--cluster-init`
- 备份用 `k3s etcd-snapshot`，配置好 cron + S3 即可