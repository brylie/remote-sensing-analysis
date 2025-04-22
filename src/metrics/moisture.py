import ee


def calculate_msi(image: ee.Image) -> ee.Image:
    """
    Calculate Moisture Stress Index (MSI) from Sentinel-2 bands.

    Args:
        image: Sentinel-2 image

    Returns:
        Image with MSI band added
    """
    msi = image.expression(
        "SWIR / NIR",
        {
            "SWIR": image.select("B11").divide(10000),  # SWIR (1.6µm)
            "NIR": image.select("B8").divide(10000),  # NIR
        },
    ).rename("MSI")

    return image.addBands(msi)
