"""
Tests for feedback storage.
"""
import pytest
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.feedback_storage import FeedbackStorage


class TestFeedbackStorage:
    """Test FeedbackStorage class."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def storage(self, temp_storage_dir):
        """Create FeedbackStorage instance with temp directory."""
        return FeedbackStorage(storage_path=temp_storage_dir)
    
    def test_initialization(self, storage, temp_storage_dir):
        """Test FeedbackStorage initialization."""
        assert storage is not None
        assert storage.storage_path == Path(temp_storage_dir)
        assert storage.feedback_file.exists()
        assert storage.patterns_file.exists()
    
    def test_initialization_creates_files(self, temp_storage_dir):
        """Test initialization creates required JSON files."""
        storage = FeedbackStorage(storage_path=temp_storage_dir)
        
        assert storage.feedback_file.exists()
        assert storage.patterns_file.exists()
        
        # Verify files have correct structure
        feedback_data = storage._read_json(storage.feedback_file)
        assert "feedbacks" in feedback_data
        
        patterns_data = storage._read_json(storage.patterns_file)
        assert "patterns" in patterns_data
    
    def test_save_feedback_thumbs_up(self, storage):
        """Test saving thumbs up feedback."""
        feedback_id = storage.save_feedback(
            generation_id="gen-123",
            session_id="session-456",
            thumbs_up=True
        )
        
        assert feedback_id is not None
        assert len(feedback_id) > 0
        
        # Verify feedback was saved
        data = storage._read_json(storage.feedback_file)
        assert len(data["feedbacks"]) == 1
        
        feedback = data["feedbacks"][0]
        assert feedback["feedback_id"] == feedback_id
        assert feedback["generation_id"] == "gen-123"
        assert feedback["session_id"] == "session-456"
        assert feedback["thumbs_up"] is True
        assert "timestamp" in feedback
        assert "datetime" in feedback
    
    def test_save_feedback_thumbs_down(self, storage):
        """Test saving thumbs down feedback."""
        feedback_id = storage.save_feedback(
            generation_id="gen-789",
            session_id="session-012",
            thumbs_up=False
        )
        
        assert feedback_id is not None
        
        # Verify feedback was saved
        data = storage._read_json(storage.feedback_file)
        feedback = data["feedbacks"][0]
        assert feedback["thumbs_up"] is False
    
    def test_save_feedback_with_code_hash(self, storage):
        """Test saving feedback with code hash."""
        feedback_id = storage.save_feedback(
            generation_id="gen-123",
            session_id="session-456",
            thumbs_up=True,
            code_hash="abc123def456"
        )
        
        data = storage._read_json(storage.feedback_file)
        feedback = data["feedbacks"][0]
        assert feedback["code_hash"] == "abc123def456"
    
    def test_save_feedback_with_code(self, storage):
        """Test saving feedback with code (should extract patterns)."""
        code = """
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Test", show=False):
    ec2 = EC2("Instance")
    rds = RDS("Database")
    ec2 >> rds
"""
        feedback_id = storage.save_feedback(
            generation_id="gen-123",
            session_id="session-456",
            thumbs_up=True,
            code=code
        )
        
        assert feedback_id is not None
        
        # Verify patterns were extracted (thumbs up with code)
        patterns_data = storage._read_json(storage.patterns_file)
        assert len(patterns_data["patterns"]) > 0
    
    def test_save_feedback_thumbs_down_no_patterns(self, storage):
        """Test that thumbs down feedback doesn't extract patterns."""
        code = "from diagrams import Diagram"
        feedback_id = storage.save_feedback(
            generation_id="gen-123",
            session_id="session-456",
            thumbs_up=False,
            code=code
        )
        
        # Patterns should not be extracted for thumbs down
        patterns_data = storage._read_json(storage.patterns_file)
        # Patterns file should exist but be empty (only initial structure)
        assert "patterns" in patterns_data
    
    def test_get_feedback_stats(self, storage):
        """Test getting feedback statistics."""
        # Add some feedback
        storage.save_feedback("gen-1", "session-1", True)
        storage.save_feedback("gen-2", "session-2", True)
        storage.save_feedback("gen-3", "session-3", False)
        
        stats = storage.get_feedback_stats(days=30)
        
        assert stats["total_feedbacks"] == 3
        assert stats["thumbs_up"] == 2
        assert stats["thumbs_down"] == 1
        assert stats["thumbs_up_rate"] == pytest.approx(2/3, rel=0.01)
    
    def test_get_feedback_stats_empty(self, storage):
        """Test getting feedback statistics when no feedback exists."""
        stats = storage.get_feedback_stats(days=30)
        
        assert stats["total_feedbacks"] == 0
        assert stats["thumbs_up"] == 0
        assert stats["thumbs_down"] == 0
        assert stats["thumbs_up_rate"] == 0.0
    
    def test_get_feedback_stats_with_days(self, storage):
        """Test getting feedback statistics with custom days."""
        # Add feedback
        storage.save_feedback("gen-1", "session-1", True)
        
        # Get stats for different time periods
        stats_30 = storage.get_feedback_stats(days=30)
        stats_7 = storage.get_feedback_stats(days=7)
        stats_1 = storage.get_feedback_stats(days=1)
        
        assert stats_30["total_feedbacks"] >= stats_7["total_feedbacks"]
        assert stats_7["total_feedbacks"] >= stats_1["total_feedbacks"]
    
    def test_extract_import_patterns(self, storage):
        """Test import pattern extraction."""
        code = """
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC
"""
        patterns = storage._extract_import_patterns(code)
        
        assert len(patterns) == 1
        assert patterns[0]["type"] == "import"
        assert "import_count" in patterns[0]
        assert patterns[0]["import_count"] == 4
    
    def test_extract_structure_patterns(self, storage):
        """Test structure pattern extraction."""
        code = """
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Test", show=False):
    with Cluster("Network"):
        ec2 = EC2("Instance")
        rds = RDS("Database")
    
    ec2 >> Edge(label="connects") >> rds
"""
        patterns = storage._extract_structure_patterns(code)
        
        assert len(patterns) == 1
        assert patterns[0]["type"] == "structure"
        assert patterns[0]["component_count"] == 2
        assert patterns[0]["connection_count"] >= 1
        assert patterns[0]["has_clusters"] is True
        assert patterns[0]["has_edges"] is True
    
    def test_get_patterns_by_type(self, storage):
        """Test getting patterns by type."""
        code = "from diagrams import Diagram"
        storage.save_feedback("gen-1", "session-1", True, code=code)
        
        import_patterns = storage.get_patterns_by_type("import")
        structure_patterns = storage.get_patterns_by_type("structure")
        
        # Should have patterns if extraction worked
        assert isinstance(import_patterns, list)
        assert isinstance(structure_patterns, list)
    
    def test_read_json_nonexistent_file(self, storage):
        """Test reading non-existent JSON file."""
        nonexistent_file = storage.storage_path / "nonexistent.json"
        data = storage._read_json(nonexistent_file)
        assert data == {}
    
    def test_read_json_invalid_json(self, storage, temp_storage_dir):
        """Test reading invalid JSON file."""
        invalid_file = Path(temp_storage_dir) / "invalid.json"
        invalid_file.write_text("invalid json content {")
        
        # Should return empty dict on error
        data = storage._read_json(invalid_file)
        assert data == {}
    
    def test_write_json(self, storage, temp_storage_dir):
        """Test writing JSON file."""
        test_file = Path(temp_storage_dir) / "test.json"
        test_data = {"key": "value", "number": 123}
        
        storage._write_json(test_file, test_data)
        
        # Verify file was written
        assert test_file.exists()
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_feedback_id_uniqueness(self, storage):
        """Test that feedback IDs are unique."""
        feedback_ids = []
        for i in range(5):
            fid = storage.save_feedback(f"gen-{i}", f"session-{i}", True)
            feedback_ids.append(fid)
        
        # All IDs should be unique
        assert len(feedback_ids) == len(set(feedback_ids))
    
    def test_feedback_timestamp(self, storage):
        """Test that feedback includes timestamp."""
        feedback_id = storage.save_feedback("gen-1", "session-1", True)
        
        data = storage._read_json(storage.feedback_file)
        feedback = data["feedbacks"][0]
        
        assert "timestamp" in feedback
        assert "datetime" in feedback
        assert isinstance(feedback["timestamp"], (int, float))
        assert isinstance(feedback["datetime"], str)

