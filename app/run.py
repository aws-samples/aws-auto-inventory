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

import aws as _aws
import config as _config
import doc as _doc

log = logging.getLogger("aws-auto-inventory.main")


def execute(name):
    """Generates a new report with the given :name"""
    log.info("Started: AWS Auto Inventory")
    log.info("Generating inventory: %s", name)

    inventory = _config.settings.get_inventory(name)
    if inventory != {}:
        inventory_name = inventory["name"]
        log.info("Inventory %s was found", inventory_name)

        data = _aws.get_data(inventory)
        if data:
            _doc.write_data(inventory_name, inventory, data)
        else:
            log.info("No data to be saved")
    else:
        print("No inventory named %s was found", name)

    log.info("Finished: AWS Auto Inventory")
