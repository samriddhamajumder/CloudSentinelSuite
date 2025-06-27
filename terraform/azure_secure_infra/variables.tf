variable "resource_group_name" {
  type        = string
  default     = "sentinel-rg"
  description = "Resource group name"
}

variable "location" {
  type        = string
  default     = "Central India"
  description = "Azure region"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment tag"
}

variable "vnet_name" {
  type        = string
  default     = "sentinel-vnet"
}

variable "vnet_address_space" {
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_name" {
  type        = string
  default     = "sentinel-subnet"
}

variable "subnet_prefix" {
  description = "Subnet CIDR range"
  default     = "10.0.1.0/24"
}

variable "subscription_id" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "client_id" {
  type = string
}

variable "client_secret" {
  type      = string
  sensitive = true
}
