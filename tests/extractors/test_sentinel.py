from unittest import mock

import ee
import pytest


class MockEEImageCollection:
    """Mock for Earth Engine ImageCollection objects"""

    def __init__(self, collection_id=None):
        self.filters = []
        self.collection_id = collection_id

    def filterDate(self, start_date, end_date):
        self.filters.append(("date", start_date, end_date))
        return self

    def filterBounds(self, area):
        self.filters.append(("bounds", area))
        return self

    def filter(self, ee_filter):
        self.filters.append(("filter", ee_filter))
        return self


class MockEEDate:
    """Mock for Earth Engine Date objects"""

    def __init__(self, date_str):
        self.date_str = date_str

    def __repr__(self):
        return f"MockEEDate({self.date_str})"


class MockEEGeometry:
    """Mock for Earth Engine Geometry objects"""

    def __init__(self, geom_type="Polygon"):
        self.geom_type = geom_type

    def __repr__(self):
        return f"MockEEGeometry({self.geom_type})"


class MockEEFilter:
    """Mock for Earth Engine Filter objects"""

    @staticmethod
    def lt(field, value):
        return {"type": "lt", "field": field, "value": value}


# Set up the mock EE module
@pytest.fixture
def mock_ee():
    with (
        mock.patch.object(ee, "ImageCollection") as mock_collection,
        mock.patch.object(ee, "Filter") as mock_filter,
    ):
        # Configure the mocks
        mock_collection.side_effect = MockEEImageCollection
        mock_filter.lt = MockEEFilter.lt

        yield ee


# Import the module under test after setting up the EE mock
from src.extractors.sentinel import get_sentinel_data  # noqa: E402


class TestSentinelExtractor:
    """Tests for the Sentinel data extraction module"""

    def test_get_sentinel_data_basic(self, mock_ee):
        """Test the basic functionality of get_sentinel_data function"""
        # Setup test inputs
        start_date = MockEEDate("2023-01-01")
        end_date = MockEEDate("2023-01-31")
        area = MockEEGeometry()

        # Call the function under test
        result = get_sentinel_data(start_date, end_date, area)

        # Verify the result is an ImageCollection
        assert isinstance(result, MockEEImageCollection)

        # Verify the collection ID is correct
        assert result.collection_id == "COPERNICUS/S2_HARMONIZED"

        # Verify the filters are applied correctly
        assert len(result.filters) == 3
        assert result.filters[0] == ("date", start_date, end_date)
        assert result.filters[1] == ("bounds", area)
        assert result.filters[2][0] == "filter"  # Cloud filter

    def test_get_sentinel_data_cloud_filter(self, mock_ee):
        """Test that cloud filtering is correctly applied"""
        # Setup test inputs
        start_date = MockEEDate("2023-01-01")
        end_date = MockEEDate("2023-01-31")
        area = MockEEGeometry()

        # Call the function under test
        result = get_sentinel_data(start_date, end_date, area)

        # Verify the cloud filter is applied with the correct threshold
        # The filter should be the third one applied
        cloud_filter = result.filters[2][1]
        assert cloud_filter["type"] == "lt"
        assert cloud_filter["field"] == "CLOUDY_PIXEL_PERCENTAGE"
        assert cloud_filter["value"] == 30

    def test_get_sentinel_data_different_dates(self, mock_ee):
        """Test with different date ranges"""
        # Setup test inputs with different dates
        start_date = MockEEDate("2022-06-01")
        end_date = MockEEDate("2022-08-31")
        area = MockEEGeometry()

        # Call the function under test
        result = get_sentinel_data(start_date, end_date, area)

        # Verify the date filter is applied correctly
        assert result.filters[0] == ("date", start_date, end_date)

    def test_get_sentinel_data_different_area(self, mock_ee):
        """Test with different area geometry"""
        # Setup test inputs with a different area
        start_date = MockEEDate("2023-01-01")
        end_date = MockEEDate("2023-01-31")
        area = MockEEGeometry("Point")  # Different geometry type

        # Call the function under test
        result = get_sentinel_data(start_date, end_date, area)

        # Verify the bounds filter is applied correctly
        assert result.filters[1] == ("bounds", area)
