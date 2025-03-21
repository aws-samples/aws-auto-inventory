# AWS Auto Inventory

AWS Auto Inventory is a tool that helps you discover and inventory AWS resources across multiple regions and accounts. It uses the AWS SDK to make API calls to various AWS services and collects information about your resources.

## Features

- Scan multiple AWS services in parallel
- Support for all AWS regions
- Configurable retry logic for API calls
- Customizable service definitions
- Multi-account scanning across an AWS Organization
- Output in JSON format for easy integration with other tools

## Prerequisites

- Python 3.6 or higher
- AWS credentials with appropriate permissions
- For multi-account scanning: AWS Organizations setup with proper IAM roles

## Installation

1. Clone the repository:

```bash
git clone https://github.com/aws-samples/aws-auto-inventory.git
cd aws-auto-inventory
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Single Account Scanning

To scan a single AWS account:

```bash
python scan.py -s scan/sample/services/s3.json
```

### Multi-Account Scanning

To scan all accounts in your AWS Organization:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan
```

### Command Line Options

- `-s, --scan`: Path to the JSON file containing the services to scan (required)
- `-r, --regions`: List of AWS regions to scan (default: all opt-in regions)
- `-o, --output_dir`: Directory to store the results (default: `output`)
- `-l, --log_level`: Set the logging level (default: `INFO`)
- `--max-retries`: Maximum number of retries for each service (default: 3)
- `--retry-delay`: Delay in seconds before each retry (default: 2)
- `--concurrent-regions`: Number of regions to process concurrently
- `--concurrent-services`: Number of services to process concurrently for each region
- `--organization-scan`: Scan all accounts in the AWS Organization
- `--role-name`: IAM role name to assume in member accounts (default: `OrganizationAccountAccessRole`)

## Multi-Account Scanning Setup Guide

### Prerequisites for Multi-Account Scanning

1. **AWS Organizations**: You must have AWS Organizations set up with multiple accounts.
2. **Management Account Access**: You need access to the AWS Organizations management account.
3. **IAM Roles**: Each member account must have an IAM role that:
   - Can be assumed by the management account
   - Has the necessary permissions to read AWS resources

### Step 1: Set Up AWS Organizations

If you haven't already set up AWS Organizations:

1. Sign in to the AWS Management Console with the account you want to use as the management account.
2. Navigate to the AWS Organizations console.
3. Choose "Create organization" and follow the prompts.
4. Add member accounts by:
   - Creating new accounts within the organization, or
   - Inviting existing accounts to join the organization

### Step 2: Create IAM Roles in Member Accounts

For each member account, you need to create an IAM role that the management account can assume:

#### Option A: Use AWS CloudFormation StackSets (Recommended)

1. In the management account, navigate to the CloudFormation console.
2. Choose "StackSets" and then "Create StackSet".
3. Use the following CloudFormation template to create the necessary IAM role in all member accounts:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'IAM Role for AWS Auto Inventory'

Resources:
  AutoInventoryRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: OrganizationAccountAccessRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/ReadOnlyAccess'
      Path: '/'
```

4. Deploy the StackSet to all organization accounts.

#### Option B: Manual Setup in Each Account

1. Sign in to each member account.
2. Navigate to the IAM console.
3. Create a new role with the following settings:
   - Trusted entity: Another AWS account
   - Account ID: Enter the management account ID
   - Role name: `OrganizationAccountAccessRole` (or your custom name)
   - Attach the `ReadOnlyAccess` managed policy

### Step 3: Configure AWS Credentials

Set up your AWS credentials for the management account:

#### Using AWS CLI

```bash
aws configure
```

#### Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials
```

#### Using .env File

Create a `.env` file in the project root:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials
ORG_ROLE_NAME=OrganizationAccountAccessRole  # Optional: custom role name
```

### Step 4: Run the Multi-Account Scan

Now you can run the scan across all accounts in your organization:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan
```

To use a custom role name:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --role-name CustomRoleName
```

### Step 5: Review the Results

The scan results are organized in the following directory structure:

```
output/organization-[timestamp]/
├── 123456789012-AccountName1/
│   └── us-east-1/
│       └── s3-list_buckets.json
├── 234567890123-AccountName2/
│   └── us-east-1/
│       └── s3-list_buckets.json
└── ...
```

## Troubleshooting Multi-Account Scanning

### Common Issues

1. **Access Denied Errors**:
   - Verify that the IAM role exists in the member account
   - Check that the role trust policy allows the management account to assume it
   - Ensure the role has the necessary permissions

2. **Role Not Found**:
   - Confirm the role name is correct (default is `OrganizationAccountAccessRole`)
   - Verify the role exists in the member account

3. **Organizations API Access**:
   - Ensure your credentials have permission to call `organizations:ListAccounts`

### Debugging

For more detailed logs, increase the log level:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --log_level DEBUG
```

## Service Definition Files

The service definition files specify which AWS services and API calls to use for scanning. They are JSON files with the following structure:

```json
[
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
```

Each entry in the array represents a service to scan and contains:

- `service`: The AWS service name (as used in boto3)
- `function`: The API function to call
- `result_key` (optional): The key in the response that contains the results
- `parameters` (optional): Parameters to pass to the API call

## Testing

AWS Auto Inventory uses pytest for testing. To run the tests:

1. Install the test dependencies:

```bash
pip install -r test_requirements.txt
```

2. Run the tests:

```bash
pytest
```

3. Run tests with coverage:

```bash
pytest --cov=. tests/
```

### Test Structure

The tests are organized as follows:

- **Unit Tests**: Test individual components in isolation
  - `test_api_calls.py`: Tests for API call handling and retry logic
  - `test_organization.py`: Tests for organization account discovery
  - `test_role_assumption.py`: Tests for role assumption functionality
  
- **Integration Tests**: Test components working together
  - `test_organization_scanner.py`: Tests for the organization scanning workflow
  - `test_service_scanning.py`: Tests for service scanning functionality

### Mocking AWS Services

The tests use the `moto` library to mock AWS services, allowing tests to run without actual AWS credentials or resources.

## Security Considerations

- Use the principle of least privilege when creating IAM roles
- Consider using temporary credentials with AWS STS
- Review the scan results to ensure no sensitive information is exposed
- Store the scan results securely

## License

This project is licensed under the MIT-0 License. See the LICENSE file for details.