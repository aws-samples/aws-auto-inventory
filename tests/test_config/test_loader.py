"""
Tests for the configuration loader.
"""
import os
import tempfile
import pytest
from aws_auto_inventory.config.loader import ConfigLoader


@pytest.fixture
def yaml_config_file():
    """Create a temporary YAML configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        f.write(b"""
inventories:
  - name: test-inventory
    aws:
      region:
        - us-east-1
    sheets:
      - name: EC2
        service: ec2
        function: describe_instances
""")
    yield f.name
    os.unlink(f.name)


@pytest.fixture
def json_config_file():
    """Create a temporary JSON configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b"""
{
  "inventories": [
    {
      "name": "test-inventory",
      "aws": {
        "region": ["us-east-1"]
      },
      "sheets": [
        {
          "name": "EC2",
          "service": "ec2",
          "function": "describe_instances"
        }
      ]
    }
  ]
}
""")
    yield f.name
    os.unlink(f.name)


@pytest.fixture
def legacy_json_config_file():
    """Create a temporary legacy JSON configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b"""
[
  {
    "service": "ec2",
    "function": "describe_instances",
    "result_key": "Reservations"
  },
  {
    "service": "s3",
    "function": "list_buckets",
    "result_key": "Buckets"
  }
]
""")
    yield f.name
    os.unlink(f.name)


def test_load_yaml_config(yaml_config_file):
    """Test loading a YAML configuration file."""
    loader = ConfigLoader()
    config = loader.load_config(yaml_config_file)
    
    assert config.inventories[0].name == "test-inventory"
    assert config.inventories[0].aws.region == ["us-east-1"]
    assert config.inventories[0].sheets[0].name == "EC2"
    assert config.inventories[0].sheets[0].service == "ec2"
    assert config.inventories[0].sheets[0].function == "describe_instances"


def test_load_json_config(json_config_file):
    """Test loading a JSON configuration file."""
    loader = ConfigLoader()
    config = loader.load_config(json_config_file)
    
    assert config.inventories[0].name == "test-inventory"
    assert config.inventories[0].aws.region == ["us-east-1"]
    assert config.inventories[0].sheets[0].name == "EC2"
    assert config.inventories[0].sheets[0].service == "ec2"
    assert config.inventories[0].sheets[0].function == "describe_instances"


def test_load_legacy_json_config(legacy_json_config_file):
    """Test loading a legacy JSON configuration file."""
    loader = ConfigLoader()
    config = loader.load_config(legacy_json_config_file)
    
    assert len(config.inventories) == 1
    assert config.inventories[0].name == "default"
    assert len(config.inventories[0].sheets) == 2
    
    assert config.inventories[0].sheets[0].service == "ec2"
    assert config.inventories[0].sheets[0].function == "describe_instances"
    assert config.inventories[0].sheets[0].result_key == "Reservations"
    
    assert config.inventories[0].sheets[1].service == "s3"
    assert config.inventories[0].sheets[1].function == "list_buckets"
    assert config.inventories[0].sheets[1].result_key == "Buckets"


def test_file_not_found():
    """Test handling of a non-existent configuration file."""
    loader = ConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_config("non_existent_file.yaml")