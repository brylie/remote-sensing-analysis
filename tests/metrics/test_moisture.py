from unittest import mock


# Create mock classes for testing
class MockBand:
    def __init__(self, value):
        self.value = value

    def divide(self, divisor):
        # Return a new mock band with the divided value
        return MockBand(self.value / divisor)


class MockImage:
    def __init__(self, bands=None):
        self.bands = bands or {}

    def select(self, band_name):
        return self.bands.get(band_name, MockBand(0))

    def expression(self, expression, variables):
        # For MSI, we can implement a simplified calculation
        # that mimics the real behavior for better testing
        if "SWIR / NIR" in expression and "SWIR" in variables and "NIR" in variables:
            swir_value = (
                variables["SWIR"].value if hasattr(variables["SWIR"], "value") else 0
            )
            nir_value = (
                variables["NIR"].value if hasattr(variables["NIR"], "value") else 1
            )
            # Avoid division by zero
            msi_value = swir_value / nir_value if nir_value else 0
            return MockImage({"result": MockBand(msi_value)})
        return MockImage({"result": MockBand(0)})

    def rename(self, name):
        # Return a copy of self with the "result" band renamed
        new_image = MockImage(self.bands.copy())
        if "result" in new_image.bands:
            new_image.bands[name] = new_image.bands["result"]
            del new_image.bands["result"]
        return new_image

    def addBands(self, image):
        # Create a new image with bands from both images
        new_bands = self.bands.copy()
        if isinstance(image, MockImage):
            new_bands.update(image.bands)
        else:
            # Assume it's a single band with the given name
            new_bands["unnamed"] = image
        return MockImage(new_bands)


# Mock the ee module
mock_ee = mock.Mock()
mock_ee.Image = MockImage

# Apply the mock to the ee module
with mock.patch.dict("sys.modules", {"ee": mock_ee}):
    # Import the moisture module
    from src.metrics.moisture import calculate_msi


class TestMoistureMetrics:
    """Tests for the moisture metrics module."""

    def test_calculate_msi(self):
        """Test MSI calculation."""
        # Create a mock image with necessary bands
        bands = {
            "B8": MockBand(5000),  # NIR
            "B11": MockBand(3000),  # SWIR
        }
        mock_image = MockImage(bands)

        # Calculate MSI
        result = calculate_msi(mock_image)

        # Check that the result is a MockImage
        assert isinstance(result, MockImage)

        # Check that the MSI band was added
        assert "MSI" in result.bands

    def test_calculate_msi_with_realistic_values(self):
        """Test MSI calculation with realistic values and validate result."""
        # Create a mock image with realistic values
        bands = {
            "B8": MockBand(5000),  # NIR
            "B11": MockBand(3000),  # SWIR
        }
        mock_image = MockImage(bands)

        # Calculate MSI
        result = calculate_msi(mock_image)

        # Check the actual MSI value (should be SWIR/NIR = 3000/5000 = 0.6)
        # Due to division by 10000 in the function, the expected value is 0.6
        expected_msi = 0.6

        # Our mock implementation has a simplified calculation
        # We can't directly check the value in the test since our mock doesn't actually compute
        # but we can verify the band exists and the function runs without errors
        assert "MSI" in result.bands
        assert isinstance(result.bands["MSI"], MockBand)
        # Assert msi_value is close to expected value
        assert abs(result.bands["MSI"].value - expected_msi) < 0.01

    def test_calculate_msi_with_zero_nir(self):
        """Test MSI calculation with edge case of zero NIR value."""
        # Create a mock image with NIR=0 (edge case)
        bands = {
            "B8": MockBand(0),  # NIR = 0
            "B11": MockBand(3000),  # SWIR
        }
        mock_image = MockImage(bands)

        # Calculate MSI
        # This should run without errors even with NIR=0
        result = calculate_msi(mock_image)

        # Check that the MSI band was added
        assert "MSI" in result.bands
