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

import argparse
import run

# Define the program description
DESCRIPTION = "Automates creation of detailed inventories from AWS resources."

# Initiate the parser with a description
parser = argparse.ArgumentParser(description=DESCRIPTION)

# Add long and short argument
parser.add_argument("--name", "-n", help="inventory name", required=True)
parser.add_argument("--profile", "-p", help="aws profile name", required=False)

# Read arguments from the command line
args = parser.parse_args()

if args.name:
    run.execute(name=args.name, profile=args.profile)
