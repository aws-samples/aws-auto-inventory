# Include standard modules
import getopt, sys

# Get full command-line arguments
full_cmd_arguments = sys.argv

# Keep all but the first
argument_list = full_cmd_arguments[1:]

# You might have noticed that the o short option was proceeded by a colon, :. This tells getopt that this option should be assigned a value.
short_options = "ho:v"
long_options = ["help", "output=", "verbose"]

print(argument_list)

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
    # Output error, and return with an error code
    print (str(err))
    sys.exit(2)

# Evaluate given options
for current_argument, current_value in arguments:
    if current_argument in ("-v", "--verbose"):
        print ("Enabling verbose mode")
    elif current_argument in ("-h", "--help"):
        print ("Displaying help")
    elif current_argument in ("-o", "--output"):
        print (("Enabling special output mode (%s)") % (current_value))