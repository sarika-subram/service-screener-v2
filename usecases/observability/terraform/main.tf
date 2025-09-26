terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for storing Service Screener reports
resource "aws_s3_bucket" "service_screener_reports" {
  bucket = "${var.bucket_prefix}-service-screener-reports-${random_string.bucket_suffix.result}"
}

# S3 bucket for processed metrics data
resource "aws_s3_bucket" "processed_metrics" {
  bucket = "${var.bucket_prefix}-service-screener-metrics-${random_string.bucket_suffix.result}"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "service_screener_reports" {
  bucket = aws_s3_bucket.service_screener_reports.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "service_screener_reports" {
  bucket = aws_s3_bucket.service_screener_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_metrics" {
  bucket = aws_s3_bucket.processed_metrics.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lambda function for processing reports and creating structured data for QuickSight
resource "aws_lambda_function" "metrics_processor" {
  filename         = "metrics_processor.zip"
  function_name    = "service-screener-metrics-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.11"
  timeout         = 300

  depends_on = [data.archive_file.lambda_zip]

  environment {
    variables = {
      METRICS_BUCKET = aws_s3_bucket.processed_metrics.bucket
      NAMESPACE = var.quicksight_namespace
    }
  }
}

# Create Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "metrics_processor.zip"
  source_dir  = "lambda"
}

# S3 bucket notification to trigger Lambda
resource "aws_s3_bucket_notification" "report_upload" {
  bucket = aws_s3_bucket.service_screener_reports.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.metrics_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "reports/"
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.s3_invoke]
}

# Lambda permission for S3 to invoke
resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.metrics_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.service_screener_reports.arn
}