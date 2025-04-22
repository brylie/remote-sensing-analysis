# Remote Sensing Analysis

A Python pipeline for analyzing remote sensing data using Google Earth Engine, focusing on vegetation and moisture indices.

## Key Features

- **Satellite Data Extraction**: Seamless integration with Google Earth Engine for acquiring Sentinel data
- **Vegetation Indices**: Implementation of multiple vegetation indices (EVI, LAI)
- **Moisture Analysis**: Calculation of Moisture Stress Index (MSI) for water stress assessment
- **Statistical Analysis**: Distribution analysis and comparison between different indices
- **Modular CLI**: Typer-based command-line interface for running separate pipeline steps
- **Resource Optimization**: Run specific pipeline stages independently to save computational resources
- **Geospatial Processing**: GeoTIFF output with proper coordinate systems and metadata
- **Visualization**: Generate plots and maps for data interpretation
- **Type Safety**: Comprehensive Python type annotations with mypy validation

## Project Goals

The primary objectives of this project are to:
- Derive or obtain Moisture Stress Index (MSI)
- Derive or obtain Leaf Area Index (LAI)
- Provide statistical analysis of vegetation and moisture indices

## Project Structure

The project follows a modular structure to separate concerns and enable reusability:

```
remote-sensing-analysis/
├── config/                # Configuration files
│   ├── areas.py           # Geographic area definitions
│   ├── pipeline.yaml      # Pipeline configuration
│   └── settings.py        # General settings
├── data/                  # Data storage
│   ├── output/            # Generated output files
│   │   └── statistics/    # Statistical analysis results
│   ├── processed/         # Intermediate processed data
│   └── raw/               # Raw input data
├── docs/                  # Documentation
│   └── research.md        # Research notes and methodology
├── notebooks/             # Jupyter notebooks for analysis
│   └── lai_finland.ipynb  # Finland LAI/MSI analysis example
├── scripts/               # Executable scripts
│   └── run_pipeline.py    # Modular CLI pipeline runner
└── src/                   # Source code
    ├── extractors/        # Data extraction modules
    │   └── sentinel.py    # Sentinel imagery extraction
    ├── metrics/           # Index calculation modules
    │   ├── moisture.py    # Moisture metrics (MSI)
    │   └── vegetation.py  # Vegetation metrics (EVI, LAI)
    ├── pipeline/          # Pipeline components
    │   └── runner.py      # Pipeline orchestration
    ├── processors/        # Data processing modules
    │   └── preprocessing.py # Common preprocessing functions
    ├── statistics/        # Statistical analysis
    │   └── distribution.py # Index distribution analysis
    └── visualization/     # Visualization utilities
        └── maps.py        # Map generation helpers
```

## Data Sources

### LAI Data Sources (Pre-computed)

1. **MODIS LAI (MOD15A2H)**
   - Resolution: 500m
   - Temporal coverage: 8-day composites
   - Source: NASA Earthdata (https://lpdaac.usgs.gov/products/mod15a2hv061/)
   - Access: Python libraries (pyhdf, netCDF4) with NASA Earthdata Login

2. **Copernicus Global Land Service LAI**
   - Resolution: 300m (PROBA-V) or 1km (global)
   - Temporal coverage: 10-day composites
   - Source: Copernicus Global Land Service
   - Access: Direct download or Python API

### MSI Source Data

Since pre-computed MSI is rarely available, we calculate it from:

1. **Sentinel-2 MSI**
   - Resolution: 10-20m (depending on bands)
   - Bands needed: NIR (B8) and SWIR (B11)
   - Source: Copernicus Open Access Hub or AWS Public Dataset
   - Access: Google Earth Engine or AWS S3 access

2. **Landsat 8/9 OLI**
   - Resolution: 30m
   - Bands needed: NIR (B5) and SWIR (B6)
   - Source: USGS EarthExplorer
   - Access: Google Earth Engine or landsatxplore package

## Implemented Metrics

### Foundational Metrics

These basic indices provide the foundation for more complex analysis:

1. **Enhanced Vegetation Index (EVI)**
   - Algorithm: `EVI = 2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))`
   - Description: Improved vegetation index with soil and atmospheric corrections
   - Implementation: `src/metrics/vegetation.py`

### Primary Goal Metrics

The core focus of the project:

1. **Moisture Stress Index (MSI)**
   - Algorithm: `MSI = SWIR / NIR`
   - Description: Assessment of water stress in vegetation
   - Implementation: `src/metrics/moisture.py`

2. **Leaf Area Index (LAI)**
   - Algorithm: `LAI = 3.618 * EVI - 0.118`
   - Description: Quantifies leaf material in an ecosystem
   - Implementation: `src/metrics/vegetation.py`

## Installation

### Prerequisites

- Python 3.12+
- UV package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/remote-sensing-analysis.git
cd remote-sensing-analysis

# Set up environment
uv create
uv install

# Install the package in development mode
uv pip install -e .

# Set up Earth Engine authentication (if not previously done)
earthengine authenticate
```

## Usage

The remote sensing analysis pipeline supports modular execution, allowing you to run specific parts of the pipeline independently to save computational resources.

### JupyterLab Environment

The project includes Jupyter notebooks for interactive analysis and visualization:

```bash
# Start JupyterLab
uv run jupyter lab
```

This will open JupyterLab in your browser, where you can access:

- `notebooks/lai_finland.ipynb`: Example notebook for analyzing LAI and MSI for Finland
- Create new notebooks to explore other regions or indices

### Command Line Interface

The CLI uses Typer to provide a structured and user-friendly interface with multiple commands:

```bash
# Show help and available commands
python scripts/run_pipeline.py --help

# Run the full pipeline
python scripts/run_pipeline.py full --config config/pipeline.yaml

# Only extract and process data (skip statistics)
python scripts/run_pipeline.py extract --area finland --start-date 2024-04-01

# Generate statistics from existing GeoTIFF files
python scripts/run_pipeline.py statistics --input-dir data/output --output-dir data/output/statistics
```

### Command Options

#### Common Options

All commands support the following options:

- `--config`, `-c`: Path to the configuration file (default: `config/pipeline.yaml`)
- `--log-level`, `-l`: Log level (DEBUG, INFO, WARNING, ERROR)

#### Full Pipeline Command

```bash
python scripts/run_pipeline.py full [OPTIONS]
```

Options:
- `--area`, `-a`: Area of interest (overrides config)
- `--start-date`, `-s`: Start date (YYYY-MM-DD, overrides config)

#### Extract Data Command

```bash
python scripts/run_pipeline.py extract [OPTIONS]
```

Options:
- `--area`, `-a`: Area of interest (overrides config)
- `--start-date`, `-s`: Start date (YYYY-MM-DD, overrides config)

#### Generate Statistics Command

```bash
python scripts/run_pipeline.py statistics [OPTIONS]
```

Options:
- `--input-dir`, `-i`: Directory containing GeoTIFF files
- `--output-dir`, `-o`: Directory to save statistics
- `--pattern`, `-p`: Glob pattern to match GeoTIFF files (default: `*.tif`)

## Configuration

The pipeline is configured through a YAML file. Example configuration:

```yaml
# Area of interest
area: "finland"

# Time range for data extraction
start_date: "2024-04-01"
end_date: "2024-04-30"

# Metrics to calculate
metrics:
  - "EVI"
  - "LAI"
  - "MSI"

# Output settings
output:
  directory: "data/output"
  prefix: "rs_metrics_"

# Statistics settings
statistics:
  enabled: true
  output_directory: "data/output/statistics"
```

## Development

### Adding New Areas

To add new geographic areas for analysis, edit `config/areas.py`:

```python
AREAS: dict[str, ee.Geometry] = {
    "finland": ee.FeatureCollection("FAO/GAUL/2015/level0")
        .filter(ee.Filter.eq("ADM0_NAME", "Finland"))
        .geometry(),
    "your_new_area": ee.Geometry.Rectangle([lon1, lat1, lon2, lat2])
}
```

### Adding New Metrics

To add a new vegetation or moisture index:

1. Add the calculation function to the appropriate module in `src/metrics/`
2. Update the pipeline to include the new metric in `src/pipeline/runner.py`
3. Add the metric name to your `config/pipeline.yaml`

### Running Type Checks

We use `mypy` for static type checking:

```bash
# Check the entire codebase
uv run mypy .

# Check a specific file
uv run mypy src/pipeline/runner.py
```

## Output Files

The pipeline generates several types of output files:

1. **GeoTIFF Files**: Raster files for each calculated index
   - Location: `data/output/rs_metrics_{area}_{date}_{metric}.tif`
   - Example: `data/output/rs_metrics_finland_20240401_EVI.tif`

2. **Metadata**: JSON file with processing details
   - Location: `data/output/rs_metrics_{area}_{date}_metadata.json`

3. **Statistics Files**: CSV files with statistical analysis
   - Location: `data/output/statistics/rs_metrics_{area}_{date}_{metric}_statistics.csv`

4. **Visualization Files**: PNG files with distribution plots
   - Location: `data/output/statistics/rs_metrics_{area}_{date}_{metric}_distribution_analysis.png`
   - Location: `data/output/statistics/index_comparison.png`

## License

This project is licensed under the [Apache License Version 2.0](LICENSE).
