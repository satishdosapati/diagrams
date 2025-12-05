import { Example } from './types'

export const azureExamples: Example[] = [
  {
    id: "azure-web-app",
    title: "Azure Web Application",
    description: "Users accessing Azure Functions → Blob Storage → Cosmos DB",
    prompt: "Create an Azure web application with users accessing through Azure Functions, Blob Storage, and Cosmos DB",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import Function
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.onprem.client import Users

with Diagram("Azure Web App", show=False, direction="TB"):
    users = Users("Users")
    func = Function("Azure Function")
    blob = BlobStorage("Blob Storage")
    cosmos = CosmosDb("Cosmos DB")
    users >> func >> blob >> cosmos`,
    category: "serverless",
    complexity: "simple",
    tags: ["function", "blob", "cosmos", "azure", "users"],
    recommendedVariations: [
      "Add Azure Front Door for CDN",
      "Use Azure SQL instead of Cosmos DB",
      "Add Azure Key Vault for secrets",
      "Include mobile clients (Android/iOS)"
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
  },
  {
    id: "azure-app-service",
    title: "App Service Web App",
    description: "Azure CDN → Application Gateway → App Service → SQL Database",
    prompt: "Create a web application with Azure CDN, Application Gateway, App Service, and SQL Database",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import AppService
from diagrams.azure.database import SQLDatabases
from diagrams.azure.network import ApplicationGateway, CDN

with Diagram("App Service Web App", show=False, direction="TB"):
    cdn = CDN("Azure CDN")
    gateway = ApplicationGateway("App Gateway")
    app = AppService("App Service")
    db = SQLDatabases("SQL Database")
    
    cdn >> gateway >> app >> db`,
    category: "three-tier",
    complexity: "medium",
    tags: ["cdn", "application-gateway", "app-service", "sql", "azure"],
    recommendedVariations: [
      "Add Redis Cache for caching",
      "Use Cosmos DB instead of SQL",
      "Add Azure Key Vault for secrets"
    ]
  },
  {
    id: "azure-aks-cluster",
    title: "AKS Kubernetes Cluster",
    description: "Traffic Manager → Load Balancer → AKS → Cosmos DB",
    prompt: "Create a Kubernetes architecture with Traffic Manager, Load Balancer, AKS cluster, and Cosmos DB",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import KubernetesServices
from diagrams.azure.database import CosmosDb
from diagrams.azure.network import LoadBalancers, TrafficManager

with Diagram("AKS Cluster", show=False):
    tm = TrafficManager("Traffic Manager")
    lb = LoadBalancers("Load Balancer")
    
    with Cluster("Kubernetes"):
        aks = KubernetesServices("AKS")
    
    db = CosmosDb("Cosmos DB")
    
    tm >> lb >> aks >> db`,
    category: "containers",
    complexity: "complex",
    tags: ["traffic-manager", "load-balancer", "aks", "cosmos", "kubernetes", "azure"],
    recommendedVariations: [
      "Add Redis Cache for caching",
      "Use Azure SQL instead of Cosmos DB",
      "Add Azure Monitor for monitoring"
    ]
  },
  {
    id: "azure-event-driven",
    title: "Event-Driven Architecture",
    description: "Event Grid → Logic Apps → Azure Functions → Storage",
    prompt: "Create an event-driven architecture with Event Grid, Logic Apps, Azure Functions, and Blob Storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import Function
from diagrams.azure.integration import EventGrid, LogicApps
from diagrams.azure.storage import BlobStorage

with Diagram("Event-Driven Azure", show=False):
    eg = EventGrid("Event Grid")
    
    with Cluster("Processing"):
        logic = LogicApps("Logic Apps")
        func = Function("Function")
    
    storage = BlobStorage("Blob Storage")
    
    eg >> logic >> func >> storage`,
    category: "event-driven",
    complexity: "medium",
    tags: ["event-grid", "logic-apps", "function", "blob", "azure"],
    recommendedVariations: [
      "Add Service Bus for queuing",
      "Use Event Hubs for streaming",
      "Add Cosmos DB for data storage"
    ]
  },
  {
    id: "azure-service-bus",
    title: "Service Bus Messaging",
    description: "Azure Functions → Service Bus → Multiple subscribers",
    prompt: "Create a messaging architecture with Azure Functions triggering Service Bus, which sends to multiple Azure Functions and Logic Apps",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import Function
from diagrams.azure.integration import LogicApps, ServiceBus

with Diagram("Service Bus Messaging", show=False):
    trigger = Function("Trigger")
    sb = ServiceBus("Service Bus")
    
    with Cluster("Subscribers"):
        func1 = Function("Processor 1")
        func2 = Function("Processor 2")
        logic = LogicApps("Logic App")
    
    trigger >> sb >> [func1, func2, logic]`,
    category: "integration",
    complexity: "medium",
    tags: ["function", "service-bus", "logic-apps", "messaging", "azure"],
    recommendedVariations: [
      "Add Event Grid for event routing",
      "Use Event Hubs for streaming",
      "Add Cosmos DB for tracking"
    ]
  },
  {
    id: "azure-event-hubs-streaming",
    title: "Event Hubs Streaming",
    description: "Data sources → Event Hubs → Stream Analytics → Cosmos DB and Blob Storage",
    prompt: "Create a real-time streaming architecture with Event Hubs receiving data, Stream Analytics processing, storing in Cosmos DB and Blob Storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.analytics import StreamAnalytics
from diagrams.azure.compute import Function, VM
from diagrams.azure.database import CosmosDb
from diagrams.azure.integration import EventHubs
from diagrams.azure.storage import BlobStorage

with Diagram("Event Hubs Streaming", show=False):
    with Cluster("Data Sources"):
        sources = [VM("source1"), VM("source2"), Function("api")]
    
    eh = EventHubs("Event Hubs")
    sa = StreamAnalytics("Stream Analytics")
    
    db = CosmosDb("Cosmos DB")
    storage = BlobStorage("Blob Storage")
    
    sources >> eh >> sa
    sa >> db
    sa >> storage`,
    category: "data-pipeline",
    complexity: "complex",
    tags: ["event-hubs", "stream-analytics", "cosmos", "blob", "streaming", "azure"],
    recommendedVariations: [
      "Add Data Lake for data lake storage",
      "Use Synapse Analytics for analytics",
      "Add Azure Monitor for monitoring"
    ]
  },
  {
    id: "azure-data-lake-analytics",
    title: "Data Lake Analytics",
    description: "Data sources → Data Lake → Synapse Analytics → Power BI",
    prompt: "Create a data lake architecture with data sources feeding Azure Data Lake, Synapse Analytics for processing, and visualization",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.analytics import SynapseAnalytics
from diagrams.azure.compute import VM
from diagrams.azure.storage import DataLake

with Diagram("Data Lake Analytics", show=False):
    with Cluster("Data Sources"):
        sources = [VM("app1"), VM("app2")]
    
    lake = DataLake("Data Lake")
    synapse = SynapseAnalytics("Synapse Analytics")
    
    sources >> lake >> synapse`,
    category: "analytics",
    complexity: "complex",
    tags: ["data-lake", "synapse", "analytics", "azure"],
    recommendedVariations: [
      "Add Stream Analytics for real-time",
      "Use Databricks for big data",
      "Add Cosmos DB for operational data"
    ]
  },
  {
    id: "azure-key-vault-security",
    title: "Key Vault Security",
    description: "App Service → Key Vault → SQL Database",
    prompt: "Create a secure application with App Service, Azure Key Vault for secrets management, and SQL Database",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import AppService
from diagrams.azure.database import SQLDatabases
from diagrams.azure.security import KeyVaults

with Diagram("Key Vault Security", show=False, direction="TB"):
    app = AppService("App Service")
    kv = KeyVaults("Key Vault")
    db = SQLDatabases("SQL Database")
    
    app >> kv >> db`,
    category: "security",
    complexity: "medium",
    tags: ["app-service", "key-vault", "sql", "security", "azure"],
    recommendedVariations: [
      "Add Azure Active Directory for auth",
      "Use Azure Firewall for network security",
      "Add Azure Monitor for monitoring"
    ]
  },
  {
    id: "azure-api-management",
    title: "API Management Gateway",
    description: "Azure CDN → API Management → Azure Functions → Cosmos DB",
    prompt: "Create an API architecture with Azure CDN, API Management gateway, Azure Functions, and Cosmos DB",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import Function
from diagrams.azure.database import CosmosDb
from diagrams.azure.integration import APIManagement
from diagrams.azure.network import CDN

with Diagram("API Management", show=False, direction="TB"):
    cdn = CDN("Azure CDN")
    apim = APIManagement("API Management")
    func = Function("Function")
    db = CosmosDb("Cosmos DB")
    
    cdn >> apim >> func >> db`,
    category: "api",
    complexity: "medium",
    tags: ["cdn", "api-management", "function", "cosmos", "api", "azure"],
    recommendedVariations: [
      "Add Key Vault for API keys",
      "Use Redis Cache for caching",
      "Add Application Gateway for load balancing"
    ]
  },
  {
    id: "azure-redis-cache",
    title: "Redis Cache Layer",
    description: "Application Gateway → App Service → Redis Cache → SQL Database",
    prompt: "Create a high-performance architecture with Application Gateway, App Service, Redis Cache, and SQL Database",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import AppService
from diagrams.azure.database import RedisCache, SQLDatabases
from diagrams.azure.network import ApplicationGateway

with Diagram("Redis Cache", show=False):
    gateway = ApplicationGateway("App Gateway")
    app = AppService("App Service")
    cache = RedisCache("Redis Cache")
    db = SQLDatabases("SQL Database")
    
    gateway >> app
    app >> cache
    app >> db`,
    category: "three-tier",
    complexity: "medium",
    tags: ["application-gateway", "app-service", "redis", "sql", "caching", "azure"],
    recommendedVariations: [
      "Add Azure CDN for edge caching",
      "Use Cosmos DB instead of SQL",
      "Add Azure Monitor for performance"
    ]
  },
  {
    id: "azure-virtual-network",
    title: "Virtual Network Architecture",
    description: "Virtual Network with subnets, VPN Gateway, and ExpressRoute",
    prompt: "Create a virtual network architecture with Virtual Network, VPN Gateway, ExpressRoute, and multiple VMs",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import VM
from diagrams.azure.network import Expressroute, VirtualNetwork, VpnGateway

with Diagram("Virtual Network", show=False):
    vnet = VirtualNetwork("VNet")
    vpn = VpnGateway("VPN Gateway")
    er = Expressroute("ExpressRoute")
    
    with Cluster("VNet"):
        vm1 = VM("VM 1")
        vm2 = VM("VM 2")
    
    vnet >> [vpn, er]
    vnet >> [vm1, vm2]`,
    category: "network",
    complexity: "medium",
    tags: ["virtual-network", "vpn-gateway", "expressroute", "vm", "network", "azure"],
    recommendedVariations: [
      "Add Application Gateway for load balancing",
      "Use Azure Firewall for security",
      "Add Azure Monitor for network monitoring"
    ]
  },
  {
    id: "azure-databricks-analytics",
    title: "Databricks Analytics",
    description: "Data Lake → Databricks → Synapse Analytics → Power BI",
    prompt: "Create an analytics pipeline with Azure Data Lake, Databricks for processing, Synapse Analytics, and visualization",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.analytics import Databricks, SynapseAnalytics
from diagrams.azure.storage import DataLake

with Diagram("Databricks Analytics", show=False, direction="TB"):
    lake = DataLake("Data Lake")
    databricks = Databricks("Databricks")
    synapse = SynapseAnalytics("Synapse Analytics")
    
    lake >> databricks >> synapse`,
    category: "analytics",
    complexity: "complex",
    tags: ["data-lake", "databricks", "synapse", "analytics", "azure"],
    recommendedVariations: [
      "Add Event Hubs for streaming data",
      "Use HDInsight for big data",
      "Add Cosmos DB for operational data"
    ]
  },
  {
    id: "azure-iot-hub",
    title: "IoT Hub Pipeline",
    description: "IoT Hub → Event Hubs → Stream Analytics → Cosmos DB and Blob Storage",
    prompt: "Create an IoT data pipeline with IoT Hub devices, Event Hubs, Stream Analytics processing, storing in Cosmos DB and Blob Storage",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.analytics import StreamAnalytics
from diagrams.azure.database import CosmosDb
from diagrams.azure.integration import EventHubs
from diagrams.azure.iot import IotHub
from diagrams.azure.storage import BlobStorage

with Diagram("IoT Pipeline", show=False):
    with Cluster("IoT Devices"):
        devices = [IotHub("device1"), IotHub("device2")]
    
    eh = EventHubs("Event Hubs")
    sa = StreamAnalytics("Stream Analytics")
    
    db = CosmosDb("Metadata")
    storage = BlobStorage("Data Storage")
    
    devices >> eh >> sa
    sa >> db
    sa >> storage`,
    category: "iot",
    complexity: "complex",
    tags: ["iot-hub", "event-hubs", "stream-analytics", "cosmos", "blob", "iot", "azure"],
    recommendedVariations: [
      "Add Logic Apps for workflows",
      "Use Time Series Insights for time-series",
      "Add Power BI for visualization"
    ]
  },
  {
    id: "azure-machine-learning",
    title: "Machine Learning Pipeline",
    description: "Blob Storage → Machine Learning → Azure Functions → Cosmos DB",
    prompt: "Create a machine learning pipeline with Blob Storage for data, Azure Machine Learning for training and inference, Azure Functions, and Cosmos DB",
    codeSnippet: `from diagrams import Diagram
from diagrams.azure.compute import Function
from diagrams.azure.database import CosmosDb
from diagrams.azure.ml import MachineLearning
from diagrams.azure.storage import BlobStorage

with Diagram("ML Pipeline", show=False, direction="TB"):
    data = BlobStorage("Training Data")
    ml = MachineLearning("Machine Learning")
    func = Function("API")
    db = CosmosDb("Results")
    
    data >> ml >> func >> db`,
    category: "ml",
    complexity: "complex",
    tags: ["blob", "machine-learning", "function", "cosmos", "ml", "azure"],
    recommendedVariations: [
      "Add API Management for ML API",
      "Use Cognitive Services for AI",
      "Add Azure Monitor for monitoring"
    ]
  },
  {
    id: "hybrid-cloud-azure",
    title: "Hybrid Cloud with Multi-OS",
    description: "On-premises datacenter with Windows and Linux VMs connecting to Azure Virtual Network via ExpressRoute",
    prompt: "Create a hybrid cloud architecture with on-premises datacenter containing Windows and Linux virtual machines connecting to Azure Virtual Network through ExpressRoute",
    codeSnippet: `from diagrams import Cluster, Diagram
from diagrams.azure.compute import VM
from diagrams.azure.network import Expressroute, VirtualNetwork
from diagrams.generic.os import Windows, LinuxGeneral
from diagrams.generic.place import Datacenter
from diagrams.generic.virtualization import Vmware
from diagrams.onprem.client import Users

with Diagram("Hybrid Cloud Architecture", show=False):
    users = Users("Users")
    
    with Cluster("On-Premises"):
        dc = Datacenter("Data Center")
        vmware = Vmware("VMware")
        with Cluster("Virtual Machines"):
            win_vm = Windows("Windows VM")
            linux_vm = LinuxGeneral("Linux VM")
    
    er = Expressroute("ExpressRoute")
    
    with Cluster("Azure"):
        vnet = VirtualNetwork("Virtual Network")
        azure_vm = VM("Azure VM")
    
    users >> dc
    dc >> vmware >> [win_vm, linux_vm]
    [win_vm, linux_vm] >> er >> vnet >> azure_vm`,
    category: "hybrid",
    complexity: "complex",
    tags: ["hybrid", "datacenter", "expressroute", "virtual-network", "windows", "linux", "vmware", "onprem", "azure"],
    recommendedVariations: [
      "Add VPN Gateway as backup connection",
      "Include multiple datacenters",
      "Use different virtualization platforms",
      "Add load balancer in Azure"
    ]
  }
]

