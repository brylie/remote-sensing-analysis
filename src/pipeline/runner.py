import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import ee

from src.extractors.sentinel import get_sentinel_data
from src.metrics.moisture import calculate_msi
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
            datetime.now().strftime("%Y-%m-01"),
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

        # Apply MSI calculation if needed
        if "MSI" in metrics:
            data = data.map(calculate_msi)

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
        # Get output configuration
        output_config = self.config.get("output", {})
        output_format = output_config.get("format", "GeoTIFF")
        output_dir = output_config.get("directory", "data/output")
        output_prefix = output_config.get("prefix", "rs_metrics_")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Get area name and dates for naming
        area_name = self.config.get("area", "finland")
        start_date = self.config.get("start_date", datetime.now().strftime("%Y-%m-01"))
        if isinstance(start_date, ee.Date):
            start_date = start_date.format("YYYY-MM-dd").getInfo()

        # Format filename: prefix_area_date
        timestamp = start_date.replace("-", "")
        filename = f"{output_prefix}{area_name}_{timestamp}"

        # Get metrics to save
        metrics = self.config.get("metrics", ["EVI", "LAI", "MSI"])

        # Set up the export region (from the area or from config)
        try:
            from config.areas import get_area

            region = get_area(area_name).geometry().bounds().getInfo()["coordinates"]
        except Exception:
            # Default to a region from config or Finland bounding box if not available
            region = self.config.get("region")

        # Set up export for each metric band
        for metric in metrics:
            if (
                processed_data.bandNames().getInfo()
                and metric in processed_data.bandNames().getInfo()
            ):
                # Create the full path for the output file
                full_path = output_path / f"{filename}_{metric}.tif"

                self.logger.info(f"Exporting {metric} to: {full_path}")

                # Set up Earth Engine export task
                export_task = ee.batch.Export.image.toDrive(
                    image=processed_data.select(metric),
                    description=f"{filename}_{metric}",
                    folder=output_dir,
                    fileNamePrefix=f"{filename}_{metric}",
                    region=region,
                    scale=10,  # 10m resolution for Sentinel-2
                    fileFormat=output_format,
                    maxPixels=1e13,
                )

                # Start the export task
                export_task.start()
                self.logger.info(f"Started export task for {metric}")

                # Store task in results for tracking
                if "export_tasks" not in self.results:
                    self.results["export_tasks"] = []
                self.results["export_tasks"].append(export_task)
            else:
                self.logger.warning(f"Metric {metric} not found in processed data")

        # Also save metadata about the processing
        metadata = {
            "area": area_name,
            "start_date": start_date,
            "end_date": self.config.get("end_date"),
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }

        self.results["metadata"] = metadata
        self.logger.info("Results processing complete, metadata stored")
