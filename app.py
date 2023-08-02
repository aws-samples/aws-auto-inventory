import boto3
import logging
import json
import argparse
import concurrent.futures
import os
from datetime import datetime

# Get the current timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define a custom JSONEncoder class to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# Initialize logger
def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f'aws_resources_{timestamp}.log'

    # Define the log file path
    log_file = os.path.join(log_dir, log_filename)

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(handler)

    logging.basicConfig(level=logging.INFO)

    return logging.getLogger(__name__)

# Define a function to get data for a specific AWS service
def _get_service_data(session, region_name, sheet, log):
    service = sheet["service"]
    function = sheet["function"]
    result_key = sheet.get("result_key", None)
    parameters = sheet.get("parameters", None)

    log.info("Getting data on service %s with function %s in region %s", service, function, region_name)

    try:
        client = session.client(service, region_name=region_name)
        if not hasattr(client, function):
            log.warning(f"Function {function} does not exist for service {service} in region {region_name}")
            return None

        # Invoke the method and get the response
        if parameters is not None:
            if result_key:
                response = getattr(client, function)(**parameters).get(result_key)
            else:
                response = getattr(client, function)(**parameters)
        elif result_key:
            response = getattr(client, function)().get(result_key)
        else:
            response = getattr(client, function)()
            if isinstance(response, dict):
                # Remove ResponseMetadata as it's not generally needed
                response.pop("ResponseMetadata", None)
    except Exception as exception:
        log.error("Error while processing %s, %s.\n%s: %s", service, region_name, type(exception).__name__, exception)
        return None

    log.info("Finished: AWS Get Service Data")
    log.debug("Result for %s, function %s, region %s: %s", service, function, region_name, response)

    return response

# Define a function to process each region
def process_region(region, services, session, log):
    region_results = []
    log.info(f'Started processing for region: {region}')

    for service in services:
        log.info(f'Started processing for service: {service["service"]}')
        result = _get_service_data(session, region, service, log)
        if result:
            region_results.append({
                'region': region,
                'service': service['service'],
                'result': result
            })
            log.info(f'Successfully processed service: {service["service"]}')
        else:
            log.info(f'No data found for service: {service["service"]}')

    log.info(f'Finished processing for region: {region}')
    return region_results

def main(services_sheet, regions, output_dir):
    session = boto3.Session()

    # Setup logging
    log = setup_logging(output_dir)

    # Load the services from the JSON file
    with open(services_sheet, 'r') as f:
        services = json.load(f)

    # Get the list of regions if not provided
    if not regions:
        ec2_client = session.client('ec2')
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions'] if region['OptInStatus'] == 'opt-in-not-required' or region['OptInStatus'] == 'opted-in']

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_region = {executor.submit(process_region, region, services, session, log): region for region in regions}
        for future in concurrent.futures.as_completed(future_to_region):
            region = future_to_region[future]
            try:
                region_results = future.result()
                results.extend(region_results)

                # Save results for each region
                for service_result in region_results:
                    directory = os.path.join(output_dir, timestamp, region)
                    os.makedirs(directory, exist_ok=True)
                    with open(os.path.join(directory, f"{service_result['service']}.json"), 'w') as f:
                        json.dump(service_result['result'], f, cls=DateTimeEncoder)

            except Exception as exc:
                log.error('%r generated an exception: %s' % (region, exc))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List all resources in all AWS services and regions.')
    parser.add_argument('-s', '--services_sheet', help='JSON file containing the AWS services to scan', required=True)
    parser.add_argument('-r', '--regions', nargs='+', help='List of AWS regions to scan')
    parser.add_argument('-o', '--output_dir', default='output', help='Directory to store the results')

    args = parser.parse_args()
    main(args.services_sheet, args.regions, args.output_dir)
