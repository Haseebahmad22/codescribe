"""
Documentation generator factory and utilities.
"""
from typing import Optional, Dict, Any

from .base import BaseDocumentationGenerator, DocumentationConfig
from .openai_generator import OpenAIDocumentationGenerator
from .huggingface_generator import HuggingFaceDocumentationGenerator
from .deepseek_generator import DeepSeekDocumentationGenerator


class GeneratorFactory:
    """Factory for creating documentation generators"""
    
    @staticmethod
    def create_generator(
        provider: str, 
        config: DocumentationConfig, 
        **kwargs
    ) -> Optional[BaseDocumentationGenerator]:
        """Create a documentation generator based on provider"""
        
        if provider.lower() == "openai":
            api_key = kwargs.get("api_key")
            model = kwargs.get("model", "gpt-3.5-turbo")
            
            if not api_key:
                raise ValueError("OpenAI API key is required")
            
            return OpenAIDocumentationGenerator(config, api_key, model)
        
        elif provider.lower() == "deepseek":
            api_key = kwargs.get("api_key")
            model = kwargs.get("model", "deepseek-r1")
            base_url = kwargs.get("base_url", "https://api.deepseek.com")
            
            if not api_key:
                raise ValueError("DeepSeek API key is required")
            
            return DeepSeekDocumentationGenerator(config, api_key, model, base_url)
        
        elif provider.lower() == "huggingface":
            model_name = kwargs.get("model", "microsoft/DialoGPT-medium")
            return HuggingFaceDocumentationGenerator(config, model_name)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """Get information about available providers"""
        return {
            "openai": {
                "name": "OpenAI GPT",
                "description": "High-quality documentation using OpenAI GPT models",
                "requires_api_key": True,
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
                "cost": "API usage based"
            },
            "deepseek": {
                "name": "DeepSeek R1",
                "description": "Cost-effective high-quality documentation using DeepSeek R1",
                "requires_api_key": True,
                "models": ["deepseek-r1", "deepseek-chat"],
                "cost": "Very low cost API usage"
            },
            "huggingface": {
                "name": "Hugging Face Transformers",
                "description": "Free local models using Hugging Face Transformers",
                "requires_api_key": False,
                "models": ["microsoft/DialoGPT-medium", "microsoft/CodeBERT-base"],
                "cost": "Free (local compute)"
            }
        }