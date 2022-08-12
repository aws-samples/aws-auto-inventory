# -*- coding: utf-8 -*-
# /usr/bin/python3

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

import logging

import config as _config
import converter as _converter
import aws as _aws
import doc as _doc

log = logging.getLogger("aws-auto-inventory.main")


def get_inventory(session, region_name, sheet):
    """Return an inventory configuration"""
    response = _aws.get(session, region_name=region_name, sheet=sheet)
    dic = _converter.flatten_list(response, ".")
    return dic


def execute(name):
    """Generates a new report with the given :name"""
    log.info("Started: AWS Auto Inventory")

    log.info("Generating inventory: %s", name)
    inventory = _config.settings.get_inventory(name)
    if inventory != {}:
        inventory_name = inventory["name"]
        session = _aws.get_session()
        # if os.environ['AWS_ACCESS_KEY_ID']:
        #     print('AWS_ACCESS_KEY_ID found')

        # if os.environ['AWS_SECRET_ACCESS_KEY']:
        #     print('AWS_SECRET_ACCESS_KEY found')

        # if 'AWS_DEFAULT_REGION' in os.environ.items:
        #     print('AWS_DEFAULT_REGION found')

        # if os.environ['AWS_PROFILE']:
        #     print('AWS_PROFILE found')

        # if os.environ['AWS_SESSION_TOKEN']:
        #     print('AWS_SESSION_TOKEN')

        # profile_name = inventory["aws"]["profile"]  # optional

        log.info("Inventory %s was found", inventory_name)
        # log.info("AWS CLI profile %s will be used", profile_name) # optional
        # log.info("AWS Regions %s will be scanned", inventory["aws"]["region"])

        data = []
        for region in inventory["aws"]["region"]:
            for sheet in inventory["sheets"]:
                name = sheet["name"]
                result = get_inventory(session=session, region_name=region, sheet=sheet)
                data.append({"Name": name, "Result": result})

        transpose = inventory["excel"]["transpose"]
        _doc.write_data(inventory_name, transpose=transpose, data=data)
    else:
        print("No inventory named %s was found", name)

    log.info("Finished: AWS Auto Inventory")
