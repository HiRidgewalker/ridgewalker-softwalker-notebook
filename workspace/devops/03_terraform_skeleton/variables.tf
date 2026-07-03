// =============================================================================
// variables.tf
// =============================================================================
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-east-1"
}

variable "env" {
  description = "Environment (dev/staging/prod)"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
}
