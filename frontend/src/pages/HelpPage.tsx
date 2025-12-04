import React, { useState } from 'react'

interface Section {
  id: string
  title: string
  content: React.ReactNode
}

const CodeBlock = ({ code, language = 'python' }: { code: string; language?: string }) => (
  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
    <code>{code}</code>
  </pre>
)

const sections: Section[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Welcome to Architecture Diagram Generator</h3>
        <p className="text-gray-700">
          Create beautiful cloud architecture diagrams from natural language descriptions or direct Python code. 
          This tool uses the <a href="https://diagrams.mingrammer.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Diagrams library</a> to generate professional diagrams.
        </p>
        
        <h4 className="text-lg font-semibold mt-6">Quick Start</h4>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li>Select your cloud provider (AWS, Azure, or GCP)</li>
          <li>Choose between <strong>Natural Language Mode</strong> or <strong>Advanced Code Mode</strong></li>
          <li>Describe your architecture or write Python code</li>
          <li>Click "Generate Diagram" or "Execute Code"</li>
          <li>View, download, and modify your diagram</li>
        </ol>

        <h4 className="text-lg font-semibold mt-6">Example - Natural Language</h4>
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <p className="font-mono text-sm text-gray-800">
            "Create a serverless API with API Gateway, Lambda functions, and DynamoDB"
          </p>
        </div>

        <h4 className="text-lg font-semibold mt-6">Example - Code Mode</h4>
        <CodeBlock code={`from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamoDB
from diagrams.aws.network import APIGateway

with Diagram("Serverless API", show=False):
    api = APIGateway("API")
    func = Lambda("Function")
    db = DynamoDB("Database")
    api >> func >> db`} />
      </div>
    )
  },
  {
    id: 'natural-language',
    title: 'Natural Language Mode',
    content: (
      <div className="space-y-6">
        <div>
          <h3 className="text-xl font-semibold">How It Works</h3>
          <p className="text-gray-700">
            Simply describe your architecture in plain English, and our AI will interpret your request and generate 
            the diagram code automatically. No coding knowledge required!
          </p>
        </div>
        
        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Best Practices</h4>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li><strong>Be specific:</strong> "Create a VPC with public and private subnets"</li>
            <li><strong>Include connections:</strong> "API Gateway connects to Lambda, Lambda connects to DynamoDB"</li>
            <li><strong>Mention provider:</strong> "AWS Lambda function" or "Azure Function App"</li>
            <li><strong>Use service names:</strong> "EC2", "S3", "Lambda", "RDS"</li>
            <li><strong>Specify quantities:</strong> "3 EC2 instances" or "multiple Lambda functions"</li>
            <li><strong>Describe relationships:</strong> "Load balancer distributes traffic to workers"</li>
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Common Architecture Patterns</h4>
          <div className="space-y-4">
            <div className="border-l-4 border-blue-500 pl-4 bg-blue-50 py-2 rounded-r">
              <strong className="text-blue-900">Serverless Architecture</strong>
              <p className="text-sm text-gray-700 mt-1">
                "Create a serverless API with API Gateway, Lambda functions, and DynamoDB"
              </p>
              <p className="text-sm text-gray-600 mt-1 italic">
                Generates: API Gateway → Lambda → DynamoDB
              </p>
            </div>
            
            <div className="border-l-4 border-green-500 pl-4 bg-green-50 py-2 rounded-r">
              <strong className="text-green-900">Three-Tier Architecture</strong>
              <p className="text-sm text-gray-700 mt-1">
                "Design a three-tier web application with ALB, EC2 instances, and RDS database"
              </p>
              <p className="text-sm text-gray-600 mt-1 italic">
                Generates: ALB → EC2 instances → RDS
              </p>
            </div>
            
            <div className="border-l-4 border-purple-500 pl-4 bg-purple-50 py-2 rounded-r">
              <strong className="text-purple-900">Microservices Architecture</strong>
              <p className="text-sm text-gray-700 mt-1">
                "Create microservices with ECS containers, API Gateway, and RDS database"
              </p>
              <p className="text-sm text-gray-600 mt-1 italic">
                Generates: API Gateway → ECS services → RDS
              </p>
            </div>

            <div className="border-l-4 border-orange-500 pl-4 bg-orange-50 py-2 rounded-r">
              <strong className="text-orange-900">Event-Driven Architecture</strong>
              <p className="text-sm text-gray-700 mt-1">
                "Create an event processing system with S3, SQS queue, Lambda functions, and DynamoDB"
              </p>
              <p className="text-sm text-gray-600 mt-1 italic">
                Generates: S3 → SQS → Lambda → DynamoDB
              </p>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Example Descriptions</h4>
          <div className="space-y-3">
            <div className="bg-gray-50 p-4 rounded border">
              <p className="text-sm font-semibold mb-2">Simple:</p>
              <p className="text-sm text-gray-700 font-mono">
                "Create a load balancer with 3 EC2 instances connected to an RDS database"
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded border">
              <p className="text-sm font-semibold mb-2">With Clusters:</p>
              <p className="text-sm text-gray-700 font-mono">
                "Create a web service with Route53 DNS, load balancer, ECS containers in a services cluster, and RDS database with read replicas"
              </p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h4 className="font-semibold mb-2">Tips for Better Results</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
            <li>Start with simple descriptions and add complexity gradually</li>
            <li>Use standard cloud service names (EC2, S3, Lambda, etc.)</li>
            <li>Explicitly state connections between components</li>
            <li>Mention quantities when you need multiple instances</li>
            <li>Use the examples panel for inspiration</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    id: 'advanced-code',
    title: 'Advanced Code Mode',
    content: (
      <div className="space-y-6">
        <div>
          <h3 className="text-xl font-semibold">Direct Code Editing</h3>
          <p className="text-gray-700">
            For advanced users, edit Python code directly with auto-completion, syntax highlighting, and real-time validation. 
            Full control over diagram structure, styling, and layout.
          </p>
        </div>
        
        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Features</h4>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li><strong>Monaco Editor:</strong> VS Code-like editing experience</li>
            <li><strong>Auto-completion:</strong> Smart suggestions for imports, classes, and operators</li>
            <li><strong>Syntax Highlighting:</strong> Python syntax coloring</li>
            <li><strong>Real-time Validation:</strong> Instant feedback on errors</li>
            <li><strong>Code Formatting:</strong> Auto-format with one click</li>
            <li><strong>Live Execution:</strong> Generate diagrams directly from code</li>
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Basic Code Structure</h4>
          <CodeBlock code={`from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB

with Diagram("My Architecture", show=False):
    alb = ALB("Load Balancer")
    ec2 = EC2("Web Server")
    rds = RDS("Database")
    alb >> ec2 >> rds`} />
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Connection Operators</h4>
          <p className="text-gray-700 mb-3">Use operators to connect components:</p>
          <div className="space-y-2 text-sm">
            <div className="flex items-start gap-3">
              <code className="bg-gray-200 px-2 py-1 rounded font-mono">>></code>
              <span className="text-gray-700">Right arrow: Forward connection (A → B)</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-gray-200 px-2 py-1 rounded font-mono"><<</code>
              <span className="text-gray-700">Left arrow: Reverse connection (A ← B)</span>
            </div>
            <div className="flex items-start gap-3">
              <code className="bg-gray-200 px-2 py-1 rounded font-mono">-</code>
              <span className="text-gray-700">Dash: Bidirectional connection (A ↔ B)</span>
            </div>
          </div>
          <CodeBlock code={`from diagrams import Diagram
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS

with Diagram("Connections", show=False):
    a = EC2("A")
    b = EC2("B")
    c = EC2("C")
    
    a >> b  # Forward connection
    b << c  # Reverse connection
    a - c   # Bidirectional`} />
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Using Clusters</h4>
          <p className="text-gray-700 mb-3">
            Group related components together for better organization:
          </p>
          <CodeBlock code={`from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Clustered Architecture", show=False):
    lb = ELB("Load Balancer")
    
    with Cluster("Web Services"):
        web1 = ECS("web1")
        web2 = ECS("web2")
        web3 = ECS("web3")
    
    with Cluster("Database Cluster"):
        primary = RDS("primary")
        replica = RDS("replica")
        primary - replica
    
    lb >> [web1, web2, web3] >> primary`} />
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Custom Edges with Labels and Colors</h4>
          <CodeBlock code={`from diagrams import Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamoDB

with Diagram("Custom Edges", show=False):
    func = Lambda("Function")
    db = DynamoDB("Database")
    
    # Colored edge with label
    func >> Edge(color="blue", label="API calls") >> db
    
    # Dashed edge
    func - Edge(style="dashed") - db
    
    # Bold colored edge
    func >> Edge(color="red", style="bold") >> db`} />
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-3">Multiple Connections</h4>
          <CodeBlock code={`from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Multiple Connections", show=False):
    lb = EC2("Load Balancer")
    
    # Connect to multiple targets
    workers = [EC2("worker1"),
               EC2("worker2"),
               EC2("worker3")]
    
    db = RDS("Database")
    
    lb >> workers >> db`} />
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
          <h4 className="font-semibold mb-2">Auto-completion Tips</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
            <li>Type <code className="bg-gray-200 px-1 rounded">from diagrams.aws.compute import </code> to see all compute classes</li>
            <li>Type <code className="bg-gray-200 px-1 rounded">from diagrams.aws.database import </code> for database classes</li>
            <li>Type <code className="bg-gray-200 px-1 rounded">from diagrams.aws.network import </code> for network classes</li>
            <li>Use <code className="bg-gray-200 px-1 rounded">Ctrl+Space</code> (or <code className="bg-gray-200 px-1 rounded">Cmd+Space</code> on Mac) to trigger suggestions</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    id: 'examples',
    title: 'Examples & Templates',
    content: (
      <div className="space-y-6">
        <div>
          <h3 className="text-xl font-semibold">Pre-built Examples</h3>
          <p className="text-gray-700">
            Browse examples for each cloud provider to get started quickly. These examples are based on the 
            <a href="https://diagrams.mingrammer.com/docs/getting-started/examples" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline"> official Diagrams library examples</a>.
          </p>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-4">AWS Examples</h4>
          
          <div className="space-y-6">
            <div className="border rounded-lg p-4 bg-gray-50">
              <h5 className="font-semibold text-md mb-2">1. Grouped Workers</h5>
              <p className="text-sm text-gray-600 mb-3">
                Load balancer distributing traffic to multiple EC2 workers connected to RDS database.
              </p>
              <CodeBlock code={`from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("Grouped Workers", show=False, direction="TB"):
    ELB("lb") >> [EC2("worker1"),
                  EC2("worker2"),
                  EC2("worker3"),
                  EC2("worker4"),
                  EC2("worker5")] >> RDS("events")`} />
            </div>

            <div className="border rounded-lg p-4 bg-gray-50">
              <h5 className="font-semibold text-md mb-2">2. Clustered Web Services</h5>
              <p className="text-sm text-gray-600 mb-3">
                Route53 DNS → Load balancer → ECS services → RDS with ElastiCache for caching.
              </p>
              <CodeBlock code={`from diagrams import Cluster, Diagram
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
    svc_group >> memcached`} />
            </div>

            <div className="border rounded-lg p-4 bg-gray-50">
              <h5 className="font-semibold text-md mb-2">3. Event Processing</h5>
              <p className="text-sm text-gray-600 mb-3">
                Kubernetes source → ECS workers → SQS queue → Lambda processors → S3 storage and Redshift analytics.
              </p>
              <CodeBlock code={`from diagrams import Cluster, Diagram
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
    handlers >> dw`} />
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-4">GCP Examples</h4>
          
          <div className="border rounded-lg p-4 bg-gray-50">
            <h5 className="font-semibold text-md mb-2">Message Collecting System</h5>
            <p className="text-sm text-gray-600 mb-3">
              IoT Core devices → Pub/Sub → Dataflow → BigQuery/GCS storage and serverless processing.
            </p>
            <CodeBlock code={`from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import AppEngine, Functions
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
                flow >> AppEngine("engine") >> BigTable("bigtable")

            with Cluster("Serverless"):
                flow >> Functions("func") >> AppEngine("appengine")

    pubsub >> flow`} />
          </div>
        </div>

        <div>
          <h4 className="text-lg font-semibold mt-6 mb-4">Advanced Features</h4>
          
          <div className="border rounded-lg p-4 bg-gray-50">
            <h5 className="font-semibold text-md mb-2">Custom Colors and Labels</h5>
            <p className="text-sm text-gray-600 mb-3">
              Use Edge objects to customize connection colors, styles, and labels.
            </p>
            <CodeBlock code={`from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Custom Styled", show=False):
    web = EC2("Web Server")
    db = RDS("Database")
    
    # Colored edge with label
    web >> Edge(color="blue", label="API calls") >> db
    
    # Dashed edge
    web - Edge(style="dashed") - db
    
    # Bold edge
    web >> Edge(style="bold") >> db`} />
          </div>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h4 className="font-semibold mb-2">Using Examples in the UI</h4>
          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
            <li>Select your cloud provider</li>
            <li>Browse examples in the "Quick Start Examples" panel</li>
            <li>Click "Use This Example" to auto-fill the description</li>
            <li>Or switch to "Advanced Code Mode" and copy the code snippet</li>
            <li>Modify as needed and generate your diagram</li>
          </ol>
        </div>
      </div>
    )
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Common Issues</h3>
        
        <h4 className="text-lg font-semibold mt-6">Class Not Found Error</h4>
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <p><strong>Problem:</strong> Component type doesn't exist in library</p>
          <p className="mt-2"><strong>Solution:</strong></p>
          <ul className="list-disc list-inside mt-1">
            <li>Check component name spelling</li>
            <li>Verify provider is correct</li>
            <li>Use suggestions provided</li>
            <li>Try alternative component names</li>
          </ul>
        </div>

        <h4 className="text-lg font-semibold mt-6">Out of Context Input</h4>
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <p><strong>Problem:</strong> Input not related to cloud architecture</p>
          <p className="mt-2"><strong>Solution:</strong></p>
          <ul className="list-disc list-inside mt-1">
            <li>Focus on cloud services</li>
            <li>Use architecture terminology</li>
            <li>Check examples for guidance</li>
          </ul>
        </div>

        <h4 className="text-lg font-semibold mt-6">Diagram Not Generating</h4>
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <ul className="list-disc list-inside">
            <li>Check description clarity</li>
            <li>Verify provider selection</li>
            <li>Review error messages</li>
            <li>Try simpler description</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    id: 'faq',
    title: 'FAQ',
    content: (
      <div className="space-y-6">
        <div>
          <h4 className="font-semibold text-lg text-gray-900">What cloud providers are supported?</h4>
          <p className="mt-2 text-gray-700">
            AWS (Amazon Web Services), Azure (Microsoft Azure), and GCP (Google Cloud Platform) are currently supported. 
            Each provider has hundreds of available components.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">Do I need to know Python?</h4>
          <p className="mt-2 text-gray-700">
            No! <strong>Natural Language Mode</strong> requires no coding knowledge. Simply describe your architecture in plain English. 
            <strong>Advanced Code Mode</strong> is optional for users who want full control over the generated code.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">Can I save my diagrams?</h4>
          <p className="mt-2 text-gray-700">
            Yes! Diagrams can be downloaded in PNG, SVG, or PDF formats. Use the download button after generating your diagram.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">Can I customize diagram colors and styles?</h4>
          <p className="mt-2 text-gray-700">
            Yes! In <strong>Advanced Code Mode</strong>, you can use Edge objects with color and style parameters. 
            See the "Advanced Code Mode" section for examples.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">How do I add labels to connections?</h4>
          <p className="mt-2 text-gray-700">
            Use Edge objects with the label parameter in Advanced Code Mode:
            <CodeBlock code={`from diagrams import Edge
component1 >> Edge(label="API calls") >> component2`} />
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">What is the Diagrams library?</h4>
          <p className="mt-2 text-gray-700">
            This tool uses the <a href="https://diagrams.mingrammer.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Diagrams library</a>, 
            an open-source Python library for creating cloud architecture diagrams. It provides icons and components for 
            major cloud providers and generates diagrams using Graphviz.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">Can I modify diagrams after generation?</h4>
          <p className="mt-2 text-gray-700">
            Yes! Use the chat interface to modify your diagram iteratively. You can add components, remove them, 
            change connections, or switch to Advanced Code Mode for direct code editing.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">What if a component I need isn't available?</h4>
          <p className="mt-2 text-gray-700">
            The system uses library-first discovery, meaning it checks what's actually available in the installed Diagrams library. 
            If a component isn't found, you'll get helpful alternatives. Check the 
            <a href="https://diagrams.mingrammer.com/docs/nodes/aws" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline"> official documentation</a> for available components.
          </p>
        </div>

        <div>
          <h4 className="font-semibold text-lg text-gray-900">How accurate are the generated diagrams?</h4>
          <p className="mt-2 text-gray-700">
            Diagrams are generated based on your description and the available components in the Diagrams library. 
            The AI interprets your request and creates appropriate connections. You can always refine using the chat interface 
            or switch to Advanced Code Mode for precise control.
          </p>
        </div>
      </div>
    )
  },
  {
    id: 'resources',
    title: 'Resources & Links',
    content: (
      <div className="space-y-6">
        <div>
          <h3 className="text-xl font-semibold">Official Documentation</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 mt-4">
            <li>
              <a href="https://diagrams.mingrammer.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Diagrams Library Homepage
              </a>
            </li>
            <li>
              <a href="https://diagrams.mingrammer.com/docs/getting-started/examples" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Official Examples
              </a>
            </li>
            <li>
              <a href="https://diagrams.mingrammer.com/docs/nodes/aws" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                AWS Components Reference
              </a>
            </li>
            <li>
              <a href="https://diagrams.mingrammer.com/docs/nodes/azure" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Azure Components Reference
              </a>
            </li>
            <li>
              <a href="https://diagrams.mingrammer.com/docs/nodes/gcp" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                GCP Components Reference
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="text-xl font-semibold">Cloud Architecture Resources</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700 mt-4">
            <li>
              <a href="https://aws.amazon.com/architecture/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                AWS Architecture Center
              </a>
            </li>
            <li>
              <a href="https://docs.microsoft.com/en-us/azure/architecture/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Azure Architecture Center
              </a>
            </li>
            <li>
              <a href="https://cloud.google.com/architecture" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Google Cloud Architecture Center
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="text-xl font-semibold">GitHub Repository</h3>
          <p className="text-gray-700 mt-2">
            The Diagrams library is open source. Check out the repository for issues, feature requests, and contributions:
          </p>
          <a href="https://github.com/mingrammer/diagrams" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
            https://github.com/mingrammer/diagrams
          </a>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h4 className="font-semibold mb-2">Need Help?</h4>
          <p className="text-sm text-gray-700">
            If you encounter issues or have questions, check the Troubleshooting section or refer to the official Diagrams library documentation. 
            The library is actively maintained and has a helpful community.
          </p>
        </div>
      </div>
    )
  }
]

function HelpPage() {
  const [selectedSection, setSelectedSection] = useState(sections[0].id)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredSections = searchQuery
    ? sections.filter(section => 
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : sections

  const currentSection = sections.find(s => s.id === selectedSection) || sections[0]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Help & Documentation</h1>
          <p className="mt-1 text-sm text-gray-500">Learn how to use Architecture Diagram Generator</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <aside className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow p-4 sticky top-4">
              {/* Search */}
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="Search help..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>

              {/* Navigation */}
              <nav className="space-y-1">
                {filteredSections.map(section => (
                  <button
                    key={section.id}
                    onClick={() => setSelectedSection(section.id)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                      selectedSection === section.id
                        ? 'bg-blue-50 text-blue-600 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {section.title}
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold mb-6">{currentSection.title}</h2>
              <div className="prose max-w-none">
                {currentSection.content}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default HelpPage

