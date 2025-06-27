output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "s3_log_bucket" {
  description = "The S3 bucket storing CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail_logs.bucket
}

output "cloudtrail_name" {
  description = "CloudTrail trail name"
  value       = aws_cloudtrail.main.name
}

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.main.id
}
