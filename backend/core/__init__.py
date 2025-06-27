"""Core package for shared components and utilities."""

# Import key components to make them easily accessible
from .config.config_loader import ConfigLoader
from .agents.base_agent import BaseResearchAgent
from .utils.common import setup_logging, ensure_directory, get_prompt_template
from .utils.response_formatter import format_response, format_error_response

__all__ = [
    'ConfigLoader',
    'BaseResearchAgent',
    'setup_logging',
    'ensure_directory',
    'get_prompt_template',
    'format_response',
    'format_error_response'
]
