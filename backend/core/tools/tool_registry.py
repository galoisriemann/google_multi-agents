"""Tool registry for flexible agent workflows.

This module provides a registry system for tools that can be used by flexible agents,
along with example tool implementations.
"""

import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class FlexibleToolRegistry:
    """Registry for tools that can be used by flexible agents.
    
    This class provides a centralized registry for tools that can be
    dynamically loaded and used by different types of flexible agents.
    """
    _tools: Dict[str, Callable] = {}

    @classmethod
    def register(cls, func: Callable) -> Callable:
        """Register a tool function.
        
        Args:
            func: The function to register as a tool
            
        Returns:
            The same function (for use as a decorator)
        """
        cls._tools[func.__name__] = func
        logger.debug(f"Registered tool: {func.__name__}")
        return func

    @classmethod
    def get(cls, name: str) -> Callable:
        """Get a registered tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The tool function
            
        Raises:
            KeyError: If the tool is not found in the registry
        """
        if name in cls._tools:
            return cls._tools[name]
        raise KeyError(f"Tool '{name}' not found in registry. Available tools: {cls.list_tools()}")

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of all registered tool names
        """
        return list(cls._tools.keys())

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered tools (useful for testing)."""
        cls._tools.clear()
        logger.debug("Tool registry cleared")


# ----------------------------------------------------------------------------
# Example Tools (can be extended or replaced with custom tools)
# ----------------------------------------------------------------------------

@FlexibleToolRegistry.register
def text_processor(text: str) -> str:
    """Example tool: process text with basic formatting.
    
    Args:
        text: Input text to process
        
    Returns:
        Processed text with additional formatting
    """
    processed = text.strip()
    if processed:
        processed = f"Processed: {processed}"
    return processed


@FlexibleToolRegistry.register
def text_analyzer(text: str) -> str:
    """Example tool: analyze text and provide basic metrics.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Analysis results including character count, word count, etc.
    """
    if not text:
        return "Analysis: Empty text provided"
    
    char_count = len(text)
    word_count = len(text.split())
    line_count = len(text.splitlines())
    
    analysis = f"""Analysis of text:
- Character count: {char_count}
- Word count: {word_count}
- Line count: {line_count}
- Average words per line: {word_count / max(line_count, 1):.1f}

Content preview: {text[:100]}{'...' if len(text) > 100 else ''}"""
    
    return analysis


@FlexibleToolRegistry.register
def code_formatter(code: str) -> str:
    """Example tool: format code with basic indentation.
    
    Args:
        code: Input code to format
        
    Returns:
        Formatted code with proper indentation
    """
    if not code:
        return "# No code provided"
    
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue
            
        # Simple indentation logic
        if stripped.endswith(':'):
            formatted_lines.append('    ' * indent_level + stripped)
            indent_level += 1
        elif stripped.startswith(('except', 'elif', 'else', 'finally')):
            indent_level = max(0, indent_level - 1)
            formatted_lines.append('    ' * indent_level + stripped)
            indent_level += 1
        else:
            formatted_lines.append('    ' * indent_level + stripped)
    
    formatted_code = '\n'.join(formatted_lines)
    return f"Formatted code:\n```\n{formatted_code}\n```"


@FlexibleToolRegistry.register
def data_validator(data: str) -> str:
    """Example tool: validate data format and structure.
    
    Args:
        data: Input data to validate
        
    Returns:
        Validation results and recommendations
    """
    if not data:
        return "Validation: No data provided"
    
    validation_results = []
    
    # Check if it looks like JSON
    if data.strip().startswith(('{', '[')):
        try:
            import json
            json.loads(data)
            validation_results.append("✅ Valid JSON format")
        except json.JSONDecodeError:
            validation_results.append("❌ Invalid JSON format")
    
    # Check if it looks like YAML
    elif ':' in data and not data.strip().startswith('<'):
        validation_results.append("📝 Appears to be YAML format")
    
    # Check if it looks like XML/HTML
    elif data.strip().startswith('<'):
        validation_results.append("🏷️ Appears to be XML/HTML format")
    
    # Check if it looks like CSV
    elif ',' in data or '\t' in data:
        validation_results.append("📊 Appears to be CSV/TSV format")
    
    # Basic content validation
    if len(data) > 10000:
        validation_results.append("⚠️ Large data size (>10k characters)")
    
    if not data.strip():
        validation_results.append("❌ Empty or whitespace-only data")
    
    return f"Validation results:\n" + '\n'.join(validation_results) 