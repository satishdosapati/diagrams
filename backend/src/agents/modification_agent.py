"""
Modification agent for iterative diagram refinement with state management.
"""
import os
import tempfile
from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager

from ..models.spec import ArchitectureSpec
from ..models.node_registry import get_registry
from ..advisors.aws_architectural_advisor import AWSArchitecturalAdvisor
import logging


class ModificationAgent:
    """Agent that modifies existing diagrams based on chat messages."""
    
    def __init__(self):
        """Initialize the modification agent with state management."""
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Create Bedrock model (region configured via AWS_REGION env var or boto3 default)
        self.model = BedrockModel(model_id=model_id)
        # Use a temporary directory for session storage (in-memory-like behavior)
        # Note: FileSessionManager requires a session_id, so we'll create one per session
        self.storage_dir = os.path.join(tempfile.gettempdir(), "diagram-generator-sessions")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load registry for generating node lists
        self.registry = get_registry()
        
        # Initialize AWS Architectural Advisor
        self.aws_advisor = AWSArchitecturalAdvisor()
        
        # Base system prompt (will be enhanced with node lists per request)
        self.base_system_prompt = """You are an expert at modifying existing architecture diagrams based on user requests.

Your task:
1. Understand the current architecture specification
2. Interpret modification requests (add, remove, change, connect)
3. Update the ArchitectureSpec accordingly
4. Maintain provider consistency
5. Preserve unchanged components

Common modifications:
- "Add X" → Add component(s) and connections
- "Remove X" → Remove component(s) and related connections
- "Change X to Y" → Update component properties
- "Connect X to Y" → Add connection
- "Add cluster for X" → Group components (future)

Always maintain the same provider as the original spec unless explicitly requested to change.
"""
    
    def modify(
        self,
        session_id: str,
        current_spec: ArchitectureSpec,
        modification: str
    ) -> tuple[ArchitectureSpec, list[str]]:
        """
        Modify diagram based on chat message.
        
        Args:
            session_id: Session ID for conversation context
            current_spec: Current architecture specification
            modification: User's modification request
            
        Returns:
            Tuple of (updated_spec, list_of_changes)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # STEP 1: Consult architecture advisor BEFORE modification
        # Get architectural guidance for the modification
        advisor_guidance = self._get_advisor_guidance(current_spec, modification)
        logger.info(f"Architecture advisor consulted for modification: {modification[:50]}...")
        
        # Create a session manager for this specific session
        # FileSessionManager requires session_id in constructor
        session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir=self.storage_dir
        )
        
        # Generate system prompt with node lists for the current provider
        system_prompt = self._generate_system_prompt(current_spec.provider)
        
        # Create agent instance with session manager for this session
        agent = Agent(
            model=self.model,
            structured_output_model=ArchitectureSpec,
            session_manager=session_manager,
            system_prompt=system_prompt
        )
        
        # Build context with advisor guidance
        context = self._build_context(current_spec)
        
        prompt = f"""
{context}

User Request: {modification}

{advisor_guidance}

Modify the architecture specification according to the user's request.
Use provider "{current_spec.provider}" and appropriate node types from the lists above.
Return the updated ArchitectureSpec as JSON.

IMPORTANT:
- Preserve all existing components unless explicitly asked to remove them
- Maintain component IDs for unchanged components
- Only add/modify/remove components as requested
- Keep the same provider unless explicitly asked to change
- Follow architectural best practices for component ordering and connections
"""

        # Agent maintains state across calls (session_manager handles session_id)
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = agent(prompt)
        except Exception as e:
            logger.error(f"Agent invocation failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to invoke modification agent: {str(e)}") from e
        
        # Get updated spec
        if not hasattr(response, 'structured_output'):
            raise ValueError(f"Agent response missing structured_output. Response type: {type(response)}")
        
        updated_spec = response.structured_output
        
        # Validate that we got a valid spec
        if not updated_spec:
            raise ValueError("Agent did not return a valid ArchitectureSpec")
        
        # Ensure provider is maintained
        if updated_spec.provider != current_spec.provider:
            # Log warning but allow it if user explicitly requested change
            logger.warning(
                f"Provider changed from {current_spec.provider} to {updated_spec.provider}. "
                "This is allowed if explicitly requested by user."
            )
        
        # STEP 2: Consult architecture advisor AFTER modification
        # Enhance spec with architectural guidance (always consult advisor)
        logger.info(f"Architecture advisor enhancing spec for provider: {updated_spec.provider}")
        updated_spec = self._enhance_with_advisor(updated_spec)
        
        # Detect changes
        changes = self._detect_changes(current_spec, updated_spec)
        
        # Log advisor contributions
        if updated_spec.metadata.get("enhanced"):
            advisor_changes = [
                "Component ordering optimized",
                "Connections validated and enhanced"
            ]
            changes.extend(advisor_changes)
            logger.info("Architecture advisor enhancements applied")
        
        return updated_spec, changes
    
    def _get_advisor_guidance(self, spec: ArchitectureSpec, modification: str) -> str:
        """
        Get architectural guidance from advisor for the modification.
        
        Args:
            spec: Current architecture specification
            modification: User's modification request
            
        Returns:
            Architectural guidance string
        """
        guidance_parts = []
        
        # Get provider-specific guidance
        if spec.provider == "aws":
            # Analyze modification to provide specific guidance
            modification_lower = modification.lower()
            
            # Check if adding components
            if any(word in modification_lower for word in ["add", "create", "new", "include"]):
                # Suggest dependencies
                if "ec2" in modification_lower or "instance" in modification_lower:
                    guidance_parts.append(
                        "NOTE: If adding EC2 instances, ensure VPC and Subnet exist. "
                        "EC2 instances should be connected: VPC → Subnet → EC2"
                    )
                if "lambda" in modification_lower or "function" in modification_lower:
                    guidance_parts.append(
                        "NOTE: Lambda functions commonly connect to API Gateway or EventBridge. "
                        "Consider adding these connections if they exist."
                    )
                if "rds" in modification_lower or "database" in modification_lower:
                    guidance_parts.append(
                        "NOTE: RDS databases require VPC and Subnet. "
                        "Ensure proper network connections: VPC → Subnet → RDS"
                    )
            
            # Check if modifying connections
            if any(word in modification_lower for word in ["connect", "link", "route"]):
                guidance_parts.append(
                    "NOTE: Ensure connections follow AWS architectural patterns. "
                    "Common patterns: API Gateway → Lambda → DynamoDB, ALB → EC2 → RDS"
                )
            
            # Add general AWS guidance
            if guidance_parts:
                return "\n\nArchitectural Guidance:\n" + "\n".join(f"- {g}" for g in guidance_parts)
        
        return ""
    
    def _enhance_with_advisor(self, spec: ArchitectureSpec) -> ArchitectureSpec:
        """
        Enhance spec with architectural advisor (provider-aware).
        
        Args:
            spec: Architecture specification to enhance
            
        Returns:
            Enhanced architecture specification
        """
        logger = logging.getLogger(__name__)
        
        # Use AWS advisor for AWS provider
        if spec.provider == "aws":
            logger.info("Consulting AWS Architectural Advisor for enhancement")
            return self.aws_advisor.enhance_spec(spec)
        
        # For other providers, return as-is (can be extended with Azure/GCP advisors)
        # TODO: Add Azure and GCP advisors
        logger.info(f"Architectural advisor not available for provider: {spec.provider}")
        return spec
    
    def _generate_system_prompt(self, provider: str) -> str:
        """Generate system prompt with node lists for the specified provider."""
        # Get node list for the provider
        provider_nodes = self.registry.get_node_list(provider)
        
        # Format node list (limit to first 50 for readability)
        def format_node_list(nodes, limit=50):
            if len(nodes) <= limit:
                return ", ".join(nodes)
            return ", ".join(nodes[:limit]) + f", ... (and {len(nodes) - limit} more)"
        
        node_list = format_node_list(provider_nodes)
        
        # Add AWS architectural guidance if AWS provider
        aws_guidance = ""
        if provider == "aws":
            aws_guidance = f"""

AWS Architectural Best Practices:
{self.aws_advisor._get_static_guidance()}

When modifying AWS architectures:
- Maintain logical component ordering: Internet/Edge → Network → Application → Compute → Data
- Ensure VPC contains Subnets, Subnets contain EC2 instances
- Follow common patterns: API Gateway → Lambda → DynamoDB, ALB → EC2 → RDS
"""
        
        return f"""{self.base_system_prompt}

Available node types for provider "{provider}":
{node_list}

When adding new components, use the exact node_id strings from the list above (e.g., "ec2", "lambda", "vpc").
{aws_guidance}

IMPORTANT: Always consult architectural best practices when modifying diagrams:
- Maintain logical component ordering
- Ensure proper connections between components
- Add missing dependencies when adding new components
- Follow provider-specific architectural patterns
"""
    
    def _build_context(self, spec: ArchitectureSpec) -> str:
        """Build context description from spec."""
        import json
        
        # Build a detailed context with both human-readable and JSON formats
        lines = [
            "Current Architecture Specification:",
            f"Title: {spec.title}",
            f"Provider: {spec.provider}",
            "",
            "Components:",
        ]
        
        for comp in spec.components:
            lines.append(f"  - ID: {comp.id}, Name: {comp.name}, Type: {comp.type}")
        
        lines.append("")
        lines.append("Connections:")
        for conn in spec.connections:
            from_comp = next((c for c in spec.components if c.id == conn.from_id), None)
            to_comp = next((c for c in spec.components if c.id == conn.to_id), None)
            if from_comp and to_comp:
                lines.append(f"  - {from_comp.name} ({from_comp.id}) → {to_comp.name} ({to_comp.id})")
            else:
                lines.append(f"  - {conn.from_id} → {conn.to_id}")
        
        lines.append("")
        lines.append("Full ArchitectureSpec JSON:")
        # Include the full spec as JSON for reference
        spec_dict = spec.model_dump()
        lines.append(json.dumps(spec_dict, indent=2))
        
        return "\n".join(lines)
    
    def _detect_changes(self, old_spec: ArchitectureSpec, new_spec: ArchitectureSpec) -> list[str]:
        """Detect what changed between specs."""
        changes = []
        
        old_comp_ids = {c.id for c in old_spec.components}
        new_comp_ids = {c.id for c in new_spec.components}
        
        # Added components
        added = new_comp_ids - old_comp_ids
        if added:
            added_names = [c.name for c in new_spec.components if c.id in added]
            changes.append(f"Added: {', '.join(added_names)}")
        
        # Removed components
        removed = old_comp_ids - new_comp_ids
        if removed:
            removed_names = [c.name for c in old_spec.components if c.id in removed]
            changes.append(f"Removed: {', '.join(removed_names)}")
        
        # Connection changes
        old_conns = {(c.from_id, c.to_id) for c in old_spec.connections}
        new_conns = {(c.from_id, c.to_id) for c in new_spec.connections}
        
        if new_conns != old_conns:
            changes.append("Updated connections")
        
        return changes

