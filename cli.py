# Include standard modules
import argparse
from aai import run
 
# Define the program description
description = 'Automates creation of detailed inventories from AWS resources.'

# Initiate the parser with a description
parser = argparse.ArgumentParser(description=description)

# Add long and short argument
parser.add_argument("--name", "-n", help="inventory name", required=True)

# Read arguments from the command line
args = parser.parse_args()

if args.name:
    run.Execute(name=args.name)