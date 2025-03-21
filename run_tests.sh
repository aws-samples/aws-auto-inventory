#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run tests with coverage
pytest --cov=. tests/

# Generate HTML coverage report
coverage html

echo "Tests complete! Check the htmlcov directory for coverage report."