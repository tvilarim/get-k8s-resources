provider:
  azurerm:
    features: {}
resource:
  azurerm_kubernetes_cluster:
    aks_cluster:
      default_node_pool:
        enable_auto_scaling: true
        max_count: 2
        min_count: 0
        name: default
        node_count: 1
        vm_size: Standard_DS2_v2
      dns_prefix: aks
      identity:
        type: SystemAssigned
      location: East US
      name: aksCluster
      network_profile:
        network_plugin: azure
      resource_group_name: k8sResourceGroup
