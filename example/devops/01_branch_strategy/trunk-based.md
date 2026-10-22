# Trunk-Based Development 实践指南

> 对应 [[小企业DevOps方案笔记]] 的 5.1 分支策略。
> 配合持续交付 / GitOps 较好。

## 核心思想

- **只有一条主分支（main / trunk）**，长期存活
- 所有开发用**短命分支**（feature/*，最好 < 3 天就合并）
- 配合 **Feature Flag**（开关）控制风险，不必"等发版"
- 任何时刻 main 都可发布

## 适用场景

- ✅ 持续部署（每天多次发布）
- ✅ SaaS / 互联网产品
- ✅ 多服务、团队规模中等
- ❌ 严格的多版本共存产品（如 SDK）→ 用 GitFlow
- ❌ 严格管控的金融场景 → GitFlow

## 工作流

```text
1. 从 main 拉分支
   git checkout -b feature/user-export main

2. 开发 + 小批量提交（多次提交，多次 push）

3. 持续同步主干（避免长时间分叉）
   git fetch origin
   git rebase origin/main    # 或 git merge，但 rebase 历史更干净

4. 提 PR
   - 受保护分支要求 review + CI 通过才能合并
   - 优先 squash merge，保持主干干净

5. 合并后，删分支 + 自动触发 CI/CD
   - 自动部署到 staging
   - 通过后人工/自动 promote 到 prod
```

## 配套实践

### Feature Flag（特性开关）

```json
// 等价 LaunchDarkly 的简易实现
{
  "feature.user-export.enabled": false,
  "feature.user-export.rollout": 0.05
}
```

**好处**：

- 主干随时可发布，没"半成品"风险
- 用开关**逐步放量**（5% → 25% → 100%）
- 紧急回退 = 关开关，不需回滚代码

### 测试

- 主干测试必须稳（PR 必过 CI）
- 自动化测试 + 强制 code review
- 监控到位（SLO 触发自动报警）

### 工具配置

**GitHub / GitLab 分支保护**：

- main 强制 PR
- 至少 1 人 approve
- CI 必过
- 强制 squash merge（或 rebase merge）

**示例 GitHub 分支保护 API**：

```bash
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/build"]}' \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field enforce_admins=true
```

## Anti-pattern（反模式）

| 坏味道 | 后果 | 怎么避 |
| --- | --- | --- |
| feature 分支活了 > 1 周 | 合并冲突地狱 | 拆小 PR + 频繁 rebase |
| 长期 release 分支 | 分支碎片 + 反复 cherry-pick | 直接用 main + flag |
| 每次大版本才合并主干 | 集成爆炸 | 强制 daily merge |
| PR 大（> 500 行） | review 难、做错 | 拆小 PR |
| 没有 flag 就合大特性 | 不变发布很慢 | 关键路径全 flag |

## 与 GitOps 的协作

主干合并 → 自动 CI → 更新 git 配置仓库 → ArgoCD sync 到 K3s

```text
[main repo dev]        [gitops config repo]
   push                      PR
    ↓                          ↑
   CI                      jenkins/gitops-sync
build image                 commit
    ↓                          ↓
harbor push                  ArgoCD sync → k8s
```

PR 改动主干 → CI 构建 → 同 PR 内同步更新 gitops 仓库 → 自动同步 K8s 集群。
