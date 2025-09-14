"""
CLI package for CodeScribe.
"""

from .main import CodeScribeCLI, main
from .utils import (
    validate_file_path,
    validate_directory_path,
    get_supported_files,
    estimate_processing_time,
    format_file_size,
    check_dependencies,
    print_dependency_status,
    ColoredOutput
)

__all__ = [
    'CodeScribeCLI',
    'main',
    'validate_file_path',
    'validate_directory_path',
    'get_supported_files',
    'estimate_processing_time',
    'format_file_size',
    'check_dependencies',
    'print_dependency_status',
    'ColoredOutput'
]