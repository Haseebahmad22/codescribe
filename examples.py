"""
Example usage scripts for CodeScribe.
"""
import asyncio
import os
import sys

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))


async def example_basic_usage():
    """Example: Basic usage of CodeScribe engine"""
    print("=== Basic Usage Example ===")
    
    from core import CodeScribeEngine
    
    # Sample Python code
    sample_code = '''
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self, initial_value: int = 0):
        self.value = initial_value
    
    def add(self, number: int) -> int:
        self.value += number
        return self.value
'''
    
    # Create a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        temp_file = f.name
    
    try:
        # Initialize engine
        engine = CodeScribeEngine()
        
        # Process the file
        print("Processing code...")
        documentation = await engine.process_file(temp_file)
        
        print(f"Found {len(documentation)} code elements:")
        for doc in documentation:
            element = doc.element
            print(f"- {element.type}: {element.name}")
            print(f"  Signature: {element.signature}")
            if doc.docstring:
                print(f"  Documentation: {doc.docstring[:100]}...")
            print()
        
        # Export to markdown
        print("Exporting to markdown...")
        markdown_output = engine.export_documentation({temp_file: documentation}, "markdown")
        print("Markdown output generated successfully!")
        
    finally:
        # Clean up
        os.unlink(temp_file)


async def example_configuration():
    """Example: Using custom configuration"""
    print("=== Configuration Example ===")
    
    from config_manager import ConfigurationManager, CodeScribeConfig, AIProviderConfig, DocumentationConfig
    
    # Create custom configuration
    config_manager = ConfigurationManager()
    
    # Update configuration
    config_manager.update_config({
        'documentation': {
            'verbosity': 'high',
            'style': 'numpy',
            'include_examples': True
        }
    })
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        print("Configuration issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Configuration is valid!")
    
    # Display configuration summary
    summary = config_manager.get_config_summary()
    print("Configuration summary:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


def example_cli_usage():
    """Example: CLI usage patterns"""
    print("=== CLI Usage Examples ===")
    
    examples = [
        "# Document a single Python file",
        "python backend/src/cli/main.py --path ./example.py --language python --output md",
        "",
        "# Document an entire project with high verbosity",
        "python backend/src/cli/main.py --path ./my_project --recursive --verbosity high --output html",
        "",
        "# Use custom configuration file",
        "python backend/src/cli/main.py --path ./src --config ./my_config.yaml",
        "",
        "# Use Hugging Face provider instead of OpenAI",
        "python backend/src/cli/main.py --path ./code --provider huggingface --model microsoft/CodeBERT-base",
        "",
        "# Dry run to see what would be processed",
        "python backend/src/cli/main.py --path ./project --dry-run",
        "",
        "# Generate inline documentation",
        "python backend/src/cli/main.py --path ./app.py --output inline",
        "",
        "# Save output to specific file",
        "python backend/src/cli/main.py --path ./src --output md --output-file ./docs/api.md"
    ]
    
    for example in examples:
        print(example)


def example_api_usage():
    """Example: API usage with curl commands"""
    print("=== API Usage Examples ===")
    
    examples = [
        "# Start the API server",
        "cd backend/src/api && python main.py",
        "",
        "# Check API health",
        "curl http://localhost:8000/health",
        "",
        "# Get API configuration",
        "curl http://localhost:8000/config",
        "",
        "# Document code snippet",
        'curl -X POST "http://localhost:8000/document/code" \\',
        '     -H "Content-Type: application/json" \\',
        '     -d \'{"code": "def hello(): return \\"Hello\\"", "language": "python"}\'',
        "",
        "# Upload and document a file",
        'curl -X POST "http://localhost:8000/document/file" \\',
        '     -F "file=@example.py" \\',
        '     -F "verbosity=high" \\',
        '     -F "output_format=markdown"',
        "",
        "# Start batch processing",
        'curl -X POST "http://localhost:8000/document/batch" \\',
        '     -F "files=@file1.py" \\',
        '     -F "files=@file2.js" \\',
        '     -F "verbosity=medium"'
    ]
    
    for example in examples:
        print(example)


def example_frontend_usage():
    """Example: Frontend usage"""
    print("=== Frontend Usage Examples ===")
    
    examples = [
        "# Start the Streamlit frontend",
        "cd frontend && streamlit run app.py",
        "",
        "# The web interface will be available at:",
        "# http://localhost:8501",
        "",
        "Features available in the web interface:",
        "- Code Input: Paste code directly for documentation",
        "- File Upload: Upload single files for processing",
        "- Batch Processing: Upload multiple files or ZIP archives",
        "- Configuration: Adjust AI provider, model, and documentation settings",
        "- Real-time Preview: See generated documentation immediately",
        "- Download Options: Get documentation in Markdown or HTML format"
    ]
    
    for example in examples:
        print(example)


async def example_parser_usage():
    """Example: Using parsers directly"""
    print("=== Parser Usage Example ===")
    
    from parsers import ParserFactory
    from parsers.python_parser import PythonParser
    
    # Sample code
    python_code = '''
class DataProcessor:
    """Process and analyze data."""
    
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = []
    
    def process(self, data: list) -> list:
        """Process raw data."""
        self.processed_data = [item.upper() for item in data if item]
        return self.processed_data
'''
    
    # Create parser
    parser = PythonParser()
    
    # Parse code
    elements = parser.parse_code(python_code)
    
    print(f"Found {len(elements)} code elements:")
    for element in elements:
        print(f"- {element.type}: {element.name}")
        print(f"  Line {element.start_line}-{element.end_line}")
        print(f"  Signature: {element.signature}")
        if element.parameters:
            print(f"  Parameters: {[p['name'] for p in element.parameters]}")
        if element.docstring:
            print(f"  Existing docstring: {element.docstring}")
        print()


def main():
    """Run all examples"""
    print("CodeScribe Usage Examples")
    print("=" * 50)
    
    # Run async examples
    asyncio.run(example_basic_usage())
    print()
    
    asyncio.run(example_configuration())
    print()
    
    asyncio.run(example_parser_usage())
    print()
    
    # Run sync examples
    example_cli_usage()
    print()
    
    example_api_usage()
    print()
    
    example_frontend_usage()
    print()
    
    print("For more information, see the README.md and documentation files.")


if __name__ == "__main__":
    main()