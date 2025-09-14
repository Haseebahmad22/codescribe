"""
Base parser interface for different programming languages.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CodeElement:
    """Represents a code element (function, class, module, etc.)"""
    name: str
    type: str  # "function", "class", "method", "module"
    signature: str
    docstring: Optional[str]
    start_line: int
    end_line: int
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    complexity: int = 1
    parent: Optional[str] = None


class BaseParser(ABC):
    """Base class for all language parsers"""
    
    def __init__(self, language: str):
        self.language = language
    
    @abstractmethod
    def parse_file(self, file_path: str) -> List[CodeElement]:
        """Parse a file and return code elements"""
        pass
    
    @abstractmethod
    def parse_code(self, code: str) -> List[CodeElement]:
        """Parse code string and return code elements"""
        pass
    
    @abstractmethod
    def extract_context(self, element: CodeElement, full_code: str) -> str:
        """Extract relevant context around a code element"""
        pass