"""
CLI utilities and helper functions.
"""
import os
import sys
from typing import List, Dict, Any
from pathlib import Path


def validate_file_path(file_path: str) -> bool:
    """Validate if file path exists and is accessible"""
    try:
        return os.path.exists(file_path) and os.path.isfile(file_path)
    except (OSError, IOError):
        return False


def validate_directory_path(dir_path: str) -> bool:
    """Validate if directory path exists and is accessible"""
    try:
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
    except (OSError, IOError):
        return False


def get_supported_files(directory: str, recursive: bool = True, extensions: List[str] = None) -> List[str]:
    """Get list of supported files in directory"""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
    
    files = []
    
    if recursive:
        for root, dirs, filenames in os.walk(directory):
            # Skip common directories that should be ignored
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and any(filename.endswith(ext) for ext in extensions):
                files.append(file_path)
    
    return sorted(files)


def estimate_processing_time(file_count: int, avg_elements_per_file: int = 5) -> str:
    """Estimate processing time based on file count"""
    # Rough estimates: ~2-3 seconds per element with OpenAI
    total_elements = file_count * avg_elements_per_file
    estimated_seconds = total_elements * 2.5
    
    if estimated_seconds < 60:
        return f"~{int(estimated_seconds)} seconds"
    elif estimated_seconds < 3600:
        minutes = int(estimated_seconds / 60)
        return f"~{minutes} minutes"
    else:
        hours = int(estimated_seconds / 3600)
        return f"~{hours} hours"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_progress_bar(current: int, total: int, width: int = 50) -> None:
    """Print a simple progress bar"""
    if total == 0:
        return
    
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    percentage = progress * 100
    
    print(f'\rProgress: |{bar}| {percentage:.1f}% ({current}/{total})', end='', flush=True)


def create_output_directory(file_path: str) -> None:
    """Create output directory if it doesn't exist"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path"""
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path


def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available"""
    dependencies = {}
    
    # Check OpenAI
    try:
        import openai
        dependencies['openai'] = True
    except ImportError:
        dependencies['openai'] = False
    
    # Check Transformers
    try:
        import transformers
        dependencies['transformers'] = True
    except ImportError:
        dependencies['transformers'] = False
    
    # Check tree-sitter
    try:
        import tree_sitter
        dependencies['tree_sitter'] = True
    except ImportError:
        dependencies['tree_sitter'] = False
    
    # Check YAML
    try:
        import yaml
        dependencies['yaml'] = True
    except ImportError:
        dependencies['yaml'] = False
    
    return dependencies


def print_dependency_status() -> None:
    """Print status of dependencies"""
    deps = check_dependencies()
    
    print("Dependency Status:")
    print("-" * 20)
    
    for dep, available in deps.items():
        status = "✓ Available" if available else "✗ Missing"
        print(f"{dep:15} {status}")
    
    if not deps['openai'] and not deps['transformers']:
        print("\nWarning: No AI providers available. Install openai or transformers.")
    
    if not deps['yaml']:
        print("Warning: YAML support missing. Configuration files won't work.")


class ColoredOutput:
    """Utility class for colored terminal output"""
    
    # Color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    @classmethod
    def is_supported(cls) -> bool:
        """Check if colored output is supported"""
        return sys.stdout.isatty() and os.name != 'nt'
    
    @classmethod
    def error(cls, message: str) -> str:
        """Format error message"""
        if cls.is_supported():
            return f"{cls.RED}{message}{cls.RESET}"
        return message
    
    @classmethod
    def success(cls, message: str) -> str:
        """Format success message"""
        if cls.is_supported():
            return f"{cls.GREEN}{message}{cls.RESET}"
        return message
    
    @classmethod
    def warning(cls, message: str) -> str:
        """Format warning message"""
        if cls.is_supported():
            return f"{cls.YELLOW}{message}{cls.RESET}"
        return message
    
    @classmethod
    def info(cls, message: str) -> str:
        """Format info message"""
        if cls.is_supported():
            return f"{cls.BLUE}{message}{cls.RESET}"
        return message
    
    @classmethod
    def bold(cls, message: str) -> str:
        """Format bold message"""
        if cls.is_supported():
            return f"{cls.BOLD}{message}{cls.RESET}"
        return message