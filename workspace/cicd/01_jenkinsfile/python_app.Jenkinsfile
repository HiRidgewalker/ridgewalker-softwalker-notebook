// =============================================================================
// Python/Flask 应用完整 CI/CD 流水线
// 对应：Hub/16_Jenkins_CICD实战笔记.md 中的"完整 Jenkinsfile 模板"
// =============================================================================
//
// 用法：
//   1) 在 Jenkins 创建 Multibranch Pipeline Job，指向此 Jenkinsfile
//   2) 配置凭据（Credentials 插件）：
//        - git-ssh-key                  (Git SSH private key)
//        - kubeconfig-prod             (File 类型：生产 K8s kubeconfig)
//        - harbor-pull-config          (Secret 类型：Kaniko 用的 dockerconfigjson)
//   3) 修改下方 parameters 段的默认值
//   4) 代码仓库根目录应有 requirements.txt + Dockerfile
//
// 依赖：
//   - Jenkins Kubernetes plugin（动态起 agent pod）
//   - Kaniko（构建镜像，无需 docker daemon）
//   - Trivy（漏洞扫描）
//   - bitnami/kubectl（部署到 K3s）
//
// 流水线：
//   1. Checkout（拉代码）
//   2. Unit Test（pytest）
//   3. Build Image（Kaniko）
//   4. Trivy Scan（CRITICAL/HIGH 则中断）
//   5. Deploy（kubectl set image + rollout status）
//   6. Notify（飞书/钉钉 Webhook）
// =============================================================================
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
        string(name: 'GIT_REPO',          defaultValue: 'git@git.example.com:myproj/webapi.git', description: '仓库 SSH URL')
        string(name: 'GIT_CREDENTIALS_ID', defaultValue: 'git-ssh-key', description: 'Git 凭据 ID')
        string(name: 'BRANCH',             defaultValue: 'main', description: '分支')
        string(name: 'IMAGE_NAME',         defaultValue: 'webapi', description: '镜像名（不含 registry）')
        string(name: 'HARBOR_PROJECT',     defaultValue: 'myproj', description: 'Harbor 项目名')
        string(name: 'KUBECONFIG_CRED',    defaultValue: 'kubeconfig-prod', description: 'kubeconfig 凭据 ID')
        string(name: 'K8S_NAMESPACE',      defaultValue: 'myapp',  description: 'K8s namespace')
    }

    environment {
        HARBOR_REGISTRY = 'harbor.example.com'
        DOCKER_IMAGE    = "${HARBOR_REGISTRY}/${params.HARBOR_PROJECT}/${params.IMAGE_NAME}"
        BUILD_TAG       = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.take(7)}"
    }

    stages {
        stage('Checkout') {
            steps {
                git credentialsId: params.GIT_CREDENTIALS_ID,
                    url: params.GIT_REPO,
                    branch: params.BRANCH
            }
        }

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

        stage('Trivy Scan') {
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

        stage('Deploy') {
            steps {
                container('kubectl') {
                    withCredentials([file(credentialsId: params.KUBECONFIG_CRED, variable: 'KUBECONFIG')]) {
                        sh """
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
            sh """
                curl -X POST -H 'Content-Type: application/json' \
                  -d '{"msg_type":"text","content":{"text":"✅ Build #${BUILD_NUMBER} ${params.IMAGE_NAME}:${BUILD_TAG}"}}' \
                  \${FEISHU_WEBHOOK}
            """
        }
        failure {
            sh """
                curl -X POST -H 'Content-Type: application/json' \
                  -d '{"msg_type":"text","content":{"text":"❌ Build #${BUILD_NUMBER} ${params.IMAGE_NAME} failed"}}' \
                  \${FEISHU_WEBHOOK}
            """
        }
    }
}
