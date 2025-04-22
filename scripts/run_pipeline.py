#!/usr/bin/env python3
"""
Run the geospatial metrics pipeline with modular steps.
"""

import logging
import os
import sys
from enum import Enum
from pathlib import Path

import typer
import yaml

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.pipeline.runner import Pipeline  # noqa: E402


class LogLevel(str, Enum):
    """Log level options for the CLI."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


app = typer.Typer(help="Remote sensing analysis pipeline")


def setup_logging(log_level: LogLevel) -> None:
    """Configure logging.

    Args:
        log_level: The log level to use
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_config(config_path: Path) -> dict:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    with open(config_path) as f:
        return yaml.safe_load(f)


@app.callback()
def callback() -> None:
    """Remote sensing analysis pipeline with modular execution steps."""
    pass


@app.command()
def full(
    config: Path = typer.Option(
        "config/pipeline.yaml",
        "--config",
        "-c",
        help="Path to config file",
    ),
    area: str | None = typer.Option(
        None,
        "--area",
        "-a",
        help="Area of interest (overrides config)",
    ),
    start_date: str | None = typer.Option(
        None,
        "--start-date",
        "-s",
        help="Start date (YYYY-MM-DD, overrides config)",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level",
        "-l",
        help="Log level",
    ),
) -> None:
    """Run the full pipeline from data extraction to statistics generation."""
    setup_logging(log_level)
    logging.info("Starting full pipeline run")

    # Load config
    config_dict = load_config(config)

    # Override with command line args
    if area:
        config_dict["area"] = area
    if start_date:
        config_dict["start_date"] = start_date

    # Run pipeline
    pipeline = Pipeline(config_dict)
    _ = pipeline.run()

    logging.info("Full pipeline completed successfully")


@app.command()
def extract(
    config: Path = typer.Option(
        "config/pipeline.yaml",
        "--config",
        "-c",
        help="Path to config file",
    ),
    area: str | None = typer.Option(
        None,
        "--area",
        "-a",
        help="Area of interest (overrides config)",
    ),
    start_date: str | None = typer.Option(
        None,
        "--start-date",
        "-s",
        help="Start date (YYYY-MM-DD, overrides config)",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level",
        "-l",
        help="Log level",
    ),
) -> None:
    """Extract and process satellite data without generating statistics."""
    setup_logging(log_level)
    logging.info("Starting data extraction and processing")

    # Load config
    config_dict = load_config(config)

    # Override with command line args
    if area:
        config_dict["area"] = area
    if start_date:
        config_dict["start_date"] = start_date

    # Disable statistics
    config_dict["statistics"] = {"enabled": False}

    # Run pipeline
    pipeline = Pipeline(config_dict)
    _ = pipeline.run()

    logging.info("Data extraction and processing completed successfully")


@app.command()
def statistics(
    config: Path = typer.Option(
        "config/pipeline.yaml",
        "--config",
        "-c",
        help="Path to config file",
    ),
    input_dir: Path | None = typer.Option(
        None,
        "--input-dir",
        "-i",
        help="Directory containing GeoTIFF files (overrides config)",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save statistics (overrides config)",
    ),
    pattern: str = typer.Option(
        "*.tif",
        "--pattern",
        "-p",
        help="Glob pattern to match GeoTIFF files",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level",
        "-l",
        help="Log level",
    ),
) -> None:
    """Generate statistics from existing GeoTIFF files."""
    setup_logging(log_level)
    logging.info("Starting statistics generation")

    # Load config
    config_dict = load_config(config)

    # Override with command line args
    if input_dir:
        if "output" not in config_dict:
            config_dict["output"] = {}
        config_dict["output"]["directory"] = str(input_dir)

    if output_dir:
        if "statistics" not in config_dict:
            config_dict["statistics"] = {}
        config_dict["statistics"]["output_directory"] = str(output_dir)

    # Ensure statistics are enabled
    if "statistics" not in config_dict:
        config_dict["statistics"] = {}
    config_dict["statistics"]["enabled"] = True

    # Load existing GeoTIFF files
    input_directory = Path(config_dict["output"]["directory"])
    geotiff_files = list(input_directory.glob(pattern))

    if not geotiff_files:
        logging.error(
            f"No GeoTIFF files found in {input_directory} matching pattern {pattern}",
        )
        raise typer.Exit(code=1)

    # Group files by metrics and run statistics generation
    logging.info(f"Found {len(geotiff_files)} GeoTIFF files")

    # Initialize pipeline and manually run statistics step
    pipeline = Pipeline(config_dict)

    # Extract metric name from file and build dictionary
    saved_files = {}
    for file_path in geotiff_files:
        # Try to extract metric from filename
        filename = file_path.name
        # Simple parsing: look for common vegetation indices
        for metric in ["EVI", "LAI", "MSI", "NDVI", "NDWI"]:
            if metric in filename:
                saved_files[metric] = file_path
                logging.info(f"Loaded {metric} from {file_path}")
                break

    if not saved_files:
        logging.error("Could not identify metrics in the filenames")
        raise typer.Exit(code=1)

    # Run just the statistics step
    pipeline._generate_statistics(saved_files)

    logging.info("Statistics generation completed successfully")


if __name__ == "__main__":
    app()
