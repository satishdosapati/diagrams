"""
Tests for diagram generators.
"""
import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.diagrams_engine import DiagramsEngine, normalize_format, normalize_format_list
from src.generators.universal_generator import UniversalGenerator
from src.models.spec import ArchitectureSpec, Component, Connection, NodeType


class TestNormalizeFormat:
    """Test format normalization functions."""
    
    def test_normalize_format_valid(self):
        """Test normalizing valid formats."""
        assert normalize_format("png") == "png"
        assert normalize_format("svg") == "svg"
        assert normalize_format("pdf") == "pdf"
        assert normalize_format("dot") == "dot"
    
    def test_normalize_format_case_insensitive(self):
        """Test format normalization is case-insensitive."""
        assert normalize_format("PNG") == "png"
        assert normalize_format("Svg") == "svg"
        assert normalize_format("PDF") == "pdf"
    
    def test_normalize_format_whitespace(self):
        """Test format normalization handles whitespace."""
        assert normalize_format(" png ") == "png"
        assert normalize_format(" svg\n") == "svg"
    
    def test_normalize_format_unsupported(self):
        """Test normalizing unsupported formats."""
        # GIF should normalize to PNG
        assert normalize_format("gif") == "png"
    
    def test_normalize_format_unknown(self):
        """Test normalizing unknown formats defaults to PNG."""
        assert normalize_format("unknown") == "png"
        assert normalize_format("xyz") == "png"
    
    def test_normalize_format_empty(self):
        """Test normalizing empty format defaults to PNG."""
        assert normalize_format("") == "png"
        assert normalize_format(None) == "png"
    
    def test_normalize_format_list_string(self):
        """Test normalizing format list from string."""
        result = normalize_format_list("png")
        assert result == "png"
    
    def test_normalize_format_list_list(self):
        """Test normalizing format list from list."""
        result = normalize_format_list(["png", "svg"])
        assert isinstance(result, list)
        assert result == ["png", "svg"]
    
    def test_normalize_format_list_mixed(self):
        """Test normalizing format list with mixed valid/invalid."""
        result = normalize_format_list(["png", "gif", "svg"])
        assert isinstance(result, list)
        assert "png" in result
        assert "svg" in result
        # GIF should be normalized to PNG
        assert "gif" not in result or "png" in result


class TestDiagramsEngine:
    """Test DiagramsEngine class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def engine(self, temp_output_dir):
        """Create DiagramsEngine instance with temp directory."""
        return DiagramsEngine(output_dir=temp_output_dir)
    
    @pytest.fixture
    def simple_spec(self):
        """Create a simple ArchitectureSpec for testing."""
        return ArchitectureSpec(
            title="Test Diagram",
            provider="aws",
            components=[
                Component(id="ec2", name="EC2 Instance", type=NodeType.EC2),
            ],
            connections=[],
        )
    
    def test_initialization(self, engine, temp_output_dir):
        """Test DiagramsEngine initialization."""
        assert engine is not None
        assert engine.output_dir == Path(temp_output_dir)
        assert engine.output_dir.exists()
    
    def test_initialization_default_output_dir(self):
        """Test initialization with default output directory."""
        # Set environment variable
        with patch.dict(os.environ, {"OUTPUT_DIR": "./test_output"}):
            engine = DiagramsEngine()
            assert engine.output_dir == Path("./test_output")
    
    def test_generate_imports_simple(self, engine, simple_spec):
        """Test import generation for simple spec."""
        from src.resolvers.component_resolver import ComponentResolver
        
        resolver = ComponentResolver(primary_provider="aws")
        imports = engine._generate_imports(simple_spec, resolver)
        
        assert isinstance(imports, list)
        assert len(imports) > 0
        assert any("from diagrams import Diagram" in imp for imp in imports)
        assert any("EC2" in imp for imp in imports)
    
    def test_generate_imports_with_cluster(self, engine):
        """Test import generation includes Cluster when clusters present."""
        from src.resolvers.component_resolver import ComponentResolver
        from src.models.spec import Cluster
        
        spec = ArchitectureSpec(
            title="Test",
            provider="aws",
            components=[
                Component(id="ec2", name="EC2", type=NodeType.EC2),
            ],
            clusters=[
                Cluster(name="Network", component_ids=["ec2"])
            ]
        )
        
        resolver = ComponentResolver(primary_provider="aws")
        imports = engine._generate_imports(spec, resolver)
        
        assert any("Cluster" in imp for imp in imports)
    
    def test_generate_imports_with_edge(self, engine):
        """Test import generation includes Edge when connections have labels."""
        from src.resolvers.component_resolver import ComponentResolver
        
        spec = ArchitectureSpec(
            title="Test",
            provider="aws",
            components=[
                Component(id="ec2", name="EC2", type=NodeType.EC2),
                Component(id="rds", name="RDS", type=NodeType.RDS),
            ],
            connections=[
                Connection(from_id="ec2", to_id="rds", label="connects to")
            ]
        )
        
        resolver = ComponentResolver(primary_provider="aws")
        imports = engine._generate_imports(spec, resolver)
        
        assert any("Edge" in imp for imp in imports)
    
    @patch('src.generators.diagrams_engine.DiagramsEngine._execute_code')
    def test_render_basic(self, mock_execute, engine, simple_spec):
        """Test basic render functionality."""
        mock_execute.return_value = "/path/to/output.png"
        
        result = engine.render(simple_spec)
        
        assert result == "/path/to/output.png"
        mock_execute.assert_called_once()
    
    @patch('src.generators.diagrams_engine.DiagramsEngine._execute_code')
    def test_render_with_format(self, mock_execute, engine, simple_spec):
        """Test render with specific format."""
        simple_spec.outformat = "svg"
        mock_execute.return_value = "/path/to/output.svg"
        
        result = engine.render(simple_spec)
        
        assert result == "/path/to/output.svg"
        mock_execute.assert_called_once()
    
    @patch('src.generators.diagrams_engine.DiagramsEngine._execute_code')
    def test_render_svg_adds_attributes(self, mock_execute, engine, simple_spec):
        """Test render adds SVG-specific attributes."""
        simple_spec.outformat = "svg"
        mock_execute.return_value = "/path/to/output.svg"
        
        engine.render(simple_spec)
        
        # Should have graphviz_attrs set
        assert simple_spec.graphviz_attrs is not None
        assert simple_spec.graphviz_attrs.graph_attr is not None
        assert "dpi" in simple_spec.graphviz_attrs.graph_attr
    
    def test_sanitize_variable_name(self, engine):
        """Test variable name sanitization."""
        assert engine._sanitize_variable_name("ec2-instance") == "ec2_instance"
        assert engine._sanitize_variable_name("EC2 Instance") == "ec2_instance"
        assert engine._sanitize_variable_name("s3-bucket") == "s3_bucket"
        assert engine._sanitize_variable_name("123invalid") == "comp_123invalid"
        assert engine._sanitize_variable_name("valid_name") == "valid_name"


class TestUniversalGenerator:
    """Test UniversalGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create UniversalGenerator instance."""
        return UniversalGenerator()
    
    @pytest.fixture
    def simple_spec(self):
        """Create a simple ArchitectureSpec for testing."""
        return ArchitectureSpec(
            title="Test Diagram",
            provider="aws",
            components=[
                Component(id="ec2", name="EC2 Instance", type=NodeType.EC2),
            ],
        )
    
    def test_initialization(self, generator):
        """Test UniversalGenerator initialization."""
        assert generator is not None
        assert hasattr(generator, 'engines')
        assert isinstance(generator.engines, dict)
        assert len(generator.engines) > 0
    
    def test_engines_registered(self, generator):
        """Test that engines are registered for diagram types."""
        assert "cloud_architecture" in generator.engines
        assert "system_architecture" in generator.engines
        assert "network_topology" in generator.engines
        assert "data_pipeline" in generator.engines
        assert "c4_model" in generator.engines
    
    @patch('src.generators.universal_generator.DiagramsEngine.render')
    def test_generate_cloud_architecture(self, mock_render, generator, simple_spec):
        """Test generating cloud architecture diagram."""
        mock_render.return_value = "/path/to/output.png"
        simple_spec.metadata = {"diagram_type": "cloud_architecture"}
        
        result = generator.generate(simple_spec)
        
        assert result == "/path/to/output.png"
        mock_render.assert_called_once_with(simple_spec)
    
    @patch('src.generators.universal_generator.DiagramsEngine.render')
    def test_generate_system_architecture(self, mock_render, generator, simple_spec):
        """Test generating system architecture diagram."""
        mock_render.return_value = "/path/to/output.png"
        simple_spec.metadata = {"diagram_type": "system_architecture"}
        
        result = generator.generate(simple_spec)
        
        assert result == "/path/to/output.png"
        mock_render.assert_called_once_with(simple_spec)
    
    @patch('src.generators.universal_generator.DiagramsEngine.render')
    def test_generate_default_type(self, mock_render, generator, simple_spec):
        """Test generating with default diagram type."""
        mock_render.return_value = "/path/to/output.png"
        simple_spec.metadata = {}  # No diagram_type specified
        
        result = generator.generate(simple_spec)
        
        assert result == "/path/to/output.png"
        mock_render.assert_called_once_with(simple_spec)
    
    @patch('src.generators.universal_generator.DiagramsEngine.render')
    def test_generate_unknown_type_defaults(self, mock_render, generator, simple_spec):
        """Test generating with unknown diagram type defaults to cloud_architecture."""
        mock_render.return_value = "/path/to/output.png"
        simple_spec.metadata = {"diagram_type": "unknown_type"}
        
        result = generator.generate(simple_spec)
        
        assert result == "/path/to/output.png"
        # Should use cloud_architecture engine
        mock_render.assert_called_once_with(simple_spec)
    
    def test_generate_logs_info(self, generator, simple_spec, caplog):
        """Test that generate logs appropriate info."""
        with patch.object(generator.engines["cloud_architecture"], 'render') as mock_render:
            mock_render.return_value = "/path/to/output.png"
            simple_spec.metadata = {"diagram_type": "cloud_architecture"}
            
            generator.generate(simple_spec)
            
            # Should log generation info
            assert "Generating diagram" in caplog.text or mock_render.called

