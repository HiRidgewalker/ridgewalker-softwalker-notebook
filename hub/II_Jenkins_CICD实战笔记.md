# Jenkins CI/CD 实战笔记

> 来自 [[I_Jenkins基础笔记]] 的延伸：完整企业级流水线。Jenkinsfile 模板见 `example/cicd/01_jenkinsfile/`，K8s 部署 manifest 模板见 `example/cicd/02_k8s_manifests/`。

---

## 1. 全链路视图

```text
                          ┌────────────┐
                          │  Gitea/    │
                          │  GitLab/   │   push / MR
                          │  GitHub    │
                          └─────┬──────┘
                                │ webhook
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                       Jenkins                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Stage 1: 克隆代码                                   │    │
│  │  Stage 2: 单元测试                                   │    │
│  │  Stage 3: 编译 / 打包                                │    │
│  │  Stage 4: 构建 Docker 镜像（BuildKit/buildx/Kaniko） │    │
│  │  Stage 5: 镜像 tag = git commit + timestamp          │    │
│  │  Stage 6: 推 Harbor                                  │    │
│  │  Stage 7: Trivy 漏洞扫描（CRITICAL/HIGH 失败则中止） │    │
│  │  Stage 8: 部署到 K3s（kubectl apply / ArgoCD sync）  │    │
│  │  Stage 9: 通知（飞书/钉钉/Webhook）                  │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────────────────┬─────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       ┌──────────┐           ┌──────────┐
       │  Harbor  │           │   K3s    │
       │  myproj  │◀──────────│  myapp   │
       │ /webapi  │           │ namespace│
       └──────────┘           └──────────┘
```

---

## 2. 典型部署拓扑

```text
                         ┌──── Git 仓库 ─────────┐
                         │  Gitea / GitLab / GitHub│
                         └────────┬──────────────┘
                                  │ webhook
                         ┌────────▼──────────────┐
                         │     Jenkins Controller │
                         │  （K3s 上跑）            │
                         └────────┬──────────────┘
                                  │ 拉临时 agent pod
                                  │（K8s plugin）
                         ┌────────▼──────────────┐
                         │   Harbor              │
                         │  harbor.example.com  │
                         └────────┬──────────────┘
                                  │ imagePullSecrets
                         ┌────────▼──────────────┐
                         │   K3s 业务集群         │
                         │  myapp namespace      │
                         └───────────────────────┘
```

---

## 3. 完整 Jenkinsfile 模板（Python + Flask 示例）

> 模板文件：`example/cicd/01_jenkinsfile/python_app.Jenkinsfile`

```groovy
pipeline {
    agent {
        kubernetes {
            label 'python-builder'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-agent: true
spec:
  containers:
  - name: python
    image: python:3.12-slim
    command: [cat]
    tty: true
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command: [cat]
    tty: true
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
  - name: kubectl
    image: bitnami/kubectl:latest
    command: [cat]
    tty: true
  - name: trivy
    image: aquasec/trivy:latest
    command: [cat]
    tty: true
  volumes:
  - name: docker-config
    secret:
      secretName: harbor-pull-config
      items:
      - key: config.json
        path: config.json
"""
        }
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    parameters {
        string(name: 'BRANCH',            defaultValue: 'main',    description: '分支')
        string(name: 'GIT_REPO',          defaultValue: 'git@git.example.com:myproj/webapi.git', description: '仓库 URL')
        string(name: 'GIT_CREDENTIALS_ID', defaultValue: 'git-ssh-key', description: 'Git 凭据')
        string(name: 'IMAGE_NAME',         defaultValue: 'webapi', description: '镜像名')
        string(name: 'HARBOR_PROJECT',     defaultValue: 'myproj', description: 'Harbor 项目')
        string(name: 'KUBECONFIG_CRED',    defaultValue: 'kubeconfig-prod', description: 'kubeconfig 凭据')
        string(name: 'K8S_NAMESPACE',      defaultValue: 'myapp',  description: 'K8s namespace')
        string(name: 'K8S_MANIFEST_DIR',   defaultValue: 'k8s/', description: 'manifest 路径')
    }

    environment {
        HARBOR_REGISTRY = 'harbor.example.com'
        DOCKER_IMAGE    = "${HARBOR_REGISTRY}/${params.HARBOR_PROJECT}/${params.IMAGE_NAME}"
        BUILD_TAG       = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.take(7)}"
    }

    stages {
        // ===== 1. 拉代码 =====
        stage('Checkout') {
            steps {
                git credentialsId: params.GIT_CREDENTIALS_ID,
                    url: params.GIT_REPO,
                    branch: params.BRANCH
            }
        }

        // ===== 2. 单测 =====
        stage('Unit Test') {
            steps {
                container('python') {
                    sh """
                        python -m venv /tmp/venv
                        . /tmp/venv/bin/activate
                        pip install -r requirements.txt
                        pip install pytest
                        python -m pytest tests/ -v --junitxml=test-report.xml
                    """
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-report.xml'
                }
            }
        }

        // ===== 3. 构建镜像（Kaniko 无特权容器版） =====
        stage('Build Image') {
            steps {
                container('kaniko') {
                    sh """
                        /kaniko/executor \
                          --context=${WORKSPACE} \
                          --dockerfile=${WORKSPACE}/Dockerfile \
                          --destination=${DOCKER_IMAGE}:${BUILD_TAG} \
                          --destination=${DOCKER_IMAGE}:latest \
                          --cache=true
                    """
                }
            }
        }

        // ===== 4. 漏洞扫描 =====
        stage('Trivy Scan') {
            when { expression { return params.SCAN != false } }
            steps {
                container('trivy') {
                    sh """
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --exit-code 1 \
                            --no-progress \
                            ${DOCKER_IMAGE}:${BUILD_TAG}
                    """
                }
            }
        }

        // ===== 5. 部署到 K3s =====
        stage('Deploy') {
            steps {
                container('kubectl') {
                    withCredentials([file(credentialsId: params.KUBECONFIG_CRED, variable: 'KUBECONFIG')]) {
                        sh """
                            kubectl -n ${params.K8S_NAMESPACE} apply -f ${params.K8S_MANIFEST_DIR} --record
                            kubectl -n ${params.K8S_NAMESPACE} set image deployment/${params.IMAGE_NAME} \
                                ${params.IMAGE_NAME}=${DOCKER_IMAGE}:${BUILD_TAG}
                            kubectl -n ${params.K8S_NAMESPACE} rollout status deployment/${params.IMAGE_NAME} --timeout=10m
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            container('python') {
                sh """
                    curl -X POST -H 'Content-Type: application/json' \
                      -d '{"msgtype":"text","content":{"text":"✅ Build #${BUILD_NUMBER} succeeded - ${BUILD_TAG}"}}' \
                      ${FEISHU_WEBHOOK}
                """
            }
        }
        failure {
            container('python') {
                sh """
                    curl -X POST -H 'Content-Type: application/json' \
                      -d '{"msgtype":"text","content":{"text":"❌ Build #${BUILD_NUMBER} failed - ${params.IMAGE_NAME}"}}' \
                      ${FEISHU_WEBHOOK}
                """
            }
        }
        always {
            echo "Build finished: ${currentBuild.currentResult}"
        }
    }
}
```

> 关键点说明：

- **Kaniko**：不需要 docker daemon 就能构建镜像（rootless 友好）
- **trivy**：扫描失败非零退出码中断流水线（`--exit-code 1`）
- **set image + rollout status**：避免整个 manifest 重写，等价"原子升级"
- **withCredentials** 注入 kubeconfig 文件，不会写到 env 变量里

---

## 4. Go / Java 模板差异

### 4.1 Go 应用

```groovy
container('go') {
    sh """
        go mod download
        go test ./... -v
        go build -ldflags '-s -w' -o /out/app .
    """
}
```

构建镜像阶段 Kaniko 用同模板，因为 Dockerfile 内已是 alpine + 静态二进制。

### 4.2 Java Spring Boot

```groovy
// 加一个 maven 容器
- name: maven
  image: maven:3.9-eclipse-temurin-17
  command: [cat]
  tty: true

// 步骤
container('mvn') {
    sh 'mvn -B clean package -DskipTests'
    sh 'mvn -B test'
}
```

构建镜像时，把 `target/*.jar` 加进 Dockerfile：

```dockerfile
FROM eclipse-temurin:17-jre
COPY target/*.jar /app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

---

## 5. K8s 部署 manifest 模板

> 见 `example/cicd/02_k8s_manifests/`

### 5.1 Deployment（无状态 Web）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapi
  namespace: myapp
  labels:
    app: webapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapi
  template:
    metadata:
      labels:
        app: webapi
    spec:
      imagePullSecrets:
        - name: harbor-pull
      containers:
        - name: webapi
          image: harbor.example.com/myproj/webapi:PLACEHOLDER   # 由 Jenkins 替换
          ports:
            - containerPort: 8080
          env:
            - name: TZ
              value: Asia/Shanghai
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
```

### 5.2 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapi
  namespace: myapp
spec:
  selector:
    app: webapi
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
      name: http
```

### 5.3 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapi
  namespace: myapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: webapi-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: webapi
                port:
                  number: 80
```

### 5.4 HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: webapi
  namespace: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: webapi
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 6. 镜像拉取凭据（Service Account 自动注入）

```bash
# 让 myapp 命名空间的默认 SA 自动带 harbor-pull
kubectl patch serviceaccount default -n myapp -p '{"imagePullSecrets":[{"name":"harbor-pull"}]}'
```

详细见 [[Harbor笔记]] 的 6.3。

---

## 7. 通知：飞书 / 钉钉 / 企业微信

### 7.1 飞书

```bash
# 飞书群机器人 Webhook
curl -X POST -H 'Content-Type: application/json' \
  -d '{"msg_type":"text","content":{"text":"deploy ok"}}' \
  https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx
```

### 7.2 钉钉

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"deploy ok"}}' \
  https://oapi.dingtalk.com/robot/send?access_token=xxxxx
```

> 推荐通过 JCasC 把 webhook URL 注入到 env（FEISHU_WEBHOOK 等），避免硬编码。

---

## 8. 优化事项

### 8.1 镜像构建缓存

- **Kaniko**：默认缓存到 Harbor（用 `--cache=true` 指定 cache repo）；每层检测改过才重跑
- **buildx**：本地 buildx 缓存目录可挂

### 8.2 测试并行

```groovy
stages {
    stage('Test') {
        parallel {
            stage('Unit') { steps { sh 'mvn test' } }
            stage('Integration') { steps { sh 'mvn verify -Pintegration' } }
        }
    }
}
```

### 8.3 跳过条件

```groovy
stage('Deploy') {
    when {
        branch 'main'
        // or tag 'v1.*'
    }
    steps { ... }
}
```

### 8.4 Slack 风格状态条

`Manage Jenkins → Appearance → Progress bar`，把 stage 显示成色块。

---

## 9. 安全清单

| 项 | 推荐 |
| --- | --- |
| Git 凭据 | SSH key 注入；不存密码 |
| Harbor 凭据 | 机器人账号，专人专用 |
| Kubeconfig | File credential，不放 env |
| 镜像 tag | 强制包含 git sha（避免 latest 漂移） |
| 漏洞扫描 | Trivy CRITICAL/HIGH 失败则门禁 |
| 容器权限 | PodSecurity restricted 命名空间 |
| 部署审批 | Multibranch pipeline + Code Review |

---

## 10. 进阶：GitOps 模式（推荐）

> 上面是 CD 阶段用 Jenkins 直接 deploy；**GitOps 模式更稳定**：

```text
Jenkins 写完 manifest → commit 到 git config 仓库
                         └─→ ArgoCD watch → 自动 sync 集群
```

```groovy
// Jenkinsfile 的最后阶段
stage('Update Manifest Repo') {
    steps {
        container('kubectl') {
            withCredentials([usernamePassword(
                credentialsId: 'git-deploy-token',
                usernameVariable: 'GIT_USER',
                passwordVariable: 'GIT_TOKEN'
            )]) {
                sh """
                    git clone https://\${GIT_TOKEN}@git.example.com/config/webapi.git /tmp/config
                    sed -i 's|image: harbor.example.com/myproj/webapi:.*|image: ${DOCKER_IMAGE}:${BUILD_TAG}|' \
                      /tmp/config/k8s/webapi.yaml
                    cd /tmp/config
                    git commit -am "deploy ${BUILD_TAG}"
                    git push origin main
                """
            }
        }
    }
}
```

**优势**：

- 集群部署的"实际状态"写在 git 里，可审计
- 回滚 = 回滚 git commit
- 生产 K8s API 账户权限最小（只允许读取，避开 apply 权限风险）
- 与 K8s 集群解耦

> ArgoCD chart 在 Rancher 应用商店一键装。

---

## 11. 一句话总结

- **全链路**：Git → Jenkins（K8s agent） → Kaniko 构建 → Trivy 扫描 → Harbor 推送 → kubectl/ArgoCD 部署 → 通知
- **关键安全**：Kaniko（不需要 docker daemon）+ 机器人账号 + 漏洞门禁 + Service Account 注入凭据
- **进阶**：把 CD 段交给 ArgoCD，Jenkins 只管构建，集群部署由 GitOps 完成