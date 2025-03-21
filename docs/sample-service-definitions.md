# Sample Service Definitions

This document provides examples of service definition files for common AWS services. These files can be used with AWS Auto Inventory to scan specific resources.

## Basic Structure

Service definition files are JSON arrays containing objects that define which AWS services and API calls to use for scanning:

```json
[
  {
    "service": "service-name",
    "function": "api-function-name",
    "result_key": "optional-result-key",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
]
```

Each object has the following properties:

- `service`: The AWS service name (as used in boto3)
- `function`: The API function to call
- `result_key` (optional): The key in the response that contains the results
- `parameters` (optional): Parameters to pass to the API call

## Common Service Definitions

### Amazon S3

```json
[
  {
    "service": "s3",
    "function": "list_buckets"
  }
]
```

### Amazon EC2

```json
[
  {
    "service": "ec2",
    "function": "describe_instances",
    "result_key": "Reservations"
  },
  {
    "service": "ec2",
    "function": "describe_vpcs",
    "result_key": "Vpcs"
  },
  {
    "service": "ec2",
    "function": "describe_subnets",
    "result_key": "Subnets"
  },
  {
    "service": "ec2",
    "function": "describe_security_groups",
    "result_key": "SecurityGroups"
  }
]
```

### Amazon RDS

```json
[
  {
    "service": "rds",
    "function": "describe_db_instances",
    "result_key": "DBInstances"
  },
  {
    "service": "rds",
    "function": "describe_db_clusters",
    "result_key": "DBClusters"
  }
]
```

### AWS Lambda

```json
[
  {
    "service": "lambda",
    "function": "list_functions",
    "result_key": "Functions"
  }
]
```

### Amazon DynamoDB

```json
[
  {
    "service": "dynamodb",
    "function": "list_tables",
    "result_key": "TableNames"
  }
]
```

### Amazon ECS

```json
[
  {
    "service": "ecs",
    "function": "list_clusters",
    "result_key": "clusterArns"
  },
  {
    "service": "ecs",
    "function": "list_services",
    "parameters": {
      "cluster": "default"
    },
    "result_key": "serviceArns"
  }
]
```

### AWS IAM (Global Service)

```json
[
  {
    "service": "iam",
    "function": "list_users",
    "result_key": "Users"
  },
  {
    "service": "iam",
    "function": "list_roles",
    "result_key": "Roles"
  },
  {
    "service": "iam",
    "function": "list_policies",
    "parameters": {
      "Scope": "Local"
    },
    "result_key": "Policies"
  }
]
```

### Amazon CloudFront (Global Service)

```json
[
  {
    "service": "cloudfront",
    "function": "list_distributions",
    "result_key": "DistributionList.Items"
  }
]
```

### AWS CloudFormation

```json
[
  {
    "service": "cloudformation",
    "function": "list_stacks",
    "result_key": "StackSummaries"
  }
]
```

### Amazon SNS

```json
[
  {
    "service": "sns",
    "function": "list_topics",
    "result_key": "Topics"
  }
]
```

### Amazon SQS

```json
[
  {
    "service": "sqs",
    "function": "list_queues",
    "result_key": "QueueUrls"
  }
]
```

## Comprehensive Multi-Service Example

This example combines multiple services into a single scan file:

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
  },
  {
    "service": "rds",
    "function": "describe_db_instances",
    "result_key": "DBInstances"
  },
  {
    "service": "lambda",
    "function": "list_functions",
    "result_key": "Functions"
  },
  {
    "service": "dynamodb",
    "function": "list_tables",
    "result_key": "TableNames"
  }
]
```

## Using JMESPath Queries

For more complex filtering of results, you can use JMESPath queries by prefixing the `result_key` with a dot:

```json
[
  {
    "service": "ec2",
    "function": "describe_instances",
    "result_key": ".Reservations[].Instances[?State.Name=='running']"
  }
]
```

This example will return only running EC2 instances.

## Creating Custom Service Definitions

To create your own service definition:

1. Identify the AWS service and API call you want to use
2. Check the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for the correct service name and function
3. Determine if you need to specify a result key or parameters
4. Create a JSON file with the appropriate structure
5. Test your definition with AWS Auto Inventory

## Tips for Service Definitions

- **Global Services**: Services like IAM and CloudFront are global and only need to be scanned in one region
- **Pagination**: AWS Auto Inventory handles pagination automatically for most services
- **Rate Limiting**: Consider using the `--max-retries` and `--retry-delay` options for services with strict API rate limits
- **Large Results**: Some API calls may return large amounts of data; consider filtering using JMESPath queries

## Using Service Definitions with Multi-Account Scanning

When using service definitions with multi-account scanning, consider:

- **Permissions**: Ensure the assumed role in each account has permissions for all services in your definition
- **Regional Services**: Some services may not be available in all regions
- **Resource Limits**: Member accounts may have different resource limits and usage patterns

Example command for multi-account scanning with a custom service definition:

```bash
python scan.py -s my-custom-services.json --organization-scan --regions us-east-1 us-west-2
```