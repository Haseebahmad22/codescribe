"""
Command-line interface for CodeScribe.
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import CodeScribeEngine


class CodeScribeCLI:
    """Command-line interface for CodeScribe"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            description="CodeScribe - AI-Powered Code Documentation Assistant",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Document a single Python file
  python cli.py --path ./src/main.py --language python --output md

  # Document an entire project
  python cli.py --path ./my_project --recursive --output html

  # Use custom configuration
  python cli.py --path ./src --config ./config.yaml --verbosity high

  # Specify output file
  python cli.py --path ./src --output md --output-file ./docs/api.md
            """
        )
        
        # Required arguments
        parser.add_argument(
            "--path", "-p",
            required=True,
            help="Path to file or directory to document"
        )
        
        # Optional arguments
        parser.add_argument(
            "--language", "-l",
            choices=["python", "javascript", "typescript"],
            help="Programming language (auto-detected if not specified)"
        )
        
        parser.add_argument(
            "--output", "-o",
            choices=["markdown", "md", "html", "inline"],
            default="markdown",
            help="Output format (default: markdown)"
        )
        
        parser.add_argument(
            "--output-file", "-f",
            help="Output file path (prints to stdout if not specified)"
        )
        
        parser.add_argument(
            "--config", "-c",
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--verbosity", "-v",
            choices=["low", "medium", "high"],
            default="medium",
            help="Documentation verbosity level (default: medium)"
        )
        
        parser.add_argument(
            "--recursive", "-r",
            action="store_true",
            help="Process directories recursively"
        )
        
        parser.add_argument(
            "--style",
            choices=["google", "numpy", "sphinx", "jsdoc"],
            help="Documentation style (language-dependent)"
        )
        
        parser.add_argument(
            "--provider",
            choices=["openai", "huggingface"],
            default="openai",
            help="AI provider for documentation generation (default: openai)"
        )
        
        parser.add_argument(
            "--model",
            help="Specific model to use (e.g., gpt-4, gpt-3.5-turbo)"
        )
        
        parser.add_argument(
            "--api-key",
            help="API key for AI provider (can also use OPENAI_API_KEY env var)"
        )
        
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be processed without generating documentation"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            help="Suppress progress output"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="CodeScribe 1.0.0"
        )
        
        return parser
    
    async def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments"""
        parsed_args = self.parser.parse_args(args)
        
        try:
            # Validate arguments
            self._validate_arguments(parsed_args)
            
            # Initialize engine with configuration
            engine = self._create_engine(parsed_args)
            
            # Process files
            if parsed_args.dry_run:
                return self._dry_run(parsed_args)
            else:
                return await self._process_files(engine, parsed_args)
        
        except Exception as e:
            if not parsed_args.quiet:
                print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _validate_arguments(self, args) -> None:
        """Validate command-line arguments"""
        # Check if path exists
        if not os.path.exists(args.path):
            raise FileNotFoundError(f"Path does not exist: {args.path}")
        
        # Check if API key is available for OpenAI
        if args.provider == "openai":
            api_key = args.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                    "or use --api-key argument."
                )
        
        # Validate output file directory
        if args.output_file:
            output_dir = os.path.dirname(args.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
    
    def _create_engine(self, args) -> CodeScribeEngine:
        """Create CodeScribe engine with configuration"""
        # Override configuration with CLI arguments
        config_overrides = {}
        
        if args.config:
            engine = CodeScribeEngine(args.config)
        else:
            engine = CodeScribeEngine()
        
        # Apply CLI overrides
        if args.verbosity:
            engine.config['documentation']['verbosity'] = args.verbosity
        
        if args.style:
            engine.config['documentation']['style'] = args.style
        
        if args.provider:
            engine.config['ai']['provider'] = args.provider
        
        if args.model:
            if args.provider == "openai":
                engine.config['ai']['openai']['model'] = args.model
            elif args.provider == "huggingface":
                engine.config['ai']['huggingface']['model'] = args.model
        
        if args.api_key:
            engine.config['ai']['openai']['api_key'] = args.api_key
        
        # Reinitialize generator with new config
        engine._initialize_generator()
        
        return engine
    
    def _dry_run(self, args) -> int:
        """Perform dry run to show what would be processed"""
        path = args.path
        
        if os.path.isfile(path):
            print(f"Would process file: {path}")
            # Try to detect language
            ext = Path(path).suffix
            from parsers import ParserFactory
            language = ParserFactory.detect_language_from_extension(ext)
            if language:
                print(f"  Detected language: {language}")
            else:
                print(f"  Warning: Unsupported file extension: {ext}")
        
        elif os.path.isdir(path):
            print(f"Would process directory: {path}")
            print(f"Recursive: {args.recursive}")
            
            # Find supported files
            supported_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
            files_found = []
            
            if args.recursive:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if any(file.endswith(ext) for ext in supported_extensions):
                            files_found.append(os.path.join(root, file))
            else:
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        if any(file.endswith(ext) for ext in supported_extensions):
                            files_found.append(file_path)
            
            print(f"Found {len(files_found)} supported files:")
            for file_path in files_found[:10]:  # Show first 10
                print(f"  {file_path}")
            
            if len(files_found) > 10:
                print(f"  ... and {len(files_found) - 10} more files")
        
        print(f"\nConfiguration:")
        print(f"  Provider: {args.provider}")
        print(f"  Output format: {args.output}")
        print(f"  Verbosity: {args.verbosity}")
        if args.style:
            print(f"  Style: {args.style}")
        
        return 0
    
    async def _process_files(self, engine: CodeScribeEngine, args) -> int:
        """Process files and generate documentation"""
        if not args.quiet:
            print("Starting CodeScribe documentation generation...")
        
        path = args.path
        
        try:
            # Process single file or directory
            if os.path.isfile(path):
                if not args.quiet:
                    print(f"Processing file: {path}")
                documentation = {path: await engine.process_file(path, args.language)}
            else:
                if not args.quiet:
                    print(f"Processing directory: {path}")
                documentation = await engine.process_directory(path, args.recursive)
            
            # Generate output
            if args.output in ["markdown", "md"]:
                output_format = "markdown"
            elif args.output == "html":
                output_format = "html"
            elif args.output == "inline":
                # For inline, we'll generate the docstrings and show them
                return self._show_inline_documentation(documentation, args.quiet)
            else:
                output_format = "markdown"
            
            output_content = engine.export_documentation(documentation, output_format)
            
            # Write to file or stdout
            if args.output_file:
                with open(args.output_file, 'w', encoding='utf-8') as file:
                    file.write(output_content)
                if not args.quiet:
                    print(f"Documentation written to: {args.output_file}")
            else:
                print(output_content)
            
            # Summary
            if not args.quiet:
                total_elements = sum(len(docs) for docs in documentation.values())
                print(f"\nCompleted! Generated documentation for {total_elements} code elements in {len(documentation)} files.")
            
            return 0
        
        except Exception as e:
            if not args.quiet:
                print(f"Error during processing: {e}", file=sys.stderr)
            return 1
    
    def _show_inline_documentation(self, documentation, quiet: bool) -> int:
        """Show generated docstrings for inline insertion"""
        for file_path, docs in documentation.items():
            print(f"\n{'='*50}")
            print(f"File: {file_path}")
            print('='*50)
            
            for doc in docs:
                element = doc.element
                print(f"\n{element.type.title()}: {element.name} (line {element.start_line})")
                print("-" * 40)
                print("Generated docstring:")
                print(doc.docstring)
                
                if doc.inline_comments:
                    print("\nSuggested inline comments:")
                    for comment in doc.inline_comments:
                        print(f"  {comment}")
        
        return 0


def main():
    """Main entry point for CLI"""
    cli = CodeScribeCLI()
    
    try:
        # Run the CLI
        exit_code = asyncio.run(cli.run())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()