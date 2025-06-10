import pytest
import os
import json
import boto3
from moto import mock_s3, mock_ec2
from scan import process_region

@pytest.fixture
def setup_aws_resources(mock_boto):
    """Set up AWS resources for testing."""
    # Create S3 buckets
    s3_client = mock_boto.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket='test-bucket-1')
    s3_client.create_bucket(Bucket='test-bucket-2')
    
    # Create EC2 instances
    ec2_client = mock_boto.client('ec2', region_name='us-east-1')
    ec2_client.run_instances(ImageId='ami-12345678', MinCount=1, MaxCount=2)
    
    return mock_boto

def test_process_region_s3(setup_aws_resources, aws_credentials, mock_log):
    """Test processing a region for S3 resources."""
    session = setup_aws_resources.Session()
    
    # Define services to scan
    services = [{"service": "s3", "function": "list_buckets"}]
    
    # Process the region
    results = process_region('us-east-1', services, session, mock_log, 3, 1, None)
    
    # Verify results
    assert len(results) == 1
    assert results[0]['region'] == 'us-east-1'
    assert results[0]['service'] == 's3'
    assert results[0]['function'] == 'list_buckets'
    assert len(results[0]['result']) >= 2  # At least our 2 test buckets
    
    # Verify bucket names
    bucket_names = [bucket['Name'] for bucket in results[0]['result']]
    assert 'test-bucket-1' in bucket_names
    assert 'test-bucket-2' in bucket_names

def test_process_region_ec2(setup_aws_resources, aws_credentials, mock_log):
    """Test processing a region for EC2 resources."""
    session = setup_aws_resources.Session()
    
    # Define services to scan
    services = [{"service": "ec2", "function": "describe_instances", "result_key": "Reservations"}]
    
    # Process the region
    results = process_region('us-east-1', services, session, mock_log, 3, 1, None)
    
    # Verify results
    assert len(results) == 1
    assert results[0]['region'] == 'us-east-1'
    assert results[0]['service'] == 'ec2'
    assert results[0]['function'] == 'describe_instances'
    assert len(results[0]['result']) >= 1  # At least one reservation
    
    # Verify instances
    instances = []
    for reservation in results[0]['result']:
        instances.extend(reservation['Instances'])
    assert len(instances) >= 2  # We created 2 instances