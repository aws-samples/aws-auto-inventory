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
import confuse as _confuse

log = logging.getLogger("aws-auto-inventory.settings")


class Settings:
    """Manages the config.yaml user settings"""

    __instance = None

    config = _confuse.Configuration("aws-auto-inventory", __name__)

    @staticmethod
    def get_instance():
        """Static access method."""
        if Settings.__instance is None:
            Settings()
        return Settings.__instance

    def __init__(self):  # sourcery skip: raise-specific-error
        """Virtually private constructor."""
        if Settings.__instance is not None:
            raise Exception("This class is a Singleton!")
        else:
            Settings.__instance = self

    @staticmethod
    def get_regions(inventory_name):
        """Return AWS Regions defined by user on settings"""
        log.info("Started: Seetings Get AWS Regions")
        inventory = Settings.get_inventory(inventory_name)
        regions = []
        if "aws" in inventory:
            regions = inventory.get("aws", None).get("region", None)
            if not regions:
                log.info("AWS Region(s) not found in config.yaml, skipping...")

        if len(regions) == 0:
            regions.append("us-east-1")  # default region

        log.info("Finished: Seetings Get AWS Regions")
        return regions

    @staticmethod
    def get_aws_profile(inventory):
        """Return the AWS Profile defined by user on settings"""
        log.info("Started: Settings Get AWS Profile")

        profile = None
        if "aws" in inventory:
            profile = inventory.get("aws", None).get("profile", None)

        if profile:
            log.info("Current AWS Profile: %s", profile)

        log.info("Finished: Settings Get AWS Profile")
        return profile

    @staticmethod
    def get_inventory(name):
        """Find and return an inventory"""
        log.info("Getting inventories %s", name)

        try:
            all_inventories = Settings.config["inventories"].get()
        except _confuse.exceptions.NotFoundError:
            print("Field inventories not found in configuration")
            sys.exit(1)

        log.info(f"Current inventories:{all_inventories}")

        return next((i for i in all_inventories if i["name"] == name), {})
