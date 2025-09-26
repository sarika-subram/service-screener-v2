variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "my-org"
}

variable "quicksight_namespace" {
  description = "Namespace for Service Screener data organization"
  type        = string
  default     = "ServiceScreener"
}

variable "enable_quicksight_automation" {
  description = "Enable automated QuickSight data source creation (requires active subscription)"
  type        = bool
  default     = false
}