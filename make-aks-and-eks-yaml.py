import subprocess
import yaml

# Função para executar comandos no shell
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout

# Função para detectar configuração do cluster local com kubectl
def get_local_cluster_info():
    print("Coletando informações do cluster local...")
    cluster_info = run_command("kubectl cluster-info")
    nodes_info = run_command("kubectl get nodes -o yaml")
    nodes = yaml.safe_load(nodes_info)
    
    # Extraindo algumas informações básicas
    node_count = len(nodes['items'])
    total_cpu = sum([int(node['status']['capacity']['cpu']) for node in nodes['items']])
    total_memory = sum([int(node['status']['capacity']['memory'][:-2]) for node in nodes['items']])  # Memory in Ki
    
    return {
        "node_count": node_count,
        "total_cpu": total_cpu,
        "total_memory": total_memory,
    }

# Função para gerar arquivo YAML de Terraform para AKS
def generate_terraform_aks(cluster_info):
    print("Gerando arquivo Terraform para AKS...")
    aks_terraform = {
        "provider": {
            "azurerm": {
                "features": {}
            }
        },
        "resource": {
            "azurerm_kubernetes_cluster": {
                "aks_cluster": {
                    "name": "aksCluster",
                    "location": "East US",
                    "resource_group_name": "k8sResourceGroup",
                    "dns_prefix": "aks",
                    "default_node_pool": {
                        "name": "default",
                        "node_count": cluster_info['node_count'],
                        "vm_size": "Standard_DS2_v2",
                        "enable_auto_scaling": True,
                        "min_count": cluster_info['node_count'] // 2,
                        "max_count": cluster_info['node_count'] * 2
                    },
                    "identity": {
                        "type": "SystemAssigned"
                    },
                    "network_profile": {
                        "network_plugin": "azure"
                    }
                }
            }
        }
    }
    
    with open("aks_cluster.tf", "w") as file:
        yaml.dump(aks_terraform, file, default_flow_style=False)
    print("Arquivo Terraform para AKS gerado: aks_cluster.tf")

# Função para gerar arquivo YAML de Terraform para EKS
def generate_terraform_eks(cluster_info):
    print("Gerando arquivo Terraform para EKS...")
    eks_terraform = {
        "provider": {
            "aws": {
                "region": "us-east-1"
            }
        },
        "resource": {
            "aws_eks_cluster": {
                "eks_cluster": {
                    "name": "eksCluster",
                    "role_arn": "arn:aws:iam::123456789012:role/eksServiceRole",
                    "vpc_config": {
                        "subnet_ids": ["subnet-abcde123", "subnet-fghij456"]
                    }
                }
            },
            "aws_eks_node_group": {
                "eks_nodes": {
                    "cluster_name": "eksCluster",
                    "node_group_name": "eksNodes",
                    "node_role_arn": "arn:aws:iam::123456789012:role/eksNodeRole",
                    "subnet_ids": ["subnet-abcde123", "subnet-fghij456"],
                    "scaling_config": {
                        "desired_size": cluster_info['node_count'],
                        "min_size": cluster_info['node_count'] // 2,
                        "max_size": cluster_info['node_count'] * 2
                    },
                    "instance_types": ["t3.medium"]
                }
            }
        }
    }
    
    with open("eks_cluster.tf", "w") as file:
        yaml.dump(eks_terraform, file, default_flow_style=False)
    print("Arquivo Terraform para EKS gerado: eks_cluster.tf")

# Função principal
def main():
    try:
        cluster_info = get_local_cluster_info()
        print(f"Informações do cluster local: {cluster_info}")
        
        # Gerar arquivos Terraform para AKS e EKS
        generate_terraform_aks(cluster_info)
        generate_terraform_eks(cluster_info)
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()

