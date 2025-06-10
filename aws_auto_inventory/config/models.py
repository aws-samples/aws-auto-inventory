"""
Configuration models for AWS Auto Inventory.
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field


class ExcelConfig(BaseModel):
    """Excel output configuration."""
    transpose: bool = False
    formatting: Dict[str, Any] = Field(default_factory=dict)


class AWSConfig(BaseModel):
    """AWS configuration."""
    profile: Optional[str] = None
    region: List[str] = Field(default_factory=lambda: ["us-east-1"])
    organization: bool = False
    role_name: str = "OrganizationAccountAccessRole"


class Sheet(BaseModel):
    """Sheet configuration for inventory."""
    name: str
    service: str
    function: str
    result_key: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Inventory(BaseModel):
    """Inventory configuration."""
    name: str
    aws: AWSConfig = Field(default_factory=AWSConfig)
    sheets: List[Sheet]
    excel: ExcelConfig = Field(default_factory=ExcelConfig)


class Config(BaseModel):
    """Main configuration model."""
    inventories: List[Inventory]
    
    def to_json(self):
        """Convert config to JSON string."""
        return self.json(indent=2)
    
    def to_yaml(self):
        """Convert config to YAML string."""
        import yaml
        return yaml.dump(self.dict(), sort_keys=False)
    
    @classmethod
    def from_dict(cls, data):
        """Create config from dictionary."""
        return cls(**data)