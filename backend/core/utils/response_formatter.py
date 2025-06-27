"""Utilities for formatting agent responses with citations and metadata."""
from typing import Dict, List, Optional, Any


def format_response(
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    tool_usage: Optional[List[Dict[str, Any]]] = None,
    query: str = "",
    model_id: str = "",
    **metadata
) -> Dict[str, Any]:
    """Format a response with optional citations and metadata.
    
    Args:
        content: The main content of the response
        sources: List of source dictionaries with 'title', 'url', 'domain'
        tool_usage: List of tools used with their details
        query: The original query
        model_id: ID of the model used
        **metadata: Additional metadata to include
        
    Returns:
        Dictionary with formatted response and metadata
    """
    sources = sources or []
    tool_usage = tool_usage or []
    
    # Build citations section if sources are provided
    citations = ""
    if sources:
        citations += "\n\n## Sources\n"
        for i, source in enumerate(sources, 1):
            citations += f"{i}. **{source.get('title', 'Untitled')}**\n"
            if 'url' in source and source['url'] != 'N/A':
                citations += f"   - URL: {source['url']}\n"
            if 'domain' in source:
                citations += f"   - Domain: {source['domain']}\n"
    
    # Add tool usage information if available
    tool_info = ""
    if tool_usage:
        tool_info = "\n\n## Tools Used\n"
        for tool in tool_usage:
            tool_info += f"- {tool.get('name', 'Unknown')}: {tool.get('description', '')}\n"
    
    # Combine all sections
    formatted_content = f"{content}{citations}{tool_info}"
    
    # Prepare metadata
    response_metadata = {
        "query": query,
        "model_id": model_id,
        "source_count": len(sources),
        "tool_count": len(tool_usage),
        **metadata
    }
    
    return {
        "content": formatted_content,
        "metadata": response_metadata
    }


def format_error_response(
    error: Exception,
    query: str = "",
    context: str = "",
    **metadata
) -> Dict[str, Any]:
    """Format an error response.
    
    Args:
        error: The exception that occurred
        query: The original query that caused the error
        context: Additional context about where the error occurred
        **metadata: Additional metadata to include
        
    Returns:
        Dictionary with error information
    """
    error_info = {
        "error": str(error),
        "error_type": error.__class__.__name__,
        "query": query,
        "context": context,
        **metadata
    }
    
    return {
        "content": f"An error occurred: {str(error)}",
        "metadata": error_info,
        "is_error": True
    }
