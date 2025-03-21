![logo][logo]

# AWS Auto Inventory

This script scans your AWS resources across multiple regions and services, and generates a detailed inventory of them. It's written in Python, and leverages Boto3, the official Amazon Web Services (AWS) SDK for Python, to interact with AWS services.

## Table of Contents

1. [Context](#context)
2. [Problem](#problem)
3. [Solution](#solution)
4. [Installation](#installation)
5. [Usage](#usage)
    - [Examples](#examples)
6. [Configuration](#configuration)
    - [Configuration Format](#configuration-format)
    - [Advanced Configuration](#advanced-configuration)
7. [Sample Configurations](#sample-configurations)
8. [Project Structure](#project-structure)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [Releases](#releases)
12. [References](#references)
13. [License](#license)
14. [Copyright](#copyright)

## Context

As the adoption of cloud technologies continues to rise, businesses have started leveraging AWS to host an increasingly diverse range of services. As your cloud presence grows, it becomes increasingly important to maintain a clear overview of your AWS resources across all services and regions.

## Problem

However, AWS's expansive list of services and geographically diverse infrastructure can make it a daunting task to maintain visibility of all resources. AWS provides over 200+ services, each of which can contain numerous different resource types. These services can be spread across 24 geographic regions worldwide.

## Solution

To address these issues, we have developed the AWS Auto Inventory, a robust, efficient, and flexible Python script that scans your AWS environment to provide a comprehensive overview of your resources.

The script provides:

- Thorough scanning across specified (or all) AWS regions and services.
- Parallel scanning capabilities, leveraging Python's multithreading to process multiple regions and services concurrently.
- Error-handling mechanisms for AWS's API call rate limits, including retry logic with exponential backoff.
- Configurable retry parameters.
- Verbose logging, useful for troubleshooting and understanding the scanning process.
- Results stored in JSON files, making it easy to feed the output into further data processing or visualization tools.

## Installation

As this tool is a Python script, you need Python 3.6+ installed on your machine. If you have Python installed, you can directly run the script. Make sure you have installed the required Python libraries. Install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

Before you start, make sure to set your AWS credentials either by using the AWS CLI:

```bash
aws configure
```

Or by setting the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=<your_access_key>
export AWS_SECRET_ACCESS_KEY=<your_secret_key>
export AWS_SESSION_TOKEN=<your_session_token> # If using temporary credentials
```

You can run the AWS Auto Inventory using the command line. Here is the general syntax:

```bash
python scan.py -s <scanfile> [parameters]
```

**Parameters:**

* `--scan`: The path to the JSON file or URL containing the AWS services to scan. This is a required parameter.
* `--regions`: Optional parameter specifying a list of AWS regions to scan. If not provided, all accessible regions will be scanned.
* `--output_dir`: Optional parameter specifying the directory to store the results. Default is "output".
* `--log_level`: Optional parameter to set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is "INFO".
* `--max-retries`: Optional parameter to set the maximum number of retries for each service. Default is 3.
* `--retry-delay`: Optional parameter to set the delay (in seconds) before each retry. Default is 2.
* `--concurrent-regions`: Optional parameter to set the number of regions to process concurrently. Default is None, which means the script will use as many as possible.
* `--concurrent-services`: Optional parameter to set the number of services to process concurrently for each region. Default is None, which means the script will use as many as possible.

### Examples

Here are some examples of how to use the tool:

1. Scan all resources specified in `scanfile.json` across all regions:

```bash
python scan.py -s scanfile.json
```

**Note:** `scanfile.json` can be local path or an URL, example:

```bash
python scan.py -s https://raw.githubusercontent.com/aws-samples/aws-auto-inventory/main/scan/sample/services/iam.json
```

2. Scan resources specified in `scanfile.json` across specific regions (us-east-1 and eu-west-1), with a maximum of 5 retries and a retry delay of 3 seconds:

```bash
python scan.py -s scanfile.json -r us-east-1 eu-west-1 --max-retries 5 --retry-delay 3
```

3. Scan resources specified in `scanfile.json` across all regions, processing up to 3 regions and 5 services concurrently:

```bash
python scan.py -s scanfile.json --concurrent-regions 3 --concurrent-services 5
```

4. Scan only S3 buckets across all regions and save results to a custom directory:

```bash
python scan.py -s scan/sample/s3_buckets.json --output_dir my_inventory
```

5. Scan only running EC2 instances with detailed logging:

```bash
python scan.py -s scan/sample/running_ec2.json --log_level DEBUG
```

## Configuration

The AWS Auto Inventory requires a JSON file specifying which AWS services and resources to scan.

### Configuration Format

The basic format of the configuration file is as follows:

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

Each JSON object represents a single AWS service to scan with the following properties:

- `service`: The AWS service name (as used in boto3)
- `function`: The boto3 client function to call
- `result_key` (optional): A key in the returned JSON object that contains the desired data. If not provided, the full JSON response will be used.
- `parameters` (optional): Parameters to pass to the function call

### Advanced Configuration

You can also use more advanced configurations with filters and parameters:

```json
[
  {
    "function": "describe_instances",
    "parameters": {
      "Filters": [
        {
          "Name": "instance-state-name",
          "Values": [
            "running"
          ]
        }
      ]
    },
    "result_key": "Reservations",
    "service": "ec2"
  }
]
```

For JMESPath-style queries, you can use a dot-prefixed `result_key`:

```json
[
  {
    "function": "list_clusters",
    "result_key": ".Clusters[].{Id: Id, Name: Name}",
    "service": "emr"
  }
]
```

## Sample Configurations

In the [scan/sample](scan) directory, you'll find numerous pre-built configurations:

- `s3_buckets.json`: Lists all S3 buckets
- `running_ec2.json`: Lists only running EC2 instances
- `running_ec2_names.json`: Lists running EC2 instances with their names
- `list_emr_clusters_id_name.json`: Lists EMR clusters with just ID and name
- `tagged_emrs.json`: Lists EMR clusters with specific tags
- `all_services.json`: A comprehensive scan of all available services

Additionally, the `scan/sample/services` directory contains individual configuration files for each AWS service.

## Project Structure

```
aws-auto-inventory/
├── scan.py                 # Main script for scanning AWS resources
├── scan_builder.py         # Utility to generate service configuration files
├── requirements.txt        # Python dependencies
├── scan/                   # Directory containing scan configurations
│   └── sample/             # Sample configurations
│       ├── services/       # Individual service configurations
│       ├── s3_buckets.json # S3 buckets configuration
│       ├── running_ec2.json # Running EC2 instances configuration
│       └── ...             # Other sample configurations
├── doc/                    # Documentation assets
│   └── logo.png            # Project logo
└── output/                 # Default directory for scan results (created at runtime)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Ensure your AWS credentials are properly configured
   - Check that your IAM user/role has sufficient permissions to scan the requested services

2. **Throttling Errors**:
   - If you're seeing many throttling errors, try reducing concurrency with `--concurrent-regions` and `--concurrent-services`
   - Increase `--max-retries` and `--retry-delay` parameters

3. **Missing Results**:
   - Check the log file in the output directory for errors
   - Ensure your configuration file is properly formatted
   - Verify that the specified services and functions exist in boto3

4. **Performance Issues**:
   - For large AWS environments, consider scanning specific regions or services instead of all
   - Adjust concurrency parameters to optimize for your environment

### Logging

For detailed troubleshooting, increase the log level:

```bash
python scan.py -s scanfile.json --log_level DEBUG
```

Log files are stored in the output directory with timestamps.

## Contributing

We welcome contributions to AWS Auto Inventory! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## Releases

You can download the latest releases [here](https://github.com/aws-samples/aws-auto-inventory/releases).

## References
- [AWS Code Habits](https://github.com/awslabs/aws-code-habits) - A library with Make targets, Ansible playbooks, Jinja templates (and more) designed to boost common software development tasks and enhance governance.
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - Official documentation for the AWS SDK for Python

## License
This project is licensed under the Apache License 2.0 License. See the [LICENSE](LICENSE) file.

## Copyright
Copyright Amazon, Inc. or its affiliates. All Rights Reserved.


[repo]: https://github.com/aws-samples/aws-auto-inventory
[logo]: doc/logo.png

[habits]: https://github.com/awslabs/aws-code-habits