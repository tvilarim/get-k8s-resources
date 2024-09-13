import subprocess
import yaml
from kubernetes import client, config

# Função para pegar todos os recursos do cluster Kubernetes
def get_kubernetes_resources():
    # Carregar configuração do kubeconfig local
    config.load_kube_config()

    # Inicializar clientes para obter informações do cluster
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    # Obter informações sobre os nós
    nodes = v1.list_node().items
    node_count = len(nodes)

    # Obter namespaces
    namespaces = v1.list_namespace().items

    # Obter ReplicaSets e seus números de réplicas
    replica_sets = apps_v1.list_replica_set_for_all_namespaces().items
    replica_set_info = []
    for rs in replica_sets:
        replica_set_info.append({
            "name": rs.metadata.name,
            "namespace": rs.metadata.namespace,
            "replicas": rs.status.replicas
        })

    resources = {
        "node_count": node_count,
        "namespaces": [ns.metadata.name for ns in namespaces],
        "replica_sets": replica_set_info
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
                        "node_count": resources["node_count"],  # Usando o número de nós do cluster atual
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

    # Adicionar namespaces e informações de ReplicaSets ao YAML gerado
    terraform_yaml["resource"]["azurerm_kubernetes_cluster"]["example"]["tags"] = {
        "namespaces": resources["namespaces"]
    }

    terraform_yaml["resource"]["azurerm_kubernetes_cluster"]["example"]["replica_sets"] = resources["replica_sets"]

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

