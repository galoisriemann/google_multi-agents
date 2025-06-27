"""Utility functions for file operations."""
import os
from pathlib import Path
from typing import Union

def ensure_directory_exists(directory: Union[str, Path]) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory that should exist
        
    Raises:
        OSError: If the directory cannot be created
    """
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise OSError(f"Failed to create directory {directory}: {str(e)}") from e
