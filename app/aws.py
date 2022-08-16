# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import logging
import boto3
import botocore

import converter as _converter
import settings as _settings

log = logging.getLogger("aws-auto-inventory.aws")


def _get_session(inventory):
    """Returns an AWS session"""

    log.info("Started: Get AWS Session")
    try:
        # environment variables overrides values loaded from a profile
        # https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
        session = boto3.Session()
        client = session.client("sts")
        client.get_caller_identity()  # test credentials
    except botocore.exceptions.NoCredentialsError:
        profile_name = _settings.Settings.get_aws_profile(inventory)
        if not profile_name:
            log.error("AWS Profile not found in config.yaml, exitting...")
            sys.exit(1)
        try:
            session = boto3.Session(profile_name=profile_name)
        except botocore.exceptions.ProfileNotFound:
            log.critical("The config profile (%s) could not be found", profile_name)
            sys.exit(1)
        client = session.client("sts")  # test credentials
        client.get_caller_identity()

    log.info("Finished: Get AWS Session")
    return session


def _display_account_info(inventory):
    """Display an AWS Account Information"""

    log.info("Started:AWS Display Account Info")

    session = _get_session(inventory)

    client = session.client(service_name="sts")
    response = client.get_caller_identity()
    account = response["Account"]
    user_id = response["UserId"]
    arn = response["Arn"]

    print(f"Account: {account}")
    print(f"UserId: {user_id}")
    print(f"Arn: {arn}")

    log.info("Finished:AWS Display Account Info")


def get_data(inventory):
    """Get AWS data from specified inventory"""
    log.info("Started: AWS Get Data")

    _display_account_info(inventory)
    settings = _settings.Settings.get_instance()

    regions = settings.get_regions(inventory["name"])  # try config

    data = []
    if regions:
        for region_name in regions:
            for sheet in inventory["sheets"]:
                session = _get_session(
                    inventory
                )  # for a whole region, session might expire

                name = sheet["name"]
                response = _get_service_data(
                    session, region_name=region_name, sheet=sheet
                )
                result = _converter.flatten_list(response, ".")
                data.append({"Name": name, "Result": result})
    return data


def _get_service_data(session, region_name, sheet):
    """Get information about a service described on :sheet allocated on a :region_name"""
    log.info("Started: AWS Get Service Data")
    service = sheet["service"]
    function = sheet["function"]

    # optional
    result_key = sheet.get("result_key", None)
    parameters = sheet.get("parameters", None)

    log.info(
        "Getting data on service %s with function %s in region %s",
        service,
        function,
        region_name,
    )

    response = ""

    try:
        # session = boto3.Session(profile_name=profile_name)
        client = session.client(service, region_name=region_name)

        if parameters is not None:
            if result_key:
                response = client.__getattribute__(function)(**parameters).get(
                    result_key
                )
            else:
                response = client.__getattribute__(function)(**parameters)
        elif result_key:
            response = client.__getattribute__(function)().get(result_key)
        else:
            response = client.__getattribute__(function)()
            # Remove ResponseMetadata as it's not useful
            response.pop("ResponseMetadata", None)
    except Exception as exception:
        log.error("Error while processing %s, %s.\n%s", service, region_name, exception)

    log.debug("Result:{{%s}}", response)

    log.info("Finished: AWS Get Service Data")

    return response
