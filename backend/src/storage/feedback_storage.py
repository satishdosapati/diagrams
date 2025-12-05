"""
Feedback storage for thumbs up/down feedback system.
Stores feedback in JSON files for simple, file-based persistence.
"""
import json
import logging
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FeedbackStorage:
    """Stores and retrieves user feedback."""
    
    def __init__(self, storage_path: str = "./data/feedback"):
        """
        Initialize feedback storage.
        
        Args:
            storage_path: Path to store feedback JSON files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.feedback_file = self.storage_path / "feedback.json"
        self.patterns_file = self.storage_path / "patterns.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist."""
        if not self.feedback_file.exists():
            self._write_json(self.feedback_file, {"feedbacks": []})
        
        if not self.patterns_file.exists():
            self._write_json(self.patterns_file, {"patterns": []})
    
    def _read_json(self, file_path: Path) -> dict:
        """Read JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}", exc_info=True)
            return {}
    
    def _write_json(self, file_path: Path, data: dict):
        """Write JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}", exc_info=True)
            raise
    
    def save_feedback(
        self,
        generation_id: str,
        session_id: str,
        thumbs_up: bool,
        code_hash: Optional[str] = None,
        code: Optional[str] = None
    ) -> str:
        """
        Save thumbs up/down feedback.
        
        Args:
            generation_id: Unique ID for this generation
            session_id: Session ID
            thumbs_up: True for thumbs up, False for thumbs down
            code_hash: SHA256 hash of generated code (optional)
            code: Generated code (optional, for pattern extraction)
            
        Returns:
            Feedback ID
        """
        import uuid
        import time
        
        feedback_id = str(uuid.uuid4())
        
        feedback_data = {
            "feedback_id": feedback_id,
            "generation_id": generation_id,
            "session_id": session_id,
            "thumbs_up": thumbs_up,
            "code_hash": code_hash,
            "timestamp": time.time(),
            "datetime": datetime.utcnow().isoformat()
        }
        
        # Read existing feedbacks
        data = self._read_json(self.feedback_file)
        if "feedbacks" not in data:
            data["feedbacks"] = []
        
        # Add new feedback
        data["feedbacks"].append(feedback_data)
        
        # Write back
        self._write_json(self.feedback_file, data)
        
        logger.info(f"Saved feedback: {feedback_id} - {'👍' if thumbs_up else '👎'} for generation {generation_id}")
        
        # Extract patterns if code provided
        if code and thumbs_up:
            self._extract_patterns(generation_id, code, code_hash)
        
        return feedback_id
    
    def _extract_patterns(self, generation_id: str, code: str, code_hash: Optional[str]):
        """
        Extract patterns from successful code (thumbs up).
        
        Args:
            generation_id: Generation ID
            code: Generated Python code
            code_hash: Code hash
        """
        try:
            patterns = []
            
            # Extract import patterns
            import_patterns = self._extract_import_patterns(code)
            if import_patterns:
                patterns.extend(import_patterns)
            
            # Extract code structure patterns
            structure_patterns = self._extract_structure_patterns(code)
            if structure_patterns:
                patterns.extend(structure_patterns)
            
            # Store patterns
            if patterns:
                self._save_patterns(patterns, generation_id, code_hash)
                
        except Exception as e:
            logger.warning(f"Error extracting patterns: {e}", exc_info=True)
    
    def _extract_import_patterns(self, code: str) -> List[Dict]:
        """Extract import patterns from code."""
        patterns = []
        
        # Find all import statements
        import_lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                import_lines.append(line)
        
        if import_lines:
            patterns.append({
                "type": "import",
                "pattern": "\n".join(import_lines),
                "import_count": len(import_lines),
                "imports": import_lines
            })
        
        return patterns
    
    def _extract_structure_patterns(self, code: str) -> List[Dict]:
        """Extract code structure patterns."""
        patterns = []
        
        # Count components (variable assignments)
        component_count = len(re.findall(r'\w+\s*=\s*\w+\(', code))
        
        # Count connections (>>, <<, -)
        connection_count = len(re.findall(r'\w+\s*[>><<-]+\s*\w+', code))
        
        # Check for clusters
        has_clusters = 'Cluster(' in code
        
        # Check for edges
        has_edges = 'Edge(' in code
        
        patterns.append({
            "type": "structure",
            "component_count": component_count,
            "connection_count": connection_count,
            "has_clusters": has_clusters,
            "has_edges": has_edges
        })
        
        return patterns
    
    def _save_patterns(self, patterns: List[Dict], generation_id: str, code_hash: Optional[str]):
        """Save extracted patterns."""
        data = self._read_json(self.patterns_file)
        if "patterns" not in data:
            data["patterns"] = []
        
        import time
        for pattern in patterns:
            pattern_entry = {
                "pattern_id": f"{generation_id}_{pattern['type']}",
                "generation_id": generation_id,
                "code_hash": code_hash,
                "pattern_type": pattern["type"],
                "pattern_data": pattern,
                "success_count": 1,
                "total_count": 1,
                "success_rate": 1.0,
                "created_at": time.time(),
                "last_used": time.time()
            }
            data["patterns"].append(pattern_entry)
        
        self._write_json(self.patterns_file, data)
        logger.info(f"Saved {len(patterns)} patterns from generation {generation_id}")
    
    def get_feedback_stats(self, days: int = 30) -> Dict:
        """
        Get feedback statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with feedback statistics
        """
        import time
        
        data = self._read_json(self.feedback_file)
        feedbacks = data.get("feedbacks", [])
        
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_feedbacks = [
            f for f in feedbacks 
            if f.get("timestamp", 0) > cutoff_time
        ]
        
        thumbs_up_count = sum(1 for f in recent_feedbacks if f.get("thumbs_up"))
        thumbs_down_count = len(recent_feedbacks) - thumbs_up_count
        
        return {
            "total_feedbacks": len(recent_feedbacks),
            "thumbs_up": thumbs_up_count,
            "thumbs_down": thumbs_down_count,
            "thumbs_up_rate": thumbs_up_count / len(recent_feedbacks) if recent_feedbacks else 0.0
        }
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Dict]:
        """
        Get patterns by type.
        
        Args:
            pattern_type: Type of pattern (e.g., "import", "structure")
            
        Returns:
            List of patterns
        """
        data = self._read_json(self.patterns_file)
        patterns = data.get("patterns", [])
        
        return [
            p for p in patterns 
            if p.get("pattern_type") == pattern_type
        ]
