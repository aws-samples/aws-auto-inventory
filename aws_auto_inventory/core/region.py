"""
Region scanner for AWS Auto Inventory.
"""
import logging
import concurrent.futures
from typing import Dict, Any, List, Optional

import boto3

from ..config.models import Inventory, Sheet
from .service import ServiceScanner, ServiceResult

# Set up logger
logger = logging.getLogger(__name__)


class RegionResult:
    """
    Result of a region scan.
    """
    
    def __init__(self, region: str, services: List[ServiceResult]):
        """
        Initialize region result.
        
        Args:
            region: AWS region.
            services: List of service scan results.
        """
        self.region = region
        self.services = services
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the region result.
        """
        return {
            "region": self.region,
            "services": [service.to_dict() for service in self.services]
        }


class RegionScanner:
    """
    Scanner for AWS regions.
    """
    
    def __init__(
        self, 
        max_retries: int = 3, 
        retry_delay: int = 2, 
        max_workers: Optional[int] = None
    ):
        """
        Initialize region scanner.
        
        Args:
            max_retries: Maximum number of retries for API calls.
            retry_delay: Base delay (in seconds) between retries.
            max_workers: Maximum number of worker threads for concurrent service scanning.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_workers = max_workers
        self.service_scanner = ServiceScanner(max_retries, retry_delay)
    
    def scan_region(
        self, 
        inventory: Inventory, 
        session: boto3.Session, 
        region: str
    ) -> RegionResult:
        """
        Scan all services in a region.
        
        Args:
            inventory: Inventory configuration.
            session: boto3 Session.
            region: AWS region.
            
        Returns:
            Region scan result.
        """
        logger.info(f"Scanning region {region}")
        
        services_results = []
        
        # Use ThreadPoolExecutor for concurrent service scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a future for each service
            future_to_sheet = {
                executor.submit(
                    self.service_scanner.scan_service,
                    sheet,
                    session,
                    region
                ): sheet
                for sheet in inventory.sheets
            }
            
            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_sheet):
                sheet = future_to_sheet[future]
                try:
                    service_result = future.result()
                    services_results.append(service_result)
                    
                    if service_result.success:
                        logger.info(
                            f"Successfully scanned service {sheet.service} with function {sheet.function} in region {region}"
                        )
                    else:
                        logger.warning(
                            f"Failed to scan service {sheet.service} with function {sheet.function} in region {region}: {service_result.error}"
                        )
                
                except Exception as e:
                    logger.error(
                        f"Error processing service {sheet.service} with function {sheet.function} in region {region}: {str(e)}"
                    )
                    
                    services_results.append(
                        ServiceResult(
                            service=sheet.service,
                            function=sheet.function,
                            region=region,
                            result=None,
                            success=False,
                            error=f"Error processing service: {str(e)}"
                        )
                    )
        
        logger.info(f"Completed scanning region {region}")
        
        return RegionResult(region=region, services=services_results)