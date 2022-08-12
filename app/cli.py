# -*- coding: utf-8 -*-
# Include standard modules
import argparse
import run

# Define the program description
DESCRIPTION = "Automates creation of detailed inventories from AWS resources."

# Initiate the parser with a description
parser = argparse.ArgumentParser(description=DESCRIPTION)

# Add long and short argument
parser.add_argument("--name", "-n", help="inventory name", required=True)

# Read arguments from the command line
args = parser.parse_args()

if args.name:
    run.execute(name=args.name)
