#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# Read the version from the package
with open(os.path.join('aws_auto_inventory', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = '0.1.0'  # Default version if not found

# Read the long description from README.md
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='aws-auto-inventory',
    version=version,
    description='AWS Auto Inventory - Scan AWS resources and generate inventory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AWS Samples',
    author_email='aws-samples@amazon.com',
    url='https://github.com/aws-samples/aws-auto-inventory',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3>=1.20.0',
        'pydantic>=1.8.0',
        'pyjq>=2.5.0',
        'pandas>=1.3.0',
        'xlsxwriter>=3.0.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'aws-auto-inventory=aws_auto_inventory.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    python_requires='>=3.8',
    keywords='aws, inventory, cloud, resources',
    license='Apache License 2.0',
)