# Generic and OnPrem Nodes Configuration

## Overview

This document describes the cross-platform generic and onprem nodes that have been added to all cloud provider configurations (AWS, Azure, GCP).

## Added Modules

The following modules are now available for all providers:

### 1. Generic OS (`diagrams.generic.os`)
Operating system nodes that can be used in any cloud architecture diagram:

- `android` - Android Operating System
- `centos` - CentOS Operating System
- `debian` - Debian Operating System
- `ios` - iOS Operating System
- `linux_general` - Linux (General)
- `raspbian` - Raspbian Operating System
- `redhat` - Red Hat Operating System
- `suse` - SUSE Operating System
- `ubuntu` - Ubuntu Operating System
- `windows` - Windows Operating System

### 2. Generic Place (`diagrams.generic.place`)
Place/location nodes:

- `datacenter` - Data Center

### 3. Generic Virtualization (`diagrams.generic.virtualization`)
Virtualization platform nodes:

- `qemu` - QEMU Virtualization
- `virtualbox` - VirtualBox
- `vmware` - VMware
- `xen` - XEN Virtualization

### 4. OnPrem Client (`diagrams.onprem.client`)
Client/user nodes:

- `client` - Client Device
- `user` - User (single)
- `users` - Multiple Users

## Usage Examples

### Example 1: Adding Users to AWS Architecture

```json
{
  "description": "Users accessing AWS EC2 instances through API Gateway",
  "provider": "aws"
}
```

The system can now recognize and include user/client nodes.

### Example 2: Multi-OS Environment

```json
{
  "description": "Windows and Linux servers in Azure Virtual Network",
  "provider": "azure"
}
```

The system can now include OS-specific nodes.

### Example 3: Data Center Location

```json
{
  "description": "On-premises datacenter connecting to GCP via Cloud Interconnect",
  "provider": "gcp"
}
```

The system can now include datacenter nodes.

## Configuration Files Updated

All three provider configuration files have been updated:

- `aws_nodes.yaml` - Added generic and onprem nodes
- `azure_nodes.yaml` - Added generic and onprem nodes
- `gcp_nodes.yaml` - Added generic and onprem nodes

## Node Registry Structure

Each provider file now includes:

```yaml
modules:
  # ... existing provider modules ...
  generic_os: diagrams.generic.os
  generic_place: diagrams.generic.place
  generic_virtualization: diagrams.generic.virtualization
  onprem_client: diagrams.onprem.client

nodes:
  # ... existing provider nodes ...
  # Generic OS nodes
  android:
    category: generic_os
    class_name: Android
    description: "Android Operating System"
  # ... more nodes ...
```

## Benefits

1. **Cross-Platform Support**: These nodes work with all cloud providers
2. **Hybrid Architecture Support**: Better representation of hybrid cloud/on-premises architectures
3. **User-Centric Diagrams**: Can now include users and clients in architecture diagrams
4. **OS Representation**: Can represent different operating systems in diagrams
5. **Virtualization Support**: Can represent various virtualization platforms

## References

- [Generic Nodes Documentation](https://diagrams.mingrammer.com/docs/nodes/generic)
- [OnPrem Nodes Documentation](https://diagrams.mingrammer.com/docs/nodes/onprem)

## Implementation Notes

- All nodes are available for AWS, Azure, and GCP providers
- The component resolver automatically handles these cross-platform nodes
- No provider-specific logic needed - these are truly generic nodes
- Works seamlessly with existing cloud provider nodes
