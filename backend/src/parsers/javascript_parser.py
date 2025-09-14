"""
JavaScript/TypeScript parser using tree-sitter.
"""
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import BaseParser, CodeElement

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class JavaScriptParser(BaseParser):
    """Parser for JavaScript/TypeScript code"""
    
    def __init__(self, language="javascript"):
        super().__init__(language)
        self.parser = None
        
        if TREE_SITTER_AVAILABLE:
            try:
                # Initialize tree-sitter parser
                if language == "javascript":
                    js_language = Language('tree-sitter-javascript', 'javascript')
                else:  # typescript
                    js_language = Language('tree-sitter-typescript', 'typescript')
                
                self.parser = Parser()
                self.parser.set_language(js_language)
            except Exception as e:
                print(f"Warning: Could not initialize tree-sitter parser: {e}")
                self.parser = None
    
    def parse_file(self, file_path: str) -> List[CodeElement]:
        """Parse a JavaScript/TypeScript file and return code elements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            return self.parse_code(code)
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return []
    
    def parse_code(self, code: str) -> List[CodeElement]:
        """Parse JavaScript/TypeScript code string and return code elements"""
        if self.parser:
            return self._parse_with_tree_sitter(code)
        else:
            return self._parse_with_regex(code)
    
    def _parse_with_tree_sitter(self, code: str) -> List[CodeElement]:
        """Parse using tree-sitter (preferred method)"""
        elements = []
        
        try:
            tree = self.parser.parse(bytes(code, 'utf8'))
            root_node = tree.root_node
            
            def traverse(node, parent_class=None):
                if node.type == 'function_declaration':
                    element = self._extract_function_info(node, code, parent_class)
                    if element:
                        elements.append(element)
                
                elif node.type == 'class_declaration':
                    element = self._extract_class_info(node, code)
                    if element:
                        elements.append(element)
                        # Parse methods within the class
                        for child in node.children:
                            traverse(child, element.name)
                
                elif node.type == 'method_definition':
                    element = self._extract_method_info(node, code, parent_class)
                    if element:
                        elements.append(element)
                
                # Continue traversing
                for child in node.children:
                    traverse(child, parent_class)
            
            traverse(root_node)
            
        except Exception as e:
            print(f"Error parsing with tree-sitter: {e}")
        
        return elements
    
    def _parse_with_regex(self, code: str) -> List[CodeElement]:
        """Fallback regex-based parsing"""
        elements = []
        lines = code.split('\n')
        
        # Regex patterns for different code elements
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*{'
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{'
        arrow_function_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{'
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for function declarations
            func_match = re.search(function_pattern, line)
            if func_match:
                element = CodeElement(
                    name=func_match.group(1),
                    type='function',
                    signature=line,
                    docstring=None,
                    start_line=i + 1,
                    end_line=i + 1,  # Simplified
                    parameters=[],
                    return_type=None,
                    complexity=1
                )
                elements.append(element)
            
            # Check for class declarations
            class_match = re.search(class_pattern, line)
            if class_match:
                element = CodeElement(
                    name=class_match.group(1),
                    type='class',
                    signature=line,
                    docstring=None,
                    start_line=i + 1,
                    end_line=i + 1,  # Simplified
                    parameters=[],
                    return_type=None,
                    complexity=1
                )
                elements.append(element)
            
            # Check for arrow functions
            arrow_match = re.search(arrow_function_pattern, line)
            if arrow_match:
                element = CodeElement(
                    name=arrow_match.group(1),
                    type='function',
                    signature=line,
                    docstring=None,
                    start_line=i + 1,
                    end_line=i + 1,  # Simplified
                    parameters=[],
                    return_type=None,
                    complexity=1
                )
                elements.append(element)
        
        return elements
    
    def _extract_function_info(self, node, code: str, parent_class=None) -> Optional[CodeElement]:
        """Extract function information from tree-sitter node"""
        try:
            # Get function name
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if not name_node:
                return None
            
            name = code[name_node.start_byte:name_node.end_byte]
            signature = code[node.start_byte:node.end_byte].split('\n')[0]
            
            return CodeElement(
                name=name,
                type='method' if parent_class else 'function',
                signature=signature,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parameters=[],
                return_type=None,
                complexity=1,
                parent=parent_class
            )
        except Exception:
            return None
    
    def _extract_class_info(self, node, code: str) -> Optional[CodeElement]:
        """Extract class information from tree-sitter node"""
        try:
            # Get class name
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if not name_node:
                return None
            
            name = code[name_node.start_byte:name_node.end_byte]
            signature = code[node.start_byte:node.end_byte].split('\n')[0]
            
            return CodeElement(
                name=name,
                type='class',
                signature=signature,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parameters=[],
                return_type=None,
                complexity=1
            )
        except Exception:
            return None
    
    def _extract_method_info(self, node, code: str, parent_class=None) -> Optional[CodeElement]:
        """Extract method information from tree-sitter node"""
        try:
            # Get method name
            name_node = None
            for child in node.children:
                if child.type in ['property_identifier', 'identifier']:
                    name_node = child
                    break
            
            if not name_node:
                return None
            
            name = code[name_node.start_byte:name_node.end_byte]
            signature = code[node.start_byte:node.end_byte].split('\n')[0]
            
            return CodeElement(
                name=name,
                type='method',
                signature=signature,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parameters=[],
                return_type=None,
                complexity=1,
                parent=parent_class
            )
        except Exception:
            return None
    
    def extract_context(self, element: CodeElement, full_code: str) -> str:
        """Extract relevant context around a code element"""
        lines = full_code.split('\n')
        
        # Get a few lines before and after for context
        context_start = max(0, element.start_line - 3)
        context_end = min(len(lines), element.end_line + 3)
        
        context_lines = lines[context_start:context_end]
        return '\n'.join(context_lines)