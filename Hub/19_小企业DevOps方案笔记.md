# 小企业 DevOps 方案笔记（50~500 技术人员）

> 来自 [[Hub/18_DevOps基础与文化笔记]] 的延伸。这一规模比前面 K3s+Rancher 笔记里提到的"10~30 节点"小企业大了一档——通常有 3~10 个产品线、多团队、多环境。

---

## 1. 典型画像

### 1.1 规模指标

```text
技术人员：        50~500 人
业务产品线：       3~10 个
服务数量：        50~500 个（含微服务 / 单体服务）
迭代并行：        多个产品线同时推进
环境数量：        dev / staging / pre-prod / prod 至少 4 套
发布频率：        一日多次（小变更）/ 一天一两次（中等变更）
可用性要求：      99.5%~99.95%（SLA 4~9 个 9 / 月宕机分钟数）
```

### 1.2 典型组织

- 多个产品研发小组：每组 5~15 人
- 公共团队：平台组 / SRE 组 / 安全组 / QA 组
- 业务职能：售前、售后、市场、法务
- 基础设施：1~3 个公有云（多云） + 自建机房（部分公司）

### 1.3 典型痛点

- 服务一多，环境/版本/CI 配置不一致
- 多个团队重复造轮子（各建各的 CI、各写各的发布脚本）
- 故障定位慢，链路长
- 安全合规靠人工审计，漏洞响应慢
- 新员工 oncall 成本高，制度不清晰

---

## 2. 主流方案对比

按"代码托管 + CI/CD + 部署"三大支柱，分为三大流派：

### 2.1 全栈商业平台（最快上手，预算敏感度低时考虑）

#### A. GitHub 一栈式

```text
GitHub              ← 代码托管 / PR / Issue
GitHub Actions      ← CI/CD（内置）
ArgoCD              ← K8s GitOps 部署
EKS / AKS / GKE     ← K8s 托管
```

| 优势 | 劣势 |
| --- | --- |
| 开发者最熟，文档生态最丰富 | GitHub Actions 成本高（大 monorepo） |
| PR/Code Review/Issue 流程完善 | 数据出企业，自托管困难 |
| Actions marketplace 插件多 | 多区域同步差 |
| 适合 IT 投资 < 团队规模，devops < 2 人 | 大型 monorepo 速度下降 |

#### B. GitLab CE/EE 自托管

```text
GitLab (CE / EE)      ← 代码 + Issue + Wiki + CI + Registry (内置)
ArgoCD                 ← K8s GitOps（可选）
K8s
```

| 优势 | 劣势 |
| --- | --- |
| 全部能力一个平台：CI / Registry / 安全扫描 / Issue | 升级痛苦（每版本都"半成品升级"） |
| 自托管：数据在自己手里 | EE 收费，CE 缺高级功能（多租户等） |
| 适合喜欢"少技术栈"团队 | 性能比专用工具稍差 |

#### C. Azure DevOps（微软生态）

```text
Azure DevOps Repos   ← Git
Azure DevOps Pipelines
Azure DevOps Artifacts
Azure Kubernetes Service + ArgoCD
```

| 优势 | 劣势 |
| --- | --- |
| 与 Azure / .NET 生态无缝 | 跨云弱 |
| 自带测试管理 / 制品库 / Wiki | 配置较复杂 |
| Build 分钟数对微软内部免费 | 商业版价格高 |

---

### 2.2 全开源 / 自托管（推荐给小规模技术团队）

#### 方案 D. "Gitea + Jenkins + Tekton + ArgoCD + K3s"

```text
Gitea (代码托管)                       ↘
Drone / Jenkins (CI)  ─────────► Harbor (镜像仓库) ──► ArgoCD ──► K8s
Tekton (云原生 CI 可选)              ↗
```

| 优势 | 劣势 |
| --- | --- |
| 完全可控、所有数据自持 | 运维成本（要管多个组件） |
| 工具都是顶流开源 | 需要有平台工程团队（2~5 人） |
| 灵活：可换组件 | 文档相对不如商业产品一致 |

#### 方案 E. "GitHub + Jenkins + ArgoCD + K8s（混合）"

```text
GitHub               ← 代码托管（不放心企业用公网的可考虑 Gitea 替代）
Jenkins              ← CI（Jenkins on K8s）
ArgoCD               ← K8s GitOps
K8s
```

> 详细配置见前面 [[Hub/15_Jenkins基础笔记]] ~ [[Hub/17_运维生产方案总览]]。

---

### 2.3 决策树

```text
Q1: 必须数据私有 / 合规要求本地部署？
├─ 是 → Q2
└─ 否 → Q3

Q2: 是否有 2~5 人专职平台工程团队？
├─ 是 → 方案 D（全开源）
└─ 否 → 方案 B（GitLab 自托管）+ ArgoCD

Q3: 是否依赖 Azure / 微软生态？
├─ 是 → Azure DevOps
└─ 否 → Q4

Q4: 团队是否熟悉 GitHub？
├─ 是 → GitHub + ArgoCD
└─ 否 → GitLab 一栈式
```

---

## 3. 落地架构

### 3.1 经典分层视图

```text
                ┌──────────────────────────────────────────────────┐
                │     业务交付层（Developer Experience）              │
                │  Backstage / 内部门户 / 新服务脚手架                │
                └──────────────────────────────────────────────────┘
                                  ↑
                ┌─────────────────┴──────────────────────────────┐
                │     持续交付层（CD）                              │
                │  ArgoCD / Flux / Spinnaker + 灰度发布                │
                │  + 制品签名（Cosign）+ 安全门禁（Kyverno/OPA）         │
                └─────────────────┬──────────────────────────────┘
                                  ↑
                ┌─────────────────┴──────────────────────────────┐
                │     持续集成层（CI）                              │
                │  Jenkins / GitHub Actions / Tekton                │
                │  + 单元测试 + 集成测试 + 镜像构建 + 漏洞扫描         │
                └─────────────────┬──────────────────────────────┘
                                  ↑
                ┌─────────────────┴──────────────────────────────┐
                │     源代码层（SC）                                │
                │  GitHub / GitLab / Gitea                          │
                │  + 评审流程 + 分支策略                            │
                └──────────────────────────────────────────────────┘

                ┌──────────────────────────────────────────────────┐
                │     平台底层（Platform）                            │
                │  K8s / 服务网格 / 存储 / 网络 / 证书管理               │
                └──────────────────────────────────────────────────┘

                ┌──────────────────────────────────────────────────┐
                │     可观测性层（Observability）                     │
                │  Metrics（Prometheus）+ Logs（Loki）+ Traces（Jaeger）│
                │  + 告警（Alertmanager / PagerDuty）                │
                └──────────────────────────────────────────────────┘
```

### 3.2 典型组合（A 方案：GitHub 一栈式）

```text
代码：   GitHub Enterprise（自托管 GitHub Connect）
CI：     GitHub Actions（含 self-hosted runner）
镜像：   AWS ECR / Azure ACR / Harbor
CD：     ArgoCD（K8s GitOps）
集群：   EKS / AKS
可观测：Datadog 或 New Relic（商业）
或：     Grafana Cloud（含 LGTM 栈）
```

---

## 4. 多环境与多集群

### 4.1 环境分层

| 环境 | 用途 | 数据 | 谁能部署 |
| --- | --- | --- | --- |
| **dev** | 开发者自测 | 假数据 | 任何人 |
| **staging** | QA 测试 / 集成测试 | 假数据或脱敏生产数据 | QA + 研发 |
| **pre-prod** | 上线前最终验证 | 脱敏数据 | Release Manager |
| **prod** | 生产 | 真实数据 | 自动化或人工审批 |

### 4.2 多集群

50~500 人通常 1~5 个生产集群：

```text
- dev cluster（开发）
- staging cluster（QA）
- prod-east cluster（生产主）
- prod-west cluster（生产灾备/灰度）
```

管理方式：

| 工具 | 特性 |
| --- | --- |
| **Rancher** | 多集群 UI / 应用商店 / GitOps 引擎 Fleet |
| **Cluster API** | 声明式集群生命周期 |
| **Clusterpedia** | 跨集群资源查询 |
| **ArgoCD ApplicationSet** | 跨集群同一应用同步 |

---

## 5. 分支策略

### 5.1 trunk-based（推荐小企业）

```text
main（主干，受保护）
  ├── feature/xxx（短命分支，1~3 天合并）
  └── hotfix/xxx（紧急修复）

策略：
  - 小批量合并，频繁集成
  - 配合 feature flag 控制风险
  - 不需要 release 分支
```

**优势**：CI/CD 简单、减少分支冲突

### 5.2 GitFlow（复杂产品 / 严格管控）

```text
main（生产）
  ├── develop（集成）
  │    ├── feature/xxx
  │    ├── release/x.x（冻结）
  │    └── bugfix/xxx
  └── hotfix/xxx（生产紧急修复）
```

**适用**：版本化产品（如 SDK、桌面软件）或者严格管控的金融场景

### 5.3 GitHub Flow（互联网产品）

```text
main
  └── feature/xxx（提交 → PR → review → merge → 自动部署）
```

**适用**：互联网产品、SaaS、CD 工具链成熟

> **决策**：
>
> - 持续交付 + 单一版本 → trunk-based
> - 多版本并存 → GitFlow
> - 团队只想用最简单的 → GitHub Flow

---

## 6. 服务网格与服务治理

### 6.1 服务网格适用场景

服务网格（Service Mesh）= 把服务间通信从应用层抽到基础设施层（sidecar）。

**适用**：

- 服务数量 > 30
- 多语言（Java / Go / Python / Node 混用）
- 需要 mTLS、流量管理、可观测性而不改应用代码

**不适用**：

- < 10 个服务
- 单一语言已经能搞定

### 6.2 选型

| 网格 | 优势 | 适用 |
| --- | --- | --- |
| **Istio** | 功能最全 | 大型、复杂需求 |
| **Linkerd** | 轻量、rust 数据面 | 中小企业首选 |
| **Cilium Service Mesh** | 内核层、eBPF、性能好 | 云原生 + 网络要求高 |

> 中小企业推荐从 **Linkerd** 起步；规模上去再考虑 Istio。

---

## 7. 团队模型与组织

### 7.1 Team Topologies（推荐）

4 类团队：

```text
┌───────────────────────────────────────────────────┐
│ Stream-aligned team（业务流团队）                      │
│   - 直接交付业务价值（5~9 人）                          │
│   - 包含：PM + 后端 + 前端 + QA（可能 oncall）         │
└───────────────────────────────────────────────────┘
            │                │
            ▼                ▼
┌──────────────────┐  ┌──────────────────────────┐
│ Platform team    │  │ Enabling team            │
│  - 提供 IDP      │  │  - 帮业务团队能力建设       │
│  - Backstage     │  │  - 教练 / SRE             │
│  - CI/CD 模板    │  └──────────────────────────┘
└──────────────────┘

特殊：Complicated-subsystem team
  - 处理复杂专门系统（ML、密码学、搜索引擎等）
```

### 7.2 SRE 团队规模

依据 Google《Site Reliability Engineering》：

> SRE 团队 = 50% ~ 100% × 研发团队总人数（业务复杂、可靠性要求高时更多）

50~500 人技术团队，建议 SRE / 平台团队 5~15 人。

---

## 8. 监控与 SLO

### 8.1 SLI/SLO 框架

```text
SLI（指标）：例如「请求延迟 P99」
SLO（目标）：例如「99.9% 请求延迟 P99 < 200ms」
SLA（协议）：对客户的承诺，含后果

Error Budget = 1 - SLO
  → 错误预算消耗完时，冻结新功能发布，专注稳定性
```

### 8.2 推荐目标

| 场景 | SLO 建议 |
| --- | --- |
| **Web API** | 可用性 99.9% / 延迟 P95 < 200ms |
| **Web API（强 SLA）** | 可用性 99.95% / 延迟 P95 < 100ms |
| **后台 Job** | 完成率 99.5%（含重试） |
| **数据 Pipeline** | 当日完成率 > 95% |

### 8.3 监控维度

- **RED**（服务）：Rate / Errors / Duration
- **USE**（资源）：Utilization / Saturation / Errors
- **Four Golden Signals**：Latency / Traffic / Errors / Saturation

工具：Prometheus + Grafana + Alertmanager（成熟自建）；Datadog / New Relic / Grafana Cloud（商业 SaaS）

---

## 9. 安全与合规

### 9.1 软件供应链安全（SLSA）

| 级别 | 含义 |
| --- | --- |
| **SLSA 1** | 基础 CI、签名镜像 |
| **SLSA 2** | 受控构建环境、签名证明 |
| **SLSA 3** | 防篡改构建 |
| **SLSA 4** | 双人审计、最高保障 |

建议小企业先到 SLSA 2。

### 9.2 安全工具链

| 阶段 | 工具 |
| --- | --- |
| 代码 | Snyk / CodeQL / GitGuardian（密钥检测） |
| 镜像 | Trivy / Anchore / Clair |
| 运行 | Falco / Tracee（运行时异常） |
| 策略 | OPA / Kyverno / Gatekeeper |
| 依赖 | Dependabot / Renovate |
| 网络 | Cilium / Calico NetworkPolicy |

### 9.3 合规模型

| 标准 | 适用 |
| --- | --- |
| **SOC 2** | 通用 SaaS |
| **ISO 27001** | 行业通用 |
| **等保** | 国内强制（按等级） |
| **GDPR / CCPA** | 涉及欧盟 / 加州用户 |
| **PCI-DSS** | 涉及支付 |

---

## 10. 成本管理

### 10.1 FinOps（云财务）

3 大能力：

1. **Inform**：成本可见（每服务、每团队）
2. **Optimize**：节省成本（Spot 实例、预留实例、自动关停）
3. **Operate**：组织流程（成本问责）

工具：

- **云原生**：KubeCost / OpenCost（开源）
- **商业**：CloudHealth / Vantage / Harness CCM

### 10.2 常见节省手段

| 手段 | 节省 |
| --- | --- |
| Spot 实例 | 60%~90% |
| 预留 / Saving Plan | 30%~60% |
| 自动关停 dev/staging | 60%~80% |
| 镜像瘦身 | 镜像分发时间 ↓ |
| HPA + VPA | 弹性避免过度配置 |

---

## 11. 演进路线（24 个月建议）

```text
Month 1~3：基线
  - Git 流程规范化
  - CI 覆盖率达到 80%
  - 接入基础监控（APM）

Month 4~6：标准化
  - 镜像化所有服务
  - 公共 Helm Chart / 模板
  - IaC（Terraform）管云资源

Month 7~12：治理
  - GitOps（ArgoCD）+ App-of-Apps
  - SLO 全面定义
  - 安全门禁（Trivy + Kyverno）
  - Harbor 漏洞门禁

Month 13~18：平台化
  - Backstage IDP
  - 自服务化
  - 共享 oncall 流程

Month 19~24：精进
  - 混沌工程（Chaos Mesh / Litmus）
  - 服务网格（如需要）
  - AIOps / 容量规划
  - DORA 指标达到 Elite
```

---

## 12. 一句话总结

- 50~500 人企业目标：**稳 L3，进 L4**
- 主流方案：**GitHub / GitLab / 自托管全开源** 三选一
- 架构关键：CI + 制品 + CD + 可观测 + SLO 五件套
- 组织关键：业务流团队 + 平台团队 + SRE 文化
- 演进路径：从痛点切入，不一上来就上服务网格 + IDP