import ee


def add_date(image: ee.Image) -> ee.Image:
    """
    Add a date band to an image.

    Args:
        image: Input satellite image

    Returns:
        Image with additional date band
    """
    img_date = ee.Date(image.date())
    img_date = ee.Number.parse(img_date.format("YYYYMMdd"))

    return image.addBands(ee.Image(img_date).rename("date").toInt())
