export interface Example {
  id: string
  title: string
  description: string
  prompt: string
  codeSnippet: string
  category: string
  complexity: "simple" | "medium" | "complex"
  tags: string[]
  recommendedVariations?: string[]
}

export interface ExamplesByProvider {
  aws: Example[]
  azure: Example[]
  gcp: Example[]
}

export const examples: ExamplesByProvider = {
  aws: [
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
  ],
  azure: [
    {
      id: "azure-web-app",
      title: "Azure Web Application",
      description: "Azure Functions → Blob Storage → Cosmos DB",
      prompt: "Create an Azure web application with Azure Functions, Blob Storage, and Cosmos DB",
      codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import Function
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import BlobStorage

with Diagram("Azure Web App", show=False, direction="TB"):
    func = Function("Azure Function")
    blob = BlobStorage("Blob Storage")
    cosmos = CosmosDb("Cosmos DB")
    func >> blob >> cosmos`,
      category: "serverless",
      complexity: "simple",
      tags: ["function", "blob", "cosmos", "azure"],
      recommendedVariations: [
        "Add Azure Front Door for CDN",
        "Use Azure SQL instead of Cosmos DB",
        "Add Azure Key Vault for secrets"
      ]
    },
    {
      id: "azure-containers",
      title: "Container Services",
      description: "Container Instances → Kubernetes Services → Azure SQL",
      prompt: "Design containerized services with Container Instances, Kubernetes Services, and Azure SQL",
      codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import ContainerInstances, KubernetesServices
from diagrams.azure.database import SQLDatabases

with Diagram("Azure Containers", show=False):
    with Cluster("Compute"):
        containers = ContainerInstances("Containers")
        aks = KubernetesServices("AKS")
    
    db = SQLDatabases("Azure SQL")
    
    containers >> aks >> db`,
      category: "containers",
      complexity: "medium",
      tags: ["containers", "kubernetes", "azure-sql", "azure"],
      recommendedVariations: [
        "Add Azure Container Registry",
        "Use Azure App Service instead",
        "Add Azure Monitor for observability"
      ]
    }
  ],
  gcp: [
    {
      id: "gcp-message-collecting",
      title: "Message Collecting System",
      description: "IoT Core → PubSub → Dataflow → BigQuery and Cloud Storage",
      prompt: "Build a message collecting system with IoT Core, PubSub, Dataflow, BigQuery, and Cloud Storage",
      codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import Functions
from diagrams.gcp.database import BigTable
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS

with Diagram("Message Collecting", show=False):
    pubsub = PubSub("pubsub")

    with Cluster("Source of Data"):
        [IotCore("core1"),
         IotCore("core2"),
         IotCore("core3")] >> pubsub

    with Cluster("Targets"):
        with Cluster("Data Flow"):
            flow = Dataflow("data flow")

        with Cluster("Data Lake"):
            flow >> [BigQuery("bq"),
                     GCS("storage")]

        with Cluster("Event Driven"):
            with Cluster("Processing"):
                flow >> Functions("func") >> BigTable("bigtable")

    pubsub >> flow`,
      category: "data-pipeline",
      complexity: "complex",
      tags: ["iot", "pubsub", "dataflow", "bigquery", "gcs", "gcp"],
      recommendedVariations: [
        "Add Cloud Functions for event processing",
        "Use Cloud Run instead of Functions",
        "Add Cloud SQL for relational data"
      ]
    },
    {
      id: "gcp-serverless",
      title: "GCP Serverless Architecture",
      description: "Cloud Functions → Cloud Storage → Firestore",
      prompt: "Create a GCP serverless architecture with Cloud Functions, Cloud Storage, and Firestore",
      codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Firestore
from diagrams.gcp.storage import GCS

with Diagram("GCP Serverless", show=False, direction="TB"):
    func = CloudFunctions("Cloud Function")
    storage = GCS("Cloud Storage")
    db = Firestore("Firestore")
    func >> storage >> db`,
      category: "serverless",
      complexity: "simple",
      tags: ["cloud-functions", "cloud-storage", "firestore", "gcp"],
      recommendedVariations: [
        "Add Cloud Run for containers",
        "Use Cloud SQL instead of Firestore",
        "Add Cloud Load Balancing"
      ]
    }
  ]
}

export function getExamplesByProvider(provider: "aws" | "azure" | "gcp"): Example[] {
  return examples[provider] || []
}

export function getExampleById(provider: "aws" | "azure" | "gcp", id: string): Example | undefined {
  return examples[provider]?.find(ex => ex.id === id)
}

export function getExamplesByCategory(provider: "aws" | "azure" | "gcp", category: string): Example[] {
  return examples[provider]?.filter(ex => ex.category === category) || []
}

