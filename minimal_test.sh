#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run a minimal test with S3 buckets in a single region
python scan.py -s scan/sample/services/s3.json --regions us-east-1 --organization-scan --log_level DEBUG

# Print the location of the results
echo "Test complete! Check the output directory for results."