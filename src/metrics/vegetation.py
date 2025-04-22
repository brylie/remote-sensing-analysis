import ee


def calculate_evi(image: ee.Image) -> ee.Image:
    """
    Calculate Enhanced Vegetation Index (EVI) from Sentinel-2 imagery.

    Args:
        image: Sentinel-2 image

    Returns:
        Image with EVI band added
    """
    evi = image.expression(
        "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
        {
            "NIR": image.select("B8").divide(10000),
            "RED": image.select("B4").divide(10000),
            "BLUE": image.select("B2").divide(10000),
        },
    ).rename("EVI")

    return image.addBands(evi)


def calculate_lai(image: ee.Image) -> ee.Image:
    """
    Calculate Leaf Area Index (LAI) from the EVI band.

    Args:
        image: Image containing EVI band

    Returns:
        Image with LAI band added
    """
    lai = image.expression(
        "(3.618 * EVI - 0.118)", {"EVI": image.select("EVI")}
    ).rename("LAI")

    return image.addBands(lai)


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
