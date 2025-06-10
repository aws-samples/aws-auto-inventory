"""
Configuration loader for AWS Auto Inventory.
"""
import os
import json
import yaml
from typing import Union, Dict, Any

from .models import Config


class ConfigLoader:
    """
    Configuration loader that supports both YAML and JSON formats.
    """
    
    def load_config(self, path: str) -> Config:
        """
        Load configuration from file.
        
        Args:
            path: Path to the configuration file.
            
        Returns:
            Config object.
            
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the configuration file format is not supported.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        format_type = self._detect_format(path)
        
        with open(path, 'r') as f:
            if format_type == 'yaml':
                config_data = yaml.safe_load(f)
            elif format_type == 'json':
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {format_type}")
        
        # Handle legacy format if needed
        if self._is_legacy_format(config_data):
            config_data = self._convert_legacy_format(config_data)
        
        return Config.from_dict(config_data)
    
    def _detect_format(self, path: str) -> str:
        """
        Detect file format based on extension.
        
        Args:
            path: Path to the configuration file.
            
        Returns:
            Format type ('yaml' or 'json').
        """
        _, ext = os.path.splitext(path)
        if ext.lower() in ['.yaml', '.yml']:
            return 'yaml'
        elif ext.lower() == '.json':
            return 'json'
        else:
            # Default to JSON if extension is not recognized
            return 'json'
    
    def _is_legacy_format(self, config_data: Union[Dict[str, Any], list]) -> bool:
        """
        Check if the configuration is in legacy format.
        
        Args:
            config_data: Configuration data.
            
        Returns:
            True if the configuration is in legacy format, False otherwise.
        """
        # Legacy JSON format is a list of dictionaries with 'service' and 'function' keys
        if isinstance(config_data, list) and len(config_data) > 0:
            first_item = config_data[0]
            return isinstance(first_item, dict) and 'service' in first_item and 'function' in first_item
        
        # Legacy YAML format has 'sheets' at the top level but no 'inventories'
        if isinstance(config_data, dict):
            return 'inventories' not in config_data and 'sheets' in config_data
        
        return False
    
    def _convert_legacy_format(self, config_data: Union[Dict[str, Any], list]) -> Dict[str, Any]:
        """
        Convert legacy format to new format.
        
        Args:
            config_data: Configuration data in legacy format.
            
        Returns:
            Configuration data in new format.
        """
        if isinstance(config_data, list):
            # Convert legacy JSON format
            return {
                "inventories": [
                    {
                        "name": "default",
                        "aws": {},
                        "sheets": [
                            {
                                "name": f"{item['service']}_{item['function']}",
                                "service": item['service'],
                                "function": item['function'],
                                "result_key": item.get('result_key'),
                                "parameters": item.get('parameters', {})
                            }
                            for item in config_data
                        ]
                    }
                ]
            }
        elif isinstance(config_data, dict):
            # Convert legacy YAML format
            return {
                "inventories": [
                    {
                        "name": config_data.get('name', 'default'),
                        "aws": config_data.get('aws', {}),
                        "sheets": config_data.get('sheets', []),
                        "excel": config_data.get('excel', {})
                    }
                ]
            }
        
        # Return as is if we can't convert
        return config_data