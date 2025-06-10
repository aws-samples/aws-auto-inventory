# AWS Auto Inventory

A tool for scanning AWS services across regions and accounts to collect resource information.

## Features

- **Multi-format Configuration**: Support for both YAML and JSON configuration formats
- **Multi-format Output**: Generate both JSON and Excel outputs
- **Multi-threading**: Concurrent scanning of regions and services for faster results
- **Organization Scanning**: Scan resources across all accounts in an AWS Organization
- **Robust Error Handling**: Retry logic for API throttling and transient errors
- **Flexible Filtering**: Filter resources by tags, IDs, and other attributes
- **Data Transformation**: Transform data for better analysis, including transposition in Excel
- **Binary Data Support**: Proper handling of binary data (bytes) returned by AWS APIs

## Installation

### From PyPI

```bash
pip install aws-auto-inventory
```

### From Source

```bash
git clone https://github.com/aws-samples/aws-auto-inventory.git
cd aws-auto-inventory
pip install -e .
```

## Usage

### Basic Usage

```bash
aws-auto-inventory --config examples/config_example.yaml --output-dir output --format both
```

### Command-line Options

```
usage: aws-auto-inventory [-h] -c CONFIG [-o OUTPUT_DIR] [-f {json,excel,both}]
                         [--max-regions MAX_REGIONS] [--max-services MAX_SERVICES]
                         [--max-retries MAX_RETRIES] [--retry-delay RETRY_DELAY]
                         [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [--validate-only]

AWS Auto Inventory - Scan AWS resources and generate inventory

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file (YAML or JSON)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to store output files (default: output)
  -f {json,excel,both}, --format {json,excel,both}
                        Output format (default: json)
  --max-regions MAX_REGIONS
                        Maximum number of regions to scan concurrently
  --max-services MAX_SERVICES
                        Maximum number of services to scan concurrently per region
  --max-retries MAX_RETRIES
                        Maximum number of retries for API calls (default: 3)
  --retry-delay RETRY_DELAY
                        Base delay in seconds between retries (default: 2)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging level (default: INFO)
  --validate-only       Validate configuration and exit without scanning
```

## Configuration

AWS Auto Inventory uses a configuration file to define what resources to scan. The configuration file can be in either YAML or JSON format.

### Example Configuration (YAML)

```yaml
inventories:
  - name: my-aws-inventory
    aws:
      profile: default
      region:
        - us-east-1
        - us-west-2
      organization: false
    excel:
      transpose: true
    sheets:
      - name: EC2Instances
        service: ec2
        function: describe_instances
        result_key: Reservations
        parameters:
          Filters:
            - Name: instance-state-name
              Values:
                - running
      - name: S3Buckets
        service: s3
        function: list_buckets
        result_key: Buckets
```

### Example Configuration (JSON)

```json
{
  "inventories": [
    {
      "name": "my-aws-inventory",
      "aws": {
        "profile": "default",
        "region": ["us-east-1", "us-west-2"],
        "organization": false
      },
      "excel": {
        "transpose": true
      },
      "sheets": [
        {
          "name": "EC2Instances",
          "service": "ec2",
          "function": "describe_instances",
          "result_key": "Reservations",
          "parameters": {
            "Filters": [
              {
                "Name": "instance-state-name",
                "Values": ["running"]
              }
            ]
          }
        },
        {
          "name": "S3Buckets",
          "service": "s3",
          "function": "list_buckets",
          "result_key": "Buckets"
        }
      ]
    }
  ]
}
```

### Organization Scanning

To scan resources across all accounts in an AWS Organization, set `organization: true` in the configuration:

```yaml
inventories:
  - name: organization-wide
    aws:
      profile: management
      region:
        - us-east-1
        - us-west-2
      organization: true
      role_name: OrganizationAccountAccessRole
    sheets:
      # ... sheets configuration ...
```

## Output

AWS Auto Inventory generates output files in the specified output directory:

- **JSON Output**: JSON files for each service in each region
- **Excel Output**: Excel spreadsheets with one sheet per service

### Handling of Binary Data

Some AWS APIs (like CloudTrail.Client.list_public_keys) return binary data as bytes. AWS Auto Inventory handles this data as follows:

- In JSON output: Binary data is encoded as base64 and stored in a special format: `{"__bytes_b64__": "base64-encoded-string"}`
- In Excel output: Binary data is converted to a string in the format: `[BYTES: base64-encoded-string]`

This ensures that all data can be properly serialized and deserialized without errors.

## Examples

Example configuration files are provided in the `examples` directory:

- `config_example.yaml`: Basic YAML configuration
- `config_example.json`: Basic JSON configuration
- `config_organization_example.yaml`: Configuration for organization-wide scanning

## AWS Credentials

AWS Auto Inventory uses the standard AWS credential providers:

1. Environment variables
2. Shared credential file (~/.aws/credentials)
3. AWS IAM Instance Profile (if running on an EC2 instance)

You can specify a profile name in the configuration file to use a specific profile from your credentials file.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.