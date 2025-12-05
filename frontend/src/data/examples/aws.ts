import { Example } from './types'

export const awsExamples: Example[] = [
  {
    id: "grouped-workers",
    title: "Grouped Workers",
    description: "Load balancer distributing traffic to multiple EC2 workers connected to RDS database",
    prompt: "Create a load balancer with multiple EC2 worker instances connected to an RDS database",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Grouped Workers", show=False, direction="TB"):
    ELB("lb") >> [EC2("worker1"),
                  EC2("worker2"),
                  EC2("worker3"),
                  EC2("worker4"),
                  EC2("worker5")] >> RDS("events")`,
    category: "three-tier",
    complexity: "simple",
    tags: ["load-balancer", "ec2", "rds", "workers"],
    recommendedVariations: [
      "Replace EC2 with Lambda for serverless workers",
      "Add Auto Scaling Group for EC2 instances",
      "Use Aurora instead of RDS for better performance"
    ]
  },
  {
    id: "clustered-web-services",
    title: "Clustered Web Services",
    description: "Route53 DNS → Load balancer → ECS services → RDS with ElastiCache",
    prompt: "Create a clustered web service architecture with Route53, load balancer, ECS containers, RDS database, and ElastiCache",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB, Route53

with Diagram("Clustered Web Services", show=False):
    dns = Route53("dns")
    lb = ELB("lb")

    with Cluster("Services"):
        svc_group = [ECS("web1"),
                     ECS("web2"),
                     ECS("web3")]

    with Cluster("DB Cluster"):
        db_primary = RDS("userdb")
        db_primary - [RDS("userdb ro")]

    memcached = ElastiCache("memcached")

    dns >> lb >> svc_group
    svc_group >> db_primary
    svc_group >> memcached`,
    category: "microservices",
    complexity: "medium",
    tags: ["route53", "elb", "ecs", "rds", "elasticache", "clusters"],
    recommendedVariations: [
      "Add CloudFront CDN in front of Route53",
      "Use EKS instead of ECS for Kubernetes",
      "Add S3 for static assets"
    ]
  },
  {
    id: "event-processing",
    title: "Event Processing Pipeline",
    description: "EKS source → ECS workers → SQS → Lambda handlers → S3 storage and Redshift analytics",
    prompt: "Build an event processing pipeline with EKS source, ECS workers, SQS queue, Lambda handlers, S3 storage, and Redshift analytics",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3

with Diagram("Event Processing", show=False):
    source = EKS("k8s source")

    with Cluster("Event Flows"):
        with Cluster("Event Workers"):
            workers = [ECS("worker1"),
                       ECS("worker2"),
                       ECS("worker3")]

        queue = SQS("event queue")

        with Cluster("Processing"):
            handlers = [Lambda("proc1"),
                        Lambda("proc2"),
                        Lambda("proc3")]

    store = S3("events store")
    dw = Redshift("analytics")

    source >> workers >> queue >> handlers
    handlers >> store
    handlers >> dw`,
    category: "data-pipeline",
    complexity: "complex",
    tags: ["eks", "ecs", "sqs", "lambda", "s3", "redshift", "events"],
    recommendedVariations: [
      "Add Kinesis Data Streams for real-time processing",
      "Use EventBridge instead of SQS",
      "Add DynamoDB for event metadata"
    ]
  },
  {
    id: "serverless-api",
    title: "Serverless API",
    description: "API Gateway → Lambda functions → DynamoDB database",
    prompt: "Create a serverless API with API Gateway, Lambda functions, and DynamoDB",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless API", show=False, direction="TB"):
    api = APIGateway("API Gateway")
    func = Lambda("Function")
    db = Dynamodb("Database")
    api >> func >> db`,
    category: "serverless",
    complexity: "simple",
    tags: ["api-gateway", "lambda", "dynamodb", "serverless"],
    recommendedVariations: [
      "Add CloudFront CDN in front of API Gateway",
      "Add S3 for static assets",
      "Use Step Functions for workflows"
    ]
  },
  {
    id: "vpc-network",
    title: "VPC Network Architecture",
    description: "VPC with public and private subnets, NAT Gateway, and Internet Gateway",
    prompt: "Create a VPC with public and private subnets, NAT Gateway, and Internet Gateway",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway, NATGateway

with Diagram("VPC Network", show=False):
    igw = InternetGateway("Internet Gateway")
    
    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            pub_sub = PublicSubnet("Public")
            nat = NATGateway("NAT")
            web = EC2("Web Server")
        
        with Cluster("Private Subnet"):
            priv_sub = PrivateSubnet("Private")
            app = EC2("App Server")
            db = EC2("Database")
    
    igw >> pub_sub
    pub_sub >> nat >> priv_sub
    web >> app >> db`,
    category: "network",
    complexity: "medium",
    tags: ["vpc", "subnet", "nat", "internet-gateway", "network"],
    recommendedVariations: [
      "Add VPN Gateway for site-to-site VPN",
      "Add Transit Gateway for multi-VPC",
      "Add Security Groups visualization"
    ]
  }
]

