"""
Organization scanner for AWS Auto Inventory.
"""
import logging
from typing import Dict, Any, List, Optional

import boto3

from ..config.models import Inventory
from .region import RegionScanner, RegionResult

# Set up logger
logger = logging.getLogger(__name__)


class AccountResult:
    """
    Result of an account scan.
    """
    
    def __init__(
        self, 
        account_id: str, 
        account_name: str, 
        regions: List[RegionResult],
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Initialize account result.
        
        Args:
            account_id: AWS account ID.
            account_name: AWS account name.
            regions: List of region scan results.
            success: Whether the scan was successful.
            error: Error message if scan failed.
        """
        self.account_id = account_id
        self.account_name = account_name
        self.regions = regions
        self.success = success
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the account result.
        """
        return {
            "account_id": self.account_id,
            "account_name": self.account_name,
            "regions": [region.to_dict() for region in self.regions],
            "success": self.success,
            "error": self.error
        }


class OrganizationScanner:
    """
    Scanner for AWS organizations.
    """
    
    def __init__(self):
        """
        Initialize organization scanner.
        """
        pass
    
    def get_organization_accounts(self, session: boto3.Session) -> List[Dict[str, str]]:
        """
        Get all active accounts in the AWS Organization.
        
        Args:
            session: boto3 Session for the management account.
            
        Returns:
            List of dictionaries containing account information (id, name, email).
        """
        logger.info("Discovering accounts in the organization")
        
        org_client = session.client('organizations')
        accounts = []
        
        try:
            paginator = org_client.get_paginator('list_accounts')
            for page in paginator.paginate():
                for account in page['Accounts']:
                    if account['Status'] == 'ACTIVE':
                        accounts.append({
                            'id': account['Id'],
                            'name': account['Name'],
                            'email': account['Email']
                        })
            
            logger.info(f"Found {len(accounts)} active accounts in the organization")
        
        except Exception as e:
            logger.error(f"Error retrieving organization accounts: {str(e)}")
            return []
        
        return accounts
    
    def assume_role(
        self, 
        session: boto3.Session, 
        account_id: str, 
        role_name: str
    ) -> Optional[boto3.Session]:
        """
        Assume a role in the specified account.
        
        Args:
            session: boto3 Session for the management account.
            account_id: AWS account ID to assume the role in.
            role_name: Name of the IAM role to assume.
            
        Returns:
            New boto3 Session with the assumed role credentials, or None if the role assumption fails.
        """
        logger.info(f"Assuming role {role_name} in account {account_id}")
        
        sts_client = session.client('sts')
        role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
        
        try:
            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName='AWSAutoInventorySession',
                DurationSeconds=3600
            )
            
            credentials = response['Credentials']
            assumed_session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            
            logger.info(f"Successfully assumed role in account {account_id}")
            return assumed_session
        
        except Exception as e:
            logger.error(f"Failed to assume role in account {account_id}: {str(e)}")
            return None
    
    def scan_organization(
        self, 
        inventory: Inventory, 
        region_scanner: RegionScanner
    ) -> List[AccountResult]:
        """
        Scan resources across all accounts in an organization.
        
        Args:
            inventory: Inventory configuration.
            region_scanner: Region scanner to use for scanning regions.
            
        Returns:
            List of account scan results.
        """
        logger.info("Starting organization scan")
        
        # Get the management account session
        management_session = boto3.Session(profile_name=inventory.aws.profile)
        
        # Get all accounts in the organization
        accounts = self.get_organization_accounts(management_session)
        
        if not accounts:
            logger.warning("No accounts found in the organization")
            return []
        
        account_results = []
        
        # Scan each account
        for account in accounts:
            account_id = account['id']
            account_name = account['name']
            
            logger.info(f"Processing account: {account_name} ({account_id})")
            
            # Assume role in the account
            account_session = self.assume_role(
                management_session, 
                account_id, 
                inventory.aws.role_name
            )
            
            if account_session:
                # Scan regions in the account
                region_results = []
                
                for region in inventory.aws.region:
                    try:
                        region_result = region_scanner.scan_region(
                            inventory, 
                            account_session, 
                            region
                        )
                        region_results.append(region_result)
                    except Exception as e:
                        logger.error(f"Error scanning region {region} in account {account_id}: {str(e)}")
                
                account_results.append(
                    AccountResult(
                        account_id=account_id,
                        account_name=account_name,
                        regions=region_results
                    )
                )
            else:
                account_results.append(
                    AccountResult(
                        account_id=account_id,
                        account_name=account_name,
                        regions=[],
                        success=False,
                        error=f"Failed to assume role in account {account_id}"
                    )
                )
        
        logger.info("Completed organization scan")
        
        return account_results