# Contributing to Remote Sensing Analysis

Thank you for considering contributing to the Remote Sensing Analysis project! This document provides guidelines and information for contributors.

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

## Development Environment

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

# Install development dependencies
uv install --group=dev

# Install the package in development mode
uv pip install -e .

# Set up Earth Engine authentication (if not previously done)
earthengine authenticate
```

## Code Style Guidelines

### Type Annotations

We use Python 3.9+ type annotations throughout the codebase. All functions must have type annotations.

Examples of proper type annotations:

```python
# Basic types
x: int = 1
x: float = 1.0
x: bool = True
x: str = "test"
x: None = None

# Collections
x: list[int] = [1, 2, 3]
x: dict[str, float] = {"field": 2.0}
x: set[str] = {"yes", "no"}
x: tuple[int, str, float] = (3, "yes", 7.5)  # Fixed size tuple
x: tuple[int, ...] = (1, 2, 3)  # Variable size tuple
```

### Type Checking

We use `mypy` for static type checking. Run mypy before submitting any PR:

```bash
uv run mypy .
```

To check a specific file:

```bash
uv run mypy src/pipeline/runner.py
```

### Package Management

We use `uv` for package management. To add new dependencies:

```bash
# Add regular dependencies
uv add <package-name>

# Add development dependencies
uv add --group=dev <package-name>
```

## Extending the Project

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

### Adding New Commands

To extend the CLI with a new command:

1. Edit `scripts/run_pipeline.py`
2. Add a new function with the `@app.command()` decorator
3. Implement the command logic
4. Update documentation

## Testing

When adding new features, make sure to add appropriate tests to validate functionality:

```bash
# Run tests
uv run pytest
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run type checking: `uv run mypy .`
5. Run tests: `uv run pytest`
6. Submit a pull request

## Output File Structure

The pipeline generates several types of output files:

1. **GeoTIFF Files**: Raster files for each calculated index
   - Location: `data/output/rs_metrics_{area}_{date}_{metric}.tif`

2. **Metadata**: JSON file with processing details
   - Location: `data/output/rs_metrics_{area}_{date}_metadata.json`

3. **Statistics Files**: CSV files with statistical analysis
   - Location: `data/output/statistics/rs_metrics_{area}_{date}_{metric}_statistics.csv`

4. **Visualization Files**: PNG files with distribution plots
   - Location: `data/output/statistics/rs_metrics_{area}_{date}_{metric}_distribution_analysis.png`
   - Location: `data/output/statistics/index_comparison.png`
