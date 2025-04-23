from unittest import mock

import pytest

# We need to mock ee module BEFORE importing areas
mock_ee = mock.Mock()
mock_ee.FeatureCollection.return_value.filter.return_value.geometry.return_value = (
    mock_ee.Geometry()
)
mock_ee.Filter.eq.return_value = {
    "type": "equals",
    "name": "ADM0_NAME",
    "value": "Finland",
}

# Apply the mock to the ee module
with mock.patch.dict("sys.modules", {"ee": mock_ee}):
    # Now we can import the areas module
    from config.areas import AREAS, get_area


class TestAreas:
    """Tests for the areas module."""

    def test_get_area_valid(self):
        """Test retrieval of a valid area."""
        # Get the area for "finland"
        result = get_area("finland")

        # Assert that we got the correct area from the AREAS dictionary
        assert result == AREAS["finland"]

    def test_get_area_invalid(self):
        """Test retrieval of an invalid area raises ValueError."""
        # Try to get an area that doesn't exist
        with pytest.raises(ValueError) as excinfo:
            get_area("invalid_area")

        # Check that the error message is as expected
        assert "not found" in str(excinfo.value)
        assert "Available areas:" in str(excinfo.value)
        assert "finland" in str(excinfo.value)

    def test_areas_dictionary_structure(self):
        """Test that the AREAS dictionary has the expected structure."""
        # Check that AREAS is a dictionary
        assert isinstance(AREAS, dict)

        # Check that "finland" is in AREAS
        assert "finland" in AREAS
