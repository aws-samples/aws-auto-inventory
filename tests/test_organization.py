import pytest
from organization_scanner import get_organization_accounts
import logging
import boto3
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_logger():
    return logging.getLogger("test")

@patch('boto3.client')
def test_get_organization_accounts_success(mock_client, mock_logger):
    # Create mock organizations client
    mock_orgs = MagicMock()
    mock_client.return_value = mock_orgs
    
    # Mock the paginator
    mock_paginator = MagicMock()
    mock_orgs.get_paginator.return_value = mock_paginator
    
    # Mock the paginate response
    mock_paginator.paginate.return_value = [
        {
            'Accounts': [
                {
                    'Id': '123456789012',
                    'Name': 'Account1',
                    'Status': 'ACTIVE'
                },
                {
                    'Id': '234567890123',
                    'Name': 'Account2',
                    'Status': 'ACTIVE'
                },
                {
                    'Id': '345678901234',
                    'Name': 'Account3',
                    'Status': 'SUSPENDED'  # This should be filtered out
                }
            ]
        }
    ]
    
    # Create a session
    session = MagicMock()
    session.client.return_value = mock_orgs
    
    # Call the function
    accounts = get_organization_accounts(session, mock_logger)
    
    # Verify the results
    assert len(accounts) == 2
    assert accounts[0]['Id'] == '123456789012'
    assert accounts[0]['Name'] == 'Account1'
    assert accounts[1]['Id'] == '234567890123'
    assert accounts[1]['Name'] == 'Account2'
    
    # Verify that the client was created correctly
    session.client.assert_called_once_with('organizations')
    mock_orgs.get_paginator.assert_called_once_with('list_accounts')

@patch('boto3.client')
def test_get_organization_accounts_error(mock_client, mock_logger):
    # Create mock organizations client that raises an exception
    mock_orgs = MagicMock()
    mock_client.return_value = mock_orgs
    mock_orgs.get_paginator.side_effect = Exception("Access denied")
    
    # Create a session
    session = MagicMock()
    session.client.return_value = mock_orgs
    
    # Call the function
    accounts = get_organization_accounts(session, mock_logger)
    
    # Verify the results
    assert accounts == []
    
    # Verify that the client was created correctly
    session.client.assert_called_once_with('organizations')