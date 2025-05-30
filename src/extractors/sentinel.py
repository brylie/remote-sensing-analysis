import ee


def get_sentinel_data(
    start_date: ee.Date,
    end_date: ee.Date,
    area: ee.Geometry,
) -> ee.ImageCollection:
    """
    Extract Sentinel-2 data for the specified time range and area.

    Args:
        start_date: Start date for data collection
        end_date: End date for data collection
        area: Area of interest

    Returns:
        ee.ImageCollection: Collection of Sentinel-2 images
    """
    # Get the Sentinel-2 image collection
    collection = (
        ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        .filterDate(start_date, end_date)
        .filterBounds(area)
    )

    # Apply cloud filtering if configured (can be extended based on config)
    collection = collection.filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))

    return collection
