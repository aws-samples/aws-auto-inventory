import json
import scan
import argparse
import boto3
import os
from typing import Dict

# keep rolling count of all services
all_services = {}


def parse_service_counts(service_file, service_counts):
    # type: (str, Dict) -> None
    """
    Parse/save recurring count of service resources
    """
    for service in service_counts:
        all_services[service] = service_counts[service]

    with open(service_file, 'w') as sfw:
        json.dump(all_services, sfw, indent=4)


def get_service_counts(output_dir, account_id, service_file_output):
    # type: (str, str, str) -> Dict
    """
    Loop output json files and get service counts
    """
    service_counts = []
    # loop all files in account / regions
    regions = [d for d in os.listdir(
        output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    for region in regions:
        region_dir_path = os.path.join(output_dir, region)
        json_files = [f for f in os.listdir(region_dir_path) if os.path.isfile(
            os.path.join(region_dir_path, f)) and f.endswith(".json")]
        for file in json_files:
            with open(file, 'r') as readfile:
                serv_data = json.load(readfile)
            first_key = next(iter(serv_data))
            count = len(serv_data[first_key])
            service_counts.append({file.split('.')[0]: count})
        parse_service_counts(service_file_output, service_counts)


def loop_accounts(args):
    # type: (str) -> None
    """
    Loop AWS accounts and get service counts
    """
    with open(args.accounts_file, 'r') as afr:
        accounts = afr.readlines()

    aws_arn_prefix = "arn:aws"
    current_region = "us-east-1"
    my_session = boto3.session.Session()
    if "gov" in my_session.region_name:
        aws_arn_prefix = "arn:aws-us-gov"
        current_region = "us-gov-west-1"

    for account in accounts:
        sts = boto3.client('sts')
        response = sts.assume_role(
            RoleArn=f'{aws_arn_prefix}:iam::{account}:role/{args.role_name}',
            RoleSessionName=f'{account}-{args.role_name}')

        credentials = response['Credentials']
        boto3.session.Session(aws_access_key_id=credentials['AccessKeyId'], aws_secret_access_key=credentials[
                              'SecretAccessKey'], aws_session_token=credentials['SessionToken'], region_name=current_region)

        scan.main(
            args.scan,
            args.regions,
            account,
            args.log_level,
            args.max_retries,
            args.retry_delay,
            args.concurrent_regions,
            args.concurrent_services,
        )

        get_service_counts(args.output_dir, args.service_file_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List all resources in all AWS services and regions."
    )
    parser.add_argument('-n', '--role-name', type=str, required=True,
                        help='AWS role name to assume in each account')
    parser.add_argument('-a', '--accounts-file', type=str, required=True,
                        help='Name/path to text file containing accounts, each account on a new line')
    parser.add_argument('-a', '--service-file-output', type=str, default='service-counts.json',
                        help='Name/path to text file containing accounts, each account on a new line')
    parser.add_argument(
        "-s",
        "--scan",
        help="The path to the JSON file or URL containing the AWS services to scan.",
        required=True,
    )
    parser.add_argument(
        "-r", "--regions", nargs="+", help="List of AWS regions to scan"
    )
    parser.add_argument(
        "-o", "--output_dir", default="output", help="Directory to store the results"
    )
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    # New arguments
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for each service",
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=2,
        help="Delay (in seconds) before each retry",
    )
    parser.add_argument(
        "--concurrent-regions",
        type=int,
        default=None,
        help="Number of regions to process concurrently. Default is None, which means the script will use as many as possible",
    )
    parser.add_argument(
        "--concurrent-services",
        type=int,
        default=None,
        help="Number of services to process concurrently for each region. Default is None, which means the script will use as many as possible",
    )
    args = parser.parse_args()

    loop_accounts(args)
