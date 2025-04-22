# Remote Sensing Analysis

Geospatial analysis of remote sensing data focused on vegetation and moisture metrics.

## Project Goals

The primary objectives of this project are to:
- Derive or obtain Moisture Stress Index (MSI)
- Derive or obtain Leaf Area Index (LAI)

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
│   ├── processed/         # Intermediate processed data
│   └── raw/               # Raw input data
├── docs/                  # Documentation
│   └── research.md        # Research notes and methodology
├── notebooks/             # Jupyter notebooks for analysis
│   └── lai_finland.ipynb  # Finland LAI/MSI analysis example
├── scripts/               # Executable scripts
│   └── run_pipeline.py    # Main pipeline runner
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

## Getting Started

### Prerequisites

- Python 3.9+
- UV package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/brylie/remote-sensing-analysis.git
   cd remote-sensing-analysis
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. Set up Earth Engine authentication (if not previously done):
   ```bash
   earthengine authenticate
   ```

### Usage

#### Running the Pipeline

The main pipeline can be run with:

```bash
python scripts/run_pipeline.py
```

Optional arguments:
- `--config PATH`: Path to config file (default: `config/pipeline.yaml`)
- `--area NAME`: Area of interest (overrides config)
- `--start-date DATE`: Start date (YYYY-MM-DD, overrides config)
- `--log-level LEVEL`: Logging level (default: INFO)

#### Configuration

Edit `config/pipeline.yaml` to customize pipeline settings:

```yaml
# Area of interest
area: "finland"

# Time range for data extraction
start_date: "2024-04-01"  # Format: YYYY-MM-DD
end_date: "2024-04-30"    # Format: YYYY-MM-DD

# Metrics to calculate
metrics:
  - "EVI"
  - "LAI"
  - "MSI"
```

#### Running the Notebooks

The project includes Jupyter notebooks for interactive analysis:

1. Start Jupyter:
   ```bash
   jupyter lab
   ```

2. Navigate to `notebooks/` and open the desired notebook.

## Development

### Adding New Areas

To add new geographic areas for analysis, edit `config/areas.py`:

```python
AREAS: Dict[str, ee.Geometry] = {
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

## License

This project is licensed under the [Apache License Version 2.0](LICENSE).
