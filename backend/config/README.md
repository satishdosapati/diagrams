# Node Registry Configuration

This directory contains the node registry configuration files that define all supported cloud provider nodes for diagram generation.

## Configuration Files

The registry is split into separate files per cloud provider for better organization:

- **`aws_nodes.yaml`** - AWS node definitions
- **`azure_nodes.yaml`** - Azure node definitions  
- **`gcp_nodes.yaml`** - GCP node definitions

### File Structure

Each provider has its own configuration file:
- **`aws_nodes.yaml`** - AWS provider nodes
- **`azure_nodes.yaml`** - Azure provider nodes
- **`gcp_nodes.yaml`** - GCP provider nodes

All three files are required for the system to function properly.

### Structure

Each provider file follows this structure:

**`aws_nodes.yaml`** (and similar for azure/gcp):
```yaml
# Provider module mappings
modules:
  compute: diagrams.aws.compute
  storage: diagrams.aws.storage
  database: diagrams.aws.database
  # ... more categories

# Node mappings: node_id -> (category, class_name)
nodes:
  ec2:
    category: compute
    class_name: EC2
    description: "EC2 Instance"
  lambda:
    category: compute
    class_name: Lambda
    description: "AWS Lambda Function"
  # ... more nodes
```

### Adding New Nodes

To add a new node:

1. **Open the appropriate provider file** (`aws_nodes.yaml`, `azure_nodes.yaml`, or `gcp_nodes.yaml`)
2. **Add the node entry** under `nodes`:
   ```yaml
   node_id:
     category: <category_name>
     class_name: <DiagramsLibraryClassName>
     description: "Human-readable description"
   ```

3. **Ensure the category exists** in the `modules` section
4. **Verify the class name** matches the actual Diagrams library class

### Example: Adding AWS EKS

Edit `aws_nodes.yaml`:
```yaml
nodes:
  eks:
    category: compute
    class_name: ElasticKubernetesService
    description: "Elastic Kubernetes Service"
```

### Node ID Rules

- Use lowercase with underscores (e.g., `api_gateway`, `cloud_function`)
- Must match the Diagrams library class name pattern
- Can be the same across providers (e.g., `vpc` for AWS and GCP)
- The resolver uses provider context to distinguish them

### Categories

Common categories per provider:
- `compute` - Compute services (EC2, Lambda, Functions, etc.)
- `storage` - Storage services (S3, Blob Storage, Cloud Storage, etc.)
- `database` - Database services (RDS, Cosmos DB, Firestore, etc.)
- `network` - Networking services (VPC, Load Balancers, DNS, etc.)
- `integration` - Integration services (SQS, Event Grid, Pub/Sub, etc.)
- `analytics` - Analytics services (Kinesis, Data Factory, BigQuery, etc.)
- `security` - Security services (IAM, Key Vault, KMS, etc.)
- `management` - Management services (CloudWatch, Monitor, etc.)
- `iot` - IoT services
- `ml` - Machine Learning services

### Validation

The registry is validated on startup:
- All required fields present (`category`, `class_name`)
- Categories exist in `modules`
- YAML syntax is valid
- Provider structure is correct

### Usage in Code

The registry is automatically loaded and used by:
- `ComponentResolver` - Resolves node types to Diagrams classes
- `DiagramAgent` - Generates prompts with available nodes
- `NodeType` enum - Provides type-safe node identifiers

### Benefits

1. **Single Source of Truth** - All nodes defined in one place
2. **Easy Updates** - Add nodes without code changes
3. **Version Control** - Track node additions in git
4. **Documentation** - Config serves as documentation
5. **Type Safety** - Enum values validated against registry

### Benefits of Separate Files

1. **Better Organization** - Each provider in its own file
2. **Easier Maintenance** - Edit provider-specific nodes without touching others
3. **Reduced Conflicts** - Less chance of merge conflicts in git
4. **Clearer Structure** - Easier to understand and navigate
5. **Selective Loading** - Can load only needed providers if desired

### Troubleshooting

**Error: "Config directory not found"**
- Ensure `backend/config/` directory exists
- Check file permissions

**Error: "No config files found"**
- Ensure all three provider files exist: `aws_nodes.yaml`, `azure_nodes.yaml`, `gcp_nodes.yaml`
- Check that files are in the `backend/config/` directory

**Error: "Node type 'xyz' not supported"**
- Check if node_id exists in the provider's config file
- Verify spelling matches registry exactly
- Check provider is correct (aws/azure/gcp)
- Ensure the provider file was loaded successfully

**Error: "Failed to import module.class_name"**
- Verify `class_name` matches Diagrams library class
- Check `category` module path is correct
- Ensure Diagrams library version supports the class

**Error: "Provider file X missing 'modules' key"**
- Ensure provider file has both `modules` and `nodes` sections
- Check YAML syntax is correct

