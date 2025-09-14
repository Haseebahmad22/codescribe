"""
Core CodeScribe engine for processing and documenting code.
"""
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml

from .parsers import ParserFactory
from .generators import GeneratorFactory, DocumentationConfig
from .parsers.base import CodeElement
from .generators.base import GeneratedDocumentation


class CodeScribeEngine:
    """Main engine for processing code and generating documentation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.doc_generator = None
        self._initialize_generator()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'ai': {
                'provider': 'openai',
                'openai': {
                    'api_key': os.getenv('OPENAI_API_KEY', ''),
                    'model': 'gpt-3.5-turbo',
                    'max_tokens': 1000,
                    'temperature': 0.3
                }
            },
            'documentation': {
                'default_language': 'python',
                'output_format': 'markdown',
                'verbosity': 'medium',
                'include_examples': True,
                'include_parameters': True,
                'include_return_values': True,
                'include_exceptions': True
            },
            'processing': {
                'batch_size': 10,
                'max_file_size_mb': 5,
                'skip_files': ['*.pyc', '*.min.js', 'node_modules/*', '__pycache__/*'],
                'supported_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx']
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    loaded_config = yaml.safe_load(file)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return default_config
    
    def _initialize_generator(self):
        """Initialize the documentation generator"""
        doc_config = DocumentationConfig(
            style=self.config['documentation'].get('style', 'google'),
            verbosity=self.config['documentation']['verbosity'],
            include_examples=self.config['documentation']['include_examples'],
            include_parameters=self.config['documentation']['include_parameters'],
            include_return_values=self.config['documentation']['include_return_values'],
            include_exceptions=self.config['documentation']['include_exceptions'],
            max_tokens=self.config['ai']['openai']['max_tokens'],
            temperature=self.config['ai']['openai']['temperature']
        )
        
        provider = self.config['ai']['provider']
        
        try:
            if provider == 'openai':
                api_key = self.config['ai']['openai']['api_key']
                model = self.config['ai']['openai']['model']
                self.doc_generator = GeneratorFactory.create_generator(
                    provider, doc_config, api_key=api_key, model=model
                )
            elif provider == 'huggingface':
                model = self.config['ai'].get('huggingface', {}).get('model', 'microsoft/DialoGPT-medium')
                self.doc_generator = GeneratorFactory.create_generator(
                    provider, doc_config, model=model
                )
        except Exception as e:
            print(f"Error initializing documentation generator: {e}")
            self.doc_generator = None
    
    async def process_file(self, file_path: str, language: Optional[str] = None) -> List[GeneratedDocumentation]:
        """Process a single file and generate documentation"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.config['processing']['max_file_size_mb']:
            raise ValueError(f"File too large: {file_size_mb:.2f}MB > {self.config['processing']['max_file_size_mb']}MB")
        
        # Detect language if not provided
        if not language:
            ext = Path(file_path).suffix
            language = ParserFactory.detect_language_from_extension(ext)
            if not language:
                raise ValueError(f"Unsupported file extension: {ext}")
        
        # Create parser
        parser = ParserFactory.create_parser(language)
        if not parser:
            raise ValueError(f"No parser available for language: {language}")
        
        # Parse file
        elements = parser.parse_file(file_path)
        if not elements:
            return []
        
        # Read full file content for context
        with open(file_path, 'r', encoding='utf-8') as file:
            full_code = file.read()
        
        # Generate documentation for each element
        documentation = []
        
        if self.doc_generator:
            for element in elements:
                context = parser.extract_context(element, full_code)
                doc = await self.doc_generator.generate_documentation(element, context)
                documentation.append(doc)
        else:
            # Fallback to basic documentation
            for element in elements:
                doc = GeneratedDocumentation(
                    element=element,
                    docstring=f"TODO: Add documentation for {element.name}",
                    inline_comments=[],
                    summary=f"Summary for {element.name}",
                    examples=[],
                    metadata={}
                )
                documentation.append(doc)
        
        return documentation
    
    async def process_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, List[GeneratedDocumentation]]:
        """Process all supported files in a directory"""
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        supported_extensions = self.config['processing']['supported_extensions']
        skip_patterns = self.config['processing']['skip_files']
        
        # Find all supported files
        files_to_process = []
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                # Skip certain directories
                dirs[:] = [d for d in dirs if not any(d.startswith(pattern.replace('*', '')) for pattern in skip_patterns)]
                
                for file in files:
                    if any(file.endswith(ext) for ext in supported_extensions):
                        if not any(self._matches_pattern(file, pattern) for pattern in skip_patterns):
                            files_to_process.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    if any(file.endswith(ext) for ext in supported_extensions):
                        if not any(self._matches_pattern(file, pattern) for pattern in skip_patterns):
                            files_to_process.append(file_path)
        
        # Process files in batches
        batch_size = self.config['processing']['batch_size']
        results = {}
        
        for i in range(0, len(files_to_process), batch_size):
            batch = files_to_process[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for file_path in batch:
                task = self.process_file(file_path)
                tasks.append((file_path, task))
            
            # Wait for batch completion
            for file_path, task in tasks:
                try:
                    documentation = await task
                    results[file_path] = documentation
                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    results[file_path] = []
        
        return results
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a glob-like pattern"""
        if '*' in pattern:
            if pattern.startswith('*'):
                return filename.endswith(pattern[1:])
            elif pattern.endswith('*'):
                return filename.startswith(pattern[:-1])
            else:
                parts = pattern.split('*')
                return filename.startswith(parts[0]) and filename.endswith(parts[1])
        else:
            return filename == pattern
    
    def export_documentation(self, documentation: Dict[str, List[GeneratedDocumentation]], output_format: str = "markdown") -> str:
        """Export generated documentation to specified format"""
        if output_format.lower() == "markdown":
            return self._export_to_markdown(documentation)
        elif output_format.lower() == "html":
            return self._export_to_html(documentation)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _export_to_markdown(self, documentation: Dict[str, List[GeneratedDocumentation]]) -> str:
        """Export documentation to Markdown format"""
        output = []
        output.append("# CodeScribe Documentation\n")
        output.append(f"Generated using CodeScribe AI-Powered Code Documentation Assistant\n")
        output.append("---\n")
        
        for file_path, docs in documentation.items():
            if not docs:
                continue
                
            output.append(f"## File: `{file_path}`\n")
            
            for doc in docs:
                element = doc.element
                output.append(f"### {element.type.title()}: `{element.name}`\n")
                
                if element.signature:
                    output.append("**Signature:**\n")
                    output.append(f"```{self._get_language_from_signature(element.signature)}")
                    output.append(element.signature)
                    output.append("```\n")
                
                if doc.docstring:
                    output.append("**Documentation:**\n")
                    output.append(doc.docstring)
                    output.append("\n")
                
                if doc.summary:
                    output.append("**Summary:**\n")
                    output.append(doc.summary)
                    output.append("\n")
                
                if doc.inline_comments:
                    output.append("**Suggested Comments:**\n")
                    for comment in doc.inline_comments:
                        output.append(f"- {comment}")
                    output.append("\n")
                
                output.append("---\n")
        
        return '\n'.join(output)
    
    def _export_to_html(self, documentation: Dict[str, List[GeneratedDocumentation]]) -> str:
        """Export documentation to HTML format"""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html><head><title>CodeScribe Documentation</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        html.append("h1, h2, h3 { color: #333; }")
        html.append("pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }")
        html.append("code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }")
        html.append(".element { margin-bottom: 30px; border-left: 3px solid #007acc; padding-left: 20px; }")
        html.append("</style></head><body>")
        
        html.append("<h1>CodeScribe Documentation</h1>")
        html.append("<p>Generated using CodeScribe AI-Powered Code Documentation Assistant</p>")
        
        for file_path, docs in documentation.items():
            if not docs:
                continue
                
            html.append(f"<h2>File: <code>{file_path}</code></h2>")
            
            for doc in docs:
                element = doc.element
                html.append("<div class='element'>")
                html.append(f"<h3>{element.type.title()}: <code>{element.name}</code></h3>")
                
                if element.signature:
                    html.append("<h4>Signature:</h4>")
                    html.append(f"<pre><code>{element.signature}</code></pre>")
                
                if doc.docstring:
                    html.append("<h4>Documentation:</h4>")
                    html.append(f"<pre>{doc.docstring}</pre>")
                
                if doc.summary:
                    html.append("<h4>Summary:</h4>")
                    html.append(f"<p>{doc.summary}</p>")
                
                if doc.inline_comments:
                    html.append("<h4>Suggested Comments:</h4>")
                    html.append("<ul>")
                    for comment in doc.inline_comments:
                        html.append(f"<li>{comment}</li>")
                    html.append("</ul>")
                
                html.append("</div>")
        
        html.append("</body></html>")
        return '\n'.join(html)
    
    def _get_language_from_signature(self, signature: str) -> str:
        """Detect language from signature for syntax highlighting"""
        if signature.strip().startswith('def ') or signature.strip().startswith('class '):
            return 'python'
        elif signature.strip().startswith('function ') or signature.strip().startswith('class '):
            return 'javascript'
        else:
            return 'text'