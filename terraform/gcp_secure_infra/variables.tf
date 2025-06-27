variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Region to deploy resources in"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone for compute resources"
  type        = string
  default     = "us-central1-a"
}

variable "vm_name" {
  default     = "secure-vm"
  description = "Name of the GCE VM"
}

variable "vpc_name" {
  default     = "sentinel-vpc"
}

variable "bucket_name" {
  default = "sentinel-secure-bucket"
}
