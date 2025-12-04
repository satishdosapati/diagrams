"""
Modification agent for iterative diagram refinement with state management.
"""
import os
from strands import Agent
from strands.models import BedrockModel
from strands.session import InMemorySessionManager

from ..models.spec import ArchitectureSpec


class ModificationAgent:
    """Agent that modifies existing diagrams based on chat messages."""
    
    def __init__(self):
        """Initialize the modification agent with state management."""
        region = os.getenv("AWS_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        model = BedrockModel(model_id=model_id, region=region)
        self.session_manager = InMemorySessionManager()
        
        self.agent = Agent(
            model=model,
            structured_output=ArchitectureSpec,
            session_manager=self.session_manager,
            system_prompt="""You are an expert at modifying existing architecture diagrams based on user requests.

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
        )
    
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
        # Build context
        context = self._build_context(current_spec)
        
        prompt = f"""
{context}

User Request: {modification}

Modify the architecture specification according to the user's request.
Return the updated ArchitectureSpec as JSON.
"""
        
        # Agent maintains state across calls
        response = self.agent.invoke(prompt, session_id=session_id)
        
        # Get updated spec
        updated_spec = response.structured_output
        
        # Detect changes
        changes = self._detect_changes(current_spec, updated_spec)
        
        return updated_spec, changes
    
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

