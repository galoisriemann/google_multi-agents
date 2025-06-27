"""Common utility functions and helpers."""
from pathlib import Path
import logging
from typing import Any, Dict, Optional, Union


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure basic logging.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file to write logs to
    """
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        path: Path to directory
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_prompt_template(
    prompts_config: Dict[str, Any], 
    template_name: str, 
    category: Optional[str] = None
) -> str:
    """Get a specific prompt template from the loaded configuration.
    
    Args:
        prompts_config: Loaded prompts configuration
        template_name: Name of the template to retrieve
        category: Optional category under which the template is organized
        
    Returns:
        The prompt template, or empty string if not found
    """
    if category:
        return prompts_config.get(category, {}).get(template_name)
    
    # Search across all categories if no category specified
    for cat_name, cat_data in prompts_config.items():
        if isinstance(cat_data, dict) and template_name in cat_data:
            return cat_data[template_name]
    
    return ""
