#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import logging
from scan import main as scan_account
import os

def get_organization_accounts(session, log):
    """
    Get all accounts in the organization.
    
    Arguments:
    session -- The boto3 session to use.
    log -- The logger to use.
    
    Returns:
    A list of account dictionaries with Id and Name.
    """
    try:
        log.info("Getting organization accounts")
        client = session.client('organizations')
        paginator = client.get_paginator('list_accounts')
        accounts = []
        
        for page in paginator.paginate():
            for account in page.get('Accounts', []):
                if account.get('Status') == 'ACTIVE':
                    accounts.append({
                        'Id': account.get('Id'),
                        'Name': account.get('Name')
                    })
        
        log.info(f"Found {len(accounts)} active accounts in the organization")
        return accounts
    except Exception as e:
        log.error(f"Error getting organization accounts: {e}")
        return []

def assume_role(session, account_id, role_name, log):
    """
    Assume a role in a member account.
    
    Arguments:
    session -- The boto3 session to use.
    account_id -- The account ID to assume the role in.
    role_name -- The name of the role to assume.
    log -- The logger to use.
    
    Returns:
    A new boto3 session with the assumed role.
    """
    try:
        log.info(f"Assuming role {role_name} in account {account_id}")
        sts_client = session.client('sts')
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"aws-auto-inventory-{account_id}"
        )
        
        credentials = response['Credentials']
        new_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        log.info(f"Successfully assumed role in account {account_id}")
        return new_session
    except Exception as e:
        log.error(f"Error assuming role in account {account_id}: {e}")
        return None

def scan_organization(args, log):
    """
    Scan all accounts in the organization.
    
    Arguments:
    args -- The command line arguments.
    log -- The logger to use.
    
    Returns:
    None
    """
    try:
        # Create a session using the management account credentials
        session = boto3.Session()
        
        # Get all accounts in the organization
        accounts = get_organization_accounts(session, log)
        if not accounts:
            log.error("No accounts found in the organization")
            return
        
        # Get the role name to assume
        role_name = os.environ.get('ORG_ROLE_NAME', 'OrganizationAccountAccessRole')
        if hasattr(args, 'role_name') and args.role_name:
            role_name = args.role_name
        
        # Create output directory for organization scan
        timestamp = args.timestamp if hasattr(args, 'timestamp') else None
        org_output_dir = os.path.join(args.output_dir, f"organization-{timestamp}" if timestamp else "organization")
        os.makedirs(org_output_dir, exist_ok=True)
        
        # Scan each account
        for account in accounts:
            account_id = account['Id']
            account_name = account['Name']
            log.info(f"Processing account {account_name} ({account_id})")
            
            # Assume role in the account
            account_session = assume_role(session, account_id, role_name, log)
            if not account_session:
                log.error(f"Skipping account {account_name} ({account_id}) due to role assumption failure")
                continue
            
            # Create account-specific output directory
            account_output_dir = os.path.join(org_output_dir, f"{account_id}-{account_name}")
            os.makedirs(account_output_dir, exist_ok=True)
            
            # Update args for this account scan
            account_args = args
            account_args.output_dir = account_output_dir
            
            # Scan the account
            log.info(f"Starting scan for account {account_name} ({account_id})")
            scan_account(account_args, log, account_session)
            log.info(f"Completed scan for account {account_name} ({account_id})")
        
        log.info("Organization scan complete")
    except Exception as e:
        log.error(f"Error during organization scan: {e}")