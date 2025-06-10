"""
Configuration validator for AWS Auto Inventory.
"""
import boto3
from typing import List, Optional, Dict, Any

from .models import Config, Inventory, Sheet


class ConfigValidator:
    """
    Validates AWS Auto Inventory configurations.
    """
    
    def validate(self, config: Config) -> List[str]:
        """
        Validate a configuration.
        
        Args:
            config: Configuration to validate.
            
        Returns:
            List of validation errors. Empty list if configuration is valid.
        """
        errors = []
        
        # Check if there are any inventories
        if not config.inventories:
            errors.append("No inventories defined in configuration")
            return errors
        
        # Validate each inventory
        for inventory in config.inventories:
            inventory_errors = self._validate_inventory(inventory)
            errors.extend([f"Inventory '{inventory.name}': {error}" for error in inventory_errors])
        
        return errors
    
    def _validate_inventory(self, inventory: Inventory) -> List[str]:
        """
        Validate an inventory configuration.
        
        Args:
            inventory: Inventory to validate.
            
        Returns:
            List of validation errors. Empty list if inventory is valid.
        """
        errors = []
        
        # Check if there are any sheets
        if not inventory.sheets:
            errors.append("No sheets defined")
            return errors
        
        # Validate AWS configuration
        aws_errors = self._validate_aws_config(inventory)
        errors.extend(aws_errors)
        
        # Validate each sheet
        for sheet in inventory.sheets:
            sheet_errors = self._validate_sheet(sheet)
            errors.extend([f"Sheet '{sheet.name}': {error}" for error in sheet_errors])
        
        return errors
    
    def _validate_aws_config(self, inventory: Inventory) -> List[str]:
        """
        Validate AWS configuration.
        
        Args:
            inventory: Inventory containing AWS configuration.
            
        Returns:
            List of validation errors. Empty list if AWS configuration is valid.
        """
        errors = []
        
        # Check if regions are specified
        if not inventory.aws.region:
            errors.append("No regions specified")
        
        # Check if profile exists (if specified)
        if inventory.aws.profile:
            try:
                session = boto3.Session(profile_name=inventory.aws.profile)
                # Try to get caller identity to verify credentials
                sts = session.client('sts')
                sts.get_caller_identity()
            except Exception as e:
                errors.append(f"Invalid AWS profile '{inventory.aws.profile}': {str(e)}")
        
        return errors
    
    def _validate_sheet(self, sheet: Sheet) -> List[str]:
        """
        Validate a sheet configuration.
        
        Args:
            sheet: Sheet to validate.
            
        Returns:
            List of validation errors. Empty list if sheet is valid.
        """
        errors = []
        
        # Check required fields
        if not sheet.service:
            errors.append("No service specified")
        
        if not sheet.function:
            errors.append("No function specified")
        
        # Check if service and function exist in boto3
        try:
            session = boto3.Session()
            if sheet.service not in session.get_available_services():
                errors.append(f"Invalid AWS service: {sheet.service}")
            else:
                # Check if function exists
                client = session.client(sheet.service, region_name='us-east-1')
                if not hasattr(client, sheet.function):
                    errors.append(f"Function '{sheet.function}' does not exist for service '{sheet.service}'")
                elif not sheet.function.startswith(('describe_', 'get_', 'list_')):
                    errors.append(f"Function '{sheet.function}' is not a read-only operation")
        except Exception as e:
            errors.append(f"Error validating service and function: {str(e)}")
        
        return errors