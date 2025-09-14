"""
Python code parser using AST (Abstract Syntax Tree).
"""
import ast
import inspect
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import BaseParser, CodeElement


class PythonParser(BaseParser):
    """Parser for Python code using AST"""
    
    def __init__(self):
        super().__init__("python")
    
    def parse_file(self, file_path: str) -> List[CodeElement]:
        """Parse a Python file and return code elements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            return self.parse_code(code)
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return []
    
    def parse_code(self, code: str) -> List[CodeElement]:
        """Parse Python code string and return code elements"""
        try:
            tree = ast.parse(code)
            elements = []
            
            # Visit all nodes and extract relevant information
            visitor = PythonASTVisitor()
            visitor.visit(tree)
            
            # Convert visitor results to CodeElements
            for item in visitor.elements:
                element = CodeElement(
                    name=item['name'],
                    type=item['type'],
                    signature=item['signature'],
                    docstring=item['docstring'],
                    start_line=item['start_line'],
                    end_line=item['end_line'],
                    parameters=item['parameters'],
                    return_type=item['return_type'],
                    complexity=item['complexity'],
                    parent=item['parent']
                )
                elements.append(element)
            
            return elements
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return []
        except Exception as e:
            print(f"Error parsing code: {e}")
            return []
    
    def extract_context(self, element: CodeElement, full_code: str) -> str:
        """Extract relevant context around a code element"""
        lines = full_code.split('\n')
        
        # Get a few lines before and after for context
        context_start = max(0, element.start_line - 3)
        context_end = min(len(lines), element.end_line + 3)
        
        context_lines = lines[context_start:context_end]
        return '\n'.join(context_lines)


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor to extract code elements from Python AST"""
    
    def __init__(self):
        self.elements = []
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        self.current_class = node.name
        
        # Extract class information
        docstring = ast.get_docstring(node)
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        element = {
            'name': node.name,
            'type': 'class',
            'signature': f"class {node.name}:",
            'docstring': docstring,
            'start_line': node.lineno,
            'end_line': getattr(node, 'end_lineno', node.lineno),
            'parameters': [],
            'return_type': None,
            'complexity': len(methods) + 1,
            'parent': None
        }
        self.elements.append(element)
        
        # Continue visiting child nodes
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        # Extract function information
        docstring = ast.get_docstring(node)
        parameters = self._extract_parameters(node)
        return_annotation = self._extract_return_annotation(node)
        
        # Calculate complexity (simplified)
        complexity = self._calculate_complexity(node)
        
        element = {
            'name': node.name,
            'type': 'method' if self.current_class else 'function',
            'signature': self._get_function_signature(node),
            'docstring': docstring,
            'start_line': node.lineno,
            'end_line': getattr(node, 'end_lineno', node.lineno),
            'parameters': parameters,
            'return_type': return_annotation,
            'complexity': complexity,
            'parent': self.current_class
        }
        self.elements.append(element)
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters with types and defaults"""
        parameters = []
        
        args = node.args.args
        defaults = node.args.defaults
        
        # Calculate default values offset
        default_offset = len(args) - len(defaults)
        
        for i, arg in enumerate(args):
            param = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else None,
                'default': None
            }
            
            # Check if this parameter has a default value
            if i >= default_offset:
                default_idx = i - default_offset
                if default_idx < len(defaults):
                    param['default'] = ast.unparse(defaults[default_idx])
            
            parameters.append(param)
        
        return parameters
    
    def _extract_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation"""
        if node.returns:
            return ast.unparse(node.returns)
        return None
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate function signature string"""
        try:
            return f"def {node.name}({ast.unparse(node.args)}):"
        except:
            return f"def {node.name}(...):"
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity