import pytest
from organization_scanner import get_organization_accounts

def test_get_organization_accounts(mock_boto, mock_organization):
    """Test retrieving accounts from an organization."""
    session = mock_boto.Session()
    
    accounts = get_organization_accounts(session)
    
    assert len(accounts) == 3
    for account in accounts:
        assert 'id' in account
        assert 'name' in account
        assert 'email' in account

def test_get_organization_accounts_empty(mock_boto):
    """Test retrieving accounts from an empty organization."""
    # Create organization but don't add accounts
    org_client = mock_boto.client('organizations')
    org_client.create_organization(FeatureSet='ALL')
    
    session = mock_boto.Session()
    accounts = get_organization_accounts(session)
    
    assert len(accounts) == 0

def test_get_organization_accounts_pagination(mocker):
    """Test pagination in organization account retrieval."""
    mock_session = mocker.MagicMock()
    mock_org_client = mocker.MagicMock()
    mock_session.client.return_value = mock_org_client
    
    # Mock paginator
    mock_paginator = mocker.MagicMock()
    mock_org_client.get_paginator.return_value = mock_paginator
    
    # Set up paginator to return two pages of results
    mock_paginator.paginate.return_value = [
        {
            'Accounts': [
                {'Id': '111111111111', 'Name': 'Account1', 'Email': 'account1@example.com', 'Status': 'ACTIVE'},
                {'Id': '222222222222', 'Name': 'Account2', 'Email': 'account2@example.com', 'Status': 'ACTIVE'}
            ]
        },
        {
            'Accounts': [
                {'Id': '333333333333', 'Name': 'Account3', 'Email': 'account3@example.com', 'Status': 'ACTIVE'},
                {'Id': '444444444444', 'Name': 'Account4', 'Email': 'account4@example.com', 'Status': 'SUSPENDED'}
            ]
        }
    ]
    
    accounts = get_organization_accounts(mock_session)
    
    # Should only include ACTIVE accounts
    assert len(accounts) == 3
    assert accounts[0]['id'] == '111111111111'
    assert accounts[1]['id'] == '222222222222'
    assert accounts[2]['id'] == '333333333333'