resource "random_string" "acr_suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_container_registry" "main" {
  name = replace(
    "${var.project_name}${var.environment}${random_string.acr_suffix.result}",
    "-",
    ""
  )

  resource_group_name = azurerm_resource_group.main.name
  location            = var.acr_location
  sku                 = "Basic"
  admin_enabled       = false

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}