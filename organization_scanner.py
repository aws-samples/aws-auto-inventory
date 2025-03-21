# -*- coding: utf-8 -*-
import boto3
import os
import json
from scan import main as scan_account
from datetime import datetime

def get_organization_accounts(session):
    """Get all active accounts in the AWS Organization.
    
    Args:
        session: The boto3 Session for the management account.
        
    Returns:
        A list of dictionaries containing account information (id, name, email).
    """
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
    except Exception as e:
        print(f"Error retrieving organization accounts: {e}")
        return []
    
    return accounts

def assume_role(session, account_id, role_name):
    """Assume a role in the specified account.
    
    Args:
        session: The boto3 Session for the management account.
        account_id: The AWS account ID to assume the role in.
        role_name: The name of the IAM role to assume.
        
    Returns:
        A new boto3 Session with the assumed role credentials, or None if the role assumption fails.
    """
    sts_client = session.client('sts')
    
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='AWSAutoInventorySession',
            DurationSeconds=3600
        )
        
        credentials = response['Credentials']
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
    except Exception as e:
        print(f"Failed to assume role in account {account_id}: {e}")
        return None

def scan_organization(org_role_name, scan_config, regions, output_dir, log_level, max_retries, retry_delay, concurrent_regions, concurrent_services):
    """Scan resources across all accounts in an organization.
    
    Args:
        org_role_name: The IAM role name to assume in each account.
        scan_config: The path to the JSON file or URL containing the AWS services to scan.
        regions: The AWS regions to scan.
        output_dir: The directory to store the results.
        log_level: The log level for the script.
        max_retries: The maximum number of retries for each service.
        retry_delay: The delay before each retry.
        concurrent_regions: The number of regions to process concurrently.
        concurrent_services: The number of services to process concurrently for each region.
    """
    # Get the management account session
    management_session = boto3.Session()
    
    # Create organization output directory with timestamp
    timestamp = datetime.now().isoformat(timespec="minutes").replace(":", "-")
    org_output_dir = os.path.join(output_dir, f"organization-{timestamp}")
    os.makedirs(org_output_dir, exist_ok=True)
    
    # Get all accounts in the organization
    print("Discovering accounts in the organization...")
    accounts = get_organization_accounts(management_session)
    print(f"Found {len(accounts)} active accounts in the organization.")
    
    # Save account information
    with open(os.path.join(org_output_dir, "accounts.json"), "w") as f:
        json.dump(accounts, f, indent=2)
    
    # Scan each account
    for account in accounts:
        account_id = account['id']
        account_name = account['name']
        
        print(f"\nProcessing account: {account_name} ({account_id})")
        
        # Assume role in the account
        print(f"Assuming role {org_role_name} in account {account_id}...")
        account_session = assume_role(management_session, account_id, org_role_name)
        
        if account_session:
            print(f"Successfully assumed role in account {account_id}")
            
            # Create account-specific output directory
            account_output_dir = os.path.join(org_output_dir, account_id)
            os.makedirs(account_output_dir, exist_ok=True)
            
            # Save account metadata
            with open(os.path.join(account_output_dir, "account_info.json"), "w") as f:
                json.dump(account, f, indent=2)
            
            # Run the scan for this account
            print(f"Starting scan for account {account_id}...")
            scan_account(
                scan_config,
                regions,
                account_output_dir,
                log_level,
                max_retries,
                retry_delay,
                concurrent_regions,
                concurrent_services,
                session=account_session
            )
            print(f"Completed scan for account {account_id}")
        else:
            print(f"Skipping account {account_name} ({account_id}) due to role assumption failure")
    
    print(f"\nOrganization scan complete. Results stored in {org_output_dir}")