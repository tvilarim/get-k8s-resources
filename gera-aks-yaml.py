import subprocess
import yaml
from kubernetes import client, config

# Função para pegar todos os recursos do cluster Kubernetes
def get_kubernetes_resources():
    # Carregar configuração do kubeconfig local
    config.load_kube_config()

    # Inicializar clientes para obter informações do cluster
    v1 = client.CoreV1Api()
    v1_networking = client.NetworkingV1Api()

    # Obter namespaces
    namespaces = v1.list_namespace().items
    network_policies = v1_networking.list_network_policy_for_all_namespaces().items
    services = v1.list_service_for_all_namespaces().items

    resources = {
        "namespaces": [ns.metadata.name for ns in namespaces],
        "network_policies": [np.metadata.name for np in network_policies],
        "services": [svc.metadata.name for svc in services]
    }

    return resources

# Função para gerar o arquivo YAML para Terraform AKS Provider
def generate_terraform_yaml(resources):
    terraform_yaml = {
        "provider": {
            "azurerm": {
                "features": {}
            }
        },
        "resource": {
            "azurerm_kubernetes_cluster": {
                "example": {
                    "name": "example-aks-cluster",
                    "location": "East US",
                    "resource_group_name": "example-resources",
                    "dns_prefix": "exampleaks",
                    "default_node_pool": {
                        "name": "default",
                        "node_count": 1,
                        "vm_size": "Standard_DS2_v2"
                    },
                    "network_profile": {
                        "network_plugin": "azure",
                        "network_policy": "azure",
                        "service_cidr": "10.0.0.0/16",
                        "dns_service_ip": "10.0.0.10",
                        "docker_bridge_cidr": "172.17.0.1/16"
                    }
                }
            }
        }
    }

    # Adicionar namespaces como tags ou informações extras se necessário
    terraform_yaml["resource"]["azurerm_kubernetes_cluster"]["example"]["tags"] = {
        "namespaces": resources["namespaces"]
    }

    return terraform_yaml

# Função para salvar o arquivo YAML
def save_yaml_file(data, filename="terraform_aks.yaml"):
    with open(filename, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
    print(f"YAML gerado e salvo em {filename}")

# Função principal para executar as etapas
def main():
    resources = get_kubernetes_resources()
    terraform_yaml = generate_terraform_yaml(resources)
    save_yaml_file(terraform_yaml)

if __name__ == "__main__":
    main()

