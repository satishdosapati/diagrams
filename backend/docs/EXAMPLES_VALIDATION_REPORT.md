# Examples Validation Report - All Cloud Providers

## Reference Documentation

Always refer to the official diagrams library documentation:
- **AWS:** https://diagrams.mingrammer.com/docs/nodes/aws
- **Azure:** https://diagrams.mingrammer.com/docs/nodes/azure  
- **GCP:** https://diagrams.mingrammer.com/docs/nodes/gcp

## Validation Methodology

1. Cross-referenced all example code snippets with official diagrams documentation
2. Verified class names match exactly as defined in the library
3. Checked against available icons from MCP server
4. Identified and fixed class name mismatches

---

## AWS Examples - Status: ✅ Most Valid (Already Updated)

### Verified Correct Class Names:
- ✅ `EC2` - diagrams.aws.compute.EC2
- ✅ `Lambda` - diagrams.aws.compute.Lambda
- ✅ `ElasticKubernetesService` (EKS) - diagrams.aws.compute.ElasticKubernetesService
- ✅ `Dynamodb` - diagrams.aws.database.Dynamodb
- ✅ `RDS` - diagrams.aws.database.RDS
- ✅ `ElbApplicationLoadBalancer` (ALB) - diagrams.aws.network.ElbApplicationLoadBalancer
- ✅ `CloudFront` - diagrams.aws.network.CloudFront
- ✅ `APIGateway` - diagrams.aws.network.APIGateway

### Recently Fixed:
- ✅ `DynamodbDax` (was `DAX` - now uses full class name)
- ✅ `EC2AutoScaling` (was `AutoScaling` - now uses specific class)
- ✅ `ElbApplicationLoadBalancer` (was `ApplicationLoadBalancer`)

---

## Azure Examples - Issues Found

### ❌ Class Name Mismatches:

1. **Azure Functions:**
   - ❌ Examples use: `Function`
   - ✅ Should be: `FunctionApps`
   - Module: `diagrams.azure.compute`
   - Found in: Multiple examples

2. **Azure Container Instances:**
   - ✅ Examples use: `ContainerInstances`
   - Status: Correct

3. **Azure Kubernetes Services:**
   - ✅ Examples use: `KubernetesServices`
   - Status: Correct

4. **Azure SQL Database:**
   - ✅ Examples use: `SQLDatabases`
   - Status: Correct

5. **Azure Event Hubs:**
   - ✅ Examples use: `EventHubs`
   - Status: Correct (from integration module)

6. **Azure Analytics Classes:**
   - ✅ `StreamAnalytics` - Correct
   - ✅ `SynapseAnalytics` - Correct
   - ✅ `Databricks` - Correct

### Action Required:
- Update all Azure examples using `Function` to use `FunctionApps`

---

## GCP Examples - Issues Found

### ❌ Class Name Mismatches:

1. **Cloud Functions:**
   - ❌ Examples use: `CloudFunctions` (in most places)
   - ✅ Should be: `Functions`
   - Module: `diagrams.gcp.compute`
   - Note: `Functions` has alias `GCF`
   - Found in: Multiple examples

2. **Cloud SQL:**
   - ❌ Examples use: `CloudSQL`
   - ✅ Should be: `SQL`
   - Module: `diagrams.gcp.compute`
   - Found in: Multiple examples

3. **Cloud Run:**
   - ❌ Examples use: `CloudRun`
   - ✅ Should be: `Run`
   - Module: `diagrams.gcp.compute`
   - Found in: Multiple examples

4. **Bigtable:**
   - ❌ Examples use: `BigTable` (inconsistent capitalization)
   - ✅ Should be: `Bigtable`
   - Module: `diagrams.gcp.database`
   - Found in: At least one example

5. **IoT Core:**
   - ✅ Examples use: `IotCore`
   - Status: Correct (from iot module)

6. **Pub/Sub:**
   - ✅ Examples use: `PubSub`
   - Status: Correct

7. **Workflows:**
   - ✅ Examples use: `Workflows`
   - Status: Correct

### Action Required:
- Update all GCP examples using `CloudFunctions` to use `Functions`
- Update all GCP examples using `CloudSQL` to use `SQL`
- Update all GCP examples using `CloudRun` to use `Run`
- Fix `BigTable` to `Bigtable`

---

## Summary of Required Fixes

### Azure Examples:
1. Replace `Function` → `FunctionApps` (all occurrences)

### GCP Examples:
1. Replace `CloudFunctions` → `Functions` (all occurrences)
2. Replace `CloudSQL` → `SQL` (all occurrences)
3. Replace `CloudRun` → `Run` (all occurrences)
4. Replace `BigTable` → `Bigtable` (if found)

---

## Verification Checklist

When updating examples, verify:

- [ ] Class name matches official documentation exactly
- [ ] Module path is correct (e.g., `diagrams.gcp.compute.Functions`)
- [ ] Capitalization is correct (e.g., `Bigtable` not `BigTable`)
- [ ] Code snippet runs without errors
- [ ] Import statements are correct

---

## Notes

1. The diagrams library uses exact class names - aliases work in imports but config should use full names
2. Case sensitivity matters - `Bigtable` ≠ `BigTable`
3. Some services are in unexpected modules (e.g., Cloud SQL is in compute, not database)
4. Always cross-reference with official docs when in doubt
