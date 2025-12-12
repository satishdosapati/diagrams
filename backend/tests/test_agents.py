"""
Tests for agent classes.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.classifier_agent import ClassifierAgent, DiagramClassification


class TestClassifierAgent:
    """Test ClassifierAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create ClassifierAgent instance."""
        # Mock the Bedrock model to avoid actual AWS calls
        with patch('src.agents.classifier_agent.BedrockModel'):
            with patch('src.agents.classifier_agent.Agent'):
                return ClassifierAgent()
    
    def test_initialization(self, agent):
        """Test ClassifierAgent initialization."""
        assert agent is not None
        assert hasattr(agent, 'agent')
    
    @patch('src.agents.classifier_agent.BedrockModel')
    @patch('src.agents.classifier_agent.Agent')
    def test_classify_cloud_architecture(self, mock_agent_class, mock_model_class):
        """Test classifying cloud architecture description."""
        # Mock the agent response
        mock_agent_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.structured_output = DiagramClassification(
            diagram_type="cloud_architecture",
            provider="aws",
            complexity="simple"
        )
        mock_agent_instance.return_value = mock_response
        mock_agent_class.return_value = mock_agent_instance
        
        agent = ClassifierAgent()
        result = agent.classify("AWS Lambda function with DynamoDB")
        
        assert result.diagram_type == "cloud_architecture"
        assert result.provider == "aws"
    
    @patch('src.agents.classifier_agent.BedrockModel')
    @patch('src.agents.classifier_agent.Agent')
    def test_classify_with_provider_hint(self, mock_agent_class, mock_model_class):
        """Test classifying with provider hint."""
        mock_agent_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.structured_output = DiagramClassification(
            diagram_type="cloud_architecture",
            provider="azure",  # Will be overridden
            complexity="medium"
        )
        mock_agent_instance.return_value = mock_response
        mock_agent_class.return_value = mock_agent_instance
        
        agent = ClassifierAgent()
        result = agent.classify("Virtual machine", provider_hint="azure")
        
        assert result.diagram_type == "cloud_architecture"
        assert result.provider == "azure"  # Should use hint
    
    @patch('src.agents.classifier_agent.BedrockModel')
    @patch('src.agents.classifier_agent.Agent')
    def test_classify_network_topology(self, mock_agent_class, mock_model_class):
        """Test classifying network topology description."""
        mock_agent_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.structured_output = DiagramClassification(
            diagram_type="network_topology",
            provider="aws",
            complexity="medium"
        )
        mock_agent_instance.return_value = mock_response
        mock_agent_class.return_value = mock_agent_instance
        
        agent = ClassifierAgent()
        result = agent.classify("VPC with public and private subnets")
        
        assert result.diagram_type == "network_topology"
    
    @patch('src.agents.classifier_agent.BedrockModel')
    @patch('src.agents.classifier_agent.Agent')
    def test_classify_data_pipeline(self, mock_agent_class, mock_model_class):
        """Test classifying data pipeline description."""
        mock_agent_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.structured_output = DiagramClassification(
            diagram_type="data_pipeline",
            provider="aws",
            complexity="complex"
        )
        mock_agent_instance.return_value = mock_response
        mock_agent_class.return_value = mock_agent_instance
        
        agent = ClassifierAgent()
        result = agent.classify("ETL pipeline with S3, Glue, and Athena")
        
        assert result.diagram_type == "data_pipeline"
    
    @patch('src.agents.classifier_agent.BedrockModel')
    @patch('src.agents.classifier_agent.Agent')
    def test_classify_system_architecture(self, mock_agent_class, mock_model_class):
        """Test classifying system architecture description."""
        mock_agent_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.structured_output = DiagramClassification(
            diagram_type="system_architecture",
            provider=None,
            complexity="medium"
        )
        mock_agent_instance.return_value = mock_response
        mock_agent_class.return_value = mock_agent_instance
        
        agent = ClassifierAgent()
        result = agent.classify("Microservices architecture with API gateway")
        
        assert result.diagram_type == "system_architecture"
    
    def test_classification_model_structure(self):
        """Test DiagramClassification model structure."""
        classification = DiagramClassification(
            diagram_type="cloud_architecture",
            provider="aws",
            complexity="simple"
        )
        
        assert classification.diagram_type == "cloud_architecture"
        assert classification.provider == "aws"
        assert classification.complexity == "simple"
    
    def test_classification_optional_provider(self):
        """Test DiagramClassification with optional provider."""
        classification = DiagramClassification(
            diagram_type="system_architecture",
            complexity="medium"
        )
        
        assert classification.diagram_type == "system_architecture"
        assert classification.provider is None
        assert classification.complexity == "medium"
    
    def test_classification_valid_types(self):
        """Test DiagramClassification accepts valid diagram types."""
        valid_types = [
            "cloud_architecture",
            "system_architecture",
            "network_topology",
            "data_pipeline",
            "c4_model"
        ]
        
        for diagram_type in valid_types:
            classification = DiagramClassification(
                diagram_type=diagram_type,
                complexity="simple"
            )
            assert classification.diagram_type == diagram_type
    
    def test_classification_valid_complexity(self):
        """Test DiagramClassification accepts valid complexity levels."""
        valid_complexities = ["simple", "medium", "complex"]
        
        for complexity in valid_complexities:
            classification = DiagramClassification(
                diagram_type="cloud_architecture",
                complexity=complexity
            )
            assert classification.complexity == complexity

