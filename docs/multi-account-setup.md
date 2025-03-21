# Multi-Account Scanning Setup Guide

This guide provides detailed instructions for setting up and using the multi-account scanning feature of AWS Auto Inventory.

## Overview

AWS Auto Inventory can scan resources across all accounts in your AWS Organization. This feature works by:

1. Discovering all accounts in your AWS Organization
2. Assuming a role in each member account
3. Scanning AWS resources in each account
4. Organizing the results by account

## Prerequisites

Before you begin, ensure you have:

- An AWS Organizations setup with a management account and one or more member accounts
- Administrator access to the management account
- Ability to create IAM roles in member accounts (or use existing ones)
- Python 3.6+ with boto3 installed

## Step-by-Step Setup Guide

### Step 1: Prepare the Management Account

The management account is where you'll run AWS Auto Inventory. It needs permission to:
- List accounts in your AWS Organization
- Assume roles in member accounts

1. **Sign in to the AWS Management Console** with your management account.

2. **Create an IAM policy** for listing organization accounts:

   Navigate to IAM > Policies > Create policy and use this JSON:

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "organizations:ListAccounts",
                   "organizations:DescribeAccount"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

   Name it `OrganizationAccountListPolicy`.

3. **Create an IAM policy** for assuming roles in member accounts:

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": "sts:AssumeRole",
               "Resource": "arn:aws:iam::*:role/OrganizationAccountAccessRole"
           }
       ]
   }
   ```

   Name it `OrganizationRoleAssumptionPolicy`.

   > **Note**: If you plan to use a custom role name instead of `OrganizationAccountAccessRole`, replace it in the policy above.

4. **Create an IAM user or role** with these policies attached:

   - `OrganizationAccountListPolicy`
   - `OrganizationRoleAssumptionPolicy`

   If creating a user, generate access keys for programmatic access.

### Step 2: Set Up Member Account Roles

Each member account needs an IAM role that:
- Can be assumed by the management account
- Has permissions to read AWS resources

#### Option A: Using AWS CloudFormation StackSets (Recommended for many accounts)

1. **Sign in to the AWS Management Console** with your management account.

2. **Navigate to CloudFormation > StackSets > Create StackSet**.

3. **Prepare permissions**:
   - Choose "Service-managed permissions" if your organization has trusted access enabled for CloudFormation
   - Otherwise, choose "Self-managed permissions" and follow the prompts to create the necessary IAM roles

4. **Create a CloudFormation template** file named `inventory-role.yaml`:

   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Description: 'IAM Role for AWS Auto Inventory'
   
   Parameters:
     ManagementAccountId:
       Type: String
       Description: The AWS account ID of the management account
   
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
                 AWS: !Sub 'arn:aws:iam::${ManagementAccountId}:root'
               Action: 'sts:AssumeRole'
         ManagedPolicyArns:
           - 'arn:aws:iam::aws:policy/ReadOnlyAccess'
         Path: '/'
   ```

5. **Upload the template** and specify parameters:
   - For `ManagementAccountId`, enter your management account ID

6. **Set deployment options**:
   - Deployment targets: Choose "Deploy to organization" or select specific OUs
   - Specify regions where to create the stack
   - Deployment options: Choose your preferences for failure tolerance

7. **Review and create** the StackSet.

#### Option B: Manual Setup in Each Account (Better for a few accounts)

For each member account:

1. **Sign in to the AWS Management Console** with the member account.

2. **Navigate to IAM > Roles > Create role**.

3. **Select trusted entity**:
   - Choose "AWS account"
   - Select "Another AWS account"
   - Enter the management account ID
   - Do not require MFA (unless your security requirements dictate otherwise)

4. **Attach permissions policies**:
   - Search for and select `ReadOnlyAccess`
   - For more granular control, create and attach custom policies with only the permissions needed

5. **Name the role** `OrganizationAccountAccessRole` (or your custom name).

6. **Review and create** the role.

### Step 3: Configure AWS Credentials

Set up AWS credentials for the management account:

#### Using AWS CLI (Recommended)

```bash
aws configure
```

Enter your access key, secret key, default region, and output format when prompted.

#### Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials
export AWS_DEFAULT_REGION=us-east-1
```

#### Using .env File

Create a `.env` file in the project root:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token  # If using temporary credentials
AWS_DEFAULT_REGION=us-east-1
ORG_ROLE_NAME=OrganizationAccountAccessRole  # Optional: custom role name
```

### Step 4: Install AWS Auto Inventory

1. **Clone the repository**:

```bash
git clone https://github.com/aws-samples/aws-auto-inventory.git
cd aws-auto-inventory
```

2. **Create a virtual environment**:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

### Step 5: Run the Multi-Account Scan

Now you can run the scan across all accounts in your organization:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan
```

To scan specific services:

```bash
# Scan S3 buckets
python scan.py -s scan/sample/services/s3.json --organization-scan

# Scan EC2 instances
python scan.py -s scan/sample/services/ec2.json --organization-scan

# Scan multiple services
python scan.py -s scan/sample/services/multiple.json --organization-scan
```

To scan specific regions:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --regions us-east-1 us-west-2
```

To use a custom role name:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --role-name CustomRoleName
```

### Step 6: Review the Results

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

Each account has its own directory named with the account ID and name. Within each account directory, results are organized by region and service.

## Troubleshooting

### Common Issues and Solutions

#### 1. Access Denied when listing organization accounts

**Error message**: `AccessDeniedException: User is not authorized to perform: organizations:ListAccounts`

**Solution**:
- Verify that your IAM user/role has the `organizations:ListAccounts` permission
- Check if your organization has SCPs (Service Control Policies) that might be restricting access

#### 2. Unable to assume role in member account

**Error message**: `AccessDenied: User is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::123456789012:role/OrganizationAccountAccessRole`

**Solutions**:
- Verify that the role exists in the member account
- Check the trust policy of the role to ensure it allows the management account to assume it
- Ensure your IAM user/role in the management account has the `sts:AssumeRole` permission

#### 3. Role exists but lacks necessary permissions

**Error message**: `AccessDeniedException: User is not authorized to perform: ec2:DescribeInstances`

**Solution**:
- Attach additional policies to the role in the member account to grant the necessary permissions
- Consider using the AWS managed `ReadOnlyAccess` policy for comprehensive read access

#### 4. Role name mismatch

**Error message**: `NoSuchEntity: The role with name OrganizationAccountAccessRole cannot be found`

**Solution**:
- Verify the role name in each member account
- Use the `--role-name` parameter to specify a custom role name if not using the default

### Debugging Tips

1. **Enable debug logging**:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --log_level DEBUG
```

2. **Test role assumption manually**:

```bash
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/OrganizationAccountAccessRole --role-session-name test-session
```

3. **Check CloudTrail** for detailed error information about API calls.

## Best Practices

1. **Security**:
   - Follow the principle of least privilege when creating IAM roles
   - Consider using temporary credentials with AWS STS
   - Regularly rotate access keys

2. **Performance**:
   - Scan only the regions you use to improve performance
   - Use service-specific scan files instead of scanning all services
   - Consider running scans during off-peak hours

3. **Organization**:
   - Create a dedicated IAM user/role for inventory scanning
   - Store scan results securely
   - Consider automating scans with AWS Lambda or AWS CodeBuild

## Advanced Configuration

### Custom Role Names

If you're using a custom role name across your organization:

```bash
python scan.py -s scan/sample/services/s3.json --organization-scan --role-name CustomRoleName
```

Or set it in your `.env` file:

```
ORG_ROLE_NAME=CustomRoleName
```

### Filtering Accounts

Currently, the tool scans all active accounts in your organization. If you need to filter accounts:

1. Export the list of accounts:
```bash
aws organizations list-accounts > accounts.json
```

2. Edit the JSON file to include only the accounts you want to scan.

3. Create a custom script that uses AWS Auto Inventory's functions with your filtered accounts.

## Conclusion

You've now set up AWS Auto Inventory for multi-account scanning. This powerful feature allows you to maintain a comprehensive inventory of resources across your entire AWS Organization, helping with compliance, security, and cost management.

For more information, refer to the main README.md file or open an issue on GitHub if you encounter any problems.