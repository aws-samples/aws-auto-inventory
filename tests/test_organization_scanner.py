import pytest
import os
from organization_scanner import scan_organization

def test_scan_organization(mocker, tmp_path):
    """Test scanning across an organization."""
    # Mock organization account discovery
    mock_get_accounts = mocker.patch(
        'organization_scanner.get_organization_accounts',
        return_value=[
            {'id': '111111111111', 'name': 'Account1', 'email': 'account1@example.com'},
            {'id': '222222222222', 'name': 'Account2', 'email': 'account2@example.com'}
        ]
    )
    
    # Mock role assumption
    mock_assume_role = mocker.patch('organization_scanner.assume_role')
    mock_session1 = mocker.MagicMock()
    mock_session2 = mocker.MagicMock()
    mock_assume_role.side_effect = [mock_session1, mock_session2]
    
    # Mock account scanning
    mock_scan_account = mocker.patch('organization_scanner.scan_account')
    
    # Mock boto3.Session
    mock_boto3_session = mocker.patch('boto3.Session')
    mock_management_session = mocker.MagicMock()
    mock_boto3_session.return_value = mock_management_session
    
    # Mock print function
    mock_print = mocker.patch('builtins.print')
    
    # Mock datetime to get consistent output directory
    mock_datetime = mocker.patch('organization_scanner.datetime')
    mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12-00'
    
    # Create output directory
    output_dir = str(tmp_path)
    
    # Call the function
    scan_organization(
        'OrganizationAccountAccessRole',
        'scan_config.json',
        ['us-east-1'],
        output_dir,
        'INFO',
        3,
        1,
        2,
        2
    )
    
    # Verify accounts were retrieved
    mock_get_accounts.assert_called_once_with(mock_management_session)
    
    # Verify role was assumed for each account
    assert mock_assume_role.call_count == 2
    mock_assume_role.assert_any_call(mock_management_session, '111111111111', 'OrganizationAccountAccessRole')
    mock_assume_role.assert_any_call(mock_management_session, '222222222222', 'OrganizationAccountAccessRole')
    
    # Verify scan was performed for each account
    assert mock_scan_account.call_count == 2
    
    # Verify output directories were created
    org_output_dir = os.path.join(output_dir, 'organization-2023-01-01T12-00')
    assert os.path.exists(os.path.join(org_output_dir, '111111111111'))
    assert os.path.exists(os.path.join(org_output_dir, '222222222222'))
    assert os.path.exists(os.path.join(org_output_dir, 'accounts.json'))

def test_scan_organization_role_assumption_failure(mocker, tmp_path):
    """Test organization scanning with role assumption failure."""
    # Mock organization account discovery
    mock_get_accounts = mocker.patch(
        'organization_scanner.get_organization_accounts',
        return_value=[
            {'id': '111111111111', 'name': 'Account1', 'email': 'account1@example.com'},
            {'id': '222222222222', 'name': 'Account2', 'email': 'account2@example.com'}
        ]
    )
    
    # Mock role assumption - fail for second account
    mock_assume_role = mocker.patch('organization_scanner.assume_role')
    mock_session1 = mocker.MagicMock()
    mock_assume_role.side_effect = [mock_session1, None]
    
    # Mock account scanning
    mock_scan_account = mocker.patch('organization_scanner.scan_account')
    
    # Mock boto3.Session
    mock_boto3_session = mocker.patch('boto3.Session')
    mock_management_session = mocker.MagicMock()
    mock_boto3_session.return_value = mock_management_session
    
    # Mock print function
    mock_print = mocker.patch('builtins.print')
    
    # Mock datetime to get consistent output directory
    mock_datetime = mocker.patch('organization_scanner.datetime')
    mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12-00'
    
    # Create output directory
    output_dir = str(tmp_path)
    
    # Call the function
    scan_organization(
        'OrganizationAccountAccessRole',
        'scan_config.json',
        ['us-east-1'],
        output_dir,
        'INFO',
        3,
        1,
        2,
        2
    )
    
    # Verify scan was performed only for the first account
    mock_scan_account.assert_called_once()
    
    # Verify output directory was created only for the first account
    org_output_dir = os.path.join(output_dir, 'organization-2023-01-01T12-00')
    assert os.path.exists(os.path.join(org_output_dir, '111111111111'))
    assert not os.path.exists(os.path.join(org_output_dir, '222222222222'))
    
    # Verify error was printed for the second account
    assert any("Skipping account" in str(call_args) for call_args in mock_print.call_args_list)