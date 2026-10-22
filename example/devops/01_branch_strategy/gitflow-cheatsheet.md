# GitFlow 速查

> 对应 [[小企业DevOps方案笔记]] 的 5.2。
> 适用于版本化产品、严格管控场景。

## 分支类型

```text
main（生产）
  └── develop（集成）
       ├── feature/*    (新功能)
       ├── release/*    (发版冻结)
       └── bugfix/*     (开发修复)

hotfix/*   从 main 切，紧急修复后 merge 回 main + develop
```

## 工作流

### 新功能

```bash
git checkout develop && git pull
git checkout -b feature/my-feature

# 开发...
git push origin feature/my-feature
# PR → develop
```

### 发版

```bash
git checkout develop && git pull
git checkout -b release/1.2.0

# 只接受 bugfix
git commit -m "fix: ..."
# PR → release/1.2.0 → merge 到 main + develop

# 打 tag
git checkout main
git tag -a v1.2.0 -m "release 1.2.0"
git push origin v1.2.0
```

### 紧急修复（hotfix）

```bash
git checkout main && git pull
git checkout -b hotfix/critical-fix

# 修复...
# PR → main + develop（两个都要合）
```

## 与 CI/CD 集成

| 分支 | 自动化行为 |
| --- | --- |
| feature/* | 跑测试，构建测试镜像 |
| develop | 部署到 staging |
| release/* | 部署到 pre-prod |
| main | tag → 部署到 prod |
| hotfix/* | 修复直发 prod |

## 缺点

- 分支多 → 新人理解成本
- 长期 release 分支 → 反复 cherry-pick
- CI 配置复杂
- 不适合"持续交付高频"产品

## 演进

GitFlow 适合多版本同存（v1.x、v2.x 同时维护）。如果你的产品只有 1 个活跃版本，**改用 trunk-based + feature flag**。
