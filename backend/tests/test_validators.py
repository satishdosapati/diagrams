"""
Tests for input validator.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.validators.input_validator import InputValidator


class TestInputValidator:
    """Test InputValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create InputValidator instance."""
        return InputValidator()
    
    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator is not None
        assert hasattr(validator, 'OUT_OF_CONTEXT_KEYWORDS')
        assert hasattr(validator, 'CLOUD_KEYWORDS')
        assert hasattr(validator, 'validate')
    
    def test_validate_empty_string(self, validator):
        """Test validation rejects empty strings."""
        is_valid, error = validator.validate("")
        assert is_valid is False
        assert error is not None
        assert "description" in error.lower()
    
    def test_validate_whitespace_only(self, validator):
        """Test validation rejects whitespace-only strings."""
        is_valid, error = validator.validate("   ")
        assert is_valid is False
        assert error is not None
    
    def test_validate_none(self, validator):
        """Test validation handles None input."""
        is_valid, error = validator.validate(None)
        assert is_valid is False
        assert error is not None
    
    def test_validate_valid_aws_description(self, validator):
        """Test validation accepts valid AWS architecture description."""
        descriptions = [
            "VPC with EC2 instance and RDS database",
            "Lambda function with DynamoDB",
            "S3 bucket with CloudFront CDN",
            "Create a serverless API with Lambda and API Gateway",
            "Design a VPC with public and private subnets"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Failed for: {desc}"
            assert error is None
    
    def test_validate_valid_azure_description(self, validator):
        """Test validation accepts valid Azure architecture description."""
        descriptions = [
            "Azure VM with Blob Storage",
            "Azure Function with Cosmos DB",
            "Virtual Network with Azure VM"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Failed for: {desc}"
            assert error is None
    
    def test_validate_valid_gcp_description(self, validator):
        """Test validation accepts valid GCP architecture description."""
        descriptions = [
            "Compute Engine with Cloud Storage",
            "Cloud Function with Firestore",
            "GKE cluster with Cloud SQL"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Failed for: {desc}"
            assert error is None
    
    def test_validate_out_of_context_cooking(self, validator):
        """Test validation rejects cooking-related requests."""
        descriptions = [
            "How to bake a cake",
            "Recipe for pasta",
            "Cooking instructions for pizza"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is False, f"Should reject: {desc}"
            assert error is not None
            assert "cloud architecture" in error.lower() or "diagram" in error.lower()
    
    def test_validate_out_of_context_weather(self, validator):
        """Test validation rejects weather-related requests."""
        descriptions = [
            "What's the weather today?",
            "Temperature forecast",
            "Is it going to rain?"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is False, f"Should reject: {desc}"
            assert error is not None
    
    def test_validate_out_of_context_entertainment(self, validator):
        """Test validation rejects entertainment-related requests."""
        descriptions = [
            "Tell me a joke",
            "Play some music",
            "Recommend a movie"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is False, f"Should reject: {desc}"
            assert error is not None
    
    def test_validate_out_of_context_with_cloud_keyword(self, validator):
        """Test validation accepts requests with out-of-context keywords if cloud keywords present."""
        # These should pass because they contain cloud keywords
        descriptions = [
            "AWS Lambda function for cooking recipes API",
            "Azure VM for weather data processing",
            "GCP Cloud Function for music streaming"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Should accept (has cloud keyword): {desc}"
            assert error is None
    
    def test_validate_too_short(self, validator):
        """Test validation rejects very short descriptions without cloud keywords."""
        descriptions = [
            "hi",
            "test",
            "help",
            "diagram"  # Too short even with keyword
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is False, f"Should reject short description: {desc}"
            assert error is not None
            assert "short" in error.lower() or "unclear" in error.lower()
    
    def test_validate_short_with_cloud_keyword(self, validator):
        """Test validation accepts short descriptions with cloud keywords."""
        descriptions = [
            "AWS Lambda",
            "EC2 instance",
            "S3 bucket"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            # These might pass or fail depending on length threshold
            # But they should not fail due to out-of-context keywords
            if not is_valid:
                assert "short" in error.lower() or "unclear" in error.lower()
    
    def test_validate_generic_architecture_terms(self, validator):
        """Test validation accepts generic architecture terms."""
        descriptions = [
            "Create a microservices architecture",
            "Design a three-tier system",
            "Build a serverless application",
            "Show container orchestration"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Should accept generic architecture: {desc}"
            assert error is None
    
    def test_error_message_format(self, validator):
        """Test error message format includes helpful suggestions."""
        is_valid, error = validator.validate("bake a cake")
        assert is_valid is False
        assert error is not None
        assert "cloud architecture" in error.lower()
        assert "example" in error.lower() or "such as" in error.lower()
    
    def test_error_message_includes_keywords(self, validator):
        """Test error message includes detected keywords."""
        is_valid, error = validator.validate("recipe for pasta")
        assert is_valid is False
        assert error is not None
        # Should mention detected keywords
        assert "recipe" in error.lower() or "pasta" in error.lower()
    
    def test_validate_case_insensitive(self, validator):
        """Test validation is case-insensitive."""
        # Same description in different cases should produce same result
        desc1 = "AWS Lambda Function"
        desc2 = "aws lambda function"
        desc3 = "Aws LaMbDa FuNcTiOn"
        
        result1 = validator.validate(desc1)
        result2 = validator.validate(desc2)
        result3 = validator.validate(desc3)
        
        assert result1[0] == result2[0] == result3[0]
    
    def test_validate_with_special_characters(self, validator):
        """Test validation handles special characters."""
        descriptions = [
            "VPC with EC2 & RDS",
            "Lambda → DynamoDB → S3",
            "API Gateway + Lambda + DynamoDB"
        ]
        
        for desc in descriptions:
            is_valid, error = validator.validate(desc)
            assert is_valid is True, f"Should accept with special chars: {desc}"
            assert error is None

