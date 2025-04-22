#!/usr/bin/env python3
"""
Run the geospatial metrics pipeline.
"""

import argparse
import logging
import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import yaml  # noqa: E402

# Import runner after adding project root to path to avoid import errors
from src.pipeline.runner import Pipeline  # noqa: E402


def setup_logging(log_level: str) -> None:
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run geospatial metrics pipeline")
    parser.add_argument(
        "--config",
        default="config/pipeline.yaml",
        help="Path to config file",
    )
    parser.add_argument("--area", help="Area of interest (overrides config)")
    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD, overrides config)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)

    # Override with command line args
    if args.area:
        config["area"] = args.area
    if args.start_date:
        config["start_date"] = args.start_date

    # Run pipeline
    pipeline = Pipeline(config)
    _ = pipeline.run()

    logging.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()
