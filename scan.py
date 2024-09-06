# -*- coding: utf-8 -*-
# Required modules
import argparse
import boto3
import botocore
import concurrent.futures
import datetime
import json
import logging
import os
import time
import traceback
from datetime import datetime
import requests

# accomodate windows and unix path
# Define the timestamp as a string, which will be the same throughout the execution of the script.
timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

def get_json_from_url(url):
    """Fetch JSON from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as e:
        print("Failed to fetch JSON from {}: {}".format(url, e))
        return None

    try:
        return response.json()
    except ValueError as e:
        print("Failed to parse JSON from {}: {}".format(url, e))
        return None

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSONEncoder that supports encoding datetime objects."""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)

def setup_logging(log_dir, log_level):
    """Set up the logging system."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_filename = "aws_resources_{}.log".format(timestamp)
    log_file = os.path.join(log_dir, log_filename)

    # Configure the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.basicConfig(level=log_level)
    return logger

def api_call_with_retry(client, function_name, parameters, max_retries, retry_delay):
    """
    Make an API call with exponential backoff.

    This function will make an API call with retries. It will exponentially back off
    with a delay of `retry_delay * 2^attempt` for transient errors.
    """

    def api_call():
        for attempt in range(max_retries):
            try:
                function_to_call = getattr(client, function_name)
                if parameters:
                    return function_to_call(**parameters)
                else:
                    return function_to_call()
            except botocore.exceptions.ClientError as error:
                error_code = error.response["Error"]["Code"]
                if error_code == "Throttling":
                    if attempt < (max_retries - 1):  # no delay on last attempt
                        time.sleep(retry_delay**attempt)
                    continue
                elif error_code == "RequestLimitExceeded":
                    time.sleep(retry_delay**attempt)
                    continue
                else:
                    raise
            except botocore.exceptions.BotoCoreError:
                if attempt < (max_retries - 1):  # no delay on last attempt
                    time.sleep(retry_delay**attempt)
                continue
        return None

    return api_call

def _get_service_data(session, region_name, service, log, max_retries, retry_delay):
    function = service["function"]
    result_key = service.get("result_key", None)
    parameters = service.get("parameters", None)

    log.info(
        "Getting data on service {} with function {} in region {}".format(
            service["service"], function, region_name
        )
    )

    try:
        client = session.client(service["service"], region_name=region_name)
        if not hasattr(client, function):
            log.error(
                "Function {} does not exist for service {} in region {}".format(
                    function, service["service"], region_name
                )
            )
            return None
        
        api_call = api_call_with_retry(client, function, parameters, max_retries, retry_delay)

        # Handling the response and filtering manually
        response = api_call()
        if result_key:
            if result_key.startswith('.'):
                # If the result_key is a JQ-style query, it needs to be implemented manually
                response = _manual_json_query(response, result_key)
            else:
                response = response.get(result_key)
        
        # Clean up the response if necessary
        if isinstance(response, dict):
            response.pop("ResponseMetadata", None)
    
    except Exception as exception:
        log.error(
            "Error while processing {}, {}.\n{}: {}".format(
                service["service"], region_name, type(exception).__name__, exception
            )
        )
        log.error(traceback.format_exc())
        return None

    log.info("Finished: AWS Get Service Data")
    log.debug(
        "Result for {}, function {}, region {}: {}".format(
            service["service"], function, region_name, response
        )
    )
    return {
        "region": region_name,
        "service": service["service"],
        "function": service["function"],
        "result": response,
    }

def _manual_json_query(data, query):
    """
    Simulate a basic JQ query for filtering JSON data manually.
    This function assumes the query is very simple (e.g., '.key').
    """
    if not isinstance(data, dict):
        return data
    
    # For a basic '.key' query
    key = query.lstrip('.')
    return data.get(key)

def process_region(
    region, services, session, log, max_retries, retry_delay, concurrent_services
):
    """
    Processes a single AWS region.

    Arguments:
    region -- The AWS region to process.
    services -- The AWS services to scan.
    session -- The boto3 Session.
    log -- The logger object.
    max_retries -- The maximum number of retries for each service.
    retry_delay -- The delay before each retry.
    concurrent_services -- The number of services to process concurrently for each region.

    Returns:
    region_results -- The scan results for the region.
    """

    log.info("Started processing for region: {}".format(region))

    region_results = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrent_services
    ) as executor:
        future_to_service = {
            executor.submit(
                _get_service_data,
                session,
                region,
                service,
                log,
                max_retries,
                retry_delay,
            ): service
            for service in services
        }
        for future in concurrent.futures.as_completed(future_to_service):
            service = future_to_service[future]
            try:
                result = future.result()
                if result is not None and result["result"]:
                    region_results.append(result)
                    log.info("Successfully processed service: {}".format(service["service"]))
                else:
                    log.info("No data found for service: {}".format(service["service"]))
            except Exception as exc:
                log.error("{} generated an exception: {}".format(service["service"], exc))
                log.error(traceback.format_exc())

    log.info("Finished processing for region: {}".format(region))
    return region_results

def display_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "{}h:{}m:{}s".format(int(hours), int(minutes), int(seconds))

def check_aws_credentials(session):
    """Check AWS credentials by calling the STS GetCallerIdentity operation."""
    try:
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print("Authenticated as: {}".format(identity['Arn']))
    except botocore.exceptions.BotoCoreError as error:
        print("Error verifying AWS credentials: {}".format(error))
        return False

    return True

def main(
    scan,
    regions,
    output_dir,
    log_level,
    max_retries,
    retry_delay,
    concurrent_regions,
    concurrent_services,
):
    """
    Main function to perform the AWS services scan.

    Arguments:
    scan -- The path to the JSON file or URL containing the AWS services to scan.
    regions -- The AWS regions to scan.
    output_dir -- The directory to store the results.
    log_level -- The log level for the script.
    max_retries -- The maximum number of retries for each service.
    retry_delay -- The delay before each retry.
    concurrent_regions -- The number of regions to process concurrently.
    concurrent_services -- The number of services to process concurrently for each region.
    """

    session = boto3.Session()
    if not check_aws_credentials(session):
        print "Invalid AWS credentials. Please configure your credentials."
        return

    log = setup_logging(output_dir, log_level)

    if scan.startswith("http://") or scan.startswith("https://"):
        services = get_json_from_url(scan)
        if services is None:
            print "Failed to load services from {}. Exiting.".format(scan)
            return
    else:
        with open(scan, "r") as f:
            services = json.load(f)
    if not regions:
        ec2_client = session.client("ec2")
        regions = [
            region["RegionName"]
            for region in ec2_client.describe_regions()["Regions"]
            if region["OptInStatus"] == "opt-in-not-required"
            or region["OptInStatus"] == "opted-in"
        ]

    start_time = time.time()

    results = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrent_regions
    ) as executor:
        future_to_region = {
            executor.submit(
                process_region,
                region,
                services,
                session,
                log,
                max_retries,
                retry_delay,
                concurrent_services,
            ): region
            for region in regions
        }
        for future in concurrent.futures.as_completed(future_to_region):
            region = future_to_region[future]
            try:
                region_results = future.result()
                results.extend(region_results)
                for service_result in region_results:
                    directory = os.path.join(output_dir, timestamp, region)
                    try:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                    except OSError as e:
                        log.error("Invalid directory name: {}".format(directory))
                        log.error(str(e))
                    try:
                        with open(
                            os.path.join(directory, "{}-{}.json".format(service_result['service'], service_result['function'])),
                            "w"
                        ) as f:
                            json.dump(service_result["result"], f, cls=DateTimeEncoder)
                    except IOError as e:
                        log.error("Error writing file: {}".format(str(e)))
            except Exception as exc:
                log.error("{} generated an exception: {}".format(region, exc))
                log.error(traceback.format_exc())

    end_time = time.time()
    elapsed_time = end_time - start_time
    print "Total elapsed time for scanning: {}".format(display_time(elapsed_time))
    print "Result stored in  {}/{}".format(output_dir, timestamp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List all resources in all AWS services and regions."
    )
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
    main(
        args.scan,
        args.regions,
        args.output_dir,
        args.log_level,
        args.max_retries,
        args.retry_delay,
        args.concurrent_regions,
        args.concurrent_services,
    )
