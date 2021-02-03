#/usr/bin/python3

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

from aai import config as _config
from aai import converter as _converter
from aai import aws as _aws
from aai import doc as _doc

log = logging.getLogger('aai.main')

def get_inventory(profile_name, region_name, sheet):
    response = _aws.get(profile_name=profile_name, region_name=region_name, sheet=sheet)
    dic = _converter.flatten_list(response, '.')
    return dic

def Execute(name):
    log.info('Started: AWS Auto Inventory')

    log.info("Generating inventory {}".format(name))
    inventory = _config.settings.get_inventory(name)
    if inventory != {}:
        inventory_name = inventory['name']
        profile_name=inventory['aws']['profile']

        log.info('Inventory {} was found'.format(inventory_name))
        log.info('AWS CLI profile {} will be used'.format(profile_name))
        log.info('AWS Regions {} will be scanned'.format(inventory['aws']['region']))

        data=[]
        for region in inventory['aws']['region']:
            for sheet in inventory['sheets']:
                name = sheet['name']
                result = get_inventory(profile_name=profile_name, region_name=region, sheet=sheet)
                data.append({'Name': name, 'Result': result})
        
        transpose = inventory['excel']['transpose']
        _doc.write_data(inventory_name, transpose=transpose, data=data)
    else:
        print("No inventory named {} was found".format(name))

    log.info('Finished: AWS Auto Inventory')
