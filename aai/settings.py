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
import configparser
import boto3
import logging
import confuse as _confuse

log = logging.getLogger("aws-auto-inventory.settings")


class Settings:
    __instance = None

    config = _confuse.Configuration("aws-auto-inventory", __name__)

    @staticmethod
    def get_instance():
        """Static access method."""
        if Settings.__instance == None:
            Settings()
        return Settings.__instance

    def __init__(self):
        """Virtually private constructor."""
        if Settings.__instance != None:
            raise Exception("This class is a Singleton!")
        else:
            Settings.__instance = self

    @staticmethod
    def get_aws_region():
        log.info("Getting AWS Region from config.ini")
        region_name = Settings.config["aws"]["region"].get()
        log.info("Current AWS Region: {}".format(region_name))
        return region_name

    @staticmethod
    def get_aws_profile():
        log.info("Getting AWS Profile")
        profile_name = Settings.config["aws"]["profile"].get()
        log.info("Current AWS Profile: {}".format(profile_name))
        return profile_name

    @staticmethod
    def get_inventory(name):
        log.info("Getting inventories {}".format(name))

        try:
            all_inventories = Settings.config["inventories"].get()
        except _confuse.exceptions.NotFoundError:
            print("Field inventories not found in configuration")
            sys.exit(1)

        log.info("Current inventories:{}".format(all_inventories))

        for i in all_inventories:
            if i["name"] == name:
                return i
        return {}
