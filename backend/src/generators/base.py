"""
Base documentation generator interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..parsers.base import CodeElement


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation"""
    style: str = "google"  # google, numpy, sphinx, jsdoc
    verbosity: str = "medium"  # low, medium, high
    include_examples: bool = True
    include_parameters: bool = True
    include_return_values: bool = True
    include_exceptions: bool = True
    max_tokens: int = 1000
    temperature: float = 0.3


@dataclass
class GeneratedDocumentation:
    """Generated documentation for a code element"""
    element: CodeElement
    docstring: str
    inline_comments: List[str]
    summary: str
    examples: List[str]
    metadata: Dict[str, Any]


class BaseDocumentationGenerator(ABC):
    """Base class for documentation generators"""
    
    def __init__(self, config: DocumentationConfig):
        self.config = config
    
    @abstractmethod
    async def generate_docstring(self, element: CodeElement, context: str = "") -> str:
        """Generate a docstring for a code element"""
        pass
    
    @abstractmethod
    async def generate_inline_comments(self, element: CodeElement, context: str = "") -> List[str]:
        """Generate inline comments for a code element"""
        pass
    
    @abstractmethod
    async def generate_summary(self, elements: List[CodeElement]) -> str:
        """Generate a summary for multiple code elements"""
        pass
    
    async def generate_documentation(self, element: CodeElement, context: str = "") -> GeneratedDocumentation:
        """Generate complete documentation for a code element"""
        docstring = await self.generate_docstring(element, context)
        inline_comments = await self.generate_inline_comments(element, context)
        summary = await self.generate_summary([element])
        
        return GeneratedDocumentation(
            element=element,
            docstring=docstring,
            inline_comments=inline_comments,
            summary=summary,
            examples=[],
            metadata={}
        )
    
    def _build_prompt(self, element: CodeElement, context: str, prompt_type: str) -> str:
        """Build AI prompt based on element and configuration"""
        base_info = f"""
Code Element: {element.name}
Type: {element.type}
Language: {element.type}
Signature: {element.signature}
"""
        
        if element.docstring:
            base_info += f"Existing docstring: {element.docstring}\n"
        
        if context:
            base_info += f"Context:\n{context}\n"
        
        # Add prompt based on type
        if prompt_type == "docstring":
            return self._build_docstring_prompt(element, base_info)
        elif prompt_type == "comments":
            return self._build_comments_prompt(element, base_info)
        elif prompt_type == "summary":
            return self._build_summary_prompt(element, base_info)
        
        return base_info
    
    def _build_docstring_prompt(self, element: CodeElement, base_info: str) -> str:
        """Build prompt for docstring generation"""
        style_guide = self._get_style_guide(element)
        
        prompt = f"""
{base_info}

Generate a comprehensive docstring for this {element.type} following the {self.config.style} style guide.

Style Guide:
{style_guide}

Requirements:
- Verbosity level: {self.config.verbosity}
- Include parameters: {self.config.include_parameters}
- Include return values: {self.config.include_return_values}
- Include examples: {self.config.include_examples}
- Include exceptions: {self.config.include_exceptions}

Please generate a well-structured, clear, and comprehensive docstring.
"""
        return prompt
    
    def _build_comments_prompt(self, element: CodeElement, base_info: str) -> str:
        """Build prompt for inline comments generation"""
        prompt = f"""
{base_info}

Generate helpful inline comments for this {element.type} that explain:
1. Complex logic or algorithms
2. Business rules or requirements
3. Non-obvious implementation details
4. Important assumptions or constraints

The comments should be:
- Concise but informative
- Focused on the "why" rather than the "what"
- Helpful for future maintainers
- Following {self.config.style} comment style

Return the comments as a list, one per line that needs commenting.
"""
        return prompt
    
    def _build_summary_prompt(self, element: CodeElement, base_info: str) -> str:
        """Build prompt for summary generation"""
        prompt = f"""
{base_info}

Generate a concise summary of this {element.type} that describes:
1. Its main purpose and functionality
2. Key responsibilities
3. How it fits into the larger system
4. Any important design decisions

The summary should be {self.config.verbosity} in detail and suitable for:
- Code reviews
- Documentation
- New team member onboarding
"""
        return prompt
    
    def _get_style_guide(self, element: CodeElement) -> str:
        """Get style guide based on language and configuration"""
        if element.type in ['function', 'method'] and 'python' in element.signature:
            if self.config.style == "google":
                return """
Google Style Python Docstring:
'''
Brief description of the function.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of return value.

Raises:
    ExceptionType: Description of when this exception is raised.

Example:
    Example usage of the function.
'''
"""
            elif self.config.style == "numpy":
                return """
NumPy Style Python Docstring:
'''
Brief description of the function.

Parameters
----------
param1 : type
    Description of param1.
param2 : type
    Description of param2.

Returns
-------
type
    Description of return value.

Raises
------
ExceptionType
    Description of when this exception is raised.

Examples
--------
Example usage of the function.
'''
"""
        
        elif 'javascript' in element.signature or 'typescript' in element.signature:
            return """
JSDoc Style:
/**
 * Brief description of the function.
 * 
 * @param {type} param1 - Description of param1.
 * @param {type} param2 - Description of param2.
 * @returns {type} Description of return value.
 * @throws {ExceptionType} Description of when this exception is thrown.
 * @example
 * // Example usage
 * const result = functionName(param1, param2);
 */
"""
        
        return "Standard documentation format for the detected language."