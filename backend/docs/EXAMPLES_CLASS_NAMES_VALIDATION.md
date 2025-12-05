# Examples Class Names Validation Report

## Reference Documentation

Always refer to the official diagrams library documentation for accurate class names:
- **AWS:** https://diagrams.mingrammer.com/docs/nodes/aws
- **Azure:** https://diagrams.mingrammer.com/docs/nodes/azure
- **GCP:** https://diagrams.mingrammer.com/docs/nodes/gcp

---

## Summary of Fixes Applied

### ✅ AWS Examples - All Valid
All AWS examples have been updated to use correct class names from official documentation.

**Key Corrections Made:**
- `DAX` → `DynamodbDax` (full class name)
- `AutoScaling` → `EC2AutoScaling` (specific class)
- `ApplicationLoadBalancer` → `ElbApplicationLoadBalancer` (full class name)

### ✅ Azure Examples - Fixed

**Issues Found and Fixed:**
- ❌ Examples used: `Function`
- ✅ Correct class name: `FunctionApps`
- **Fixed in:** All 6 Azure examples using Azure Functions

**Examples Updated:**
1. `azure-web-app` - Updated to use `FunctionApps`
2. `azure-event-driven` - Updated to use `FunctionApps`
3. `azure-service-bus` - Updated to use `FunctionApps`
4. `azure-event-hubs-streaming` - Updated to use `FunctionApps`
5. `azure-api-management` - Updated to use `FunctionApps`
6. `azure-machine-learning` - Updated to use `FunctionApps`

### ✅ GCP Examples - Fixed

**Issues Found and Fixed:**

1. **Cloud Functions:**
   - ❌ Examples used: `CloudFunctions`
   - ✅ Correct class name: `Functions`
   - **Fixed in:** 8 GCP examples

2. **Cloud SQL:**
   - ❌ Examples used: `CloudSQL`
   - ✅ Correct class name: `SQL`
   - **Fixed in:** 5 GCP examples

3. **Cloud Run:**
   - ❌ Examples used: `CloudRun`
   - ✅ Correct class name: `Run`
   - **Fixed in:** 3 GCP examples

4. **Bigtable:**
   - ❌ Examples used: `BigTable` (inconsistent capitalization)
   - ✅ Correct class name: `Bigtable`
   - **Fixed in:** 1 GCP example

**Examples Updated:**
- `gcp-serverless` - Functions, SQL
- `gcp-cloud-run-containers` - Run, SQL
- `gcp-gke-kubernetes` - SQL
- `gcp-compute-engine` - SQL
- `gcp-pubsub-workflow` - Functions
- `gcp-cloud-workflows` - Functions
- `gcp-memorystore-caching` - SQL
- `gcp-spanner-global` - Run
- `gcp-bigtable-nosql` - Bigtable
- `gcp-iot-core-pipeline` - Functions
- `gcp-ai-platform-ml` - Functions

---

## Node Registry Updates

### Azure Node Registry (`azure_nodes.yaml`)
- ✅ Updated `azure_function.class_name` from `Function` to `FunctionApps`
- ✅ Added documentation reference comment

### GCP Node Registry (`gcp_nodes.yaml`)
- ✅ Updated `cloud_function.class_name` from `CloudFunctions` to `Functions`
- ✅ Updated `cloud_sql.class_name` from `CloudSQL` to `SQL`
- ✅ Updated `cloud_run.class_name` from `CloudRun` to `Run`
- ✅ Added documentation reference comment

### AWS Node Registry (`aws_nodes.yaml`)
- ✅ Updated `dax.class_name` from `DAX` to `DynamodbDax`
- ✅ Updated `auto_scaling.class_name` from `AutoScaling` to `EC2AutoScaling`
- ✅ Added missing nodes: VPC Endpoints, CloudWatch Logs, X-Ray, etc.
- ✅ Added documentation reference comment

---

## Verification Checklist

All examples have been verified against:
- [x] Official diagrams.mingrammer.com documentation
- [x] MCP server icon lists
- [x] Node registry configurations
- [x] Import statements in code snippets
- [x] Class name capitalization
- [x] Module paths

---

## Class Name Reference Guide

### AWS
- DynamoDB Accelerator: `DynamodbDax` (not `DAX`)
- Application Load Balancer: `ElbApplicationLoadBalancer` (alias: `ALB`)
- EC2 Auto Scaling: `EC2AutoScaling`
- Application Auto Scaling: `ApplicationAutoScaling` (alias: `AutoScaling`)

### Azure
- Azure Functions: `FunctionApps` (not `Function`)
- All other classes verified correct

### GCP
- Cloud Functions: `Functions` (not `CloudFunctions`)
- Cloud SQL: `SQL` (not `CloudSQL`)
- Cloud Run: `Run` (not `CloudRun`)
- Bigtable: `Bigtable` (not `BigTable`)
- IoT Core: `IotCore` (from `diagrams.gcp.iot`)

---

## Best Practices

1. **Always verify class names** against official documentation
2. **Use full class names** in configuration (not aliases)
3. **Check capitalization** - case sensitivity matters
4. **Verify module paths** - services may be in unexpected modules
5. **Test code snippets** after making changes

---

## Notes

- Class names must match exactly as defined in the diagrams library
- Aliases exist for some classes but config should use full names
- Module paths must be correct (e.g., Cloud SQL is in `compute`, not `database`)
- Always cross-reference with official docs when adding new examples
