# Kubernetes 部署特性笔记

> 来自 [[I_Kubernetes基础笔记]] 的延伸：部署一个 K8s 应用到底需要哪些对象与机制。

---

## 1. 资源对象总图

按用途分组：

```text
                  ┌─── 部署模型 ────┐
                  │ Deployment     │  ← 无状态服务（Web/API）
                  │ StatefulSet    │  ← 有状态服务（DB/消息队列）
                  │ DaemonSet      │  ← 节点级（日志收集/网络代理）
                  │ Job / CronJob  │  ← 一次性 / 定时任务
                  └────────────────┘
                  ┌─── 服务发现 ────┐
                  │ Service        │  ← 稳定 IP + 端口
                  │ Ingress        │  ← 7 层路由
                  │ Headless Service│ ← 配合 StatefulSet
                  └────────────────┘
                  ┌─── 配置与密文 ────┐
                  │ ConfigMap      │  ← 普通配置
                  │ Secret         │  ← 敏感（仅 base64）
                  └────────────────┘
                  ┌─── 存储 ────────┐
                  │ PersistentVolume / PVC / StorageClass
                  └────────────────┘
                  ┌─── 弹性 ────────┐
                  │ HPA / VPA / Cluster Autoscaler
                  └────────────────┘
                  ┌─── 调度 ────────┐
                  │ NodeSelector / Affinity / Taint + Toleration
                  └────────────────┘
                  ┌─── 安全 / 隔离 ─────┐
                  │ RBAC / NetworkPolicy / PodSecurity
                  └────────────────┘
```

---

## 2. 部署模型

### 2.1 Deployment（最常用，无状态）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1               # 多于期望副本的最大值
      maxUnavailable: 0         # 不可用副本的最大值（推荐 0）
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: myapp:v1
          ports:
            - containerPort: 8080
          resources:
            requests:           # 调度依据
              cpu: 100m
              memory: 128Mi
            limits:             # 硬上限（OOM 会杀）
              cpu: 500m
              memory: 512Mi
          readinessProbe:       # 就绪探针：通过则接流量
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:        # 存活探针：失败则重启
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
          env:
            - name: TZ
              value: Asia/Shanghai
            - name: DB_URL
              valueFrom:
                configMapKeyRef:
                  name: web-config
                  key: db_url
          volumeMounts:
            - name: data
              mountPath: /app/data
      volumes:
        - name: data
          emptyDir: {}
      imagePullSecrets:
        - name: harbor-pull-secret
```

#### 探针

| 类型 | 作用 | 失败时 |
| --- | --- | --- |
| readinessProbe | 是否就绪到接流量 | 从 Service endpoints 摘掉 |
| livenessProbe | 是否存活 | 容器重启 |
| startupProbe | 启动期探测（避免启动慢被 liveness 误杀） | 没准备好不算 ready |

#### 资源 requests vs limits

```text
requests = 调度的最小值（scheduler 据此决定放哪个节点）
limits   = 运行时的上限（超过会节流 [cpu] / OOM [memory]）
```

**生产必须设**，否则 OOM 时随机杀容器，难定位。

#### 优雅停机

```yaml
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - name: web
      lifecycle:
        preStop:
          exec:
            command:
              - /bin/sh
              - -c
              - "sleep 5"        # 给 Service endpoint 摘流量留时间
```

### 2.2 StatefulSet（有状态：固定网络 ID + 稳定存储）

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres           # Headless Service 名
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:           # 每个 Pod 自动一份
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: longhorn
        resources:
          requests:
            storage: 10Gi
```

**特征**：

- Pod 名固定为 `postgres-0 / -1 / -2`
- Headless Service 给每个 Pod 一个 DNS 记录：`postgres-0.postgres.default.svc.cluster.local`
- 每个 Pod 有独立 PVC（`volumeClaimTemplates`）

### 2.3 DaemonSet（节点级守护进程）

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true           # 用主机网络（节点端口）
      containers:
        - name: exporter
          image: prom/node-exporter:v1.8
          ports:
            - containerPort: 9100
              hostPort: 9100
```

每节点跑一份，常用于节点监控、日志采集、CNI 插件。

### 2.4 Job / CronJob

```yaml
# Job：一次性任务，成功结束
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
spec:
  completions: 1
  backoffLimit: 3
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: job
          image: myapp-migrate:v1
          args: ["migrate", "--once"]

---
# CronJob：定时
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup
spec:
  schedule: "0 3 * * *"           # 每天凌晨 3 点
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cleanup
              image: myapp-cli:v1
              args: ["cleanup"]
```

---

## 3. Service 与 DNS

### 3.1 Service 类型

| 类型 | 用途 | 集群外可达 |
| --- | --- | --- |
| ClusterIP | 集群内部访问（默认） | ❌ |
| NodePort | 节点端口暴露（30000-32767） | ✅（任意节点 IP） |
| LoadBalancer | 云厂商 / MetalLB 分配外部 IP | ✅ |
| ExternalName | CNAME 别名（外部服务） | ✅（DNS 别名） |
| Headless（clusterIP: None） | 直连 Pod IP（StatefulSet 等） | ❌（但每个 Pod 有 DNS） |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
      name: http
```

### 3.2 DNS 解析规则（Pod 里）

```text
service-name                    → 同 namespace 内 ClusterIP
service-name.namespace          → 跨 namespace
pod-ip.d.namespace.pod.cluster.local   → Pod 访问（StatefulSet）
```

### 3.3 Endpoints / EndpointSlice

Service 自动维护一个 `Endpoints`（旧）或 `EndpointSlice`（新），列出所有被选中的 Pod IP。

```bash
kubectl get endpoints web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

---

## 4. Ingress

Service 提供 L4 负载均衡，**Ingress 提供 L7 路由（HTTP/HTTPS）**。

### 4.1 需要 Ingress Controller

Ingress 资源只是声明，**实际流量转发由 controller 处理**。常见：

- Nginx Ingress（最常用）
- Traefik（k3s 默认）
- HAProxy、Envoy 等

### 4.2 Ingress 资源示例

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - example.com
      secretName: example-tls
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 8080
```

### 4.3 自动证书：cert-manager

见后续 [[IV_Rancher笔记]] 中的"应用商店装 cert-manager"。

---

## 5. ConfigMap 与 Secret

### 5.1 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  db_url: "postgresql://db:5432/myapp"
  log_level: "info"
```

```yaml
# Pod 里使用
spec:
  containers:
    - name: web
      envFrom:
        - configMapRef:
            name: web-config
      volumeMounts:
        - name: cfg
          mountPath: /app/config
          readOnly: true
  volumes:
    - name: cfg
      configMap:
        name: web-config
```

### 5.2 Secret（只是 base64，不加密）

```bash
# 创建 secret
kubectl create secret generic db-cred \
  --from-literal=username=appuser \
  --from-literal=password=secret
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-cred
type: Opaque
data:
  # base64 编码
  username: YXBwdXNlcg==
  password: c2VjcmV0
stringData:                   # 明文，K8s 自动 base64
  username: appuser
```

```yaml
# Pod 使用
spec:
  containers:
    - name: web
      envFrom:
        - secretRef:
            name: db-cred
```

### 5.3 docker-registry 类型的 Secret（拉私有仓库镜像）

```bash
kubectl create secret docker-registry harbor-pull-secret \
  --docker-server=harbor.example.com \
  --docker-username=robot\$ci \
  --docker-password=xxxxxx \
  --docker-email=ci@example.com
```

```yaml
spec:
  imagePullSecrets:
    - name: harbor-pull-secret
```

> 详细见 [[05_Harbor笔记]]。

---

## 6. 持久化存储

### 6.1 三层结构

```text
PV（PersistentVolume）──集群里的存储"供应"（类似磁盘）
PVC（PersistentVolumeClaim）──Pod 申请存储的"申请单"
StorageClass ──按需动态创建 PV 的"模板"
```

### 6.2 静态申请（手动建 PV）

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data   # 仅本机测试
```

### 6.3 动态申请（StorageClass）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
parameters:
  fsType: ext4
  numberOfReplicas: 3
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
```

Pod 内挂载后，StorageClass 自动让 Longhorn 创建真正的卷。

---

## 7. 弹性扩缩容

### 7.1 HPA（Horizontal Pod Autoscaler）

```bash
# 先确保 metrics-server 装好（K3s 默认带）
kubectl top nodes

# 创建 HPA
kubectl autoscale deploy web --min=2 --max=10 --cpu-percent=80
```

或者 YAML：

```yaml
apiVersion: autoscaling/v22
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue
          averageValue: 200Mi
```

### 7.2 VPA（Vertical Pod Autoscaler）

调整 Pod 的 resources requests/limits。HPA + VPA 不要同一指标并存。

### 7.3 Cluster Autoscaler

节点不够时自动扩节点（云厂商或自建 + K3s server `--node-taint`）。

---

## 8. 调度策略

### 8.1 NodeSelector（粗）

```yaml
nodeSelector:
  disktype: ssd
```

### 8.2 Affinity（细）

```yaml
affinity:
  podAntiAffinity:                    # 反亲和：分散到不同节点
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: web
          topologyKey: kubernetes.io/hostname
```

### 8.3 Taint & Toleration（驱逐）

```bash
# 在节点上打 taint
kubectl taint nodes node1 key=value:NoSchedule
```

```yaml
# Pod 容忍才能调度
tolerations:
  - key: key
    operator: Equal
    value: value
    effect: NoSchedule
```

| Effect | 含义 |
| --- | --- |
| NoSchedule | 不容忍就不调度（最弱） |
| PreferNoSchedule | 尽量不调度（更弱） |
| NoExecute | 不容忍则驱逐已有 Pod（最强） |

---

## 9. RBAC（权限控制）

### 9.1 最小例子：让某个 SA 只读 default ns

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: viewer
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: viewer-role
rules:
  - apiGroups: ["", "apps", "batch"]
    resources: ["pods", "services", "deployments", "jobs"]
    verbs: ["get", "list", "watch"]   # 只读
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: viewer-binding
  namespace: default
subjects:
  - kind: ServiceAccount
    name: viewer
    namespace: default
roleRef:
  kind: Role
  name: viewer-role
  apiGroup: rbac.authorization.k8s.io
```

### 9.2 ClusterRole / ClusterRoleBinding（跨 namespace）

授予集群级权限（如 K8s 节点管理）。生产对人类用户也用 Rancher/OIDC 对接。

---

## 10. NetworkPolicy

默认 K8s 网络互通，**生产一定要按 namespace 加 NetworkPolicy 限制**。

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-only
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress
        - podSelector:
            matchLabels:
              app: db
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: db
      ports:
        - port: 5432
```

> 需要支持 NetworkPolicy 的 CNI（Calico、Cilium）。Flannel 默认不支持。

---

## 11. PodSecurity

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    pod-security.kubernetes.io/enforce: restricted        # 强制
    pod-security.kubernetes.io/audit: restricted          # 审计
    pod-security.kubernetes.io/warn: restricted           # 警告
```

`restricted` 模式要求：

- 非 root 运行
- 限定 capabilities（如禁 NET_ADMIN）
- 只读 rootfs（部分场景）
- 不许特权（privileged: false）

---

## 12. 滚动升级策略

| 字段 | 默认 | 推荐 |
| --- | --- | --- |
| `maxSurge` | 25% | 1（即副本数 +1） |
| `maxUnavailable` | 25% | 0（零停机，但得有 readinessProbe） |

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

回滚：

```bash
kubectl rollout undo deploy/myapp
kubectl rollout undo deploy/myapp --to-revision=2
```

---

## 13. 一句话总结

- 部署一个 K8s 应用 = Deployment + Service + ConfigMap + PVC + healthcheck
- 入口流量 = IngressController + Ingress + （可选）cert-manager
- 生产必设：`resources requests/limits`、`readinessProbe / livenessProbe`、`NetworkPolicy`、`imagePullSecrets`
- 想要灵活扩缩上 HPA（K8s 推荐路线）；状态服务用 StatefulSet + Headless Service