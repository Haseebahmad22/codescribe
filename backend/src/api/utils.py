"""
API utilities and helper functions.
"""
import os
import mimetypes
from typing import Dict, Any, Optional
from pathlib import Path


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information"""
    path = Path(file_path)
    
    try:
        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "size_human": _format_bytes(stat.st_size),
            "extension": path.suffix,
            "mime_type": mimetypes.guess_type(file_path)[0],
            "is_text": _is_text_file(file_path),
            "language": _detect_language(path.suffix)
        }
    except OSError:
        return {"error": "Could not read file information"}


def _format_bytes(bytes_value: int) -> str:
    """Format bytes in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def _is_text_file(file_path: str) -> bool:
    """Check if file is a text file"""
    try:
        with open(file_path, 'rb') as file:
            # Read first 1024 bytes
            chunk = file.read(1024)
            
        # Check for null bytes (binary files usually have them)
        if b'\x00' in chunk:
            return False
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    except (OSError, IOError):
        return False


def _detect_language(extension: str) -> Optional[str]:
    """Detect programming language from file extension"""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.m': 'matlab',
        '.sh': 'bash',
        '.ps1': 'powershell',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.tex': 'latex'
    }
    
    return language_map.get(extension.lower())


def validate_api_key(provider: str, api_key: Optional[str]) -> bool:
    """Validate API key for AI provider"""
    if provider == "openai":
        return api_key is not None and len(api_key) > 20 and api_key.startswith('sk-')
    elif provider == "huggingface":
        # Hugging Face doesn't require API key for basic usage
        return True
    else:
        return False


def get_error_response(error: Exception, job_id: Optional[str] = None) -> Dict[str, Any]:
    """Generate standardized error response"""
    response = {
        "success": False,
        "error": type(error).__name__,
        "message": str(error)
    }
    
    if job_id:
        response["job_id"] = job_id
    
    return response


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path separators and dangerous characters
    import re
    
    # Replace path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip().strip('.')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def create_documentation_metadata(
    file_path: str,
    language: str,
    elements_count: int,
    processing_time: float,
    provider: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Create metadata for generated documentation"""
    return {
        "source_file": file_path,
        "language": language,
        "elements_documented": elements_count,
        "processing_time_seconds": round(processing_time, 2),
        "ai_provider": provider,
        "ai_model": model,
        "generated_at": _get_current_timestamp(),
        "version": "1.0.0"
    }


def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()


class APIError(Exception):
    """Custom API error class"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error"""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class ProcessingError(APIError):
    """Processing error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500, error_code="PROCESSING_ERROR")


class AuthenticationError(APIError):
    """Authentication error"""
    
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


def handle_file_upload_error(filename: str, error: Exception) -> Dict[str, Any]:
    """Handle file upload errors gracefully"""
    error_messages = {
        "UnicodeDecodeError": f"File '{filename}' contains invalid characters and cannot be read as text",
        "FileNotFoundError": f"File '{filename}' was not found",
        "PermissionError": f"Permission denied when accessing file '{filename}'",
        "OSError": f"System error when processing file '{filename}'",
        "MemoryError": f"File '{filename}' is too large to process"
    }
    
    error_type = type(error).__name__
    message = error_messages.get(error_type, f"Unknown error processing file '{filename}': {str(error)}")
    
    return {
        "filename": filename,
        "success": False,
        "error": error_type,
        "message": message
    }