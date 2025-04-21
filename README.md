# Remote Observation Analysis

Geospatial analysis of remote observation data focused on vegetation and moisture metrics.

## Project Goals

The primary objectives of this project are to:
- Derive or obtain Moisture Stress Index (MSI)
- Derive or obtain Leaf Area Index (LAI)

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

1. Acquire appropriate satellite imagery (Landsat, Sentinel, MODIS)
2. Process and prepare bands (NIR, Red, SWIR, etc.)
3. Calculate foundational metrics (NDVI, NDWI)
4. Derive intermediate metrics
5. Compute goal metrics (MSI, LAI)
6. Optionally calculate advanced composite metrics

## Data Requirements

- Multi-spectral satellite imagery with:
  - Near-infrared (NIR) band
  - Red band
  - Shortwave infrared (SWIR) band
  - Blue band (for EVI)
  - Thermal band (for some advanced indices)
- Historical data (for VCI calculation)
- Ground truth data (for validation)
