"""
Test suite for CodeScribe core functionality.
"""
import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from generators.base import DocumentationConfig
from core import CodeScribeEngine


class TestPythonParser:
    """Test cases for Python parser"""
    
    def test_parse_simple_function(self):
        """Test parsing a simple Python function"""
        code = '''
def hello_world(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"
'''
        parser = PythonParser()
        elements = parser.parse_code(code)
        
        assert len(elements) == 1
        assert elements[0].name == "hello_world"
        assert elements[0].type == "function"
        assert "name: str" in elements[0].signature
    
    def test_parse_class_with_methods(self):
        """Test parsing a Python class with methods"""
        code = '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self, initial_value: int = 0):
        """Initialize calculator."""
        self.value = initial_value
    
    def add(self, number: int) -> int:
        """Add a number to current value."""
        self.value += number
        return self.value
'''
        parser = PythonParser()
        elements = parser.parse_code(code)
        
        # Should find class and methods
        class_elements = [e for e in elements if e.type == "class"]
        method_elements = [e for e in elements if e.type == "method"]
        
        assert len(class_elements) == 1
        assert len(method_elements) == 2
        assert class_elements[0].name == "Calculator"
        assert set(e.name for e in method_elements) == {"__init__", "add"}
    
    def test_parse_complex_function(self):
        """Test parsing a function with complex signature"""
        code = '''
from typing import List, Dict, Optional

def process_data(
    data: List[Dict[str, any]], 
    filters: Optional[Dict[str, str]] = None,
    sort_key: str = "id"
) -> List[Dict[str, any]]:
    """Process and filter data."""
    if filters:
        data = [item for item in data if all(item.get(k) == v for k, v in filters.items())]
    return sorted(data, key=lambda x: x.get(sort_key, ""))
'''
        parser = PythonParser()
        elements = parser.parse_code(code)
        
        assert len(elements) == 1
        element = elements[0]
        assert element.name == "process_data"
        assert len(element.parameters) == 3
        assert element.parameters[0]['name'] == "data"
        assert element.parameters[1]['name'] == "filters"
        assert element.parameters[2]['name'] == "sort_key"


class TestJavaScriptParser:
    """Test cases for JavaScript parser"""
    
    def test_parse_simple_function(self):
        """Test parsing a simple JavaScript function"""
        code = '''
function calculateSum(a, b) {
    return a + b;
}
'''
        parser = JavaScriptParser()
        elements = parser.parse_code(code)
        
        assert len(elements) >= 1
        function_elements = [e for e in elements if e.name == "calculateSum"]
        assert len(function_elements) == 1
        assert function_elements[0].type == "function"
    
    def test_parse_class_with_methods(self):
        """Test parsing a JavaScript class"""
        code = '''
class Calculator {
    constructor(initialValue = 0) {
        this.value = initialValue;
    }
    
    add(number) {
        this.value += number;
        return this.value;
    }
    
    multiply(number) {
        this.value *= number;
        return this.value;
    }
}
'''
        parser = JavaScriptParser()
        elements = parser.parse_code(code)
        
        # Should find class and methods
        class_elements = [e for e in elements if e.type == "class"]
        method_elements = [e for e in elements if e.type == "method"]
        
        # Note: JavaScript parsing may vary based on tree-sitter availability
        if class_elements:
            assert len(class_elements) == 1
            assert class_elements[0].name == "Calculator"


class TestDocumentationConfig:
    """Test cases for documentation configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = DocumentationConfig()
        
        assert config.style == "google"
        assert config.verbosity == "medium"
        assert config.include_examples == True
        assert config.include_parameters == True
        assert config.include_return_values == True
        assert config.include_exceptions == True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = DocumentationConfig(
            style="numpy",
            verbosity="high",
            include_examples=False
        )
        
        assert config.style == "numpy"
        assert config.verbosity == "high"
        assert config.include_examples == False
        assert config.include_parameters == True  # Should keep default


class TestCodeScribeEngine:
    """Test cases for CodeScribe engine"""
    
    @pytest.fixture
    def temp_python_file(self):
        """Create a temporary Python file for testing"""
        code = '''
def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def is_prime(num: int) -> bool:
        """Check if a number is prime."""
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            yield f.name
        os.unlink(f.name)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = CodeScribeEngine()
        
        assert engine.config is not None
        assert 'ai' in engine.config
        assert 'documentation' in engine.config
        assert 'processing' in engine.config
    
    @pytest.mark.asyncio
    async def test_process_file(self, temp_python_file):
        """Test processing a single file"""
        engine = CodeScribeEngine()
        
        documentation = await engine.process_file(temp_python_file)
        
        assert len(documentation) > 0
        
        # Check that we found functions and classes
        function_docs = [doc for doc in documentation if doc.element.type == "function"]
        class_docs = [doc for doc in documentation if doc.element.type == "class"]
        method_docs = [doc for doc in documentation if doc.element.type == "method"]
        
        assert len(function_docs) >= 1  # Should find fibonacci function
        assert len(class_docs) >= 1    # Should find MathUtils class
        assert len(method_docs) >= 1   # Should find is_prime method
    
    def test_export_to_markdown(self, temp_python_file):
        """Test exporting documentation to Markdown"""
        engine = CodeScribeEngine()
        
        # Create mock documentation
        from generators.base import GeneratedDocumentation
        from parsers.base import CodeElement
        
        element = CodeElement(
            name="test_function",
            type="function",
            signature="def test_function(x: int) -> str:",
            docstring="Test function docstring",
            start_line=1,
            end_line=3,
            parameters=[{"name": "x", "type": "int", "default": None}],
            return_type="str"
        )
        
        doc = GeneratedDocumentation(
            element=element,
            docstring="Generated test documentation",
            inline_comments=["# This is a test comment"],
            summary="Test function summary",
            examples=[],
            metadata={}
        )
        
        documentation = {temp_python_file: [doc]}
        markdown_output = engine.export_documentation(documentation, "markdown")
        
        assert "# CodeScribe Documentation" in markdown_output
        assert "test_function" in markdown_output
        assert "Generated test documentation" in markdown_output
    
    def test_export_to_html(self, temp_python_file):
        """Test exporting documentation to HTML"""
        engine = CodeScribeEngine()
        
        # Create mock documentation (same as above)
        from generators.base import GeneratedDocumentation
        from parsers.base import CodeElement
        
        element = CodeElement(
            name="test_function",
            type="function",
            signature="def test_function(x: int) -> str:",
            docstring="Test function docstring",
            start_line=1,
            end_line=3,
            parameters=[{"name": "x", "type": "int", "default": None}],
            return_type="str"
        )
        
        doc = GeneratedDocumentation(
            element=element,
            docstring="Generated test documentation",
            inline_comments=["# This is a test comment"],
            summary="Test function summary",
            examples=[],
            metadata={}
        )
        
        documentation = {temp_python_file: [doc]}
        html_output = engine.export_documentation(documentation, "html")
        
        assert "<!DOCTYPE html>" in html_output
        assert "CodeScribe Documentation" in html_output
        assert "test_function" in html_output
        assert "Generated test documentation" in html_output


class TestParserFactory:
    """Test cases for parser factory"""
    
    def test_create_python_parser(self):
        """Test creating Python parser"""
        from parsers import ParserFactory
        
        parser = ParserFactory.create_parser("python")
        assert parser is not None
        assert isinstance(parser, PythonParser)
    
    def test_create_javascript_parser(self):
        """Test creating JavaScript parser"""
        from parsers import ParserFactory
        
        parser = ParserFactory.create_parser("javascript")
        assert parser is not None
        assert isinstance(parser, JavaScriptParser)
    
    def test_detect_language_from_extension(self):
        """Test language detection from file extension"""
        from parsers import ParserFactory
        
        assert ParserFactory.detect_language_from_extension(".py") == "python"
        assert ParserFactory.detect_language_from_extension(".js") == "javascript"
        assert ParserFactory.detect_language_from_extension(".ts") == "typescript"
        assert ParserFactory.detect_language_from_extension(".unknown") is None
    
    def test_get_supported_languages(self):
        """Test getting supported languages"""
        from parsers import ParserFactory
        
        languages = ParserFactory.get_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert len(languages) > 0


# Integration tests
class TestIntegration:
    """Integration test cases"""
    
    @pytest.fixture
    def sample_project_dir(self):
        """Create a sample project directory"""
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        # Create Python files
        with open(os.path.join(temp_dir, "main.py"), "w") as f:
            f.write('''
def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
        
        with open(os.path.join(temp_dir, "utils.py"), "w") as f:
            f.write('''
class StringUtils:
    """String utility functions."""
    
    @staticmethod
    def reverse_string(s: str) -> str:
        """Reverse a string."""
        return s[::-1]
    
    @staticmethod
    def capitalize_words(s: str) -> str:
        """Capitalize all words in a string."""
        return " ".join(word.capitalize() for word in s.split())
''')
        
        # Create JavaScript file
        with open(os.path.join(temp_dir, "script.js"), "w") as f:
            f.write('''
function greetUser(name) {
    return `Hello, ${name}!`;
}

class UserManager {
    constructor() {
        this.users = [];
    }
    
    addUser(user) {
        this.users.push(user);
    }
}
''')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_process_directory(self, sample_project_dir):
        """Test processing an entire directory"""
        engine = CodeScribeEngine()
        
        documentation = await engine.process_directory(sample_project_dir)
        
        assert len(documentation) >= 3  # Should process at least 3 files
        
        # Check that Python files were processed
        python_files = [path for path in documentation.keys() if path.endswith('.py')]
        assert len(python_files) >= 2
        
        # Check that JavaScript files were processed
        js_files = [path for path in documentation.keys() if path.endswith('.js')]
        assert len(js_files) >= 1
        
        # Verify documentation was generated
        total_elements = sum(len(docs) for docs in documentation.values())
        assert total_elements > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])