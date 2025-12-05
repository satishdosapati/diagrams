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
  },
  {
    id: "cloudfront-s3-static",
    title: "CloudFront Static Website",
    description: "CloudFront CDN → S3 bucket for static website hosting",
    prompt: "Create a static website architecture with CloudFront CDN distributing content from S3 bucket",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.network import CloudFront, Route53
from diagrams.aws.storage import S3

with Diagram("CloudFront Static Site", show=False, direction="TB"):
    dns = Route53("DNS")
    cdn = CloudFront("CloudFront")
    bucket = S3("S3 Bucket")
    
    dns >> cdn >> bucket`,
    category: "static-hosting",
    complexity: "simple",
    tags: ["cloudfront", "s3", "route53", "cdn", "static"],
    recommendedVariations: [
      "Add Lambda@Edge for edge computing",
      "Use S3 website hosting endpoint",
      "Add WAF for security"
    ]
  },
  {
    id: "kinesis-streaming",
    title: "Kinesis Real-Time Streaming",
    description: "Data sources → Kinesis Data Streams → Lambda processors → DynamoDB and S3",
    prompt: "Create a real-time streaming architecture with Kinesis Data Streams receiving data, Lambda functions processing, storing in DynamoDB and S3",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3

with Diagram("Kinesis Streaming", show=False):
    with Cluster("Data Sources"):
        sources = [EC2("app1"), EC2("app2")]
    
    kinesis = KinesisDataStreams("Kinesis Streams")
    
    with Cluster("Processing"):
        processors = [Lambda("process"), Lambda("transform")]
    
    dynamodb = Dynamodb("DynamoDB")
    s3 = S3("S3 Storage")
    
    sources >> kinesis >> processors
    processors >> dynamodb
    processors >> s3`,
    category: "streaming",
    complexity: "medium",
    tags: ["kinesis", "lambda", "dynamodb", "s3", "streaming"],
    recommendedVariations: [
      "Add Kinesis Firehose for batch delivery",
      "Use EventBridge for event routing",
      "Add Redshift for analytics"
    ]
  },
  {
    id: "step-functions-workflow",
    title: "Step Functions Workflow",
    description: "API Gateway → Step Functions orchestrating Lambda functions → DynamoDB",
    prompt: "Create a workflow orchestration with API Gateway, Step Functions coordinating multiple Lambda functions, and DynamoDB",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import StepFunctions
from diagrams.aws.network import APIGateway

with Diagram("Step Functions Workflow", show=False, direction="TB"):
    api = APIGateway("API Gateway")
    sf = StepFunctions("Step Functions")
    func1 = Lambda("Validate")
    func2 = Lambda("Process")
    func3 = Lambda("Store")
    db = Dynamodb("DynamoDB")
    
    api >> sf >> func1 >> func2 >> func3 >> db`,
    category: "serverless",
    complexity: "medium",
    tags: ["api-gateway", "step-functions", "lambda", "dynamodb", "workflow"],
    recommendedVariations: [
      "Add SNS for notifications",
      "Use SQS for queuing between steps",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "aurora-serverless",
    title: "Aurora Serverless Database",
    description: "Application Load Balancer → ECS Fargate → Aurora Serverless",
    prompt: "Create a serverless database architecture with ALB, ECS Fargate containers, and Aurora Serverless database",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, Fargate
from diagrams.aws.database import Aurora
from diagrams.aws.network import ApplicationLoadBalancer

with Diagram("Aurora Serverless", show=False):
    alb = ApplicationLoadBalancer("ALB")
    
    with Cluster("Fargate"):
        containers = [Fargate("service1"), Fargate("service2")]
    
    aurora = Aurora("Aurora")
    
    alb >> containers >> aurora`,
    category: "serverless",
    complexity: "medium",
    tags: ["alb", "fargate", "aurora", "serverless", "containers"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use RDS Proxy for connection pooling",
      "Add CloudFront for CDN"
    ]
  },
  {
    id: "eks-kubernetes",
    title: "EKS Kubernetes Cluster",
    description: "Route53 → CloudFront → ALB → EKS cluster → RDS",
    prompt: "Create a Kubernetes architecture with Route53, CloudFront CDN, Application Load Balancer, EKS cluster, and RDS database",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import ElasticKubernetesService
from diagrams.aws.database import RDS
from diagrams.aws.network import ApplicationLoadBalancer, CloudFront, Route53

with Diagram("EKS Cluster", show=False):
    dns = Route53("Route53")
    cdn = CloudFront("CloudFront")
    alb = ApplicationLoadBalancer("ALB")
    
    with Cluster("Kubernetes"):
        eks = ElasticKubernetesService("EKS")
    
    db = RDS("RDS")
    
    dns >> cdn >> alb >> eks >> db`,
    category: "containers",
    complexity: "complex",
    tags: ["route53", "cloudfront", "alb", "eks", "rds", "kubernetes"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use Aurora instead of RDS",
      "Add S3 for object storage"
    ]
  },
  {
    id: "sns-pubsub",
    title: "SNS Pub/Sub Messaging",
    description: "Lambda trigger → SNS topic → Multiple Lambda subscribers",
    prompt: "Create a pub/sub messaging architecture with Lambda triggering SNS topic, which sends to multiple Lambda subscribers",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import SNS

with Diagram("SNS Pub/Sub", show=False):
    trigger = Lambda("Trigger")
    sns = SNS("SNS Topic")
    
    with Cluster("Subscribers"):
        func1 = Lambda("Email")
        func2 = Lambda("SMS")
        func3 = Lambda("Webhook")
    
    trigger >> sns >> [func1, func2, func3]`,
    category: "integration",
    complexity: "medium",
    tags: ["lambda", "sns", "pubsub", "messaging"],
    recommendedVariations: [
      "Add SQS for queuing",
      "Use EventBridge for event routing",
      "Add DynamoDB for tracking"
    ]
  },
  {
    id: "eventbridge-events",
    title: "EventBridge Event-Driven",
    description: "Multiple sources → EventBridge → Lambda functions → DynamoDB",
    prompt: "Create an event-driven architecture with multiple sources sending to EventBridge, Lambda functions processing events, and DynamoDB storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge

with Diagram("EventBridge Events", show=False):
    with Cluster("Event Sources"):
        sources = [EC2("app"), Lambda("api"), Dynamodb("db")]
    
    eb = Eventbridge("EventBridge")
    
    with Cluster("Event Handlers"):
        handlers = [Lambda("process"), Lambda("notify")]
    
    db = Dynamodb("DynamoDB")
    
    sources >> eb >> handlers >> db`,
    category: "event-driven",
    complexity: "medium",
    tags: ["eventbridge", "lambda", "dynamodb", "events"],
    recommendedVariations: [
      "Add SQS for dead letter queue",
      "Use Step Functions for workflows",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "cognito-auth-api",
    title: "Cognito Authentication API",
    description: "API Gateway → Cognito → Lambda → DynamoDB",
    prompt: "Create a secure API with API Gateway, Cognito for authentication, Lambda functions, and DynamoDB",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway
from diagrams.aws.security import Cognito

with Diagram("Cognito Auth API", show=False, direction="TB"):
    api = APIGateway("API Gateway")
    cognito = Cognito("Cognito")
    func = Lambda("Function")
    db = Dynamodb("DynamoDB")
    
    api >> cognito >> func >> db`,
    category: "security",
    complexity: "medium",
    tags: ["api-gateway", "cognito", "lambda", "dynamodb", "auth"],
    recommendedVariations: [
      "Add WAF for additional security",
      "Use Secrets Manager for API keys",
      "Add CloudFront for CDN"
    ]
  },
  {
    id: "sagemaker-ml",
    title: "SageMaker ML Pipeline",
    description: "S3 → SageMaker → Lambda → DynamoDB",
    prompt: "Create a machine learning pipeline with S3 for training data, SageMaker for model training and inference, Lambda API, and DynamoDB",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.ml import SageMaker
from diagrams.aws.storage import S3

with Diagram("SageMaker ML", show=False, direction="TB"):
    data = S3("Training Data")
    sagemaker = SageMaker("SageMaker")
    api = Lambda("API")
    db = Dynamodb("Results")
    
    data >> sagemaker >> api >> db`,
    category: "ml",
    complexity: "complex",
    tags: ["s3", "sagemaker", "lambda", "dynamodb", "ml"],
    recommendedVariations: [
      "Add API Gateway for ML API",
      "Use Step Functions for ML workflows",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "athena-data-lake",
    title: "Athena Data Lake Analytics",
    description: "Data sources → S3 → Glue → Athena → QuickSight",
    prompt: "Create a data lake analytics architecture with data sources, S3 storage, Glue for ETL, Athena for querying, and QuickSight for visualization",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.analytics import Athena, Glue, Quicksight
from diagrams.aws.compute import EC2
from diagrams.aws.storage import S3

with Diagram("Athena Data Lake", show=False):
    with Cluster("Data Sources"):
        sources = [EC2("app1"), EC2("app2")]
    
    s3 = S3("Data Lake")
    glue = Glue("Glue ETL")
    athena = Athena("Athena")
    quicksight = Quicksight("QuickSight")
    
    sources >> s3 >> glue >> athena >> quicksight`,
    category: "analytics",
    complexity: "complex",
    tags: ["s3", "glue", "athena", "quicksight", "data-lake"],
    recommendedVariations: [
      "Add Kinesis for real-time data",
      "Use Redshift for data warehouse",
      "Add EventBridge for event triggers"
    ]
  },
  {
    id: "emr-big-data",
    title: "EMR Big Data Processing",
    description: "S3 → EMR → S3 processed data → Athena",
    prompt: "Create a big data processing architecture with S3 input data, EMR for Spark/Hadoop processing, storing results in S3, and Athena for querying",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.analytics import Athena, EMR
from diagrams.aws.storage import S3

with Diagram("EMR Big Data", show=False, direction="TB"):
    raw_data = S3("Raw Data")
    emr = EMR("EMR Cluster")
    processed = S3("Processed Data")
    athena = Athena("Athena")
    
    raw_data >> emr >> processed >> athena`,
    category: "analytics",
    complexity: "complex",
    tags: ["s3", "emr", "athena", "big-data"],
    recommendedVariations: [
      "Add Glue for data catalog",
      "Use Redshift for data warehouse",
      "Add QuickSight for visualization"
    ]
  },
  {
    id: "appsync-graphql",
    title: "AppSync GraphQL API",
    description: "AppSync → Lambda resolvers → DynamoDB and RDS",
    prompt: "Create a GraphQL API with AppSync, Lambda resolvers, connecting to both DynamoDB and RDS databases",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, RDS
from diagrams.aws.integration import AppSync

with Diagram("AppSync GraphQL", show=False, direction="TB"):
    appsync = AppSync("AppSync")
    resolver = Lambda("Resolver")
    dynamodb = Dynamodb("DynamoDB")
    rds = RDS("RDS")
    
    appsync >> resolver >> [dynamodb, rds]`,
    category: "api",
    complexity: "medium",
    tags: ["appsync", "lambda", "dynamodb", "rds", "graphql"],
    recommendedVariations: [
      "Add Cognito for authentication",
      "Use ElastiCache for caching",
      "Add CloudFront for CDN"
    ]
  },
  {
    id: "iot-core-pipeline",
    title: "IoT Core Data Pipeline",
    description: "IoT Core → Kinesis → Lambda → DynamoDB and S3",
    prompt: "Create an IoT data pipeline with IoT Core devices, Kinesis Data Streams, Lambda processors, storing in DynamoDB and S3",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.iot import IotCore
from diagrams.aws.storage import S3

with Diagram("IoT Pipeline", show=False):
    with Cluster("IoT Devices"):
        devices = [IotCore("device1"), IotCore("device2")]
    
    kinesis = KinesisDataStreams("Kinesis")
    processor = Lambda("Processor")
    
    dynamodb = Dynamodb("Metadata")
    s3 = S3("Data Storage")
    
    devices >> kinesis >> processor
    processor >> dynamodb
    processor >> s3`,
    category: "iot",
    complexity: "complex",
    tags: ["iot-core", "kinesis", "lambda", "dynamodb", "s3", "iot"],
    recommendedVariations: [
      "Add EventBridge for event routing",
      "Use Kinesis Firehose for batch delivery",
      "Add QuickSight for visualization"
    ]
  },
  {
    id: "multi-region-ha",
    title: "Multi-Region High Availability",
    description: "Route53 → CloudFront → Multiple regions with ALB and RDS",
    prompt: "Create a multi-region high availability architecture with Route53 DNS, CloudFront CDN, Application Load Balancers in multiple regions, and RDS Multi-AZ",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ApplicationLoadBalancer, CloudFront, Route53

with Diagram("Multi-Region HA", show=False):
    dns = Route53("Route53")
    cdn = CloudFront("CloudFront")
    
    with Cluster("Region 1"):
        alb1 = ApplicationLoadBalancer("ALB")
        ec2_1 = EC2("EC2")
        rds_1 = RDS("RDS")
        alb1 >> ec2_1 >> rds_1
    
    with Cluster("Region 2"):
        alb2 = ApplicationLoadBalancer("ALB")
        ec2_2 = EC2("EC2")
        rds_2 = RDS("RDS")
        alb2 >> ec2_2 >> rds_2
    
    dns >> cdn >> [alb1, alb2]`,
    category: "high-availability",
    complexity: "complex",
    tags: ["route53", "cloudfront", "alb", "ec2", "rds", "multi-region"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use Aurora Global Database",
      "Add S3 for cross-region replication"
    ]
  },
  {
    id: "lambda-sqs-async",
    title: "Lambda SQS Async Processing",
    description: "API Gateway → Lambda → SQS → Lambda workers → DynamoDB",
    prompt: "Create an async processing architecture with API Gateway, Lambda triggering SQS queue, Lambda workers processing, and DynamoDB storage",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.network import APIGateway

with Diagram("Lambda SQS Async", show=False, direction="TB"):
    api = APIGateway("API Gateway")
    trigger = Lambda("Trigger")
    sqs = SQS("SQS Queue")
    worker = Lambda("Worker")
    db = Dynamodb("DynamoDB")
    
    api >> trigger >> sqs >> worker >> db`,
    category: "serverless",
    complexity: "medium",
    tags: ["api-gateway", "lambda", "sqs", "dynamodb", "async"],
    recommendedVariations: [
      "Add DLQ for error handling",
      "Use Step Functions for workflows",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "kinesis-firehose-ingestion",
    title: "Kinesis Firehose Data Ingestion",
    description: "Data sources → Kinesis Firehose → S3 and Redshift",
    prompt: "Create a data ingestion pipeline with data sources, Kinesis Firehose for batch delivery, storing in S3 and Redshift",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.analytics import KinesisDataFirehose
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws.storage import S3

with Diagram("Kinesis Firehose", show=False):
    with Cluster("Data Sources"):
        sources = [EC2("app"), Lambda("api")]
    
    firehose = KinesisDataFirehose("Firehose")
    
    s3 = S3("S3 Storage")
    redshift = Redshift("Redshift")
    
    sources >> firehose >> [s3, redshift]`,
    category: "data-pipeline",
    complexity: "medium",
    tags: ["kinesis-firehose", "s3", "redshift", "ingestion"],
    recommendedVariations: [
      "Add Lambda for transformation",
      "Use Kinesis Data Streams for real-time",
      "Add Athena for querying S3"
    ]
  },
  {
    id: "backup-disaster-recovery",
    title: "Backup and Disaster Recovery",
    description: "EC2 → EBS → Backup → S3 Glacier",
    prompt: "Create a backup and disaster recovery architecture with EC2 instances, EBS volumes, AWS Backup service, and S3 Glacier for long-term storage",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.storage import Backup, ElasticBlockStoreEBS, S3Glacier

with Diagram("Backup DR", show=False, direction="TB"):
    ec2 = EC2("EC2")
    ebs = ElasticBlockStoreEBS("EBS")
    backup = Backup("Backup")
    glacier = S3Glacier("Glacier")
    
    ec2 >> ebs >> backup >> glacier`,
    category: "backup",
    complexity: "medium",
    tags: ["ec2", "ebs", "backup", "glacier", "disaster-recovery"],
    recommendedVariations: [
      "Add S3 for standard backups",
      "Use Cross-Region replication",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "waf-secure-api",
    title: "WAF Protected API",
    description: "CloudFront → WAF → API Gateway → Lambda → DynamoDB",
    prompt: "Create a secure API architecture with CloudFront CDN, WAF for protection, API Gateway, Lambda functions, and DynamoDB",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import WAF

with Diagram("WAF Protected API", show=False, direction="TB"):
    cdn = CloudFront("CloudFront")
    waf = WAF("WAF")
    api = APIGateway("API Gateway")
    func = Lambda("Function")
    db = Dynamodb("DynamoDB")
    
    cdn >> waf >> api >> func >> db`,
    category: "security",
    complexity: "medium",
    tags: ["cloudfront", "waf", "api-gateway", "lambda", "dynamodb", "security"],
    recommendedVariations: [
      "Add Cognito for authentication",
      "Use Shield for DDoS protection",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "fargate-serverless-containers",
    title: "Fargate Serverless Containers",
    description: "ALB → ECS Fargate → Aurora",
    prompt: "Create a serverless container architecture with Application Load Balancer, ECS Fargate containers, and Aurora database",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, Fargate
from diagrams.aws.database import Aurora
from diagrams.aws.network import ApplicationLoadBalancer

with Diagram("Fargate Containers", show=False):
    alb = ApplicationLoadBalancer("ALB")
    
    with Cluster("Fargate Services"):
        fargate1 = Fargate("service1")
        fargate2 = Fargate("service2")
        fargate3 = Fargate("service3")
    
    aurora = Aurora("Aurora")
    
    alb >> [fargate1, fargate2, fargate3] >> aurora`,
    category: "containers",
    complexity: "medium",
    tags: ["alb", "fargate", "aurora", "serverless", "containers"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use CloudFront for CDN",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "documentdb-mongodb",
    title: "DocumentDB MongoDB",
    description: "EC2 → DocumentDB → S3 backup",
    prompt: "Create a MongoDB-compatible architecture with EC2 application servers, DocumentDB cluster, and S3 for backups",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import DocumentdbMongodbCompatibility
from diagrams.aws.storage import S3

with Diagram("DocumentDB", show=False):
    with Cluster("Application"):
        apps = [EC2("app1"), EC2("app2")]
    
    with Cluster("Database"):
        docdb = DocumentdbMongodbCompatibility("DocumentDB")
    
    backup = S3("S3 Backup")
    
    apps >> docdb >> backup`,
    category: "database",
    complexity: "medium",
    tags: ["ec2", "documentdb", "mongodb", "s3"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use Multi-AZ for high availability",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "neptune-graph-db",
    title: "Neptune Graph Database",
    description: "Lambda → Neptune → S3",
    prompt: "Create a graph database architecture with Lambda functions, Neptune graph database, and S3 for data export",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Neptune
from diagrams.aws.storage import S3

with Diagram("Neptune Graph", show=False, direction="TB"):
    func = Lambda("Function")
    neptune = Neptune("Neptune")
    s3 = S3("S3 Export")
    
    func >> neptune >> s3`,
    category: "database",
    complexity: "medium",
    tags: ["lambda", "neptune", "graph-db", "s3"],
    recommendedVariations: [
      "Add API Gateway for GraphQL",
      "Use ElastiCache for caching",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "efs-shared-storage",
    title: "EFS Shared File Storage",
    description: "Multiple EC2 instances → EFS → Backup to S3",
    prompt: "Create a shared file storage architecture with multiple EC2 instances accessing EFS, with backups to S3",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.storage import ElasticFileSystemEFS, S3

with Diagram("EFS Shared Storage", show=False):
    with Cluster("EC2 Instances"):
        instances = [EC2("web1"), EC2("web2"), EC2("app1")]
    
    efs = ElasticFileSystemEFS("EFS")
    backup = S3("S3 Backup")
    
    instances >> efs >> backup`,
    category: "storage",
    complexity: "medium",
    tags: ["ec2", "efs", "s3", "shared-storage"],
    recommendedVariations: [
      "Add EBS for block storage",
      "Use FSx for Windows file shares",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "batch-processing",
    title: "AWS Batch Processing",
    description: "S3 → Batch → ECS → Results to S3",
    prompt: "Create a batch processing architecture with S3 input data, AWS Batch running ECS tasks, storing results back to S3",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import Batch, ECS
from diagrams.aws.storage import S3

with Diagram("Batch Processing", show=False, direction="TB"):
    input_s3 = S3("Input Data")
    batch = Batch("Batch")
    ecs = ECS("ECS Task")
    output_s3 = S3("Output Data")
    
    input_s3 >> batch >> ecs >> output_s3`,
    category: "compute",
    complexity: "medium",
    tags: ["s3", "batch", "ecs", "processing"],
    recommendedVariations: [
      "Add Step Functions for orchestration",
      "Use Lambda for triggering",
      "Add CloudWatch for monitoring"
    ]
  },
  {
    id: "elastic-beanstalk-paas",
    title: "Elastic Beanstalk PaaS",
    description: "Route53 → CloudFront → Elastic Beanstalk → RDS",
    prompt: "Create a Platform-as-a-Service architecture with Route53, CloudFront CDN, Elastic Beanstalk application, and RDS database",
    codeSnippet: `from diagrams import Diagram
from diagrams.aws.compute import ElasticBeanstalk
from diagrams.aws.database import RDS
from diagrams.aws.network import CloudFront, Route53

with Diagram("Elastic Beanstalk", show=False, direction="TB"):
    dns = Route53("Route53")
    cdn = CloudFront("CloudFront")
    eb = ElasticBeanstalk("Elastic Beanstalk")
    db = RDS("RDS")
    
    dns >> cdn >> eb >> db`,
    category: "paas",
    complexity: "medium",
    tags: ["route53", "cloudfront", "elastic-beanstalk", "rds"],
    recommendedVariations: [
      "Add ElastiCache for caching",
      "Use S3 for static assets",
      "Add CloudWatch for monitoring"
    ]
  }
]

