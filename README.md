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

* `--scan`: Path to the JSON file containing the AWS services to scan. This is a required parameter.
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

2. Scan resources specified in `scanfile.json` across specific regions (us-east-1 and eu-west-1), with a maximum of 5 retries and a retry delay of 3 seconds:

```bash
python scan.py -s scanfile.json -r us-east-1 eu-west-1 --max-retries 5 --retry-delay 3
```

3. Scan resources specified in `scanfile.json` across all regions, processing up to 3 regions and 5 services concurrently:

```bash
python scan.py -s scanfile.json --concurrent-regions 3 --concurrent-services 5
```

### Samples

In the [scan](scan) directory, you can find a list of several configuration that you could use. However, be aware that not all of the `function` properties were tested and might fail, so just use it as a reference.

## Configuration

The AWS Auto Inventory requires a JSON file specifying which AWS services and resources to scan. The format of this file is as follows:

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

Each JSON object represents a single AWS service to scan. The `service` key specifies the service, and the `function` key specifies the boto3 client function to call. The optional `result_key` can be used to specify a key in the returned JSON object that contains the desired data. If not provided, the full JSON response will be used.

## Releases

You can download the latest releases [here](https://github.com/aws-samples/aws-auto-inventory/releases).

## References
- [AWS Code Habits](https://github.com/awslabs/aws-code-habits) - A library with Make targets, Ansible playbooks, Jinja templates (and more) designed to boost common software development tasks and enhance governance.


## License
This project is licensed under the Apache License 2.0 License. See the [LICENSE](LICENSE) file.

## Copyright
Copyright Amazon, Inc. or its affiliates. All Rights Reserved.


[repo]: https://github.com/aws-samples/aws-auto-inventory
[logo]: doc/logo.png

[habits]: https://github.com/awslabs/aws-code-habits
