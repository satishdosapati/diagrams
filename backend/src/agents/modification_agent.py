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
        
        # Build context
        context = self._build_context(current_spec)
        
        prompt = f"""
{context}

User Request: {modification}

Modify the architecture specification according to the user's request.
Use provider "{current_spec.provider}" and appropriate node types from the lists above.
Return the updated ArchitectureSpec as JSON.
"""
        
        # Agent maintains state across calls
        response = agent.invoke(prompt, session_id=session_id)
        
        # Get updated spec
        updated_spec = response.structured_output
        
        # Detect changes
        changes = self._detect_changes(current_spec, updated_spec)
        
        return updated_spec, changes
    
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
        
        return f"""{self.base_system_prompt}

Available node types for provider "{provider}":
{node_list}

When adding new components, use the exact node_id strings from the list above (e.g., "ec2", "lambda", "vpc").
"""
    
    def _build_context(self, spec: ArchitectureSpec) -> str:
        """Build context description from spec."""
        lines = [
            "Current Architecture:",
            f"Title: {spec.title}",
            f"Provider: {spec.provider}",
            "",
            "Components:",
        ]
        
        for comp in spec.components:
            lines.append(f"  - {comp.name} ({comp.type})")
        
        lines.append("")
        lines.append("Connections:")
        for conn in spec.connections:
            from_comp = next((c for c in spec.components if c.id == conn.from_id), None)
            to_comp = next((c for c in spec.components if c.id == conn.to_id), None)
            if from_comp and to_comp:
                lines.append(f"  - {from_comp.name} → {to_comp.name}")
        
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

