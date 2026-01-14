"""
AWS client with retry logic for AWS Auto Inventory.
"""
import time
import json
import logging
from typing import Optional, Dict, Any, Union

import boto3
import botocore
import jq

# Set up logger
logger = logging.getLogger(__name__)


class AWSClientError(Exception):
    """Base exception for AWS client errors."""
    pass


class ThrottlingError(AWSClientError):
    """Exception raised when AWS API throttling occurs."""
    def __init__(self, service: str, function: str, retry_after: Optional[int] = None):
        self.service = service
        self.function = function
        self.retry_after = retry_after
        super().__init__(f"API throttling for {service}.{function}")


class AWSClient:
    """
    AWS client with retry logic for API calls.
    """
    
    def __init__(self, session: boto3.Session, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize AWS client.
        
        Args:
            session: boto3 Session.
            max_retries: Maximum number of retries for API calls.
            retry_delay: Base delay (in seconds) between retries.
        """
        self.session = session
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def call_api(
        self, 
        service: str, 
        function_name: str, 
        region: Optional[str] = None, 
        parameters: Optional[Dict[str, Any]] = None,
        result_key: Optional[str] = None
    ) -> Any:
        """
        Call AWS API with retry logic.
        
        Args:
            service: AWS service name.
            function_name: API function name.
            region: AWS region.
            parameters: API parameters.
            result_key: Key to extract from the response.
            
        Returns:
            API response or extracted data if result_key is specified.
            
        Raises:
            AWSClientError: If the API call fails after all retries.
        """
        client = self.session.client(service, region_name=region)
        
        if not hasattr(client, function_name):
            raise AWSClientError(f"Function {function_name} does not exist for service {service}")
        
        function_to_call = getattr(client, function_name)
        
        for attempt in range(self.max_retries):
            try:
                if parameters:
                    response = function_to_call(**parameters)
                else:
                    response = function_to_call()
                
                # Process the response
                if result_key:
                    if result_key.startswith('.'):
                        # Use jq for complex queries
                        return jq.compile(result_key).input_value(json.loads(json.dumps(response, default=str))).all()
                    else:
                        # Simple key extraction
                        return response.get(result_key)
                else:
                    # Return full response with metadata removed
                    if isinstance(response, dict):
                        response.pop("ResponseMetadata", None)
                    return response
                
            except botocore.exceptions.ClientError as error:
                error_code = error.response["Error"]["Code"]
                if error_code in ["Throttling", "RequestLimitExceeded"]:
                    if attempt < (self.max_retries - 1):
                        wait_time = self.retry_delay ** attempt
                        logger.warning(
                            f"Throttling for {service}.{function_name}, retrying in {wait_time}s "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ThrottlingError(service, function_name)
                else:
                    logger.error(f"AWS API error for {service}.{function_name}: {error}")
                    raise AWSClientError(f"AWS API error: {error}")
            except botocore.exceptions.BotoCoreError as error:
                if attempt < (self.max_retries - 1):
                    wait_time = self.retry_delay ** attempt
                    logger.warning(
                        f"BotoCore error for {service}.{function_name}, retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"BotoCore error for {service}.{function_name}: {error}")
                    raise AWSClientError(f"BotoCore error: {error}")
            except Exception as error:
                logger.error(f"Unexpected error for {service}.{function_name}: {error}")
                raise AWSClientError(f"Unexpected error: {error}")
        
        # This should not be reached, but just in case
        raise AWSClientError(f"Failed to call {service}.{function_name} after {self.max_retries} attempts")