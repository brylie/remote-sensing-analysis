import sys
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest


# Define our mock Earth Engine classes first, so they can be used in the module mocks
class MockEEImage:
    def __init__(self, bands=None):
        self.bands = bands or {}

    def select(self, band_name):
        return self

    def getDownloadURL(self, params):
        return f"https://example.com/download/{list(self.bands.keys())[0] if self.bands else 'default'}"

    def bandNames(self):
        return MockEEList(list(self.bands.keys()))


class MockEEImageCollection:
    def __init__(self, images=None):
        self.images = images or [MockEEImage()]

    def map(self, func):
        # Apply the function to each image (simplified)
        return self

    def median(self):
        return MockEEImage({"EVI": 0.5, "LAI": 2.5, "MSI": 0.9})


class MockEEFeature:
    def __init__(self):
        pass

    def geometry(self):
        return MockEEGeometry()


class MockEEGeometry:
    def __init__(self):
        pass

    def bounds(self):
        return MockEEGeometry()

    def getInfo(self):
        return {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        }


class MockEEDate:
    def __init__(self, date_str):
        self.date_str = date_str

    def advance(self, count, unit):
        # Simple mock just returns a new date
        return MockEEDate(f"{self.date_str}_advanced")

    def format(self, format_str):
        return MockEEString(self.date_str)

    def getInfo(self):
        return self.date_str


class MockEEString:
    def __init__(self, value):
        self.value = value

    def getInfo(self):
        return self.value


class MockEEList:
    def __init__(self, values):
        self.values = values

    def getInfo(self):
        return self.values


# Create a proper areas module with the required functions and mocks
class MockAreasModule:
    @staticmethod
    def get_area(area_name):
        return MockEEGeometry()


# Create a proper mock Earth Engine module with classes that can be used for isinstance checks
class MockEarthEngine:
    def __init__(self):
        # Create the Date class that can be used in isinstance checks
        self.Date = type("EEDate", (MockEEDate,), {})

        # For instantiation, we use a factory that returns our mock objects
        self._date_factory = mock.MagicMock(side_effect=MockEEDate)

        # When called as a constructor, use our factory
        self.Date.__call__ = self._date_factory

        # Mock other EE classes
        self.Image = mock.MagicMock(side_effect=MockEEImage)
        self.ImageCollection = mock.MagicMock(return_value=MockEEImageCollection())
        self.FeatureCollection = mock.MagicMock(return_value=MockEEFeature())
        self.Initialize = mock.MagicMock()


# Create mock modules
mock_ee = MockEarthEngine()
mock_areas = MockAreasModule()
mock_sentinel = mock.MagicMock()
mock_sentinel.get_sentinel_data = mock.MagicMock(return_value=MockEEImageCollection())
mock_vegetation = mock.MagicMock()
mock_vegetation.calculate_evi = mock.MagicMock()
mock_vegetation.calculate_lai = mock.MagicMock()
mock_moisture = mock.MagicMock()
mock_moisture.calculate_msi = mock.MagicMock()
mock_preprocessing = mock.MagicMock()
mock_preprocessing.add_date = mock.MagicMock()
mock_distribution = mock.MagicMock()
mock_vegetation_analyzer = mock.MagicMock()
mock_vegetation_analyzer.analyze_index.return_value = {"mean": 0.5, "median": 0.4}
mock_vegetation_analyzer.compare_indices.return_value = pd.DataFrame(
    {"mean": {"EVI": 0.5, "LAI": 2.5}, "median": {"EVI": 0.4, "LAI": 2.3}},
)
mock_distribution.VegetationIndexAnalyzer.return_value = mock_vegetation_analyzer

# Apply all mocks
sys.modules["ee"] = mock_ee  # type: ignore
sys.modules["config.areas"] = mock_areas  # type: ignore
sys.modules["src.extractors.sentinel"] = mock_sentinel  # type: ignore
sys.modules["src.metrics.vegetation"] = mock_vegetation  # type: ignore
sys.modules["src.metrics.moisture"] = mock_moisture  # type: ignore
sys.modules["src.processors.preprocessing"] = mock_preprocessing  # type: ignore
sys.modules["src.statistics.distribution"] = mock_distribution  # type: ignore

# Now import the Pipeline class after mocks are in place
from src.pipeline.runner import Pipeline  # noqa: E402


# Create real fixtures for actual test mocking
@pytest.fixture
def mock_ee_module():
    with mock.patch("src.pipeline.runner.ee", mock_ee):
        yield mock_ee


@pytest.fixture
def mock_httpx_module():
    with mock.patch("src.pipeline.runner.httpx") as mock_httpx:
        # Mock the stream context manager
        mock_response = mock.MagicMock()
        mock_response.__enter__.return_value.headers.get.return_value = "1000"
        mock_response.__enter__.return_value.raise_for_status = mock.MagicMock()
        mock_response.__enter__.return_value.iter_bytes.return_value = [b"test data"]

        mock_httpx.stream.return_value = mock_response

        yield mock_httpx


@pytest.fixture
def mock_file_ops():
    with (
        mock.patch("builtins.open", mock.mock_open()),
        mock.patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        yield mock_mkdir


@pytest.fixture
def mock_tqdm_module():
    with mock.patch("src.pipeline.runner.tqdm") as mock_tqdm:
        mock_progress = mock.MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        yield mock_tqdm


class TestPipeline:
    """Tests for the Pipeline class"""

    def test_init(self):
        """Test pipeline initialization"""
        config = {"area": "finland", "metrics": ["EVI", "LAI"]}
        pipeline = Pipeline(config)

        assert pipeline.config == config
        assert pipeline.results == {}

    def test_extract_data(self):
        """Test data extraction"""
        # Create pipeline with config and convert start_date to ee.Date
        config = {
            "area": "finland",
            "metrics": ["EVI", "LAI"],
            "start_date": mock_ee.Date("2023-01-01"),  # Use our MockEEDate object
        }
        pipeline = Pipeline(config)

        # Call the method
        result = pipeline._extract_data()

        # Verify sentinel data was requested
        assert mock_sentinel.get_sentinel_data.called
        assert isinstance(result, MockEEImageCollection)

    def test_calculate_metrics_evi_lai(self):
        """Test metric calculation for EVI and LAI"""
        # Create pipeline with config
        config = {"metrics": ["EVI", "LAI"]}
        pipeline = Pipeline(config)

        # Create test data
        data = MockEEImageCollection()

        # Call the method
        result = pipeline._calculate_metrics(data)

        # Verify the metrics were calculated
        assert isinstance(result, MockEEImage)
        assert "composite" in pipeline.results

    def test_calculate_metrics_msi(self):
        """Test metric calculation for MSI"""
        # Create pipeline with MSI config
        config = {"metrics": ["MSI"]}
        pipeline = Pipeline(config)

        # Create test data
        data = MockEEImageCollection()

        # Call the method
        result = pipeline._calculate_metrics(data)

        # Verify the result
        assert isinstance(result, MockEEImage)

    def test_prepare_file_info(self):
        """Test file info preparation"""
        # Create pipeline with config and ensure start_date is an ee.Date
        config = {
            "area": "finland",
            "start_date": mock_ee.Date("2023-01-01"),
            "output": {"prefix": "test_"},
        }
        pipeline = Pipeline(config)

        # Call the method
        result = pipeline._prepare_file_info()

        # Verify the returned structure
        assert "area_name" in result
        assert "start_date" in result
        assert "filename_base" in result
        assert result["area_name"] == "finland"
        assert result["filename_base"] == "test_finland_20230101"

    def test_get_export_region(self):
        """Test export region retrieval"""
        # Create pipeline
        pipeline = Pipeline({})

        # Call the method
        result = pipeline._get_export_region("finland")

        # Verify the coordinates were returned
        assert isinstance(result, list)

    def test_save_metric_geotiff(
        self,
        mock_httpx_module,
        mock_file_ops,
        mock_tqdm_module,
    ):
        """Test saving GeoTIFF file for a metric"""
        # Create pipeline with mocked logger
        pipeline = Pipeline({})
        pipeline.logger = mock.MagicMock()

        # Explicitly mock the _download_file_with_progress method to call httpx directly
        def mock_download(url, output_file, desc):
            mock_httpx_module.stream("GET", url, timeout=300)

        with mock.patch.object(
            pipeline,
            "_download_file_with_progress",
            side_effect=mock_download,
        ):
            # Set up test data
            metric = "EVI"
            image = MockEEImage({"EVI": 0.5})
            output_path = Path("test_output")
            file_info = {
                "filename_base": "test_finland_20230101",
                "area_name": "finland",
            }
            region = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]

            # Call the method
            result = pipeline._save_metric_geotiff(
                metric,
                image,
                output_path,
                file_info,
                region,
            )

            # Verify the file path was returned
            assert isinstance(result, Path)
            assert str(result).endswith("_EVI.tif")

            # Verify the download was initiated
            mock_httpx_module.stream.assert_called_once()

    def test_save_metadata(self, mock_file_ops):
        """Test saving metadata"""
        # Create pipeline
        pipeline = Pipeline({})

        # Set up test data
        output_path = Path("test_output")
        file_info = {
            "area_name": "finland",
            "start_date": "2023-01-01",
            "filename_base": "test_finland_20230101",
        }
        metrics = ["EVI", "LAI"]
        saved_files = ["test_finland_20230101_EVI.tif", "test_finland_20230101_LAI.tif"]

        # Call the method
        pipeline._save_metadata(output_path, file_info, metrics, saved_files)

        # Verify metadata was stored in results
        assert "metadata" in pipeline.results
        assert pipeline.results["metadata"]["area"] == "finland"
        assert pipeline.results["metadata"]["metrics"] == ["EVI", "LAI"]

    def test_generate_statistics(self):
        """Test statistics generation"""
        # Create pipeline with statistics enabled
        config = {"statistics": {"enabled": True}}
        pipeline = Pipeline(config)
        pipeline.logger = mock.MagicMock()

        # Set up test data
        saved_files = {
            "EVI": Path("test_output/test_finland_20230101_EVI.tif"),
            "LAI": Path("test_output/test_finland_20230101_LAI.tif"),
        }

        # Call the method
        pipeline._generate_statistics(saved_files)

        # Verify stats analyzer was called
        assert mock_vegetation_analyzer.analyze_index.call_count == 2
        mock_vegetation_analyzer.compare_indices.assert_called_once()

        # Verify results were stored
        assert "index_statistics" in pipeline.results
        assert "index_comparison" in pipeline.results

    def test_run_full_pipeline(self, mock_httpx_module, mock_file_ops):
        """Test the full pipeline execution"""
        # Create pipeline with basic config
        config = {
            "area": "finland",
            "metrics": ["EVI", "LAI"],
            "start_date": mock_ee.Date("2023-01-01"),
        }
        pipeline = Pipeline(config)
        pipeline.logger = mock.MagicMock()

        # Mock the internal methods to isolate this test
        with (
            mock.patch.object(pipeline, "_extract_data") as mock_extract,
            mock.patch.object(pipeline, "_calculate_metrics") as mock_calc,
            mock.patch.object(pipeline, "_save_results") as mock_save,
        ):
            # Configure mocks
            mock_extract.return_value = MockEEImageCollection()
            mock_calc.return_value = MockEEImage({"EVI": 0.5, "LAI": 2.5})
            mock_save.return_value = {
                "EVI": Path("test_output/test_finland_20230101_EVI.tif"),
                "LAI": Path("test_output/test_finland_20230101_LAI.tif"),
            }

            # Run the pipeline
            _ = pipeline.run()

            # Verify Earth Engine was initialized
            assert mock_ee.Initialize.called

            # Verify each step was called
            mock_extract.assert_called_once()
            mock_calc.assert_called_once()
            mock_save.assert_called_once()
