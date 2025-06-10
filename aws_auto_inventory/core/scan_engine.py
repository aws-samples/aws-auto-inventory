"""
Main scanning engine for AWS Auto Inventory.
"""
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional, Union

import boto3

from ..config.models import Config, Inventory
from .organization import OrganizationScanner, AccountResult
from .region import RegionScanner, RegionResult

# Set up logger
logger = logging.getLogger(__name__)


class ScanResult:
    """
    Result of a scan.
    """
    
    def __init__(
        self, 
        inventory_name: str, 
        account_results: Optional[List[AccountResult]] = None,
        region_results: Optional[List[RegionResult]] = None
    ):
        """
        Initialize scan result.
        
        Args:
            inventory_name: Name of the inventory.
            account_results: List of account scan results (for organization scans).
            region_results: List of region scan results (for single account scans).
        """
        self.inventory_name = inventory_name
        self.account_results = account_results or []
        self.region_results = region_results or []
        self.is_organization_scan = account_results is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the scan result.
        """
        result = {
            "inventory_name": self.inventory_name,
        }
        
        if self.is_organization_scan:
            result["organization_results"] = [
                account.to_dict() for account in self.account_results
            ]
        else:
            result["account_results"] = [
                region.to_dict() for region in self.region_results
            ]
        
        return result


class ScanEngine:
    """
    Main scanning engine for AWS Auto Inventory.
    """
    
    def __init__(
        self, 
        max_retries: int = 3, 
        retry_delay: int = 2,
        max_workers_regions: Optional[int] = None,
        max_workers_services: Optional[int] = None
    ):
        """
        Initialize scan engine.
        
        Args:
            max_retries: Maximum number of retries for API calls.
            retry_delay: Base delay (in seconds) between retries.
            max_workers_regions: Maximum number of worker threads for concurrent region scanning.
            max_workers_services: Maximum number of worker threads for concurrent service scanning.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_workers_regions = max_workers_regions
        self.max_workers_services = max_workers_services
        
        self.organization_scanner = OrganizationScanner()
        self.region_scanner = RegionScanner(
            max_retries=max_retries,
            retry_delay=retry_delay,
            max_workers=max_workers_services
        )
    
    def scan(self, config: Config) -> List[ScanResult]:
        """
        Perform scanning based on configuration.
        
        Args:
            config: Configuration to use for scanning.
            
        Returns:
            List of scan results, one for each inventory in the configuration.
        """
        results = []
        
        for inventory in config.inventories:
            logger.info(f"Starting scan for inventory: {inventory.name}")
            
            if inventory.aws.organization:
                # Scan across organization
                result = self._scan_organization(inventory)
            else:
                # Scan single account
                result = self._scan_account(inventory)
            
            results.append(result)
            logger.info(f"Completed scan for inventory: {inventory.name}")
        
        return results
    
    def _scan_organization(self, inventory: Inventory) -> ScanResult:
        """
        Scan across an organization.
        
        Args:
            inventory: Inventory configuration.
            
        Returns:
            Scan result.
        """
        logger.info(f"Starting organization scan for inventory: {inventory.name}")
        
        account_results = self.organization_scanner.scan_organization(
            inventory, 
            self.region_scanner
        )
        
        logger.info(f"Completed organization scan for inventory: {inventory.name}")
        
        return ScanResult(
            inventory_name=inventory.name,
            account_results=account_results
        )
    
    def _scan_account(self, inventory: Inventory) -> ScanResult:
        """
        Scan a single account.
        
        Args:
            inventory: Inventory configuration.
            
        Returns:
            Scan result.
        """
        logger.info(f"Starting account scan for inventory: {inventory.name}")
        
        # Create session
        session = boto3.Session(profile_name=inventory.aws.profile)
        
        # Scan regions concurrently
        region_results = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers_regions
        ) as executor:
            # Create a future for each region
            future_to_region = {
                executor.submit(
                    self.region_scanner.scan_region,
                    inventory,
                    session,
                    region
                ): region
                for region in inventory.aws.region
            }
            
            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    region_result = future.result()
                    region_results.append(region_result)
                    logger.info(f"Successfully scanned region {region}")
                except Exception as e:
                    logger.error(f"Error scanning region {region}: {str(e)}")
        
        logger.info(f"Completed account scan for inventory: {inventory.name}")
        
        return ScanResult(
            inventory_name=inventory.name,
            region_results=region_results
        )