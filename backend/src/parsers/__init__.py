"""
Parser factory for creating language-specific parsers.
"""
from typing import Dict, Type, Optional
from .base import BaseParser
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser


class ParserFactory:
    """Factory class for creating language-specific parsers"""
    
    _parsers: Dict[str, Type[BaseParser]] = {
        'python': PythonParser,
        'py': PythonParser,
        'javascript': JavaScriptParser,
        'js': JavaScriptParser,
        'typescript': JavaScriptParser,
        'ts': JavaScriptParser,
        'jsx': JavaScriptParser,
        'tsx': JavaScriptParser,
    }
    
    @classmethod
    def create_parser(cls, language: str) -> Optional[BaseParser]:
        """Create a parser for the specified language"""
        language = language.lower()
        
        if language in cls._parsers:
            parser_class = cls._parsers[language]
            if language in ['typescript', 'ts', 'tsx']:
                return parser_class('typescript')
            return parser_class()
        
        return None
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """Get list of supported languages"""
        return list(set(cls._parsers.keys()))
    
    @classmethod
    def detect_language_from_extension(cls, file_extension: str) -> Optional[str]:
        """Detect language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
        }
        
        return ext_map.get(file_extension.lower())