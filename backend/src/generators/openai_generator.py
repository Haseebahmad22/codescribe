"""
OpenAI-based documentation generator.
"""
import asyncio
from typing import List, Optional
import openai
from openai import AsyncOpenAI

from .base import BaseDocumentationGenerator, DocumentationConfig, CodeElement


class OpenAIDocumentationGenerator(BaseDocumentationGenerator):
    """Documentation generator using OpenAI GPT models"""
    
    def __init__(self, config: DocumentationConfig, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_docstring(self, element: CodeElement, context: str = "") -> str:
        """Generate a docstring for a code element using OpenAI"""
        prompt = self._build_prompt(element, context, "docstring")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software developer who writes excellent documentation. Generate clear, comprehensive, and well-structured docstrings."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating docstring: {e}")
            return f"# TODO: Add documentation for {element.name}"
    
    async def generate_inline_comments(self, element: CodeElement, context: str = "") -> List[str]:
        """Generate inline comments for a code element"""
        prompt = self._build_prompt(element, context, "comments")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software developer who writes helpful inline comments. Focus on explaining complex logic, business rules, and non-obvious implementation details."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens // 2,
                temperature=self.config.temperature
            )
            
            comments_text = response.choices[0].message.content.strip()
            # Split into individual comments
            comments = [comment.strip() for comment in comments_text.split('\n') if comment.strip()]
            return comments
        
        except Exception as e:
            print(f"Error generating inline comments: {e}")
            return []
    
    async def generate_summary(self, elements: List[CodeElement]) -> str:
        """Generate a summary for multiple code elements"""
        if not elements:
            return "No code elements provided."
        
        # For single element
        if len(elements) == 1:
            element = elements[0]
            prompt = self._build_prompt(element, "", "summary")
        else:
            # For multiple elements, create a combined prompt
            elements_info = "\n".join([
                f"- {elem.type}: {elem.name} ({elem.signature})"
                for elem in elements
            ])
            prompt = f"""
Code Elements Summary:
{elements_info}

Generate a comprehensive summary that describes:
1. The overall purpose and functionality of these code elements
2. How they work together
3. Key design patterns or architectural decisions
4. Main responsibilities and interactions

Verbosity level: {self.config.verbosity}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software architect who writes clear technical summaries. Focus on high-level design and system understanding."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Error generating summary."
    
    async def generate_batch_documentation(self, elements: List[CodeElement], contexts: List[str] = None) -> List[str]:
        """Generate documentation for multiple elements in batch"""
        if contexts is None:
            contexts = [""] * len(elements)
        
        # Create tasks for parallel processing
        tasks = []
        for element, context in zip(elements, contexts):
            task = self.generate_docstring(element, context)
            tasks.append(task)
        
        # Execute in batches to avoid rate limits
        batch_size = 5
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(f"# TODO: Error generating documentation - {result}")
                else:
                    results.append(result)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(tasks):
                await asyncio.sleep(1)
        
        return results