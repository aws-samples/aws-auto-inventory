import pytest
import boto3
from organization_scanner import scan_organization
import logging
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_logger():
    return logging.getLogger("test")

@pytest.fixture
def mock_args():
    args = MagicMock()
    args.output_dir = "test_output"
    args.timestamp = "2025-03-21T08-33"
    args.role_name = "TestRole"
    return args

@patch('organization_scanner.get_organization_accounts')
@patch('organization_scanner.assume_role')
@patch('organization_scanner.scan_account')
@patch('os.makedirs')
def test_scan_organization_success(mock_makedirs, mock_scan_account, mock_assume_role, mock_get_accounts, mock_args, mock_logger):
    # Mock the get_organization_accounts function
    mock_get_accounts.return_value = [
        {'Id': '123456789012', 'Name': 'Account1'},
        {'Id': '234567890123', 'Name': 'Account2'}
    ]
    
    # Mock the assume_role function
    mock_session = MagicMock()
    mock_assume_role.return_value = mock_session
    
    # Call the function
    scan_organization(mock_args, mock_logger)
    
    # Verify the results
    assert mock_get_accounts.call_count == 1
    assert mock_assume_role.call_count == 2
    assert mock_scan_account.call_count == 2
    
    # Verify the makedirs calls
    expected_org_dir = os.path.join("test_output", "organization-2025-03-21T08-33")
    expected_account1_dir = os.path.join(expected_org_dir, "123456789012-Account1")
    expected_account2_dir = os.path.join(expected_org_dir, "234567890123-Account2")
    
    mock_makedirs.assert_any_call(expected_org_dir, exist_ok=True)
    mock_makedirs.assert_any_call(expected_account1_dir, exist_ok=True)
    mock_makedirs.assert_any_call(expected_account2_dir, exist_ok=True)

@patch('organization_scanner.get_organization_accounts')
@patch('organization_scanner.assume_role')
@patch('organization_scanner.scan_account')
@patch('os.makedirs')
def test_scan_organization_no_accounts(mock_makedirs, mock_scan_account, mock_assume_role, mock_get_accounts, mock_args, mock_logger):
    # Mock the get_organization_accounts function to return empty list
    mock_get_accounts.return_value = []
    
    # Call the function
    scan_organization(mock_args, mock_logger)
    
    # Verify the results
    assert mock_get_accounts.call_count == 1
    assert mock_assume_role.call_count == 0
    assert mock_scan_account.call_count == 0

@patch('organization_scanner.get_organization_accounts')
@patch('organization_scanner.assume_role')
@patch('organization_scanner.scan_account')
@patch('os.makedirs')
def test_scan_organization_role_assumption_failure(mock_makedirs, mock_scan_account, mock_assume_role, mock_get_accounts, mock_args, mock_logger):
    # Mock the get_organization_accounts function
    mock_get_accounts.return_value = [
        {'Id': '123456789012', 'Name': 'Account1'},
        {'Id': '234567890123', 'Name': 'Account2'}
    ]
    
    # Mock the assume_role function to fail for the second account
    mock_session = MagicMock()
    mock_assume_role.side_effect = [mock_session, None]
    
    # Call the function
    scan_organization(mock_args, mock_logger)
    
    # Verify the results
    assert mock_get_accounts.call_count == 1
    assert mock_assume_role.call_count == 2
    assert mock_scan_account.call_count == 1  # Only one account should be scanned