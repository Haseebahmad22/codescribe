"""
Hugging Face Transformers-based documentation generator.
"""
import asyncio
from typing import List, Optional
import torch

from .base import BaseDocumentationGenerator, DocumentationConfig, CodeElement

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        pipeline
    )
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


class HuggingFaceDocumentationGenerator(BaseDocumentationGenerator):
    """Documentation generator using Hugging Face Transformers"""
    
    def __init__(self, config: DocumentationConfig, model_name: str = "microsoft/DialoGPT-medium"):
        super().__init__(config)
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        if HF_AVAILABLE:
            self._initialize_model()
        else:
            print("Warning: Hugging Face Transformers not available. Install with: pip install transformers torch")
    
    def _initialize_model(self):
        """Initialize the Hugging Face model and tokenizer"""
        try:
            # For text generation, use a more suitable model
            if "DialoGPT" in self.model_name:
                # Use a better model for code documentation
                self.model_name = "microsoft/CodeBERT-base"
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Use CPU for smaller models to avoid memory issues
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.tokenizer,
                device=device,
                max_length=512,
                do_sample=True,
                temperature=self.config.temperature,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        except Exception as e:
            print(f"Error initializing Hugging Face model: {e}")
            self.pipeline = None
    
    async def generate_docstring(self, element: CodeElement, context: str = "") -> str:
        """Generate a docstring for a code element using Hugging Face"""
        if not self.pipeline:
            return self._fallback_docstring(element)
        
        prompt = self._build_simplified_prompt(element, context, "docstring")
        
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_text, 
                prompt
            )
            
            return self._clean_response(response, element.name)
        
        except Exception as e:
            print(f"Error generating docstring with HF: {e}")
            return self._fallback_docstring(element)
    
    async def generate_inline_comments(self, element: CodeElement, context: str = "") -> List[str]:
        """Generate inline comments for a code element"""
        if not self.pipeline:
            return []
        
        prompt = self._build_simplified_prompt(element, context, "comments")
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_text, 
                prompt
            )
            
            # Extract comments from response
            comments = self._extract_comments(response)
            return comments
        
        except Exception as e:
            print(f"Error generating comments with HF: {e}")
            return []
    
    async def generate_summary(self, elements: List[CodeElement]) -> str:
        """Generate a summary for multiple code elements"""
        if not self.pipeline:
            return "Summary generation not available."
        
        if not elements:
            return "No code elements provided."
        
        # Simplified summary for HF models
        elements_info = ", ".join([f"{elem.type} {elem.name}" for elem in elements])
        prompt = f"Summarize these code elements: {elements_info}. Purpose and functionality:"
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_text, 
                prompt
            )
            
            return self._clean_response(response, "summary")
        
        except Exception as e:
            print(f"Error generating summary with HF: {e}")
            return "Error generating summary."
    
    def _generate_text(self, prompt: str) -> str:
        """Generate text using the HF pipeline"""
        try:
            # Truncate prompt if too long
            max_prompt_length = 256
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "..."
            
            outputs = self.pipeline(
                prompt,
                max_new_tokens=128,
                num_return_sequences=1,
                temperature=self.config.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = outputs[0]['generated_text']
            
            # Remove the original prompt from the response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        
        except Exception as e:
            print(f"Error in text generation: {e}")
            return ""
    
    def _build_simplified_prompt(self, element: CodeElement, context: str, prompt_type: str) -> str:
        """Build simplified prompt for HF models (shorter context)"""
        if prompt_type == "docstring":
            return f"Document this {element.type} {element.name}: {element.signature[:100]}... Documentation:"
        elif prompt_type == "comments":
            return f"Add comments to explain this {element.type}: {element.signature[:100]}... Comments:"
        else:
            return f"Explain {element.type} {element.name}:"
    
    def _clean_response(self, response: str, element_name: str) -> str:
        """Clean and format the generated response"""
        if not response:
            return f"# TODO: Add documentation for {element_name}"
        
        # Remove common artifacts
        response = response.strip()
        
        # Remove repetitive text
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line in cleaned_lines:
                cleaned_lines.append(line)
        
        cleaned_response = '\n'.join(cleaned_lines[:5])  # Limit to 5 lines
        
        return cleaned_response if cleaned_response else f"# TODO: Add documentation for {element_name}"
    
    def _extract_comments(self, response: str) -> List[str]:
        """Extract individual comments from generated text"""
        if not response:
            return []
        
        lines = response.split('\n')
        comments = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Filter out very short lines
                # Clean up the comment
                if not line.startswith('#') and not line.startswith('//'):
                    line = f"# {line}"
                comments.append(line)
        
        return comments[:3]  # Limit to 3 comments
    
    def _fallback_docstring(self, element: CodeElement) -> str:
        """Generate a basic docstring when AI generation fails"""
        if element.type == "function":
            return f'"""\n{element.name.replace("_", " ").title()} function.\n\nTODO: Add detailed documentation.\n"""'
        elif element.type == "class":
            return f'"""\n{element.name} class.\n\nTODO: Add detailed documentation.\n"""'
        elif element.type == "method":
            return f'"""\n{element.name.replace("_", " ").title()} method.\n\nTODO: Add detailed documentation.\n"""'
        else:
            return f'"""\nTODO: Add documentation for {element.name}.\n"""'