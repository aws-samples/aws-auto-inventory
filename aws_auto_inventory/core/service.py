"""
Service scanner for AWS Auto Inventory.
"""
import logging
from typing import Dict, Any, List, Optional

import boto3

from ..config.models import Sheet
from .aws_client import AWSClient, AWSClientError

# Set up logger
logger = logging.getLogger(__name__)


class ServiceResult:
    """
    Result of a service scan.
    """
    
    def __init__(
        self, 
        service: str, 
        function: str, 
        region: str, 
        result: Any, 
        success: bool = True, 
        error: Optional[str] = None
    ):
        """
        Initialize service result.
        
        Args:
            service: AWS service name.
            function: API function name.
            region: AWS region.
            result: API response.
            success: Whether the scan was successful.
            error: Error message if scan failed.
        """
        self.service = service
        self.function = function
        self.region = region
        self.result = result
        self.success = success
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the service result.
        """
        return {
            "service": self.service,
            "function": self.function,
            "region": self.region,
            "result": self.result,
            "success": self.success,
            "error": self.error
        }


class ServiceScanner:
    """
    Scanner for AWS services.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize service scanner.
        
        Args:
            max_retries: Maximum number of retries for API calls.
            retry_delay: Base delay (in seconds) between retries.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def scan_service(
        self, 
        sheet: Sheet, 
        session: boto3.Session, 
        region: str
    ) -> ServiceResult:
        """
        Scan a service in a region.
        
        Args:
            sheet: Sheet configuration.
            session: boto3 Session.
            region: AWS region.
            
        Returns:
            Service scan result.
        """
        logger.info(
            f"Scanning service {sheet.service} with function {sheet.function} in region {region}"
        )
        
        aws_client = AWSClient(session, self.max_retries, self.retry_delay)
        
        try:
            result = aws_client.call_api(
                sheet.service,
                sheet.function,
                region,
                sheet.parameters,
                sheet.result_key
            )
            
            logger.info(
                f"Successfully scanned service {sheet.service} with function {sheet.function} in region {region}"
            )
            
            return ServiceResult(
                service=sheet.service,
                function=sheet.function,
                region=region,
                result=result
            )
        
        except AWSClientError as e:
            logger.error(
                f"Error scanning service {sheet.service} with function {sheet.function} in region {region}: {str(e)}"
            )
            
            return ServiceResult(
                service=sheet.service,
                function=sheet.function,
                region=region,
                result=None,
                success=False,
                error=str(e)
            )
        
        except Exception as e:
            logger.error(
                f"Unexpected error scanning service {sheet.service} with function {sheet.function} in region {region}: {str(e)}"
            )
            
            return ServiceResult(
                service=sheet.service,
                function=sheet.function,
                region=region,
                result=None,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )


class ResourceFilter:
    """
    Filter for AWS resources.
    """
    
    def apply_filters(self, results: Any, filters: Dict[str, Any]) -> Any:
        """
        Apply filters to results.
        
        Args:
            results: API results.
            filters: Filters to apply.
            
        Returns:
            Filtered results.
        """
        # This is a placeholder for more complex filtering logic
        # In a real implementation, this would apply JMESPath or similar filtering
        
        if not filters or not results:
            return results
        
        # For now, just return the results as is
        return results