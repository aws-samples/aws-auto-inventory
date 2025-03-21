import os
import pytest
import boto3
import json
from moto import mock_s3, mock_ec2, mock_iam, mock_sts, mock_organizations

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def mock_boto():
    """Setup mock boto3 services."""
    with mock_s3(), mock_ec2(), mock_iam(), mock_sts(), mock_organizations():
        yield boto3

@pytest.fixture
def sample_scan_config():
    """Return a sample scan configuration."""
    return [
        {
            "service": "s3",
            "function": "list_buckets"
        },
        {
            "service": "ec2",
            "function": "describe_instances",
            "result_key": "Reservations"
        }
    ]

@pytest.fixture
def mock_organization(mock_boto):
    """Create a mock AWS Organization with multiple accounts."""
    org_client = mock_boto.client('organizations')
    
    # Create organization
    org_client.create_organization(FeatureSet='ALL')
    
    # Create member accounts
    accounts = []
    for i in range(3):
        response = org_client.create_account(
            Email=f'test{i}@example.com',
            AccountName=f'TestAccount{i}'
        )
        accounts.append(response['CreateAccountStatus']['AccountId'])
    
    return accounts

class MockLog:
    """Mock logger for testing."""
    def __init__(self):
        self.info_messages = []
        self.error_messages = []
        self.debug_messages = []
        self.warning_messages = []
    
    def info(self, message, *args, **kwargs):
        self.info_messages.append(message % args if args else message)
    
    def error(self, message, *args, **kwargs):
        self.error_messages.append(message % args if args else message)
    
    def debug(self, message, *args, **kwargs):
        self.debug_messages.append(message % args if args else message)
    
    def warning(self, message, *args, **kwargs):
        self.warning_messages.append(message % args if args else message)

@pytest.fixture
def mock_log():
    """Return a mock logger."""
    return MockLog()