import subprocess
import yaml

# Função para executar comandos kubectl e capturar saída
def run_kubectl_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar o comando {command}: {result.stderr}")
        return None
    return result.stdout

# Função para coletar todos os recursos do cluster
def get_kubernetes_resources():
    resources = ['pod', 'service', 'deployment', 'configmap', 'secret', 'ingress', 'networkpolicy']
    cluster_resources = {}

    for resource in resources:
        command = ['kubectl', 'get', resource, '--all-namespaces', '-o', 'yaml']
        output = run_kubectl_command(command)
        if output:
            cluster_resources[resource] = yaml.safe_load(output)
    
    return cluster_resources

# Função para gerar configuração Terraform a partir dos manifestos
def generate_terraform_config(resources):
    terraform_config = []
    for resource_type, resource_list in resources.items():
        if not resource_list or 'items' not in resource_list:
            continue

        for item in resource_list['items']:
            resource_name = item['metadata']['name']
            namespace = item['metadata'].get('namespace', 'default')

            resource_block = {
                'resource': {
                    f'kubernetes_{resource_type}': {
                        resource_name: {
                            'metadata': {
                                'name': resource_name,
                                'namespace': namespace
                            },
                            'spec': item.get('spec', {})
                        }
                    }
                }
            }
            terraform_config.append(resource_block)

    return terraform_config

# Função para salvar a configuração Terraform em arquivo
def save_to_yaml(terraform_config, filename='terraform_config.yaml'):
    with open(filename, 'w') as file:
        yaml.dump(terraform_config, file, default_flow_style=False)
    print(f"Configuração Terraform salva em {filename}")

if __name__ == "__main__":
    # 1. Coletar manifestos Kubernetes do cluster
    resources = get_kubernetes_resources()
    
    if resources:
        # 2. Gerar configuração Terraform
        terraform_config = generate_terraform_config(resources)

        # 3. Salvar a configuração em YAML para o Terraform Kubernetes Provider
        save_to_yaml(terraform_config)

