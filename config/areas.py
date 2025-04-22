import ee

# Dictionary of predefined areas of interest
AREAS: dict[str, ee.Geometry] = {
    "finland": ee.FeatureCollection("FAO/GAUL/2015/level0")
    .filter(ee.Filter.eq("ADM0_NAME", "Finland"))
    .geometry(),
    # Add more areas as needed
}


def get_area(name: str) -> ee.Geometry:
    """
    Get area of interest by name.

    Args:
        name: Name of the predefined area

    Returns:
        Geometry object representing the area

    Raises:
        ValueError: If the specified area name is not found
    """
    if name not in AREAS:
        raise ValueError(
            f"Area '{name}' not found. Available areas: {list(AREAS.keys())}"
        )
    return AREAS[name]
