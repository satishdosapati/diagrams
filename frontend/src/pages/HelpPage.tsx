import { useState } from 'react'

interface Section {
  id: string
  title: string
  content: React.ReactNode
}

const sections: Section[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Welcome to Architecture Diagram Generator</h3>
        <p>Create beautiful cloud architecture diagrams from natural language descriptions.</p>
        
        <h4 className="text-lg font-semibold mt-6">Quick Start</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Select your cloud provider (AWS, Azure, or GCP)</li>
          <li>Describe your architecture in natural language</li>
          <li>Click "Generate Diagram"</li>
          <li>View and download your diagram</li>
          <li>Modify using the chat interface</li>
        </ol>

        <h4 className="text-lg font-semibold mt-6">Example</h4>
        <div className="bg-gray-100 p-4 rounded">
          <p className="font-mono text-sm">
            "Create a serverless API with API Gateway, Lambda functions, and DynamoDB"
          </p>
        </div>
      </div>
    )
  },
  {
    id: 'natural-language',
    title: 'Natural Language Mode',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">How It Works</h3>
        <p>Simply describe your architecture in plain English, and our AI will generate the diagram for you.</p>
        
        <h4 className="text-lg font-semibold mt-6">Best Practices</h4>
        <ul className="list-disc list-inside space-y-2">
          <li>Be specific: "Create a VPC with public and private subnets"</li>
          <li>Include connections: "API Gateway connects to Lambda, Lambda connects to DynamoDB"</li>
          <li>Mention provider: "AWS Lambda function" or "Azure Function"</li>
          <li>Use service names: "EC2", "S3", "Lambda"</li>
        </ul>

        <h4 className="text-lg font-semibold mt-6">Common Patterns</h4>
        <div className="space-y-3">
          <div className="border-l-4 border-blue-500 pl-4">
            <strong>Serverless:</strong> "Create a serverless API with API Gateway, Lambda, and DynamoDB"
          </div>
          <div className="border-l-4 border-green-500 pl-4">
            <strong>Three-Tier:</strong> "Design a three-tier web application with ALB, EC2 instances, and RDS"
          </div>
          <div className="border-l-4 border-purple-500 pl-4">
            <strong>Microservices:</strong> "Create microservices with ECS containers, API Gateway, and RDS"
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'advanced-code',
    title: 'Advanced Code Mode',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Direct Code Editing</h3>
        <p>For advanced users, edit Python code directly with auto-completion and live preview.</p>
        
        <h4 className="text-lg font-semibold mt-6">Features</h4>
        <ul className="list-disc list-inside space-y-2">
          <li>Syntax highlighting</li>
          <li>Auto-completion for imports and classes</li>
          <li>Real-time validation</li>
          <li>Code formatting</li>
          <li>Live preview</li>
        </ul>

        <h4 className="text-lg font-semibold mt-6">Code Structure</h4>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
{`from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB

with Diagram("My Architecture", show=False):
    alb = ALB("Load Balancer")
    ec2 = EC2("Web Server")
    rds = RDS("Database")
    alb >> ec2 >> rds`}
        </pre>
      </div>
    )
  },
  {
    id: 'examples',
    title: 'Examples & Templates',
    content: (
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Pre-built Examples</h3>
        <p>Browse examples for each cloud provider to get started quickly.</p>
        
        <h4 className="text-lg font-semibold mt-6">Available Examples</h4>
        <ul className="list-disc list-inside space-y-2">
          <li><strong>AWS:</strong> Grouped Workers, Clustered Web Services, Event Processing, Serverless API, VPC Network</li>
          <li><strong>Azure:</strong> Web Application, Container Services</li>
          <li><strong>GCP:</strong> Message Collecting System, Serverless Architecture</li>
        </ul>

        <h4 className="text-lg font-semibold mt-6">Using Examples</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Click "Show Examples" button</li>
          <li>Browse examples by category</li>
          <li>Click "Use This Example" to auto-fill</li>
          <li>Modify as needed</li>
          <li>Generate your diagram</li>
        </ol>
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
          <h4 className="font-semibold text-lg">What cloud providers are supported?</h4>
          <p className="mt-2">AWS, Azure, and GCP are currently supported.</p>
        </div>

        <div>
          <h4 className="font-semibold text-lg">Do I need to know Python?</h4>
          <p className="mt-2">No, Natural Language Mode requires no coding. Advanced Code Mode is optional for advanced users.</p>
        </div>

        <div>
          <h4 className="font-semibold text-lg">Can I save my diagrams?</h4>
          <p className="mt-2">Yes, download diagrams as PNG, SVG, or PDF formats.</p>
        </div>

        <div>
          <h4 className="font-semibold text-lg">Can I customize diagram colors?</h4>
          <p className="mt-2">Yes, in Advanced Code Mode using Graphviz attributes.</p>
        </div>

        <div>
          <h4 className="font-semibold text-lg">How do I add labels to connections?</h4>
          <p className="mt-2">Use Edge with label parameter in Advanced Code Mode.</p>
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

