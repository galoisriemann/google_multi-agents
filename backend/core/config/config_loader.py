"""Core configuration loader and validator."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ConfigLoader:
    """Load and validate configuration from YAML files."""
    
    def __init__(self, config_path: Union[str, Path]):
        """Initialize with path to config file or directory."""
        self.config_path = Path(config_path)
        self.config = {}
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.is_dir():
            raise ValueError(f"Expected config file, got directory: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        
        return self.config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def validate_required_keys(self, required_keys: list[str]) -> list[str]:
        """Validate that required configuration keys are present."""
        missing_keys = []
        for key_path in required_keys:
            if self.get_value(key_path) is None:
                missing_keys.append(key_path)
        return missing_keys


def load_prompts_config(prompts_path: Union[str, Path]) -> Dict[str, Any]:
    """Load prompts configuration from YAML file."""
    prompts_path = Path(prompts_path)
    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"⚠️ Prompts file not found at {prompts_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"⚠️ Error parsing prompts YAML: {e}")
        return {}
