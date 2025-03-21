import pytest
import botocore
from organization_scanner import assume_role

def test_assume_role_success(mocker):
    """Test successful role assumption."""
    mock_session = mocker.MagicMock()
    mock_sts_client = mocker.MagicMock()
    mock_session.client.return_value = mock_sts_client
    
    # Mock successful assume_role response
    mock_sts_client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'test-access-key',
            'SecretAccessKey': 'test-secret-key',
            'SessionToken': 'test-session-token'
        }
    }
    
    # Mock boto3.Session constructor
    mock_boto3_session = mocker.patch('boto3.Session')
    
    result = assume_role(mock_session, '123456789012', 'TestRole')
    
    # Verify assume_role was called with correct parameters
    mock_sts_client.assume_role.assert_called_once_with(
        RoleArn='arn:aws:iam::123456789012:role/TestRole',
        RoleSessionName='AWSAutoInventorySession',
        DurationSeconds=3600
    )
    
    # Verify boto3.Session was created with credentials
    mock_boto3_session.assert_called_once_with(
        aws_access_key_id='test-access-key',
        aws_secret_access_key='test-secret-key',
        aws_session_token='test-session-token'
    )
    
    assert result is not None

def test_assume_role_failure(mocker):
    """Test role assumption failure."""
    mock_session = mocker.MagicMock()
    mock_sts_client = mocker.MagicMock()
    mock_session.client.return_value = mock_sts_client
    
    # Mock assume_role to raise an exception
    mock_sts_client.assume_role.side_effect = botocore.exceptions.ClientError(
        {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
        'AssumeRole'
    )
    
    # Mock print function
    mock_print = mocker.patch('builtins.print')
    
    result = assume_role(mock_session, '123456789012', 'TestRole')
    
    # Verify error was printed
    mock_print.assert_called_once()
    assert "Failed to assume role" in mock_print.call_args[0][0]
    
    # Verify function returned None
    assert result is None