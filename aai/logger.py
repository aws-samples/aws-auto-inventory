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


import time
import logging
import json
import os
import boto3
from time import gmtime, strftime

t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
file_name = 'AWS_Inventory_{}.xlsx'.format(timestamp)
filepath = "./output/"
os.makedirs(filepath, exist_ok=True)

# --- logging variables

log_filepath    = "./log/"
os.makedirs(log_filepath, exist_ok=True)

# create logger with 'aai_application'
logger = logging.getLogger('aai')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(log_filepath+'aai.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)