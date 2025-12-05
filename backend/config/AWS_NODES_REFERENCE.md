# AWS Nodes Configuration Reference

## Documentation Source

**Always refer to the official diagrams library documentation:**
- **AWS Nodes:** https://diagrams.mingrammer.com/docs/nodes/aws

## Key Points

1. **Class Names**: Use the exact class names as defined in the official documentation
2. **Aliases**: While aliases exist (e.g., `DAX` for `DynamodbDax`), use the full class name in configuration for clarity
3. **Categories**: Match the module/category exactly as defined in the diagrams library
4. **Updates**: When adding new nodes, always verify against the official documentation first

## Recently Updated Nodes

The following nodes were added/updated based on official documentation:

### Database
- **DAX**: `DynamodbDax` (class name) in `diagrams.aws.database`
- **Timestream**: `Timestream` in `diagrams.aws.database`

### Network
- **VPC Endpoint**: `Endpoint` in `diagrams.aws.network`
- **VPC Flow Logs**: `VPCFlowLogs` in `diagrams.aws.network`
- **Global Accelerator**: `GlobalAccelerator` in `diagrams.aws.network`
- **Application Load Balancer**: `ElbApplicationLoadBalancer` in `diagrams.aws.network` (alias: `ALB`)
- **Network Load Balancer**: `ElbNetworkLoadBalancer` in `diagrams.aws.network` (alias: `NLB`)

### Compute
- **EC2 Auto Scaling**: `EC2AutoScaling` in `diagrams.aws.compute`
- **Application Auto Scaling**: `ApplicationAutoScaling` in `diagrams.aws.compute` (alias: `AutoScaling`)

### Management
- **CloudWatch Logs**: `CloudwatchLogs` in `diagrams.aws.management`
- **Parameter Store**: `SystemsManagerParameterStore` in `diagrams.aws.management` (alias: `ParameterStore`)

### DevTools
- **X-Ray**: `XRay` in `diagrams.aws.devtools`

## Verification Checklist

When adding or updating nodes:

- [ ] Check the official documentation: https://diagrams.mingrammer.com/docs/nodes/aws
- [ ] Verify the exact class name (not alias)
- [ ] Verify the correct module/category
- [ ] Update examples if class name changes
- [ ] Test code generation with the new node

## Common Class Name Patterns

- Most classes use PascalCase: `ElbApplicationLoadBalancer`
- Some use exact AWS service names: `DynamodbDax`, `VPCFlowLogs`
- Aliases are often shorter: `DAX`, `ALB`, `NLB`

When in doubt, check the official documentation first!
