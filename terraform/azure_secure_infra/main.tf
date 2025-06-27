

# Random suffix for globally unique resource names
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# 🌐 Resource Group
resource "azurerm_resource_group" "main" {
  name     = "sentinel-rg"
  location = var.location
}

# 🌐 Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "sentinel-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# 🧱 Subnet
resource "azurerm_subnet" "main" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_prefix]
}

# 🔐 Secure Storage Account
resource "azurerm_storage_account" "log" {
  name                     = "sentinellog${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"


  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    ip_rules                   = []
    virtual_network_subnet_ids = []
  }

  tags = {
    Environment = var.environment
    Secure      = "true"
  }
}

# 📂 Storage Container for Diagnostic Logs
resource "azurerm_storage_container" "logs" {
  name                  = "diagnostic-logs"
  storage_account_id    = azurerm_storage_account.log.id
  container_access_type = "private"
}

# 📈 Diagnostic Logs for Storage Account
# ✅ Recommended: Storage Management Policy for log retention
resource "azurerm_storage_management_policy" "retention" {
  storage_account_id = azurerm_storage_account.log.id

  rule {
    name    = "log-retention"
    enabled = true

    filters {
      blob_types = ["blockBlob"]
    }

    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = 30
      }

      snapshot {
        delete_after_days_since_creation_greater_than = 30
      }
    }
  }
}

resource "azurerm_network_watcher" "nw" {
  name                = "network-watcher"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_network_watcher_flow_log" "nsg_flow" {
  name                      = "nsg-flow-logs"
  network_watcher_name      = "NetworkWatcher_centralindia"
  resource_group_name       = "NetworkWatcherRG"
  network_security_group_id = azurerm_network_security_group.main.id
  storage_account_id        = azurerm_storage_account.log.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 30
  }
}




# 🛡️ Microsoft Defender for Cloud (for VMs)
resource "azurerm_security_center_subscription_pricing" "defender" {
  tier          = "Standard"
  resource_type = "VirtualMachines"
}

# 🚫 NSG with Inbound Deny-All Rule
resource "azurerm_network_security_group" "main" {
  name                = "sentinel-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "deny-inbound-all"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
