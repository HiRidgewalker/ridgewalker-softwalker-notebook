# workspace/cicd

CI/CD 相关模板与示例，对应 [[06_Jenkins基础笔记]]、[[07_Jenkins_CICD实战笔记]]、[[05_Harbor笔记]]。

## 目录

```
workspace/cicd/
├── README.md                       ← 本文件
├── 01_jenkinsfile/
│   ├── python_app.Jenkinsfile      ← Python/Flask 流水线
│   ├── go_app.Jenkinsfile          ← Go 流水线
│   └── java_app.Jenkinsfile        ← Java Spring Boot 流水线
├── 02_k8s_manifests/
│   ├── flask-deployment.yaml       ← Deployment 示例
│   ├── flask-service.yaml          ← Service 示例
│   ├── ingress-nginx.yaml          ← Ingress 示例
│   ├── imagepullsecret-harbor.yaml ← 镜像凭据示例（kubectl apply 参考）
│   └── hpa.yaml                    ← HPA 示例
├── 03_harbor_setup/
│   └── docker-compose.yml          ← 单机 Harbor 部署（demo 环境）
└── 04_helm_values/
    └── jenkins-values.yaml         ← jenkinsci/jenkins Helm 自定义 values
```

## 使用说明

每个模板的文件顶部注释写明：

- 适用场景
- 用法（参数说明）
- 与 Hub 笔记的对应章节
