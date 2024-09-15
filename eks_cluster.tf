provider:
  aws:
    region: us-east-1
resource:
  aws_eks_cluster:
    eks_cluster:
      name: eksCluster
      role_arn: arn:aws:iam::123456789012:role/eksServiceRole
      vpc_config:
        subnet_ids:
        - subnet-abcde123
        - subnet-fghij456
  aws_eks_node_group:
    eks_nodes:
      cluster_name: eksCluster
      instance_types:
      - t3.medium
      node_group_name: eksNodes
      node_role_arn: arn:aws:iam::123456789012:role/eksNodeRole
      scaling_config:
        desired_size: 1
        max_size: 2
        min_size: 0
      subnet_ids:
      - subnet-abcde123
      - subnet-fghij456
