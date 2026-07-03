# DevOps 基础与文化

> 原 `文档/DevOps.md` 的重新整理版本。DevOps 系列共 3 篇：本文是**概念与文化**；[[02_小企业DevOps方案笔记]] 是**50~500 人企业主流方案**；[[03_DevOps工具链对比笔记]] 是**工具链横向选型参考**。原笔记保留在 `文档/DevOps.md` 供回溯。

---

## 1. DevOps 是什么

### 1.1 定义

**DevOps** 是 Development（开发）+ Operations（运维）的合并缩写，是一套**文化、实践与工具**的组合，目标是**缩短系统变更从提交到上线的时间，同时保证质量与稳定性**。

核心思想：

- 打破开发与运维之间的「墙」
- 把交付过程**自动化、可重复**
- 用**反馈回路**持续改进
- 把**可靠性**当成产品的一部分（而非事后靠运维救火）

### 1.2 不是什么

- ❌ 不是某种职位（「DevOps 工程师」）— DevOps 是文化与实践，单设一个职位意味着 DevOps 失败
- ❌ 不是某个工具（Jenkins / Docker / K8s 都只是支撑）
- ❌ 不是只搞 CI/CD（CI/CD 只是其中一环）
- ❌ 不是运维工程师 + 几个脚本

### 1.3 一句话总结

> DevOps = **让交付从「靠人堆」变成「靠系统自动化」，把责任从运维单独背变成开发从始至终一起承担**。

---

## 2. DevOps 的核心价值

### 2.1 三大指标（Westrum 指标 / DORA）

Google DORA 团队对软件交付效能的多年研究总结出 4 个指标：

| 指标 | Elite | Low | 含义 |
| --- | --- | --- | --- |
| **部署频率（Deployment Frequency）** | 按需（一天多次） | 几个月一次 | 发布节奏 |
| **变更前置时间（Lead Time for Changes）** | < 1h | > 1 month | 从 commit 到 production |
| **变更失败率（Change Failure Rate）** | 0~15% | 46~60% | 上线后回滚或修复的比例 |
| **故障恢复时间（MTTR）** | < 1h | > 1 month | 出问题到恢复 |

> Elite vs Low 的企业，运营表现有 30~50 倍差距（事故数、可用性、业务连续性）。

### 2.2 商业价值

- **更快交付**：小步快跑，缩短 idea-to-prod 周期
- **更高稳定性**：自动化测试 + 灰度发布 + 快速回滚
- **更低成本**：减少救火 SLA、减少返工
- **更高研发幸福感**：开发者不再怕上线、值班更有方向
- **组织敏捷**：应对市场变化更快

---

## 3. CALMS 框架

CALMS 是 Damon Edwards 提出的 DevOps 文化框架：

| 字母 | 含义 | 体现 |
| --- | --- | --- |
| **C**ulture | 文化 | 跨职能合作、无指责复盘、共享 oncall |
| **A**utomation | 自动化 | CI/CD、IaC、测试自动化、监控告警自动化 |
| **L**ean | 精益 | 减少浪费（小批量、限制在制品 WIP） |
| **M**easurement | 度量 | DORA 指标、SLI/SLO、用户业务指标 |
| **S**haring | 共享 | 共享库、Wiki、复盘文档、内部技术会议 |

> 文化先行（C），技术与工具是支撑（ALMS）。**只买工具不改文化 → 工具用不起来**。

---

## 4. DevOps 成熟度模型

按阶段划分（0~5）：

| 级别 | 名称 | 特征 |
| --- | --- | --- |
| **L0** | 手动时代 | 手动部署、手动测试、FTP 推代码 |
| **L1** | 脚本化 | Bash 脚本、cron、基础监控 |
| **L2** | CI/CD | Jenkins/GitHub Actions 自动化构建+测试 |
| **L3** | IaC + 可观测 | Terraform/Ansible；Prometheus + Grafana；ELK |
| **L4** | GitOps + 服务网格 + SLO | ArgoCD/Flux；Istio；SLO 管理；灰度发布 |
| **L5** | 自服务 IDP + AIOps | Backstage 内部开发者平台；自动扩缩容；AIOps 异常检测 |

> **小企业（50~500 技术人员）目标**：**稳定 L3，争取 L4**。L5 是巨型企业的游戏。

---

## 5. DevOps vs SRE vs Platform Engineering

近年来兴起的几个相邻概念容易混淆：

### 5.1 DevOps

- **范围**：文化 + 工具 + 实践
- **关注点**：整个交付链路
- **组织意义**：跨职能合作
- **负责人**：人人（不是某个团队）

### 5.2 SRE（Site Reliability Engineering，源自 Google）

- **范围**：生产环境的**可靠性**工程
- **关注点**：SLO/SLA、错误预算（Error Budget）、oncall、事后复盘（Postmortem）
- **角色**：SRE Engineer（实际岗位）
- **经典指标**：可用性 MTTR MTBF
- **典型实践**：
  - SLO 定义（99.9% 可用 = 每月允许 43 分钟宕机）
  - Error Budget 消耗 100% 后，冻结发布
  - Toil（手动工作）控制
- **与 DevOps 的关系**：SRE 是 DevOps 在「运营可靠性」方向的**具体落地**

### 5.3 Platform Engineering（平台工程，2022+ 兴起）

- **范围**：搭建**内部开发者平台**（IDP）
- **关注点**：让开发者**自助**完成常见任务（新服务创建、CI 模板、部署、监控接入）
- **代表工具**：**Backstage**（Spotify 开源 IDP）
- **与 DevOps 的关系**：当 DevOps 文化成熟后，组织会自然演化出"平台团队"专门搭建 IDP
- **与 SRE 关系**：平台工程给开发者**自助工具**，SRE 确保**生产可靠性**

### 5.4 三者关系图

```text
                ┌──────────────────────────┐
                │      DevOps（文化层）      │
                │     跨职能协作 / 反馈       │
                └──────────┬───────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐        ┌──────────────────────┐
    │ SRE（可靠性层）    │        │ Platform Eng（平台层）│
    │ SLO / oncall /   │        │ Backstage / IDP /    │
    │ postmortem       │        │ 自服务化              │
    └──────────────────┘        └──────────────────────┘
```

> **实际分工**：DevOps 是思想，SRE 把「可靠性」做到极致，Platform Eng 把「自助化」做到极致。一个组织往往三者都有。

---

## 6. DevOps 与周边概念的关系

### 6.1 Agile（敏捷）

- 关注**需求与产品迭代**（Scrum / Kanban）
- DevOps 关注**开发到上线**的链路
- 二者**互补**：Agile 解决「做正确的事」，DevOps 解决「正确地做事」

### 6.2 Lean（精益）

- 起源于丰田生产方式
- DevOps 的"L"（Lean）：减少浪费（WIP）、缩短反馈
- 核心观点：**构建质量（Build Quality In）**，而非事后检测

### 6.3 持续集成（CI）

- **频繁合并代码**到主干，每次合并自动跑构建+测试
- 目标：早发现集成问题
- 是 DevOps 的"A"（Automation）层的一环

### 6.4 持续交付 / 持续部署（CD）

- **Continuous Delivery**：代码任何时候都可发布（人工决定何时发布）
- **Continuous Deployment**：自动化通过所有测试后**自动发布**到生产
- 与 CI 是同源概念

### 6.5 GitOps（详见 [[07_Jenkins_CICD实战笔记]] / [[02_小企业DevOps方案笔记]]）

- 以 Git 为单一真相源
- 通过 PR/MR 改动生产环境
- ArgoCD/Flux 是事实标准工具

---

## 7. 小企业（50~500 人）做 DevOps 的现实路径

### 7.1 当前痛点

- 产品迭代快，部署频率赶不上
- 服务一多，环境/版本混乱
- 故障定位慢，SLA 压力大
- 团队各自为政，没有标准化

### 7.2 落地顺序（按 ROI 由高到低）

```text
阶段 1（基础）：
  - Git 工作流规范化（trunk-based 或规范化的 GitFlow）
  - CI 流水线（PR 触发自动测试 + 自动化单测）
  - 基础监控（接入 APM、链路追踪）

阶段 2（演进）：
  - 镜像化所有服务 + K8s 容器化
  - CD 流水线（自动推镜像、自动部署）
  - IaC（Terraform 管理云资源）

阶段 3（治理）：
  - GitOps（ArgoCD + App-of-Apps）
  - SLO 管理 + Error Budget 流程
  - 安全门禁（Trivy、OPA、镜像签名）

阶段 4（平台化）：
  - Backstage IDP
  - 内部共享库、模板化新服务
  - AIOps、混沌工程、灰度发布
```

> **不要一上来就上服务网格 + IDP**，从最痛点（部署慢 / 故障多）切入。

### 7.3 关键组织变化

- **运维团队转型**：从「纯救火」变「平台建设 + SRE 兼 SRE 思路」
- **开发承担 oncall**：共同对生产负责
- **建立 blameless postmortem 文化**：复盘不追责，找系统问题
- **共享指标**：DORA 4 指标透明、考核按团队而非个人

---

## 8. 组织/团队模型

### 8.1 反向康威定律

**康威定律**："系统结构反映组织沟通结构"。

DevOps 时代常**反向**：先决定系统/团队结构，反过来调整组织：

- **微服务 = 小团队 + 全栈**：每个服务由一个 5~9 人小队全权负责（含 oncall）
- **平台团队**：构建 CI/CD 模板、可观测性、镜像仓库
- **产品团队**：聚焦业务，平台能力由平台团队提供

### 8.2 经典模型

| 模型 | 来源 | 适用 |
| --- | --- | --- |
| **Spotify 模型** | Spotify | 大型、矩阵化、产品线多 |
| **Team Topologies** | Skelton & Pais | 演化出 4 种团队类型：业务流、平台、赋能、复杂子系统 |
| **SRE 拓扑** | Google | 强 oncall 流程 |
| **Platform Engineering** | 2022+ 兴起 | 自服务化优先 |

> Team Topologies 4 类：
>
> - **Stream-aligned team**：业务流团队（按业务价值流）
> - **Platform team**：提供 IDP
> - **Enabling team**：传帮带
> - **Complicated-subsystem team**：复杂专门系统（如 ML 平台）

---

## 9. 一句话总结

- DevOps = 文化（CALMS）+ 自动化 + 度量 + 共享
- 目标：DORA 4 指标达到 Elite（部署频率高 / 前置时间短 / 变更失败率低 / MTTR 短）
- 区分 DevOps / SRE / Platform Engineering：文化 / 可靠性 / 自服务
- 小企业落地分阶段，从痛点切入（CI + 监控），再演进到 L3~L4（IaC + GitOps）