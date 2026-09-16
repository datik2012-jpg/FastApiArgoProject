output "resource_group_name" {
  description = "Created Azure Resource Group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Azure Resource Group location"
  value       = azurerm_resource_group.main.location
}

output "acr_name" {
  description = "Azure Container Registry name"
  value       = azurerm_container_registry.main.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "aks_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}