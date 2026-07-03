# =============================================================================
# Terraform 模块骨架：通用 IaC 起点
# 对应：Hub/03_DevOps工具链对比笔记.md 中的 IaC 选型参考
# =============================================================================
# 思路：
#   modules/<name>/     ← 可复用模块
#   envs/<env>/          ← 每个环境的调用
#     ├─ main.tf          （引用模块）
#     ├─ variables.tf
#     ├─ outputs.tf
#     └─ terraform.tfvars
# =============================================================================
terraform {
  required_version = ">= 1.6.0"

  # 状态文件后端（S3 / OSS / COS / GCS）
  backend "s3" {
    bucket         = "myorg-tfstate-prod"
    key            = "envs/prod/terraform.tfstate"
    region         = "ap-east-1"
    dynamodb_table = "myorg-tfstate-lock"
    encrypt        = true
  }
}

# Provider
provider "aws" {
  region = var.region

  default_tags {
    managed_by = "terraform"
    env        = var.env
    project    = var.project
  }
}

# 本环境通用变量
variable "region" {
  type    = string
  default = "ap-east-1"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "project" {
  type    = string
  default = "myproj"
}

# 引用模块
module "network" {
  source = "../../modules/network"

  env              = var.env
  vpc_cidr         = "10.0.0.0/16"
  azs              = ["ap-east-1a", "ap-east-1b", "ap-east-1c"]
  public_subnets   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets  = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

module "eks" {
  source = "../../modules/eks"

  env              = var.env
  vpc_id           = module.network.vpc_id
  subnet_ids       = module.network.private_subnets
  cluster_name     = "${var.project}-${var.env}"
  cluster_version  = "1.30"
  node_groups = {
    general = {
      instance_type = "m6i.large"
      desired_size  = 3
      min_size      = 3
      max_size      = 10
    }
  }
}

# 输出
output "cluster_endpoint" {
  value     = module.eks.cluster_endpoint
  sensitive = true
}

output "cluster_name" {
  value = module.eks.cluster_name
}
