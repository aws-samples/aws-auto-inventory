"""
Command-line interface for AWS Auto Inventory.
"""
import os
import sys
import argparse
import logging
from typing import List, Optional

import boto3

from .config.loader import ConfigLoader
from .config.validator import ConfigValidator
from .core.scan_engine import ScanEngine
from .output.processor import OutputProcessor
from .utils.logging import setup_logging


def check_aws_credentials(profile_name: Optional[str] = None) -> bool:
    """
    Check AWS credentials by calling the STS GetCallerIdentity operation.
    
    Args:
        profile_name: AWS profile name.
        
    Returns:
        True if credentials are valid, False otherwise.
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"Authenticated as: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"Error verifying AWS credentials: {e}")
        return False


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="AWS Auto Inventory - Scan AWS resources and generate inventory"
    )
    
    parser.add_argument(
        "-c", "--config", required=True,
        help="Path to configuration file (YAML or JSON)"
    )
    
    parser.add_argument(
        "-o", "--output-dir", default="output",
        help="Directory to store output files (default: output)"
    )
    
    parser.add_argument(
        "-f", "--format", choices=["json", "excel", "both"], default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--max-regions", type=int, default=None,
        help="Maximum number of regions to scan concurrently"
    )
    
    parser.add_argument(
        "--max-services", type=int, default=None,
        help="Maximum number of services to scan concurrently per region"
    )
    
    parser.add_argument(
        "--max-retries", type=int, default=3,
        help="Maximum number of retries for API calls (default: 3)"
    )
    
    parser.add_argument(
        "--retry-delay", type=int, default=2,
        help="Base delay in seconds between retries (default: 2)"
    )
    
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO", help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Validate configuration and exit without scanning"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for AWS Auto Inventory.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    log_dir = os.path.join(args.output_dir, "logs")
    logger = setup_logging(log_dir, args.log_level)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config_loader = ConfigLoader()
        try:
            config = config_loader.load_config(args.config)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            print(f"Error loading configuration: {e}")
            return 1
        
        # Validate configuration
        logger.info("Validating configuration")
        validator = ConfigValidator()
        validation_errors = validator.validate(config)
        
        if validation_errors:
            logger.error("Configuration validation failed:")
            for error in validation_errors:
                logger.error(f"  - {error}")
                print(f"Configuration error: {error}")
            
            return 1
        
        if args.validate_only:
            logger.info("Configuration validation successful")
            print("Configuration validation successful")
            return 0
        
        # Check AWS credentials
        for inventory in config.inventories:
            if not check_aws_credentials(inventory.aws.profile):
                logger.error(f"Invalid AWS credentials for inventory {inventory.name}")
                print(f"Invalid AWS credentials for inventory {inventory.name}")
                return 1
        
        # Determine output formats
        formats = []
        if args.format in ["json", "both"]:
            formats.append("json")
        if args.format in ["excel", "both"]:
            formats.append("excel")
        
        # Create scan engine
        scan_engine = ScanEngine(
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
            max_workers_regions=args.max_regions,
            max_workers_services=args.max_services
        )
        
        # Run scan
        logger.info("Starting scan")
        try:
            results = scan_engine.scan(config)
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            print(f"Error during scan: {e}")
            return 1
        
        # Process output
        logger.info("Processing output")
        output_processor = OutputProcessor()
        output_processor.process(results, args.output_dir, formats)
        
        logger.info("Scan completed successfully")
        print(f"Scan completed successfully. Results stored in {args.output_dir}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())