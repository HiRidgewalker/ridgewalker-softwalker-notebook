---
title: "DevOps 工具链对比笔记"
date: 2026-11-06
tags: ["Git","Docker","Kubernetes","Jenkins"]
---

# DevOps 工具链对比笔记

> 来自 [小企业DevOps方案笔记](./小企业DevOps方案笔记.md) 的延伸：按领域横向对比 8 个细分赛道的开源与商业选型。

---

## 1. 代码托管（Source Code Management）

| 工具 | 类型 | 简介 | 适用 |
| --- | --- | --- | --- |
| **GitHub** | 商业/SaaS + 自托管 EE | 最广泛的代码托管 + PR + Actions | 几乎全员 |
| **GitLab CE** | 开源 | 自托管"一体化平台" | 数据本地化、自托管 |
| **GitLab EE** | 商业 | CE + 安全/合规等高级能力 | 大企业、有预算 |
| **Gitea** | 开源/轻量 | 用 Go 写的迷你 GitHub | 资源受限、要轻量 |
| **Forgejo** | 开源 | Gitea 的社区分叉 | 同上、避免 Gitea 商业化 |
| **Bitbucket** | 商业/SaaS | Atlassian 生态 | 已用 Jira 的团队 |
| **Codeberg** | 开源/SaaS | 公益型 Forgejo | 个人/小团队 |
| **Sourcehut** | 开源/SaaS | 无 JS、邮件驱动 | 极简主义者 |

**选型建议**：

- 主流 SaaS 团队 → **GitHub**
- 自托管 / 数据本地化 → **GitLab CE** 或 **Gitea**
- 阿里云/腾讯云生态 → **CodeUp / TAPD**
- 已用 Jira → **Bitbucket**

---

## 2. CI（持续集成）

| 工具 | 类型 | 简介 | 适用 |
| --- | --- | --- | --- |
| **GitHub Actions** | SaaS + 自托管 runner | 内置 | GitHub 生态 |
| **GitLab CI** | 内置 | 自托管 / SaaS | GitLab 生态 |
| **Jenkins** | 开源/Java | 最老牌、插件最多 | 高度可定制 |
| **Drone** | 开源/Go | 容器化、易上手 | 中小项目 |
| **Woodpecker** | 开源 | Drone 的社区分叉 | 同上 |
| **Tekton** | 开源/Cloud Native | K8s 原生、CIDR | K8s 重度用户 |
| **CircleCI** | SaaS | 老牌、性能好 | 大 monorepo |
| **Buildkite** | SaaS + 自托管 agent | 灵活、CI as Code | 私有化 |
| **Argo Workflows** | 开源 | K8s 原生工作流 | 不只是 CI |
| **TeamCity** | 商业 | JetBrains 出品 | Kotlin/Java 团队 |

**选型建议**：

- 已用 GitHub → **GitHub Actions**（小项目）
- 已用 GitLab → **GitLab CI**
- K8s 重度 + 复杂流水线 → **Tekton** / **Argo Workflows**
- 复杂自定义 + 大量 plugin → **Jenkins**
- 中小团队 + 简单 + 容器原生 → **Drone** / **Woodpecker**

---

## 3. CD（持续部署）

| 工具 | 类型 | 简介 | 适用 |
| --- | --- | --- | --- |
| **ArgoCD** | 开源 | K8s GitOps 事实标准 | **K8s 首选** |
| **Flux CD** | 开源 | GitOps Toolkit，比 ArgoCD 轻 | 同上 |
| **Spinnaker** | 开源/Netflix 出品 | 多云部署、复杂发布策略 | 大型多云 |
| **Harness** | 商业 | 一站式 CD | 中大型 |
| **Codefresh** | 商业 | K8s CD | K8s 中型 |
| **Octopus Deploy** | 商业 | 传统应用部署 | .NET / 老系统 |
| **Flagger** | 开源 | ArgoCD 配套、灰度发布 | K8s + Argo |

**选型建议**：

- 用 K8s → **ArgoCD**（最稳）
- K8s + 需要轻量 → **Flux**
- 多云 + 复杂发布 → **Spinnaker**
- 商业、省心 → **Harness**

---

## 4. IaC（基础设施即代码）

| 工具 | 类型 | 简介 | 适用 |
| --- | --- | --- | --- |
| **Terraform** | 商业（MPL） | 行业标准 | 多云 |
| **OpenTofu** | 开源 | Terraform 1.5+ 的开源分叉 | 避免 HashiCorp 许可变更 |
| **Pulumi** | 开源/商业 | 用编程语言（TS/Go/Python）写 IaC | 程序员友好 |
| **Ansible** | 开源 | 配置管理 / 简单编排 | 配置管理、轻 IaC |
| **CloudFormation** | 商业（AWS 专） | AWS 原生 | AWS 单一云 |
| **ARM Template** | 商业（Azure 专） | Azure 原生 | Azure 单一云 |
| **CDK** | 商业 | CloudFormation 的编程版本 | 程序员 |
| **Crossplane** | 开源 | K8s 原生管理云资源 | K8s 生态 |
| **Helm** | 开源 | K8s 应用打包 | K8s 部署 |

**选型建议**：

- 多云 → **Terraform** / **OpenTofu**
- 单一云（AWS） → **CloudFormation** / **CDK**
- 程序员团队 → **Pulumi**
- 配置管理、运维自动化 → **Ansible**
- K8s 应用 → **Helm** + **Kustomize**

---

## 5. 容器镜像与制品库（Artifacts）

| 工具 | 类型 | 简介 | 适用 |
| --- | --- | --- | --- |
| **Harbor** | 开源/CNCF | 容器镜像 + 漏洞扫描 + 复制 | **首选**（见 [Harbor笔记](/harbor)） |
| **AWS ECR** | 商业 | AWS 容器镜像 | AWS 单云 |
| **Azure ACR** | 商业 | Azure 容器镜像 | Azure 单云 |
| **GCP Artifact Registry** | 商业 | GCP 镜像 | GCP 单云 |
| **Docker Hub** | SaaS | 公有 | 公开镜像 |
| **Nexus Repository** | 商业/OSS | 容器 + Maven + npm + PyPI 全能 | 多语言 |
| **Artifactory** | 商业 | 最全 | 商业重型 |
| **GitHub Packages** | SaaS | 与 GitHub 集成 | GitHub 用户 |

**选型建议**：

- 多语言、大企业 → **Nexus Repository** / **Artifactory**
- 纯容器镜像 → **Harbor**
- 单一云 → 用云厂商的（ECR/ACR）
- GitHub 项目 → **GitHub Container Registry**

---

## 6. 可观测性（Observability）

### 6.1 Metrics

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Prometheus** | 开源 | K8s 监控事实标准 |
| **VictoriaMetrics** | 开源 | 高性能 Prometheus 替代 |
| **Thanos** | 开源 | Prometheus 长期存储 |
| **Cortex** | 开源 | Prometheus 集群方案 |
| **InfluxDB** | 开源 | 时序数据库 |
| **Datadog** | SaaS | SaaS 一体化 |
| **New Relic** | SaaS | 老牌 APM |
| **Dynatrace** | SaaS | 企业级自动化 |
| **Splunk Observability** | SaaS | 来自 Splunk |
| **CloudWatch** | 商业 | AWS 原生 |
| **Azure Monitor** | 商业 | Azure 原生 |

### 6.2 Logs

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Loki** | 开源 | Grafana 全家桶 |
| **ELK Stack** | 开源 | 经典（Elasticsearch + Logstash + Kibana） |
| **OpenSearch** | 开源 | ES 分叉（合规） |
| **Grafana Enterprise Logs** | 商业 | Grafana 商业版 |
| **Splunk** | 商业 | 商业重型 |
| **Datadog Logs** | SaaS | 商业 |

### 6.3 Traces

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Jaeger** | 开源 | CNCF 毕业 |
| **Tempo** | 开源 | Grafana 出品 |
| **Zipkin** | 开源 | 老牌（Twitter） |
| **OpenTelemetry** | 开源/CNCF | 标准化采集 SDK |
| **Datadog APM** | SaaS | 商业 |
| **New Relic APM** | SaaS | 商业 |

### 6.4 整合方案

- **Grafana Stack（LGTM + Prometheus）**：最常见的自建
- **Datadog**：一体化 SaaS
- **New Relic**：一体化 SaaS
- **Dynatrace**：企业级

**选型建议**：

- 完全自建、Grafana + Loki + Tempo + Prometheus
- 省心、大预算 → Datadog
- 多云混合 → Dynatrace
- Java 重 → New Relic

---

## 7. 告警（Alerting）

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Alertmanager** | 开源 | Prometheus 标配 |
| **Grafana Alerting** | 开源 | Grafana 内置 |
| **Grafana OnCall** | 开源/商业 | 值班调度 |
| **PagerDuty** | SaaS | 值班调度之王 |
| **OpsGenie** | SaaS | 现被 Atlassian 收，集成 Jira |
| **钉钉 / 飞书 / 企微 机器人** | SaaS | 国内常用 webhook |
| **Telegram / Slack** | SaaS | 国际常用 |
| **Pager** | 开源 | 老牌，PagerDuty 替代品 |

---

## 8. 安全（Security Toolchain）

### 8.1 代码 SAST

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **CodeQL** | 开源/商业 | GitHub 内置 |
| **Snyk Code** | 商业 | 多语言 |
| **SonarQube** | 开源/商业 | 自托管经典 |
| **Semgrep** | 开源 | 轻量规则引擎 |
| **Bandit** | 开源 | Python 专用 |
| **gosec** | 开源 | Go 专用 |
| **Checkov** | 开源 | IaC 安全（Terraform） |

### 8.2 镜像 / 容器

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Trivy** | 开源 | 全能扫描器（见前文） |
| **Snyk Container** | 商业 | 商业加固 |
| **Clair** | 开源/CNCF | 静态分析 |
| **Anchore** | 开源/商业 | 深度合规 |
| **Docker Scout** | SaaS | Docker 官方 |

### 8.3 运行时

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Falco** | 开源/CNCF | 运行时安全（syscall） |
| **Tracee** | 开源 | eBPF 运行时安全 |
| **Tetragon** | 开源 | Cilium 出品 eBPF |
| **Aqua Security** | 商业 | 重型商业 |
| **Prisma Cloud** | 商业 | Palo Alto |

### 8.4 策略 / 合规

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **OPA** | 开源 | 策略引擎（Rego） |
| **Gatekeeper** | 开源 | OPA in K8s |
| **Kyverno** | 开源 | K8s 策略，YAML 友好 |
| **Conftest** | 开源 | OPA CLI 测试 |
| **Falco Rules** | 开源 | Falco 默认规则 |

### 8.5 密钥 / Secret

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **HashiCorp Vault** | 开源 | 业界标准 |
| **Sealed Secrets** | 开源 | Bitnami 出品 |
| **External Secrets Operator** | 开源 | 集成云厂商 Secrets |
| **AWS Secrets Manager** | 商业 | AWS 集成 |
| **Azure Key Vault** | 商业 | Azure 集成 |

### 8.6 依赖

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Dependabot** | SaaS | GitHub 内置 |
| **Renovate** | 开源 | 自托管 / SaaS |
| **Snyk Open Source** | 商业 | 含已知漏洞库 |
| **OWASP Dependency-Check** | 开源 | Java/Node/.NET |

**选型建议**：

- 小企业最小集：**Trivy** + **Renovate/Dependabot** + **Vault** + **Kyverno**
- 中型：+ **Snyk** + **Falco** + **OPA**

---

## 9. 服务网格（Service Mesh）

| 工具 | 类型 | 数据面 |
| --- | --- | --- |
| **Istio** | 开源/Envoy | Envoy（功能最强） |
| **Linkerd** | 开源/Conduit | Linkerd-proxy（轻量） |
| **Consul Connect** | 商业/HashiCorp | Envoy |
| **Cilium Service Mesh** | 开源 | eBPF（内核） |
| **Kuma** | 开源 | Envoy |
| **AWS App Mesh** | 商业 | Envoy |

**选型建议**：

- 中小规模 → **Linkerd**（轻量） 或 **Cilium**（性能）
- 大规模 + 复杂 → **Istio**
- 单云 + 已用 ASM → **AWS App Mesh**

---

## 10. 多集群管理（Multi-Cluster Orchestration）

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Rancher** | 开源/商业 | 见 [IV_Rancher笔记](/kubernetes/04-rancher) |
| **Cluster API** | 开源/K8s sig | 声明式 K8s 集群生命周期 |
| **Clusterpedia** | 开源 | 跨集群查询 |
| **ArgoCD ApplicationSet** | 开源 | ArgoCD 多集群部署 |
| **Rafay** | SaaS/商业 | 企业级 |
| **Nirmata** | SaaS/商业 | 企业级 |

---

## 11. 平台工程 / IDP

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Backstage** | 开源/CNCF | Spotify 出品，事实标准 |
| **Compass** | SaaS | Atlassian |
| **Port** | SaaS | 商业 |
| **Cortex** | SaaS | 商业 |
| **Roadmap.sh** | 开源/Wiki | 简单 |

---

## 12. 混沌工程（Chaos Engineering）

| 工具 | 类型 | 简介 |
| --- | --- | --- |
| **Chaos Monkey** | 开源/Netflix | 杀实例 |
| **Chaos Mesh** | 开源/PingCAP | K8s 混沌 |
| **LitmusChaos** | 开源/CNCF | K8s 混沌 |
| **Gremlin** | SaaS | 商业 |
| **ChaosBlade** | 开源/阿里 | 国内通用 |

---

## 13. 选型速查（按主题一图一表）

```text
代码：   GitHub / GitLab CE / Gitea
CI：     GitHub Actions / GitLab CI / Tekton / Jenkins
CD：     ArgoCD / Flux / Harness
IaC：   Terraform / OpenTofu / Pulumi
镜像：   Harbor / ECR / Nexus
日志：   Loki / ELK
指标：   Prometheus + Grafana
链路：   Tempo / Jaeger / OpenTelemetry
告警：   Alertmanager + PagerDuty / 飞书
镜像扫描：Trivy / Snyk
运行时：Falco / Tetragon
策略：  Kyverno / OPA
密钥：   Vault
Mesh：  Linkerd / Istio / Cilium
多集群：Rancher / ClusterAPI
IDP：   Backstage
混沌：  Chaos Mesh / Litmus
```

---

## 14. 一句话总结

- **小企业**：开源工具够用，重点在**整合**而非单一工具好坏
- **17 个细分领域**只是参考，实际企业只用到 5~8 个核心
- 选型原则：
  1. 先用主流（Jenkins / ArgoCD / Trivy / Prometheus），少创新
  2. 自托管 vs SaaS 看团队规模与合规
  3. 工具要**统一生态**（如 Grafana 全家桶 / Datadog 一体化）
  4. **可替换性**：每层解耦，避免绑死某家

标签：#git #docker #kubernetes #jenkins
