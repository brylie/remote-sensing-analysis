import logging
from datetime import datetime
from typing import Any

import ee

from src.extractors.sentinel import get_sentinel_data
from src.metrics.vegetation import calculate_evi, calculate_lai
from src.processors.preprocessing import add_date


class Pipeline:
    def __init__(self, config: dict[str, Any]):
        """
        Initialize pipeline with configuration.

        Args:
            config: Dictionary with pipeline configuration
        """
        self.config = config
        self.logger = logging.getLogger("geospatial_pipeline")
        self.results: dict[str, Any] = {}

    def run(self) -> dict[str, Any]:
        """
        Run the complete pipeline.

        Returns:
            Dictionary with processing results
        """
        try:
            ee.Initialize()
            self.logger.info("Starting pipeline run")

            # Extract data
            self.logger.info("Extracting Sentinel data")
            sentinel_data = self._extract_data()

            # Process and calculate metrics
            self.logger.info("Calculating metrics")
            processed_data = self._calculate_metrics(sentinel_data)

            # Save results
            self.logger.info("Saving results")
            self._save_results(processed_data)

            return self.results

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    def _extract_data(self) -> ee.ImageCollection:
        """
        Extract raw data.

        Returns:
            Image collection from Sentinel data
        """
        start_date = self.config.get("start_date") or ee.Date(
            datetime.now().strftime("%Y-%m-01")
        )
        end_date = self.config.get("end_date") or start_date.advance(1, "month")
        area_name = self.config.get("area", "finland")

        from config.areas import get_area

        area = get_area(area_name)

        return get_sentinel_data(start_date, end_date, area)

    def _calculate_metrics(self, data: ee.ImageCollection) -> ee.Image:
        """
        Calculate all configured metrics.

        Args:
            data: Collection of satellite images

        Returns:
            Composite image with calculated metrics
        """
        metrics = self.config.get("metrics", ["EVI", "LAI"])

        # Apply EVI calculation to all images
        if "EVI" in metrics:
            data = data.map(calculate_evi)

        # Apply LAI calculation if needed
        if "LAI" in metrics and "EVI" in metrics:
            data = data.map(calculate_lai)

        # Add date bands
        data = data.map(add_date)

        # Create composite
        composite = data.median()

        # Store in results
        self.results["composite"] = composite
        return composite

    def _save_results(self, processed_data: ee.Image) -> None:
        """
        Save results to specified output locations.

        Args:
            processed_data: Processed image with calculated metrics
        """
        # Implementation depends on your needs
        pass
