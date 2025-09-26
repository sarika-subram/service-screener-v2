output "s3_bucket_name" {
  description = "Name of the S3 bucket for Service Screener reports"
  value       = aws_s3_bucket.service_screener_reports.bucket
}

output "lambda_function_name" {
  description = "Name of the Lambda function for metrics processing"
  value       = aws_lambda_function.metrics_processor.function_name
}

output "quicksight_setup_instructions" {
  description = "Instructions for setting up QuickSight"
  value       = "1. Go to QuickSight console 2. Create data source (S3) 3. Use bucket: ${aws_s3_bucket.processed_metrics.bucket} 4. Manifest file: manifest.json"
}

output "metrics_bucket_name" {
  description = "Name of the S3 bucket for processed metrics"
  value       = aws_s3_bucket.processed_metrics.bucket
}