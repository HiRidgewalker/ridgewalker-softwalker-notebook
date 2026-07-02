# Jenkins 基础笔记

> 来自 [[Hub/16_Jenkins_CICD实战笔记]] 的前半段基础铺垫。完整流水线范例见实战篇。

---

## 1. Jenkins 是什么

**Jenkins** 是开源最老牌、用量最大的 CI 引擎（Java 编写）。一切"构建、测试、部署"的工作流由 **Pipeline（Jenkinsfile）** 声明。

> K8s 时代其他选项：GitLab CI、Drone CI、Buildkite、GitHub Actions。Jenkins 生态最大，但相对沉重。本笔记用 Jenkins on K8s（jenkinsci/jenkins Helm chart）方案。

---

## 2. 架构：Controller + Agent

```text
┌────────────────────┐                ┌────────────────────┐
│ Jenkins Controller │  ──dispatch──▶│ Jenkins Agents     │
│    （master）       │                │   （运行 Job）      │
│  - UI              │                │  - label 匹配     │
│  - Job 配置        │                │  - 临时或固定     │
│  - Credentials     │                │  - K8s pod 形式   │
└────────────────────┘                └────────────────────┘
```

- **Controller**（旧称 master）：常驻进程，跑 UI、调度 Job、存配置（XML / JDBC 兼容元数据）
- **Agent**：执行 Job 的 worker
  - **静态 Agent**：独立机器 SSH 连
  - **动态 Agent**（推荐）：K8s 插件按 Job 需要起 pod，用完销毁

---

## 3. 在 K3s 上装 Jenkins

> 推荐用 Helm chart `jenkinsci/jenkins`，详细 values 见 `workspace/cicd/04_helm_values/jenkins-values.yaml`。

### 3.1 添加 Helm repo

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
```

### 3.2 创建 namespace + PVC

```bash
kubectl create namespace jenkins
cat <<EOF | kubectl apply -n jenkins -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 20Gi
EOF
```

### 3.3 安装 Jenkins Helm chart

```bash
helm install jenkins jenkins/jenkins \
  -n jenkins \
  -f workspace/cicd/04_helm_values/jenkins-values.yaml
```

### 3.4 关键 values（部分）

```yaml
controller:
  image: jenkins/jenkins:2.462.3-lts
  tag: 2.462.3-lts

  serviceType: ClusterIP
  adminPassword: <初次密码>

  # 数据外置
  persistence:
    enabled: true
    size: 20Gi
    storageClass: longhorn

  # 资源配置
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2
      memory: 4Gi

  # JCasC：Configuration as Code（推荐）
  JCasC:
    enabled: true
    configScripts:
      jenkins.yaml: |
        jenkins:
          systemMessage: "Production Jenkins"
        credentials:
          system:
            domainCredentials:
              - credentials:
                  - usernamePassword:
                      scope: GLOBAL
                      id: harbor-robot
                      username: 'robot$myproj+robot-ci'
                      password: 'xxxx'
                  - file:
                      scope: GLOBAL
                      id: kubeconfig
                      fileName: 'kubeconfig'
                      secretBytes: '<base64-kubeconfig>'
        security:
          globalJobDslJobConfigurationSecurity:
            useJobDslSecurity: false

# 关键插件
plugins:
  - kubernetes
  - workflow-aggregator
  - git
  - configuration-as-code
  - credentials-binding
  - generic-webhook-trigger
  - pipeline-stage-view
```

> 安装完成后：`kubectl get svc -n jenkins jenkins`，NodePort 方式外部访问，或挂个 Ingress。

### 3.5 获取 admin 密码

```bash
kubectl exec -it deploy/jenkins -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 4. K8s 插件：动态 Agent

在 K3s 上跑 Jenkins 时，**Job 每次跑都拉一个临时 Pod 当 Agent**：

```groovy
// Jenkinsfile 中
pipeline {
  agent {
    kubernetes {
      label 'jenkins-agent'      // 标记
      yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-agent: true
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:3324.7
    args: ['$(JENKINS_SECRET)', '$(JENKINS_NAME)']
  - name: maven
    image: maven:3.9-eclipse-temurin-17
    command:
    - cat
    tty: true
"""
    }
  }
  stages {
    stage('Build') {
      steps {
        container('maven') {
          sh 'mvn -B clean package'
        }
      }
    }
  }
}
```

> 每个 stage 的 `container('maven')` 切换到 Pod 内对应容器跑命令。
>
> 配置方法：`Manage Jenkins → Cloud → Kubernetes Cloud → Configure`，也是 JCasC 里写死。详见 [[Hub/16_Jenkins_CICD实战笔记]]。

### 4.1 自动 Agent Pod 行为

- Job 开始 → Controller 调度 K8s 创建 Pod
- Pod 跑 stage 步骤
- Job 结束 → Pod 自动删除（默认；可保留）

---

## 5. Credentials（凭据管理）

Jenkins 有专门的凭据系统，类型丰富：

| 类型 | 用途 |
| --- | --- |
| Username with password | Harbor 机器人账号 |
| Secret text | API token |
| SSH username + private key | Git 仓库 SSH |
| File | kubeconfig 文件 |
| Certificate | TLS 证书 |
| Docker Host | Docker Registry（已弃用，用 docker-registry 类型） |

```groovy
// 在 Pipeline 里用
withCredentials([
    usernamePassword(
        credentialsId: 'harbor-robot',
        usernameVariable: 'HARBOR_USER',
        passwordVariable: 'HARBOR_PASS'
    )
]) {
    sh 'docker login harbor.example.com -u $HARBOR_USER -p $HARBOR_PASS'
}
```

> 推荐把所有凭据通过 JCasC（Configuration as Code）从外部 Secret 注入，避免明文写。

---

## 6. Jenkinsfile：声明式 Pipeline

### 6.1 语法结构

```groovy
pipeline {
    agent any                    // 跑在哪（agent）

    options {
        // 通用设置
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()   // 同一 Job 不并发
        timestamps()                // 日志加时间戳
    }

    parameters {
        // 参数化构建
        string(name: 'TAG', defaultValue: 'v1', description: '镜像 tag')
        choice(name: 'ENV', choices: ['dev', 'prod'], description: '环境')
        booleanParam(name: 'SCAN', defaultValue: true, description: '是否扫描')
    }

    triggers {
        // 触发方式
        pollSCM('*/5 * * * *')      // 轮询
        // 或者 GenericWebhookTrigger（推荐）
    }

    environment {
        // 全局环境变量（Groovy 不在这里解析 → 单纯值）
        APP_NAME = 'webapi'
        REGISTRY = 'harbor.example.com'
        PROJECT  = 'myproj'
    }

    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'git-ssh-key',
                    url: 'git@github.com:team/webapi.git',
                    branch: 'main'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn -B clean package -DskipTests'
            }
        }

        stage('Test') {
            steps {
                sh 'mvn -B test'
            }
        }

        stage('Docker build & push') {
            steps {
                script {
                    dockerImage = docker.build("${REGISTRY}/${PROJECT}/${APP_NAME}:${params.TAG}")
                    docker.withRegistry("https://${REGISTRY}", "harbor-robot") {
                        dockerImage.push()
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                sh "kubectl -n myapp apply -f k8s/"
            }
        }
    }

    post {
        always {
            // 不管成败都跑
            echo "build done"
        }
        success {
            // 成功通知
            sh 'curl -X POST https://feishu-webhook/...'
        }
        failure {
            // 失败通知
        }
    }
}
```

### 6.2 常用 step 速查

```groovy
// 简单命令
sh 'mvn package'                              // 跑 shell
bat 'dir'                                    // Windows
script { def x = 1 }                         // 嵌 Groovy

// 文件
writeFile file: 'config.yaml', text: '...'    // 写文件
readFile 'config.yaml'

// HTTP
httpRequest url: 'http://api/foo'

// Git
git url: 'https://...', credentialsId: 'git', branch: 'main'

// Docker（Jenkins docker 插件）
docker.withRegistry('https://harbor.example.com', 'harbor-robot') {
    def img = docker.build("name:v1")
    img.push()
}

// 时间戳
timestamps { ... }
```

### 6.3 流水线超时

```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
    timeout(activity: true, time: 60)        // 整体超时
}
```

---

## 7. 多分支 / Git SCM 触发

### 7.1 多分支 pipeline

`Jenkinsfile` 与代码同仓，扫描每个分支：

```groovy
// Multibranch pipeline 配置：
//   Sources: Git → repo URL → credentials
//   Discover branches: All branches / only PR
//   Build strategies: named branches / tags / PRs
```

### 7.2 自动从 Gitea / GitHub / GitLab 触发

- **WebHook**：SCM 侧配置 push → Jenkins URL + token
- **Generic Webhook Trigger 插件**：接收任意 webhook + payload 解析

```groovy
triggers {
    GenericTrigger(
        causeString: 'Triggered by $ref',
        token: 'gitea-token',
        tokenCredentialId: '',
        printPostContent: true,
        regexpFilterText: '',
        regexpFilterExpression: '',
        jsonParam: 'BRANCH_COMMIT'
    )
}
```

---

## 8. 共享库（Shared Libraries）

抽公共步骤到 `vars/` 或 `src/`：

```text
shared-library/
└── vars/
    ├── buildAndPush.groovy
    └── notifyFeishu.groovy
```

```groovy
// Jenkinsfile
@Library('my-shared-library') _

pipeline {
    stages {
        stage('Build & Push') {
            steps { buildAndPush('webapi', 'v1') }
        }
    }
}
```

> 在 Jenkins 全局配置 `Manage Jenkins → System → Global Pipeline Libraries` 加。

---

## 9. 备份与高可用

### 9.1 主要备份对象

| 数据 | 位置 | 备份方法 |
| --- | --- | --- |
| Job / Pipeline 配置 | `/var/jenkins_home/jobs/` | 整 PVC 备份 |
| 凭据（敏感） | `/var/jenkins_home/credentials.xml` | 同上 + 加密 |
| 插件 | `/var/jenkins_home/plugins/` | 同上 |
| 全局设置 | `/var/jenkins_home/config.xml` | 同上 |

### 9.2 备份实操

```bash
# Job → ThinBackup 插件：定时备份到 /tmp/jenkins-backups
# 或脚本备份
kubectl -n jenkins cp jenkins-0:/var/jenkins_home ./jenkins-backup
```

### 9.3 HA

- 单 Controller + 持久化：最简
- 多 Controller（HA）：Jenkins 官方 CAS（Cloud Native）方案（用 K8s + shared storage + cloud-consistency 协议）。小团队没必要上。

---

## 10. 安全清单

✅ 不要做的事

- 不要把凭据写在 Jenkinsfile 里用 `sh 'docker login -p secret'`
- 不要给 anonymous 用户 `Overall/Read` 以外的权限
- 不要 default admin 一直留初始密码
- 不要把 Jenkins 暴露在公网上

✅ 推荐

- 凭据用 Credentials 系统 + JCasC 注入
- 内部 RBAC：项目管理员只能动自己 namespace 的 Job
- `Pipeline` 权限限制：用 `Approve` 流程审批改动 Jenkinsfile
- 启用 Agent ↔ Controller 之间的 JNLP over TLS

---

## 11. 常见坑点

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| Pipeline 一直 pending | 没有 Agent 可用 / Label 不匹配 | 检查 K8s plugin 配置 + Pod 日志 |
| `cannot connect to docker daemon` | Agent pod 没挂 docker.sock | 用 buildah/kaniko；或挂 `.docker.sock`（生产慎用） |
| Multibranch 扫不到新分支 | hook 没通 / token 不对 | `Manage Jenkins → Branch Sources → Scan repo now` |
| Plugin 装不上 / 启动失败 | 镜像 lock / 网络 | 检查 `kubectl logs` |
| LDAP 登不上 | 配置错 / 启用了全局锁 | 检查 JCasC 配置 |
| 慢 | Job 配置混乱 / 依赖远程慢 | 用 `timestamps + time` step 看时长分布 |

---

## 12. 一句话总结

- **Jenkins = 老牌、最通用**；在 K8s 上跑 = Controller 跑控制台 + Agent 临时 Pod 跑 build
- **声明式 Pipeline（Jenkinsfile）是第一公民**；脚本式（groovy script）只在特殊场景
- **凭据**走 Credentials 系统 + JCasC 注入，不要写死在 Jenkinsfile
- 跨 Job 复用逻辑放**共享库**