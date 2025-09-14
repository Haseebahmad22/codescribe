"""
DeepSeek R1-based documentation generator.
"""
import asyncio
from typing import List, Optional
import openai
from openai import AsyncOpenAI

from .base import BaseDocumentationGenerator, DocumentationConfig, CodeElement


class DeepSeekDocumentationGenerator(BaseDocumentationGenerator):
    """Documentation generator using DeepSeek R1 models"""
    
    def __init__(self, config: DocumentationConfig, api_key: str, model: str = "deepseek-r1", base_url: str = "https://api.deepseek.com"):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    async def generate_docstring(self, element: CodeElement, context: str = "") -> str:
        """Generate a docstring for a code element using DeepSeek R1"""
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
            print(f"Error generating docstring with DeepSeek: {e}")
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
                        "content": "You are an expert software developer. Generate helpful inline comments that explain complex logic and non-obvious code sections."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content.strip()
            # Parse response into individual comments
            return [line.strip() for line in content.split('\n') if line.strip()]
        
        except Exception as e:
            print(f"Error generating comments with DeepSeek: {e}")
            return [f"# TODO: Add comments for {element.name}"]
    
    async def generate_explanation(self, element: CodeElement, context: str = "") -> str:
        """Generate a detailed explanation for a code element"""
        prompt = self._build_prompt(element, context, "explanation")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software developer and technical writer. Provide clear, detailed explanations of code functionality, purpose, and usage."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating explanation with DeepSeek: {e}")
            return f"Error generating explanation for {element.name}"
    
    def _build_prompt(self, element: CodeElement, context: str, task: str) -> str:
        """Build a prompt for the DeepSeek model"""
        base_prompt = f"""
Language: {element.language}
Element Type: {element.element_type}
Name: {element.name}
Code:
```{element.language}
{element.code}
```
"""
        
        if context:
            base_prompt += f"\nContext:\n{context}"
        
        if task == "docstring":
            task_prompt = f"""
Please generate a comprehensive docstring for this {element.element_type}. The docstring should:
1. Clearly describe what the code does
2. Document parameters and their types
3. Document return values and types
4. Include any important notes about usage or behavior
5. Follow {element.language} docstring conventions
"""
        elif task == "comments":
            task_prompt = f"""
Please generate helpful inline comments for this {element.element_type}. Comments should:
1. Explain complex logic or algorithms
2. Clarify non-obvious code sections
3. Be concise but informative
4. Follow {element.language} comment conventions
Provide each comment on a separate line.
"""
        elif task == "explanation":
            task_prompt = f"""
Please provide a detailed explanation of this {element.element_type}. The explanation should:
1. Describe the overall purpose and functionality
2. Explain the approach or algorithm used
3. Discuss any important design decisions
4. Mention how it fits into the larger codebase (if context is provided)
5. Be clear and accessible to other developers
"""
        else:
            task_prompt = f"Please analyze and document this {element.element_type}."
        
        return base_prompt + task_prompt