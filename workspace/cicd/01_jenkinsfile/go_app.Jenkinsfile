// =============================================================================
// Go 应用 CI/CD 流水线
// 对应：Hub/16_Jenkins_CICD实战笔记.md 中的 "Go / Java 模板差异" 小节
// =============================================================================
pipeline {
    agent {
        kubernetes {
            label 'go-builder'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-agent: true
spec:
  containers:
  - name: go
    image: golang:1.22-alpine
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
    }

    parameters {
        string(name: 'GIT_REPO',          defaultValue: 'git@git.example.com:myproj/mygo.git', description: '仓库 SSH URL')
        string(name: 'GIT_CREDENTIALS_ID', defaultValue: 'git-ssh-key')
        string(name: 'BRANCH',             defaultValue: 'main')
        string(name: 'IMAGE_NAME',         defaultValue: 'mygo')
        string(name: 'HARBOR_PROJECT',     defaultValue: 'myproj')
        string(name: 'KUBECONFIG_CRED',    defaultValue: 'kubeconfig-prod')
        string(name: 'K8S_NAMESPACE',      defaultValue: 'myapp')
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

        stage('Test') {
            steps {
                container('go') {
                    sh """
                        go mod download
                        go test ./... -race -v
                    """
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
}
