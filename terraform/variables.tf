variable "location" {
  description = "Azure region for project resources"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for Azure resources"
  type        = string
  default     = "medical-api"
}


variable "acr_location" {
  description = "Azure region for Container Registry"
  type        = string
  default     = "northeurope"
}


variable "aks_location" {
  description = "Azure region for the AKS cluster"
  type        = string
  default     = "eastus"
}