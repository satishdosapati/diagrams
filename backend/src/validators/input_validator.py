"""
Input Validator - Validates user input before processing.
Rejects out-of-context inputs early to prevent nonsensical diagrams.
"""
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates user input before processing."""
    
    # Out-of-context keywords that indicate non-cloud architecture requests
    OUT_OF_CONTEXT_KEYWORDS = [
        # Cooking/Food
        "bake", "cake", "cook", "recipe", "food", "cooking", "kitchen",
        "pasta", "pizza", "restaurant", "meal", "dinner", "breakfast",
        "ingredient", "flour", "sugar", "oven", "stove",
        
        # Weather
        "weather", "temperature", "rain", "sunny", "cloudy", "snow",
        "forecast", "humidity", "wind", "storm",
        
        # Entertainment
        "joke", "funny", "laugh", "comedy", "movie", "film", "cinema",
        "music", "song", "album", "artist", "concert",
        
        # General non-technical
        "poem", "story", "book", "novel", "author",
        "sport", "game", "play", "team", "player",
        "travel", "vacation", "hotel", "flight",
        "shopping", "store", "buy", "purchase",
        "health", "doctor", "medicine", "hospital",
        "school", "teacher", "student", "class",
        "pet", "dog", "cat", "animal",
    ]
    
    # Cloud-related keywords that indicate valid architecture requests
    CLOUD_KEYWORDS = [
        # Providers
        "aws", "amazon", "azure", "microsoft", "gcp", "google cloud",
        
        # Services (AWS)
        "lambda", "ec2", "s3", "rds", "dynamodb", "vpc", "subnet",
        "alb", "elb", "api gateway", "cloudfront", "route53",
        "ecs", "eks", "fargate", "sns", "sqs", "eventbridge",
        "aurora", "redshift", "elasticache", "efs", "ebs",
        "iam", "kms", "secrets manager", "cognito",
        
        # Services (Azure)
        "azure function", "azure vm", "blob storage", "cosmos db",
        "azure sql", "app service", "kubernetes service",
        
        # Services (GCP)
        "cloud function", "compute engine", "cloud storage", "cloud sql",
        "cloud run", "gke", "bigquery", "firestore",
        
        # Architecture terms
        "architecture", "diagram", "infrastructure", "deployment",
        "serverless", "microservices", "monolith", "container",
        "kubernetes", "docker", "orchestration",
        
        # Technical terms
        "api", "rest", "graphql", "database", "storage", "compute",
        "network", "security", "authentication", "authorization",
        "load balancer", "cdn", "dns", "vpn", "firewall",
        "data pipeline", "etl", "analytics", "machine learning",
        "iot", "edge", "hybrid", "multi-cloud",
        
        # General cloud terms
        "cloud", "server", "service", "application", "app",
        "backend", "frontend", "fullstack",
        "scalable", "high availability", "disaster recovery",
        "monitoring", "logging", "metrics", "alerting",
    ]
    
    def validate(self, description: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if input is relevant to cloud architecture.
        
        Args:
            description: User input description
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if input is valid, False otherwise
            - error_message: Error message if invalid, None if valid
        """
        if not description or not description.strip():
            return False, "Please provide a description of the architecture you want to create."
        
        description_lower = description.lower()
        
        # Check for out-of-context keywords
        has_out_of_context = any(
            keyword in description_lower 
            for keyword in self.OUT_OF_CONTEXT_KEYWORDS
        )
        
        # Check for cloud-related keywords
        has_cloud_keywords = any(
            keyword in description_lower 
            for keyword in self.CLOUD_KEYWORDS
        )
        
        # If has out-of-context keywords AND no cloud keywords, reject
        if has_out_of_context and not has_cloud_keywords:
            # Find which out-of-context keywords were found
            found_keywords = [
                keyword for keyword in self.OUT_OF_CONTEXT_KEYWORDS
                if keyword in description_lower
            ]
            
            error_message = self._build_error_message(found_keywords[:3])
            logger.info(f"Rejected out-of-context input: {description[:50]}...")
            return False, error_message
        
        # If no cloud keywords at all, might still be valid (generic architecture terms)
        # But if it's very short and has no technical terms, warn
        if len(description.strip()) < 10 and not has_cloud_keywords:
            return False, (
                "Your request seems too short or unclear. "
                "Please provide more details about the cloud architecture you want to create."
            )
        
        return True, None
    
    def _build_error_message(self, found_keywords: list[str]) -> str:
        """Build helpful error message with suggestions."""
        error_parts = [
            "I can only help you create cloud architecture diagrams. "
            "Your request doesn't seem to be related to cloud architecture."
        ]
        
        if found_keywords:
            error_parts.append(f"\n\nDetected keywords: {', '.join(found_keywords)}")
        
        error_parts.append(
            "\n\nPlease provide a description of a cloud architecture, such as:\n"
            "- 'Create a serverless API with Lambda and DynamoDB'\n"
            "- 'Design a VPC with public and private subnets'\n"
            "- 'Show a three-tier architecture with ALB, EC2, and RDS'\n"
            "- 'Build a data pipeline with S3, Glue, and Athena'\n"
            "- 'Create a microservices architecture with ECS and RDS'\n\n"
            "If you're trying to create a diagram, please rephrase your request "
            "to include cloud services or architecture components."
        )
        
        return "".join(error_parts)

