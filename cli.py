# Include standard modules
import argparse
from aai import run
 
# Define the program description
text = 'This is a test program. It demonstrates how to use the argparse module with a program description.'

# Initiate the parser with a description
parser = argparse.ArgumentParser(description=text)

# Add long and short argument
parser.add_argument("--name", "-n", help="inventory name", required=True)

# Read arguments from the command line
args = parser.parse_args()

if args.name:
    run.Execute(name=args.name)