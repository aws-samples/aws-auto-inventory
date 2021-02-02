# Include standard modules
import argparse

# Define the program description
text = 'This is a test program. It demonstrates how to use the argparse module with a program description.'

# Initiate the parser with a description
parser = argparse.ArgumentParser(description=text)

# Add long and short argument
parser.add_argument("--width", "-w", help="set output width")

# Read arguments from the command line
args = parser.parse_args()

# Check for --width
if args.width:
    print("Set output width to %s" % args.width)