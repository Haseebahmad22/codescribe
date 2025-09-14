"""
API package for CodeScribe.
"""

from .main import app
from .utils import (
    get_file_info,
    validate_api_key,
    get_error_response,
    sanitize_filename,
    create_documentation_metadata,
    APIError,
    ValidationError,
    ProcessingError,
    AuthenticationError,
    handle_file_upload_error
)

__all__ = [
    'app',
    'get_file_info',
    'validate_api_key',
    'get_error_response',
    'sanitize_filename',
    'create_documentation_metadata',
    'APIError',
    'ValidationError',
    'ProcessingError',
    'AuthenticationError',
    'handle_file_upload_error'
]