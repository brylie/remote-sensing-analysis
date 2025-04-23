[![codecov](https://codecov.io/gh/brylie/remote-sensing-analysis/graph/badge.svg?token=HN2WAH38B4)](https://codecov.io/gh/brylie/remote-sensing-analysis)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Contributors](https://img.shields.io/github/contributors/brylie/remote-sensing-analysis)](https://github.com/brylie/remote-sensing-analysis/graphs/contributors)
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg)](#contributors-)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

# Remote Sensing Analysis

A Python pipeline for analyzing remote sensing data using Google Earth Engine, focusing on vegetation and moisture indices.

## Key Features

- **Satellite Data Extraction**: Seamless integration with Google Earth Engine for acquiring Sentinel data
- **Vegetation Indices**: Implementation of multiple vegetation indices (EVI, LAI)
- **Moisture Analysis**: Calculation of Moisture Stress Index (MSI) for water stress assessment
- **Statistical Analysis**: Distribution analysis and comparison between different indices
- **Modular CLI**: Command-line interface for running separate pipeline steps
- **Resource Optimization**: Run specific pipeline stages independently to save computational resources
- **Geospatial Processing**: GeoTIFF output with proper coordinate systems and metadata
- **Visualization**: Generate plots and maps for data interpretation

## About the Project

Remote Sensing Analysis provides tools for analyzing satellite imagery to derive vegetation and moisture indices. The primary objectives are to:

- Extract and process Sentinel satellite data using Google Earth Engine
- Calculate vegetation indices (EVI, LAI) and moisture stress index (MSI)
- Generate statistical analysis of these indices for environmental assessment
- Provide both a command-line interface and notebooks for interactive analysis

## Data Sources

The pipeline works with the following data sources:

### Sentinel-2 MSI
- Used for calculating vegetation and moisture indices
- Accessed through Google Earth Engine
- 10-20m resolution (depending on bands)

### MODIS and Copernicus Products (Optional)
- Can be integrated for comparison with pre-calculated indices
- Available through their respective APIs

## Installation

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/remote-sensing-analysis.git
cd remote-sensing-analysis
```

```bash
# Set up environment
uv venv
```

```bash
# Activate the environment Mac/Linux
source .venv/bin/activate
```

```bash
# Activate the environment Windows
.venv\Scripts\activate
```

```bash
# Install dependencies
uv sync
```

```bash
# Set up Earth Engine authentication
earthengine authenticate
```

## Usage

The remote sensing analysis pipeline supports modular execution, allowing you to run specific parts of the pipeline independently.

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

## Testing

The project includes comprehensive unit tests for all modules. Run tests using pytest:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests for a specific module
uv run pytest tests/processors/

# Run a specific test file
uv run pytest tests/processors/test_preprocessing.py
```

### Test Coverage

You can check test coverage using pytest-cov:

```bash
# Run tests with coverage report
uv run pytest --cov=src

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# View coverage for specific modules
uv run pytest --cov=src.processors --cov=src.statistics
```

After generating the HTML report, open `htmlcov/index.html` in your browser to view detailed coverage information.

## Results and Output Files

The pipeline generates the following outputs:

1. **GeoTIFF Files**: Raster files for each calculated index
   - Example: `data/output/rs_metrics_finland_20240401_EVI.tif`

2. **Statistical Analysis**: CSV files with summary statistics and distribution plots
   - Example: `data/output/statistics/rs_metrics_finland_20240401_EVI_statistics.csv`

3. **Comparison Plots**: Visualizations comparing different indices
   - Example: `data/output/statistics/index_comparison.png`

## Implemented Metrics

### Enhanced Vegetation Index (EVI)
- Improved vegetation index with soil and atmospheric corrections
- Formula: `EVI = 2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))`

### Leaf Area Index (LAI)
- Quantifies leaf material in an ecosystem
- Formula: `LAI = 3.618 * EVI - 0.118`

### Moisture Stress Index (MSI)
- Assessment of water stress in vegetation
- Formula: `MSI = SWIR / NIR`

## Contributing

For information on contributing to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [Apache License Version 2.0](LICENSE).

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/brylie"><img src="https://avatars.githubusercontent.com/u/17307?v=4" width="100px;" alt="Brylie Christopher Oxley"/><br /><sub><b>Brylie Christopher Oxley</b></sub></a><br /><a href="https://github.com/brylie/remote-sensing-analysis/commits?author=brylie" title="Code">💻</a> <a href="https://github.com/brylie/remote-sensing-analysis/commits?author=brylie" title="Documentation">📖</a> <a href="#ideas-brylie" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind are welcome!

## Code of Conduct

We are committed to fostering an open and welcoming environment. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Community Support

- **Issues**: Please use [GitHub Issues](https://github.com/brylie/remote-sensing-analysis/issues) for bug reports, feature requests, and discussions.
- **Discussions**: For questions and general discussions, use [GitHub Discussions](https://github.com/brylie/remote-sensing-analysis/discussions).

We welcome contributions from developers of all skill levels. If you're new to the project or to remote sensing in general, look for issues labeled `good first issue` to get started.
