# Example Updates - Generic and OnPrem Nodes

This document outlines suggested changes to examples to showcase the new generic and onprem nodes.

## Updated Examples

### 1. AWS Examples

#### Updated: Serverless API (Add Users)
**Current:** "Create a serverless API with API Gateway, Lambda functions, and DynamoDB"
**Updated:** "Users accessing serverless API through API Gateway with Lambda functions and DynamoDB database"

**Changes:**
- Add user/client nodes to show who is accessing the API
- More realistic user-centric architecture

#### New: Hybrid Cloud with On-Premises Datacenter
**New Example:** "On-premises datacenter connecting to AWS VPC via Direct Connect, with Windows and Linux servers"

**Shows:**
- Generic place (datacenter)
- Generic OS (Windows, Linux)
- Hybrid cloud connectivity

#### Updated: VPC Network (Add Users)
**Current:** Basic VPC with subnets
**Updated:** "Users accessing web application through VPC with public and private subnets"

**Changes:**
- Add user nodes accessing the architecture
- More complete user-to-infrastructure flow

### 2. Azure Examples

#### Updated: Azure Web Application (Add Users)
**Current:** "Azure Functions → Blob Storage → Cosmos DB"
**Updated:** "Users accessing Azure web application with Functions, Blob Storage, and Cosmos DB"

#### New: Multi-OS Virtual Machines
**New Example:** "Azure Virtual Network with Windows and Linux VMs, connecting to on-premises datacenter"

**Shows:**
- Generic OS nodes (Windows, Linux)
- Generic place (datacenter)
- Hybrid architecture

### 3. GCP Examples

#### Updated: Message Collecting System (Add Users)
**Current:** IoT Core → PubSub → Dataflow
**Updated:** "Mobile users and IoT devices sending messages through PubSub to Dataflow pipeline"

**Changes:**
- Add client/user nodes
- Show both mobile users and IoT devices

#### New: Hybrid Cloud Architecture
**New Example:** "On-premises datacenter with VMware virtualization connecting to GCP VPC via Cloud Interconnect"

**Shows:**
- Generic virtualization (VMware)
- Generic place (datacenter)
- Hybrid connectivity

## Code Snippet Updates

All updated examples include imports for:
- `diagrams.onprem.client` - User, Users, Client
- `diagrams.generic.os` - Windows, Linux, Android, etc.
- `diagrams.generic.place` - Datacenter
- `diagrams.generic.virtualization` - VMware, VirtualBox, QEMU, XEN

## Natural Language Prompt Updates

Updated prompts to naturally include:
- "Users accessing..."
- "On-premises datacenter..."
- "Windows/Linux servers..."
- "Mobile clients..."
- "Hybrid cloud..."

These prompts will trigger the system to include the new generic/onprem nodes.
