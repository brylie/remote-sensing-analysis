# Remote Sensing Analysis

Geospatial analysis of remote sensing data focused on vegetation and moisture metrics.

## Project Goals

The primary objectives of this project are to:
- Derive or obtain Moisture Stress Index (MSI)
- Derive or obtain Leaf Area Index (LAI)

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

Since pre-computed MSI is rarely available, we'll calculate it from:

1. **Sentinel-2 MSI**
   - Resolution: 10-20m (depending on bands)
   - Bands needed: NIR (B8) and SWIR (B11)
   - Source: Copernicus Open Access Hub or AWS Public Dataset
   - Access: sentinelsat package or direct AWS S3 access

2. **Landsat 8/9 OLI**
   - Resolution: 30m
   - Bands needed: NIR (B5) and SWIR (B6)
   - Source: USGS EarthExplorer
   - Access: landsatxplore package

## Metric Progression

### Foundational Metrics

These basic indices provide the foundation for more complex analysis:

1. **Normalized Difference Vegetation Index (NDVI)**
   - Algorithm: NDVI = (NIR - Red) / (NIR + Red)
   - Description: Basic vegetation health and density

2. **Enhanced Vegetation Index (EVI)**
   - Algorithm: EVI = G × [(NIR - Red) / (NIR + C1 × Red - C2 × Blue + L)]
   - Description: Improved vegetation index with soil and atmospheric corrections

3. **Normalized Difference Water Index (NDWI)**
   - Algorithm: NDWI = (NIR - SWIR) / (NIR + SWIR) or (Green - NIR) / (Green + NIR)
   - Description: Water content in vegetation or water bodies

### Intermediate Metrics

These build upon the foundational indices:

4. **Normalized Difference Soil Index (NDSI)**
   - Algorithm: NDSI = (SWIR - NIR) / (SWIR + NIR)
   - Description: Soil exposure assessment

5. **Vegetation Condition Index (VCI)**
   - Algorithm: VCI = 100 × (NDVI - NDVImin) / (NDVImax - NDVImin)
   - Description: Normalized vegetation vigor relative to historical data

### Primary Goal Metrics

The core focus of the project:

6. **Moisture Stress Index (MSI)**
   - Algorithm: MSI = NIR / SWIR
   - Description: Assessment of water stress in vegetation
   - Dependency: Requires NIR and SWIR bands

7. **Leaf Area Index (LAI)**
   - Algorithms:
     - Empirical: LAI = f(NDVI)
     - Physical: LAI = -ln(1-fPAR)/k
     - ML-based: Regression models using spectral data
   - Description: Quantifies leaf material in an ecosystem
   - Dependency: Often derived from NDVI or other vegetation indices

### Advanced Composite Metrics

These more complex indices can provide additional insights:

8. **Vegetation Health Index (VHI)**
   - Algorithm: VHI = α × VCI + (1-α) × TCI
   - Description: Combined vegetation condition and temperature stress
   - Dependency: Requires VCI and temperature data

9. **Normalized Difference Built-up Index (NDBI)**
   - Algorithm: NDBI = (SWIR - NIR) / (SWIR + NIR)
   - Description: Urban area detection

10. **Normalized Difference Urban Index (NDUI)**
    - Algorithm: NDUI = (SWIR - NIR) / (SWIR + NIR + Red)
    - Description: Refined urban feature detection

11. **Normalized Difference Impervious Surface Index (NDISI)**
    - Algorithm: NDISI = (TIR - [(MNDWI + NIR + MIR)/3]) / (TIR + [(MNDWI + NIR + MIR)/3])
    - Description: Impervious surface identification
    - Dependency: Requires thermal data and multiple other indices

## Implementation Strategy

1. Set up environment with necessary Python packages
2. Download pre-computed LAI products from NASA Earthdata or Copernicus
3. Acquire Sentinel-2 or Landsat data for MSI calculation
4. Process and validate the LAI data
5. Calculate MSI from satellite bands
6. Optionally compute additional vegetation indices
7. Perform analysis and visualization

## Software Requirements

- Python libraries:
  - Data access: pyhdf, netCDF4, sentinelsat, landsatxplore, pystac-client
  - Processing: rasterio, xarray, rioxarray, numpy, scipy
  - Analysis: pandas, geopandas
  - Visualization: matplotlib, folium, seaborn
  - Notebook: marimo or jupyter
