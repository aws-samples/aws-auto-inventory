# -*- coding: utf-8 -*-
import boto3
import logging
import json
import argparse
import concurrent.futures
import os
from datetime import datetime
import traceback
import botocore
import time

# Get the current timestamp
timestamp = datetime.now().isoformat(timespec="minutes")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def setup_logging(log_dir, log_level):
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"aws_resources_{timestamp}.log"
    log_file = os.path.join(log_dir, log_filename)
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
    return logging.getLogger(__name__)

def api_call_with_retry(client, method, **kwargs):
    for i in range(10):
        try:
            return getattr(client, method)(**kwargs)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'Throttling':
                wait_time = 2 ** i
                print(f"Throttling AWS API requests, will retry in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise error
    return None

def _get_service_data(session, region_name, service, log):
    function = service["function"]
    result_key = service.get("result_key", None)
    parameters = service.get("parameters", None)

    log.info(
        "Getting data on service %s with function %s in region %s",
        service["service"],
        function,
        region_name,
    )

    try:
        client = session.client(service["service"], region_name=region_name)
        if not hasattr(client, function):
            log.warning(
                "Function %s does not exist for service %s in region %s",
                function,
                service["service"],
                region_name,
            )
            return None
        if parameters is not None:
            if result_key:
                response = api_call_with_retry(client, function, **parameters).get(result_key)
            else:
                response = api_call_with_retry(client, function, **parameters)
        elif result_key:
            response = api_call_with_retry(client, function)().get(result_key)
        else:
            response = api_call_with_retry(client, function)()
            if isinstance(response, dict):
                response.pop("ResponseMetadata", None)
    except Exception as exception:
        log.error(
            "Error while processing %s, %s.\n%s: %s",
            service["service"],
            region_name,
            type(exception).__name__,
            exception,
        )
        log.error(traceback.format_exc())
        return None

    log.info("Finished: AWS Get Service Data")
    log.debug(
        "Result for %s, function %s, region %s: %s",
        service["service"],
        function,
        region_name,
        response,
    )
    return {"region": region_name, "service": service["service"], "result": response}


def process_region(region, services, session, log):
    log.info("Started processing for region: %s", region)

    region_results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_service = {
            executor.submit(_get_service_data, session, region, service, log): service
            for service in services
        }
        for future in concurrent.futures.as_completed(future_to_service):
            service = future_to_service[future]
            try:
                result = future.result()
                if result["result"]:
                    region_results.append(result)
                    log.info("Successfully processed service: %s", service["service"])
                else:
                    log.info("No data found for service: %s", service["service"])
            except Exception as exc:
                log.error("%r generated an exception: %s" % (service["service"], exc))
                log.error(traceback.format_exc())

    log.info("Finished processing for region: %s", region)
    return region_results

def display_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

def main(scan, regions, output_dir, log_level):
    import time

    session = boto3.Session()
    log = setup_logging(output_dir, log_level)

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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_region = {
            executor.submit(process_region, region, services, session, log): region
            for region in regions
        }
        for future in concurrent.futures.as_completed(future_to_region):
            region = future_to_region[future]
            try:
                region_results = future.result()
                results.extend(region_results)
                for service_result in region_results:
                    directory = os.path.join(output_dir, timestamp, region)
                    os.makedirs(directory, exist_ok=True)
                    with open(
                        os.path.join(directory, f"{service_result['service']}.json"),
                        "w",
                    ) as f:
                        json.dump(service_result["result"], f, cls=DateTimeEncoder)
            except Exception as exc:
                log.error("%r generated an exception: %s" % (region, exc))
                log.error(traceback.format_exc())

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total elapsed time for scanning: {display_time(elapsed_time)}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List all resources in all AWS services and regions."
    )
    parser.add_argument(
        "-s",
        "--scan",
        help="JSON file containing the AWS services to scan",
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
    args = parser.parse_args()
    main(args.scan, args.regions, args.output_dir, args.log_level)
