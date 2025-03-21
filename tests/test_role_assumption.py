import pytest
import boto3
from organization_scanner import assume_role
import logging
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_logger():
    return logging.getLogger("test")

@patch('boto3.Session')
def test_assume_role_success(mock_session_class, mock_logger):
    # Create mock STS client
    mock_sts = MagicMock()
    
    # Mock the assume_role response
    mock_sts.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
            'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'SessionToken': 'AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT+FvwqnKwRcOIfrRh3c/LTo6UDdyJwOOvEVPvLXCrrrUtdnniCEXAMPLE/IvU1dYUg2RVAJBanLiHb4IgRmpRV3zrkuWJOgQs8IZZaIv2BXIa2R4OlgkBN9bkUDNCJiBeb/AXlzBBko7b15fjrBs2+cTQtpZ3CYWFXG8C5zqx37wnOE49mRl/+OtkIKGO7fAE',
            'Expiration': '2025-03-21T09:00:00Z'
        },
        'AssumedRoleUser': {
            'AssumedRoleId': 'AROAIOSFODNN7EXAMPLE:aws-auto-inventory-123456789012',
            'Arn': 'arn:aws:sts::123456789012:assumed-role/OrganizationAccountAccessRole/aws-auto-inventory-123456789012'
        }
    }
    
    # Create a session
    session = MagicMock()
    session.client.return_value = mock_sts
    
    # Mock the new session that will be created
    new_session = MagicMock()
    mock_session_class.return_value = new_session
    
    # Call the function
    result = assume_role(session, '123456789012', 'TestRole', mock_logger)
    
    # Verify the results
    assert result is new_session
    
    # Verify that the client was created correctly
    session.client.assert_called_once_with('sts')
    mock_sts.assume_role.assert_called_once_with(
        RoleArn='arn:aws:iam::123456789012:role/TestRole',
        RoleSessionName='aws-auto-inventory-123456789012'
    )
    
    # Verify that the new session was created with the right credentials
    credentials = mock_sts.assume_role.return_value['Credentials']
    mock_session_class.assert_called_once_with(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

def test_assume_role_error(mock_logger):
    # Create mock STS client that raises an exception
    mock_sts = MagicMock()
    mock_sts.assume_role.side_effect = Exception("Access denied")
    
    # Create a session
    session = MagicMock()
    session.client.return_value = mock_sts
    
    # Call the function
    result = assume_role(session, '123456789012', 'TestRole', mock_logger)
    
    # Verify the results
    assert result is None
    
    # Verify that the client was created correctly
    session.client.assert_called_once_with('sts')
    mock_sts.assume_role.assert_called_once_with(
        RoleArn='arn:aws:iam::123456789012:role/TestRole',
        RoleSessionName='aws-auto-inventory-123456789012'
    )