import { Example } from './types'

export const gcpExamples: Example[] = [
  {
    id: "gcp-message-collecting",
    title: "Message Collecting System",
    description: "Mobile users and IoT devices sending messages through PubSub → Dataflow → BigQuery and Cloud Storage",
    prompt: "Build a message collecting system with mobile users and IoT devices sending data through PubSub, Dataflow processing, storing in BigQuery and Cloud Storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import Functions
from diagrams.gcp.database import BigTable
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users

with Diagram("Message Collecting", show=False):
    users = Users("Users")
    mobile = Mobile("Mobile Clients")
    pubsub = PubSub("pubsub")

    with Cluster("Source of Data"):
        [IotCore("core1"),
         IotCore("core2"),
         IotCore("core3")] >> pubsub
        [users, mobile] >> pubsub

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
    tags: ["iot", "pubsub", "dataflow", "bigquery", "gcs", "mobile", "users", "gcp"],
    recommendedVariations: [
      "Add Cloud Functions for event processing",
      "Use Cloud Run instead of Functions",
      "Add Cloud SQL for relational data",
      "Include Android/iOS specific clients"
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
  },
  {
    id: "gcp-cloud-run-containers",
    title: "Cloud Run Container Services",
    description: "Cloud CDN → Load Balancing → Cloud Run → Cloud SQL",
    prompt: "Create a containerized architecture with Cloud CDN, Load Balancing, Cloud Run containers, and Cloud SQL",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import CloudRun, CloudSQL
from diagrams.gcp.network import CloudCDN, LoadBalancing

with Diagram("Cloud Run Services", show=False):
    cdn = CloudCDN("Cloud CDN")
    lb = LoadBalancing("Load Balancer")
    
    with Cluster("Cloud Run"):
        containers = [CloudRun("service1"), CloudRun("service2"), CloudRun("service3")]
    
    db = CloudSQL("Cloud SQL")
    
    cdn >> lb >> containers >> db`,
    category: "containers",
    complexity: "medium",
    tags: ["cloud-cdn", "load-balancing", "cloud-run", "cloud-sql", "containers", "gcp"],
    recommendedVariations: [
      "Add Memorystore for caching",
      "Use GKE for Kubernetes",
      "Add Cloud Storage for assets"
    ]
  },
  {
    id: "gcp-gke-kubernetes",
    title: "GKE Kubernetes Cluster",
    description: "Cloud CDN → Load Balancing → GKE → Cloud SQL",
    prompt: "Create a Kubernetes architecture with Cloud CDN, Load Balancing, GKE cluster, and Cloud SQL",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import GKE, CloudSQL
from diagrams.gcp.network import CloudCDN, LoadBalancing

with Diagram("GKE Cluster", show=False):
    cdn = CloudCDN("CDN")
    lb = LoadBalancing("Load Balancer")
    
    with Cluster("Kubernetes"):
        gke = GKE("GKE Cluster")
    
    db = CloudSQL("Cloud SQL")
    
    cdn >> lb >> gke >> db`,
    category: "containers",
    complexity: "complex",
    tags: ["cloud-cdn", "load-balancing", "gke", "cloud-sql", "kubernetes", "gcp"],
    recommendedVariations: [
      "Add Memorystore for caching",
      "Use Cloud Run for serverless containers",
      "Add Cloud Storage for object storage"
    ]
  },
  {
    id: "gcp-compute-engine",
    title: "Compute Engine Web App",
    description: "Cloud CDN → Load Balancing → Compute Engine VMs → Cloud SQL",
    prompt: "Create a web application with Cloud CDN, Load Balancing, Compute Engine VMs, and Cloud SQL",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import ComputeEngine, CloudSQL
from diagrams.gcp.network import CloudCDN, LoadBalancing

with Diagram("Compute Engine Web App", show=False):
    cdn = CloudCDN("Cloud CDN")
    lb = LoadBalancing("Load Balancer")
    
    with Cluster("Compute"):
        vms = [ComputeEngine("vm1"), ComputeEngine("vm2"), ComputeEngine("vm3")]
    
    db = CloudSQL("Cloud SQL")
    
    cdn >> lb >> vms >> db`,
    category: "three-tier",
    complexity: "medium",
    tags: ["cloud-cdn", "load-balancing", "compute-engine", "cloud-sql", "gcp"],
    recommendedVariations: [
      "Add Memorystore for caching",
      "Use Cloud Run instead of VMs",
      "Add Cloud Storage for static assets"
    ]
  },
  {
    id: "gcp-pubsub-workflow",
    title: "Pub/Sub Workflow",
    description: "Cloud Functions → Pub/Sub → Cloud Tasks → Cloud Functions → Firestore",
    prompt: "Create a workflow architecture with Cloud Functions triggering Pub/Sub, Cloud Tasks for scheduling, and Firestore for storage",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Firestore
from diagrams.gcp.integration import CloudTasks, PubSub

with Diagram("Pub/Sub Workflow", show=False, direction="TB"):
    trigger = CloudFunctions("Trigger")
    pubsub = PubSub("Pub/Sub")
    tasks = CloudTasks("Cloud Tasks")
    processor = CloudFunctions("Processor")
    db = Firestore("Firestore")
    
    trigger >> pubsub >> tasks >> processor >> db`,
    category: "event-driven",
    complexity: "medium",
    tags: ["cloud-functions", "pubsub", "cloud-tasks", "firestore", "workflow", "gcp"],
    recommendedVariations: [
      "Add Cloud Scheduler for cron jobs",
      "Use Cloud Workflows for orchestration",
      "Add Cloud Storage for file storage"
    ]
  },
  {
    id: "gcp-bigquery-analytics",
    title: "BigQuery Data Warehouse",
    description: "Data sources → Cloud Storage → Dataflow → BigQuery → Data Studio",
    prompt: "Create a data warehouse architecture with data sources, Cloud Storage, Dataflow ETL, BigQuery data warehouse, and visualization",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow
from diagrams.gcp.compute import ComputeEngine
from diagrams.gcp.storage import GCS

with Diagram("BigQuery Analytics", show=False):
    with Cluster("Data Sources"):
        sources = [ComputeEngine("app1"), ComputeEngine("app2")]
    
    storage = GCS("Cloud Storage")
    dataflow = Dataflow("Dataflow")
    bigquery = BigQuery("BigQuery")
    
    sources >> storage >> dataflow >> bigquery`,
    category: "analytics",
    complexity: "complex",
    tags: ["cloud-storage", "dataflow", "bigquery", "data-warehouse", "gcp"],
    recommendedVariations: [
      "Add Pub/Sub for real-time data",
      "Use Dataproc for big data",
      "Add Data Fusion for data integration"
    ]
  },
  {
    id: "gcp-cloud-workflows",
    title: "Cloud Workflows Orchestration",
    description: "API Gateway → Cloud Workflows → Cloud Functions → Firestore",
    prompt: "Create a workflow orchestration with API Gateway, Cloud Workflows orchestrating Cloud Functions, and Firestore",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Firestore
from diagrams.gcp.integration import APIGateway, Workflows

with Diagram("Cloud Workflows", show=False, direction="TB"):
    api = APIGateway("API Gateway")
    workflow = Workflows("Cloud Workflows")
    func1 = CloudFunctions("Process")
    func2 = CloudFunctions("Validate")
    func3 = CloudFunctions("Store")
    db = Firestore("Firestore")
    
    api >> workflow >> [func1, func2] >> func3 >> db`,
    category: "serverless",
    complexity: "medium",
    tags: ["api-gateway", "workflows", "cloud-functions", "firestore", "orchestration", "gcp"],
    recommendedVariations: [
      "Add Pub/Sub for async processing",
      "Use Cloud Tasks for scheduling",
      "Add Cloud Storage for file storage"
    ]
  },
  {
    id: "gcp-memorystore-caching",
    title: "Memorystore Caching Layer",
    description: "Load Balancing → Compute Engine → Memorystore → Cloud SQL",
    prompt: "Create a high-performance architecture with Load Balancing, Compute Engine VMs, Memorystore for caching, and Cloud SQL",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import ComputeEngine, CloudSQL
from diagrams.gcp.database import Memorystore
from diagrams.gcp.network import LoadBalancing

with Diagram("Memorystore Caching", show=False):
    lb = LoadBalancing("Load Balancer")
    
    with Cluster("Compute"):
        vms = [ComputeEngine("vm1"), ComputeEngine("vm2"), ComputeEngine("vm3")]
    
    cache = Memorystore("Memorystore")
    db = CloudSQL("Cloud SQL")
    
    lb >> vms
    vms >> cache
    vms >> db`,
    category: "three-tier",
    complexity: "medium",
    tags: ["load-balancing", "compute-engine", "memorystore", "cloud-sql", "caching", "gcp"],
    recommendedVariations: [
      "Add Cloud CDN for edge caching",
      "Use Cloud Spanner instead of Cloud SQL",
      "Add Cloud Storage for static assets"
    ]
  },
  {
    id: "gcp-spanner-global",
    title: "Cloud Spanner Global Database",
    description: "Cloud CDN → Load Balancing → Cloud Run → Cloud Spanner",
    prompt: "Create a globally distributed architecture with Cloud CDN, Load Balancing, Cloud Run services, and Cloud Spanner global database",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import CloudRun
from diagrams.gcp.database import Spanner
from diagrams.gcp.network import CloudCDN, LoadBalancing

with Diagram("Spanner Global", show=False):
    cdn = CloudCDN("Cloud CDN")
    lb = LoadBalancing("Load Balancer")
    
    with Cluster("Cloud Run"):
        services = [CloudRun("region1"), CloudRun("region2")]
    
    spanner = Spanner("Cloud Spanner")
    
    cdn >> lb >> services >> spanner`,
    category: "database",
    complexity: "complex",
    tags: ["cloud-cdn", "load-balancing", "cloud-run", "spanner", "global", "gcp"],
    recommendedVariations: [
      "Add Memorystore for caching",
      "Use Firestore for document storage",
      "Add Cloud Armor for security"
    ]
  },
  {
    id: "gcp-bigtable-nosql",
    title: "Bigtable NoSQL Database",
    description: "Cloud Functions → Bigtable → Cloud Storage",
    prompt: "Create a NoSQL architecture with Cloud Functions, Bigtable for high-throughput data, and Cloud Storage",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Bigtable
from diagrams.gcp.storage import GCS

with Diagram("Bigtable NoSQL", show=False, direction="TB"):
    func = CloudFunctions("Function")
    bigtable = Bigtable("Bigtable")
    storage = GCS("Cloud Storage")
    
    func >> bigtable >> storage`,
    category: "database",
    complexity: "medium",
    tags: ["cloud-functions", "bigtable", "cloud-storage", "nosql", "gcp"],
    recommendedVariations: [
      "Add Pub/Sub for streaming",
      "Use Firestore for document storage",
      "Add Dataflow for processing"
    ]
  },
  {
    id: "gcp-dataproc-bigdata",
    title: "Dataproc Big Data",
    description: "Cloud Storage → Dataproc → BigQuery → Data Studio",
    prompt: "Create a big data processing architecture with Cloud Storage, Dataproc for Spark/Hadoop, BigQuery, and visualization",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.analytics import BigQuery, Dataproc
from diagrams.gcp.storage import GCS

with Diagram("Dataproc Big Data", show=False, direction="TB"):
    storage = GCS("Cloud Storage")
    dataproc = Dataproc("Dataproc")
    bigquery = BigQuery("BigQuery")
    
    storage >> dataproc >> bigquery`,
    category: "analytics",
    complexity: "complex",
    tags: ["cloud-storage", "dataproc", "bigquery", "big-data", "gcp"],
    recommendedVariations: [
      "Add Pub/Sub for real-time data",
      "Use Dataflow for streaming",
      "Add Data Fusion for integration"
    ]
  },
  {
    id: "gcp-iot-core-pipeline",
    title: "IoT Core Data Pipeline",
    description: "IoT Core → Pub/Sub → Cloud Functions → Bigtable and Cloud Storage",
    prompt: "Create an IoT data pipeline with IoT Core devices, Pub/Sub messaging, Cloud Functions processors, storing in Bigtable and Cloud Storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Bigtable
from diagrams.gcp.integration import PubSub
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS

with Diagram("IoT Pipeline", show=False):
    with Cluster("IoT Devices"):
        devices = [IotCore("device1"), IotCore("device2"), IotCore("device3")]
    
    pubsub = PubSub("Pub/Sub")
    
    with Cluster("Processing"):
        processors = [CloudFunctions("process"), CloudFunctions("analyze")]
    
    bigtable = Bigtable("Bigtable")
    storage = GCS("Cloud Storage")
    
    devices >> pubsub >> processors
    processors >> bigtable
    processors >> storage`,
    category: "iot",
    complexity: "complex",
    tags: ["iot-core", "pubsub", "cloud-functions", "bigtable", "cloud-storage", "iot", "gcp"],
    recommendedVariations: [
      "Add Cloud Workflows for orchestration",
      "Use BigQuery for analytics",
      "Add Data Studio for visualization"
    ]
  },
  {
    id: "gcp-ai-platform-ml",
    title: "AI Platform ML Pipeline",
    description: "Cloud Storage → AI Platform → Cloud Functions → Firestore",
    prompt: "Create a machine learning pipeline with Cloud Storage for data, AI Platform for model training and inference, Cloud Functions, and Firestore",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions
from diagrams.gcp.database import Firestore
from diagrams.gcp.ml import AIPlatform
from diagrams.gcp.storage import GCS

with Diagram("ML Pipeline", show=False, direction="TB"):
    data = GCS("Training Data")
    ai = AIPlatform("AI Platform")
    func = CloudFunctions("API")
    db = Firestore("Results")
    
    data >> ai >> func >> db`,
    category: "ml",
    complexity: "complex",
    tags: ["cloud-storage", "ai-platform", "cloud-functions", "firestore", "machine-learning", "gcp"],
    recommendedVariations: [
      "Add API Gateway for ML API",
      "Use AutoML for no-code ML",
      "Add Cloud Monitoring for monitoring"
    ]
  },
  {
    id: "gcp-vpc-network",
    title: "VPC Network Architecture",
    description: "VPC with Cloud NAT, Cloud VPN, and Cloud Interconnect",
    prompt: "Create a VPC network architecture with VPC, Cloud NAT, Cloud VPN, Cloud Interconnect, and Compute Engine VMs",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import ComputeEngine
from diagrams.gcp.network import CloudInterconnect, CloudNAT, CloudVPN, VPC

with Diagram("VPC Network", show=False):
    vpc = VPC("VPC")
    nat = CloudNAT("Cloud NAT")
    vpn = CloudVPN("Cloud VPN")
    interconnect = CloudInterconnect("Cloud Interconnect")
    
    with Cluster("VPC"):
        vm1 = ComputeEngine("VM 1")
        vm2 = ComputeEngine("VM 2")
    
    vpc >> [nat, vpn, interconnect]
    vpc >> [vm1, vm2]`,
    category: "network",
    complexity: "medium",
    tags: ["vpc", "cloud-nat", "cloud-vpn", "cloud-interconnect", "compute-engine", "network", "gcp"],
    recommendedVariations: [
      "Add Load Balancing for load distribution",
      "Use Cloud Armor for security",
      "Add Cloud Monitoring for network monitoring"
    ]
  },
  {
    id: "gcp-cloud-armor-security",
    title: "Cloud Armor Protected API",
    description: "Cloud CDN → Cloud Armor → Load Balancing → Cloud Run",
    prompt: "Create a protected API architecture with Cloud CDN, Cloud Armor for DDoS protection, Load Balancing, and Cloud Run services",
    codeSnippet: `from diagrams import Diagram
from diagrams.gcp.compute import CloudRun
from diagrams.gcp.network import CloudArmor, CloudCDN, LoadBalancing

with Diagram("Cloud Armor Protected", show=False, direction="TB"):
    cdn = CloudCDN("Cloud CDN")
    armor = CloudArmor("Cloud Armor")
    lb = LoadBalancing("Load Balancer")
    run = CloudRun("Cloud Run")
    
    cdn >> armor >> lb >> run`,
    category: "security",
    complexity: "medium",
    tags: ["cloud-cdn", "cloud-armor", "load-balancing", "cloud-run", "security", "gcp"],
    recommendedVariations: [
      "Add IAM for access control",
      "Use Secret Manager for secrets",
      "Add Cloud Monitoring for security monitoring"
    ]
  },
  {
    id: "hybrid-cloud-gcp",
    title: "Hybrid Cloud Architecture",
    description: "On-premises datacenter with VMware virtualization connecting to GCP VPC via Cloud Interconnect",
    prompt: "Create a hybrid cloud architecture with on-premises datacenter using VMware virtualization connecting to GCP VPC through Cloud Interconnect",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.gcp.compute import ComputeEngine
from diagrams.gcp.network import CloudInterconnect, VPC
from diagrams.generic.os import LinuxGeneral, Windows
from diagrams.generic.place import Datacenter
from diagrams.generic.virtualization import Vmware
from diagrams.onprem.client import Users

with Diagram("Hybrid Cloud Architecture", show=False):
    users = Users("Users")
    
    with Cluster("On-Premises"):
        dc = Datacenter("Data Center")
        vmware = Vmware("VMware")
        with Cluster("Virtual Machines"):
            win_vm = Windows("Windows Server")
            linux_vm = LinuxGeneral("Linux Server")
    
    interconnect = CloudInterconnect("Cloud Interconnect")
    
    with Cluster("GCP VPC"):
        vpc = VPC("VPC")
        gce = ComputeEngine("Compute Engine")
    
    users >> dc
    dc >> vmware >> [win_vm, linux_vm]
    [win_vm, linux_vm] >> interconnect >> vpc >> gce`,
    category: "hybrid",
    complexity: "complex",
    tags: ["hybrid", "datacenter", "cloud-interconnect", "vpc", "vmware", "windows", "linux", "onprem", "gcp"],
    recommendedVariations: [
      "Add Cloud VPN as backup connection",
      "Include multiple datacenters",
      "Use different virtualization platforms (QEMU, VirtualBox)",
      "Add load balancer in GCP VPC"
    ]
  }
]

