output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "virtual_network_name" {
  value = azurerm_virtual_network.main.name
}

output "subnet_id" {
  value = azurerm_subnet.main.id
}

output "storage_account_name" {
  value = azurerm_storage_account.log.name
}

output "nsg_id" {
  value = azurerm_network_security_group.main.id
}
