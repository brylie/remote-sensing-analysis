import unittest.mock as mock

import pytest


# Mock classes for Earth Engine objects
class MockDate:
    def __init__(self, date_millis):
        self.date_millis = date_millis

    def format(self, format_str: str) -> str:
        """Mock the format method for a specific test case."""
        if (
            format_str == "YYYYMMdd" and self.date_millis == 1617235200000
        ):  # April 1, 2021
            return "20210401"
        return "00000000"


class MockImage:
    def __init__(self, bands=None, date_millis=None):
        self.bands = bands or {}
        self.date_millis = date_millis or 0

    def addBands(self, image):
        """Add bands from another image to this one."""
        new_bands = self.bands.copy()

        if isinstance(image, MockImage):
            new_bands.update(image.bands)
        return MockImage(new_bands, self.date_millis)

    def rename(self, name: str):
        """Rename the most recent band."""
        new_bands = self.bands.copy()
        if "unnamed" in new_bands:
            new_bands[name] = new_bands["unnamed"]
            del new_bands["unnamed"]
        return MockImage(new_bands, self.date_millis)

    def toInt(self):
        """Convert image values to integers."""
        # In our mock, this doesn't do anything meaningful but returns self
        return self

    def date(self):
        """Return the image date in milliseconds since Unix epoch."""
        return self.date_millis


@pytest.fixture
def mock_ee():
    """Fixture to create a properly mocked ee module"""
    mock_ee = mock.Mock()

    # Configure mock for ee.Date
    mock_date = MockDate(1617235200000)
    mock_ee.Date = mock.Mock(return_value=mock_date)

    # Configure mock for ee.Number.parse to return a value
    mock_ee.Number = mock.Mock()
    mock_ee.Number.parse = mock.Mock(return_value=20210401)

    # Configure mock for ee.Image to return a MockImage with the value in an unnamed band
    mock_ee.Image = mock.Mock(side_effect=lambda x: MockImage({"unnamed": x}))

    return mock_ee


class TestPreprocessing:
    """Tests for the preprocessing module."""

    def test_add_date(self, mock_ee):
        """Test adding date band to an image."""
        # Create a mock image with a specific date (April 1, 2021)
        mock_image = MockImage(
            {"B2": 1000, "B4": 2000, "B8": 5000},
            date_millis=1617235200000,
        )  # April 1, 2021 in milliseconds

        # Import with the mock
        with mock.patch.dict("sys.modules", {"ee": mock_ee}):
            # Now import the actual module - after the mock is in place
            from src.processors.preprocessing import add_date

            # Call the actual function
            result = add_date(mock_image)

        # Check that the result is a MockImage
        assert isinstance(result, MockImage)

        # Check that the date band was added
        assert "date" in result.bands

        # Check that the original bands are preserved
        assert "B2" in result.bands
        assert "B4" in result.bands
        assert "B8" in result.bands

    def test_date_formatting(self, mock_ee):
        """Test that the date is correctly formatted as YYYYMMDD."""
        # Create a mock image with a specific date
        mock_image = MockImage({}, date_millis=1617235200000)  # April 1, 2021

        # Import with the mock
        with mock.patch.dict("sys.modules", {"ee": mock_ee}):
            # Now import the actual module - after the mock is in place
            from src.processors.preprocessing import add_date

            # Call the actual function
            result = add_date(mock_image)

        # Verify that the date band was added
        assert "date" in result.bands

        # Verify the date value is correct (20210401)
        assert result.bands["date"] == 20210401
