import ee

# Dictionary of predefined areas of interest
AREAS = {
    "finland": ee.FeatureCollection("FAO/GAUL/2015/level0")
    .filter(ee.Filter.eq("ADM0_NAME", "Finland"))
    .geometry(),
    # Add more areas as needed
}


def get_area(name: str):
    """Get area of interest by name."""
    if name not in AREAS:
        raise ValueError(
            f"Area '{name}' not found. Available areas: {list(AREAS.keys())}"
        )
    return AREAS[name]
