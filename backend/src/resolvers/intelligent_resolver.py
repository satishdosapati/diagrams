"""
Intelligent Node Resolver - Maps generic/user-friendly terms to specific node types.
Uses fuzzy matching, context, and semantic understanding to resolve ambiguous terms.
"""
import re
from typing import Optional, Tuple, List, Dict
from difflib import SequenceMatcher
import logging

from ..models.node_registry import get_registry

logger = logging.getLogger(__name__)


class IntelligentNodeResolver:
    """
    Intelligently resolves generic or ambiguous node types to specific registry nodes.
    Uses fuzzy matching, context clues, and semantic understanding.
    """
    
    def __init__(self, provider: str):
        """
        Initialize intelligent resolver for a provider.
        
        Args:
            provider: Provider name (aws, azure, gcp)
        """
        self.provider = provider
        self.registry = get_registry()
        self._build_node_index()
    
    def _build_node_index(self):
        """Build index of nodes with normalized names and keywords."""
        self.node_index: Dict[str, Dict] = {}
        self.keyword_index: Dict[str, List[str]] = {}
        
        nodes = self.registry.get_all_nodes(self.provider)
        
        for node_id, node_config in nodes.items():
            description = node_config.get("description", "").lower()
            class_name = node_config.get("class_name", "").lower()
            
            # Normalize node_id
            normalized_id = self._normalize(node_id)
            
            # Extract keywords from description and class name
            keywords = self._extract_keywords(node_id, description, class_name)
            
            self.node_index[node_id] = {
                "normalized": normalized_id,
                "keywords": keywords,
                "description": description,
                "class_name": class_name,
                "config": node_config
            }
            
            # Index keywords for reverse lookup
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(node_id)
    
    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove underscores, hyphens, convert to lowercase
        return re.sub(r'[_\-\s]+', '', text.lower())
    
    def _extract_keywords(self, node_id: str, description: str, class_name: str) -> List[str]:
        """Extract keywords from node identifier, description, and class name."""
        keywords = set()
        
        # Add normalized node_id
        keywords.add(self._normalize(node_id))
        
        # Add parts of node_id (e.g., "private_subnet" -> ["private", "subnet"])
        parts = re.split(r'[_\-\s]+', node_id.lower())
        keywords.update(parts)
        
        # Extract meaningful words from description
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'aws', 'azure', 'gcp', 'amazon', 'google', 'microsoft'}
        desc_words = re.findall(r'\b\w+\b', description.lower())
        keywords.update(w for w in desc_words if w not in stop_words and len(w) > 2)
        
        # Add class name parts
        class_parts = re.split(r'[A-Z]', class_name)
        keywords.update(p.lower() for p in class_parts if p and len(p) > 2)
        
        return list(keywords)
    
    def resolve(self, node_id: str, component_name: Optional[str] = None, 
                context: Optional[Dict] = None) -> Optional[str]:
        """
        Intelligently resolve a generic node_id to a specific registry node_id.
        
        Args:
            node_id: Generic or user-provided node identifier
            component_name: Optional component name for context
            context: Optional additional context (e.g., other components in diagram)
            
        Returns:
            Resolved node_id from registry, or None if no match found
        """
        # Try context-aware matching FIRST (before exact match)
        # This allows context to override generic terms
        if component_name or context:
            context_match = self._context_match(node_id, component_name, context)
            if context_match:
                logger.info(f"Context match: '{node_id}' -> '{context_match}' (from context)")
                return context_match
        
        # Then try exact match
        if node_id in self.node_index:
            logger.debug(f"Exact match found: {node_id}")
            return node_id
        
        # Normalize the input
        normalized_input = self._normalize(node_id)
        
        # Try normalized exact match
        for registry_node_id, node_info in self.node_index.items():
            if node_info["normalized"] == normalized_input:
                logger.debug(f"Normalized match found: {node_id} -> {registry_node_id}")
                return registry_node_id
        
        # Try fuzzy matching with similarity scores
        matches = self._fuzzy_match(node_id, component_name)
        
        if matches:
            best_match = matches[0]
            similarity = best_match[1]
            
            # Only return if similarity is above threshold
            if similarity >= 0.6:  # 60% similarity threshold
                resolved_id = best_match[0]
                logger.info(
                    f"Fuzzy match: '{node_id}' -> '{resolved_id}' "
                    f"(similarity: {similarity:.2f})"
                )
                return resolved_id
            else:
                logger.debug(
                    f"Best match '{matches[0][0]}' similarity {similarity:.2f} "
                    f"below threshold 0.6 for '{node_id}'"
                )
        
        # Try keyword-based matching
        keyword_match = self._keyword_match(node_id, component_name)
        if keyword_match:
            logger.info(f"Keyword match: '{node_id}' -> '{keyword_match}'")
            return keyword_match
        
        logger.warning(f"No intelligent match found for '{node_id}'")
        return None
    
    def _fuzzy_match(self, node_id: str, component_name: Optional[str] = None) -> List[Tuple[str, float]]:
        """Find fuzzy matches using string similarity."""
        matches = []
        normalized_input = self._normalize(node_id)
        
        for registry_node_id, node_info in self.node_index.items():
            # Compare normalized forms
            similarity = SequenceMatcher(None, normalized_input, node_info["normalized"]).ratio()
            
            # Boost similarity if component name matches description keywords
            if component_name:
                name_lower = component_name.lower()
                for keyword in node_info["keywords"]:
                    if keyword in name_lower and len(keyword) > 3:
                        similarity += 0.1  # Small boost
                        break
            
            matches.append((registry_node_id, similarity))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def _keyword_match(self, node_id: str, component_name: Optional[str] = None) -> Optional[str]:
        """Match based on keyword overlap."""
        # Extract keywords from input
        input_keywords = set(self._extract_keywords(node_id, "", ""))
        
        if component_name:
            name_keywords = set(re.findall(r'\b\w+\b', component_name.lower()))
            input_keywords.update(k for k in name_keywords if len(k) > 2)
        
        best_match = None
        best_score = 0
        
        for registry_node_id, node_info in self.node_index.items():
            registry_keywords = set(node_info["keywords"])
            
            # Calculate overlap
            overlap = input_keywords.intersection(registry_keywords)
            if overlap:
                # Score based on overlap ratio
                score = len(overlap) / max(len(input_keywords), len(registry_keywords))
                
                # Prefer exact keyword matches
                if self._normalize(node_id) in registry_keywords:
                    score += 0.2
                
                if score > best_score:
                    best_score = score
                    best_match = registry_node_id
        
        # Only return if score is meaningful
        if best_score >= 0.4:
            return best_match
        
        return None
    
    def _context_match(self, node_id: str, component_name: Optional[str] = None,
                      context: Optional[Dict] = None) -> Optional[str]:
        """Match based on context clues."""
        if not component_name and not context:
            return None
        
        # Common context-based mappings
        context_patterns = {
            # Network context
            "subnet": {
                "private": "private_subnet",
                "public": "public_subnet",
                "internal": "private_subnet",
                "external": "public_subnet",
            },
            # Database context
            "database": {
                "relational": "rds",
                "nosql": "dynamodb",
                "document": "dynamodb",
                "key-value": "dynamodb",
            },
            # Compute context
            "function": {
                "lambda": "lambda",  # Explicit lambda mention
                "serverless": "lambda",
                "container": "ecs",
                "kubernetes": "eks",
                "step": "step_functions",  # Step Functions
            },
        }
        
        # Check if node_id matches a pattern
        node_lower = node_id.lower()
        name_lower = (component_name or "").lower()
        combined = f"{node_lower} {name_lower}"
        
        for pattern, mappings in context_patterns.items():
            if pattern in node_lower:
                # Check context for hints first (more specific)
                for hint, mapped_node in mappings.items():
                    if hint in combined:
                        if mapped_node in self.node_index:
                            logger.debug(
                                f"Context hint '{hint}' found, mapping '{node_id}' -> '{mapped_node}'"
                            )
                            return mapped_node
                
                # Default mappings for common patterns (less specific)
                if pattern == "subnet":
                    # Provider-specific handling: GCP doesn't have subnet nodes (subnets are part of VPC)
                    if self.provider == "gcp":
                        if "vpc" in self.node_index:
                            logger.debug("Mapping subnet to VPC for GCP (subnets are part of VPC)")
                            return "vpc"
                        return None
                    
                    # AWS/Azure subnet resolution
                    # Check component name for public/private indicators
                    if component_name:
                        name_lower = component_name.lower()
                        # Public indicators
                        if any(word in name_lower for word in ["public", "external", "dmz", "internet"]):
                            if "public_subnet" in self.node_index:
                                logger.debug("Public subnet detected from component name")
                                return "public_subnet"
                        # Private indicators
                        if any(word in name_lower for word in ["private", "internal", "app", "data"]):
                            if "private_subnet" in self.node_index:
                                logger.debug("Private subnet detected from component name")
                                return "private_subnet"
                    
                    # Default to private subnet if no clear indicator (AWS only)
                    if "private_subnet" in self.node_index:
                        logger.debug("Defaulting to private_subnet")
                        return "private_subnet"
                
                elif pattern == "function":
                    # Check component name for function type indicators
                    if component_name:
                        name_lower = component_name.lower()
                        # Lambda indicators (most common)
                        if any(word in name_lower for word in ["lambda", "serverless", "aws lambda"]):
                            if "lambda" in self.node_index:
                                logger.debug("Lambda function detected from component name")
                                return "lambda"
                        # Step Functions indicators
                        if "step" in name_lower or "workflow" in name_lower:
                            if "step_functions" in self.node_index:
                                logger.debug("Step Functions detected from component name")
                                return "step_functions"
                        # Container indicators
                        if any(word in name_lower for word in ["container", "docker", "fargate"]):
                            if "ecs" in self.node_index:
                                logger.debug("ECS function detected from component name")
                                return "ecs"
                        # Kubernetes indicators
                        if any(word in name_lower for word in ["kubernetes", "k8s", "eks"]):
                            if "eks" in self.node_index:
                                logger.debug("EKS function detected from component name")
                                return "eks"
                    
                    # Default to lambda (most common serverless function)
                    if "lambda" in self.node_index:
                        logger.debug("Defaulting to lambda")
                        return "lambda"
        
        return None
    
    def get_suggestions(self, node_id: str, limit: int = 5) -> List[Tuple[str, float, str]]:
        """
        Get suggestions for a node_id that doesn't match exactly.
        
        Returns:
            List of (node_id, similarity_score, description) tuples
        """
        matches = self._fuzzy_match(node_id)
        suggestions = []
        
        for registry_node_id, similarity in matches[:limit]:
            node_info = self.node_index[registry_node_id]
            description = node_info["config"].get("description", "")
            suggestions.append((registry_node_id, similarity, description))
        
        return suggestions

