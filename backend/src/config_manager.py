"""
Configuration management for CodeScribe.
"""
import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class AIProviderConfig:
    """AI provider configuration"""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.3


@dataclass
class DocumentationConfig:
    """Documentation generation configuration"""
    default_language: str = "python"
    output_format: str = "markdown"
    verbosity: str = "medium"
    style: str = "google"
    include_examples: bool = True
    include_parameters: bool = True
    include_return_values: bool = True
    include_exceptions: bool = True


@dataclass
class ProcessingConfig:
    """Processing configuration"""
    batch_size: int = 10
    max_file_size_mb: int = 5
    skip_files: List[str] = None
    supported_extensions: List[str] = None
    
    def __post_init__(self):
        if self.skip_files is None:
            self.skip_files = ['*.pyc', '*.min.js', 'node_modules/*', '__pycache__/*']
        if self.supported_extensions is None:
            self.supported_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "localhost"
    port: int = 8000
    cors_origins: List[str] = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:8501"]


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/codescribe.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class CodeScribeConfig:
    """Main CodeScribe configuration"""
    ai: AIProviderConfig = None
    documentation: DocumentationConfig = None
    processing: ProcessingConfig = None
    api: APIConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.ai is None:
            self.ai = AIProviderConfig()
        if self.documentation is None:
            self.documentation = DocumentationConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigurationManager:
    """Manages CodeScribe configuration"""
    
    DEFAULT_CONFIG_PATHS = [
        "config.yaml",
        "codescribe.yaml",
        "~/.codescribe/config.yaml",
        "/etc/codescribe/config.yaml"
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> CodeScribeConfig:
        """Load configuration from file or environment"""
        config_data = {}
        
        # Try to load from file
        if self.config_path:
            config_data = self._load_from_file(self.config_path)
        else:
            # Try default paths
            for path in self.DEFAULT_CONFIG_PATHS:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    config_data = self._load_from_file(expanded_path)
                    self.config_path = expanded_path
                    break
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Create configuration objects
        return self._create_config_objects(config_data)
    
    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            print(f"Warning: Could not load config from {file_path}: {e}")
            return {}
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables"""
        env_mappings = {
            'OPENAI_API_KEY': ['ai', 'api_key'],
            'CODESCRIBE_AI_PROVIDER': ['ai', 'provider'],
            'CODESCRIBE_AI_MODEL': ['ai', 'model'],
            'CODESCRIBE_VERBOSITY': ['documentation', 'verbosity'],
            'CODESCRIBE_STYLE': ['documentation', 'style'],
            'CODESCRIBE_OUTPUT_FORMAT': ['documentation', 'output_format'],
            'CODESCRIBE_API_HOST': ['api', 'host'],
            'CODESCRIBE_API_PORT': ['api', 'port'],
            'CODESCRIBE_LOG_LEVEL': ['logging', 'level'],
            'CODESCRIBE_BATCH_SIZE': ['processing', 'batch_size'],
            'CODESCRIBE_MAX_FILE_SIZE': ['processing', 'max_file_size_mb']
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the correct nested dictionary
                current = config_data
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                if final_key in ['port', 'batch_size', 'max_file_size_mb']:
                    current[final_key] = int(value)
                elif final_key in ['temperature']:
                    current[final_key] = float(value)
                elif final_key in ['include_examples', 'include_parameters', 'include_return_values', 'include_exceptions']:
                    current[final_key] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    current[final_key] = value
        
        return config_data
    
    def _create_config_objects(self, config_data: Dict[str, Any]) -> CodeScribeConfig:
        """Create configuration objects from data"""
        # AI configuration
        ai_data = config_data.get('ai', {})
        ai_config = AIProviderConfig(
            provider=ai_data.get('provider', 'openai'),
            api_key=ai_data.get('api_key', os.getenv('OPENAI_API_KEY', '')),
            model=ai_data.get('model', 'gpt-3.5-turbo'),
            max_tokens=ai_data.get('max_tokens', 1000),
            temperature=ai_data.get('temperature', 0.3)
        )
        
        # Documentation configuration
        doc_data = config_data.get('documentation', {})
        doc_config = DocumentationConfig(
            default_language=doc_data.get('default_language', 'python'),
            output_format=doc_data.get('output_format', 'markdown'),
            verbosity=doc_data.get('verbosity', 'medium'),
            style=doc_data.get('style', 'google'),
            include_examples=doc_data.get('include_examples', True),
            include_parameters=doc_data.get('include_parameters', True),
            include_return_values=doc_data.get('include_return_values', True),
            include_exceptions=doc_data.get('include_exceptions', True)
        )
        
        # Processing configuration
        proc_data = config_data.get('processing', {})
        proc_config = ProcessingConfig(
            batch_size=proc_data.get('batch_size', 10),
            max_file_size_mb=proc_data.get('max_file_size_mb', 5),
            skip_files=proc_data.get('skip_files'),
            supported_extensions=proc_data.get('supported_extensions')
        )
        
        # API configuration
        api_data = config_data.get('api', {})
        api_config = APIConfig(
            host=api_data.get('host', 'localhost'),
            port=api_data.get('port', 8000),
            cors_origins=api_data.get('cors_origins')
        )
        
        # Logging configuration
        log_data = config_data.get('logging', {})
        log_config = LoggingConfig(
            level=log_data.get('level', 'INFO'),
            file=log_data.get('file', 'logs/codescribe.log'),
            format=log_data.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        return CodeScribeConfig(
            ai=ai_config,
            documentation=doc_config,
            processing=proc_config,
            api=api_config,
            logging=log_config
        )
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        if file_path is None:
            file_path = self.config_path or "config.yaml"
        
        try:
            # Convert config to dictionary
            config_dict = asdict(self.config)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(config_dict, file, default_flow_style=False, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving config to {file_path}: {e}")
            return False
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        for key, value in updates.items():
            if hasattr(self.config, key):
                if isinstance(getattr(self.config, key), (AIProviderConfig, DocumentationConfig, ProcessingConfig, APIConfig, LoggingConfig)):
                    # Update nested configuration
                    nested_config = getattr(self.config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self.config, key, value)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate AI configuration
        if self.config.ai.provider == "openai" and not self.config.ai.api_key:
            issues.append("OpenAI API key is required when using OpenAI provider")
        
        if self.config.ai.max_tokens <= 0:
            issues.append("max_tokens must be greater than 0")
        
        if not 0 <= self.config.ai.temperature <= 2:
            issues.append("temperature must be between 0 and 2")
        
        # Validate documentation configuration
        valid_verbosity = ["low", "medium", "high"]
        if self.config.documentation.verbosity not in valid_verbosity:
            issues.append(f"verbosity must be one of: {valid_verbosity}")
        
        valid_formats = ["markdown", "html", "inline"]
        if self.config.documentation.output_format not in valid_formats:
            issues.append(f"output_format must be one of: {valid_formats}")
        
        # Validate processing configuration
        if self.config.processing.batch_size <= 0:
            issues.append("batch_size must be greater than 0")
        
        if self.config.processing.max_file_size_mb <= 0:
            issues.append("max_file_size_mb must be greater than 0")
        
        # Validate API configuration
        if not 1 <= self.config.api.port <= 65535:
            issues.append("API port must be between 1 and 65535")
        
        return issues
    
    def create_template_config(self, file_path: str) -> bool:
        """Create a template configuration file"""
        template_config = CodeScribeConfig()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("# CodeScribe Configuration Template\n")
                file.write("# Copy this file to config.yaml and customize as needed\n\n")
                yaml.dump(asdict(template_config), file, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"Error creating template config: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "config_file": self.config_path,
            "ai_provider": self.config.ai.provider,
            "ai_model": self.config.ai.model,
            "documentation_style": self.config.documentation.style,
            "output_format": self.config.documentation.output_format,
            "verbosity": self.config.documentation.verbosity,
            "batch_size": self.config.processing.batch_size,
            "api_port": self.config.api.port,
            "log_level": self.config.logging.level
        }