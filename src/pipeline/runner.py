import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import ee
import httpx
from tqdm import tqdm

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
        Save results to specified output locations as GeoTIFF files.

        Args:
            processed_data: Processed image with calculated metrics
        """
        # Get output configuration
        output_config = self.config.get("output", {})
        output_dir = output_config.get("directory", "data/output")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Prepare base file information
        file_info = self._prepare_file_info()

        # Get metrics to save
        metrics = self.config.get("metrics", ["EVI", "LAI", "MSI"])

        # Get area geometry for export
        region = self._get_export_region(file_info["area_name"])

        # Download and save each metric
        saved_files: list[str] = []
        for metric in metrics:
            if (
                processed_data.bandNames().getInfo()
                and metric in processed_data.bandNames().getInfo()
            ):
                output_file = self._save_metric_geotiff(
                    metric=metric,
                    image=processed_data,
                    output_path=output_path,
                    file_info=file_info,
                    region=region,
                )
                if output_file:
                    saved_files.append(str(output_file.name))
            else:
                self.logger.warning(f"Metric {metric} not found in processed data")

        # Save metadata
        self._save_metadata(output_path, file_info, metrics, saved_files)

        self.logger.info(f"Results processing complete, files saved to {output_dir}")

    def _prepare_file_info(self) -> dict[str, str]:
        """
        Prepare base file information for output files.

        Returns:
            Dictionary containing file naming information
        """
        output_config = self.config.get("output", {})
        output_prefix = output_config.get("prefix", "rs_metrics_")

        # Get area name and dates for naming
        area_name = self.config.get("area", "finland")
        start_date = self.config.get("start_date", datetime.now().strftime("%Y-%m-01"))

        if isinstance(start_date, ee.Date):
            start_date = start_date.format("YYYY-MM-dd").getInfo()

        # Format filename: prefix_area_date
        timestamp = start_date.replace("-", "")
        filename_base = f"{output_prefix}{area_name}_{timestamp}"

        return {
            "area_name": area_name,
            "start_date": start_date,
            "filename_base": filename_base,
        }

    def _get_export_region(self, area_name: str) -> list:
        """
        Get the region coordinates for export.

        Args:
            area_name: Name of the area to export

        Returns:
            List of coordinates defining the region bounds
        """
        from config.areas import get_area

        area = get_area(area_name)
        return area.bounds().getInfo()["coordinates"]

    def _save_metric_geotiff(
        self,
        metric: str,
        image: ee.Image,
        output_path: Path,
        file_info: dict[str, str],
        region: list,
    ) -> Optional[Path]:
        """
        Download and save a single metric as a GeoTIFF file.

        Args:
            metric: Name of the metric to save
            image: Earth Engine image containing the metric
            output_path: Directory to save the file
            file_info: Dictionary with file naming information
            region: Coordinates defining the export region

        Returns:
            Path to the saved file, or None if saving failed
        """
        output_file = output_path / f"{file_info['filename_base']}_{metric}.tif"
        self.logger.info(f"Saving {metric} to: {output_file}")

        try:
            # Set up parameters for the GeoTIFF export
            params = {
                "region": region,
                "dimensions": 1024,  # Limit size for reasonable download
                "format": "GEO_TIFF",
                "crs": "EPSG:4326",  # WGS84
            }

            # Get download URL for this band
            url = image.select(metric).getDownloadURL(params)

            # Download the GeoTIFF with progress indication
            self._download_file_with_progress(url, output_file, f"Downloading {metric}")

            self.logger.info(f"Successfully saved {metric} to {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Failed to save {metric} to {output_file}: {str(e)}")
            return None

    def _download_file_with_progress(
        self, url: str, output_file: Path, desc: str
    ) -> None:
        """
        Download a file with progress indication.

        Args:
            url: URL to download from
            output_file: Path where the file should be saved
            desc: Description for the progress bar
        """
        with httpx.stream("GET", url, timeout=300) as response:
            response.raise_for_status()

            # Get total size if available
            total_size = int(response.headers.get("Content-Length", 0))

            # Set up progress bar
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc=desc, leave=True
            ) as progress_bar:
                with open(output_file, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))

    def _save_metadata(
        self,
        output_path: Path,
        file_info: dict[str, str],
        metrics: list[str],
        saved_files: list[str],
    ) -> None:
        """
        Save metadata about the processing run.

        Args:
            output_path: Directory where metadata should be saved
            file_info: Dictionary with file naming information
            metrics: List of metrics that were processed
            saved_files: List of files that were successfully saved
        """
        metadata_file = output_path / f"{file_info['filename_base']}_metadata.json"

        metadata = {
            "area": file_info["area_name"],
            "start_date": file_info["start_date"],
            "end_date": self.config.get("end_date"),
            "metrics": metrics,
            "files_saved": saved_files,
            "timestamp": datetime.now().isoformat(),
        }

        self.results["metadata"] = metadata

        try:
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Saved processing metadata to {metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {str(e)}")
