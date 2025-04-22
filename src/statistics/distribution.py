import os
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio  # type: ignore
import seaborn as sns
from scipy import stats  # type: ignore


class StatisticsCalculator:
    """Calculate basic statistics from geospatial raster data."""

    @staticmethod
    def load_raster_data(
        geotiff_path: str,
    ) -> tuple[np.ndarray, float | None, dict[str, Any]]:
        """
        Load data from a GeoTIFF file.

        Args:
            geotiff_path: Path to the GeoTIFF file

        Returns:
            Tuple containing the valid data array, nodata value, and metadata
        """
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            nodata = src.nodata
            meta = src.meta

            # Filter out nodata values
            if nodata is not None:
                valid_data = data[data != nodata]
            else:
                valid_data = data.flatten()

        return valid_data, nodata, meta

    @staticmethod
    def calculate_basic_stats(data: np.ndarray) -> dict[str, float]:
        """
        Calculate basic statistical measures for the given data.

        Args:
            data: Array of valid data values

        Returns:
            dictionary containing basic statistics
        """
        return {
            "count": len(data),
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std": float(np.std(data)),
            "var": float(np.var(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "range": float(np.max(data) - np.min(data)),
            "percentile_25": float(np.percentile(data, 25)),
            "percentile_75": float(np.percentile(data, 75)),
            "iqr": float(np.percentile(data, 75) - np.percentile(data, 25)),
            "skewness": float(stats.skew(data)),
            "kurtosis": float(stats.kurtosis(data)),
        }


class NormalityTester:
    """Perform normality tests on geospatial data."""

    @staticmethod
    def sample_data(data: np.ndarray, max_sample: int = 5000) -> np.ndarray:
        """
        Sample data for normality tests to improve computational efficiency.

        Args:
            data: Original data array
            max_sample: Maximum sample size

        Returns:
            Sampled data array
        """
        sample_size = min(max_sample, len(data))
        return np.random.choice(data, size=sample_size, replace=False)

    @staticmethod
    def shapiro_test(data: np.ndarray) -> dict[str, float]:
        """
        Perform Shapiro-Wilk normality test.

        Args:
            data: Data array

        Returns:
            Dictionary with test statistic and p-value
        """
        result = stats.shapiro(data)
        return {
            "shapiro_statistic": float(result.statistic),
            "shapiro_p_value": float(result.pvalue),
        }

    @staticmethod
    def dagostino_test(data: np.ndarray) -> dict[str, float]:
        """
        Perform D'Agostino's K-squared normality test.

        Args:
            data: Data array

        Returns:
            Dictionary with test statistic and p-value
        """
        result = stats.normaltest(data)
        return {
            "dagostino_statistic": float(result.statistic),
            "dagostino_p_value": float(result.pvalue),
        }

    @staticmethod
    def anderson_test(data: np.ndarray) -> dict[str, float]:
        """
        Perform Anderson-Darling normality test.

        Args:
            data: Data array

        Returns:
            Dictionary with test statistic and critical value
        """
        result = stats.anderson(data)
        return {
            "anderson_statistic": float(result.statistic),
            "anderson_critical_value": float(
                result.critical_values[2],
            ),  # Critical values at 5% significance
        }

    @classmethod
    def run_all_tests(cls, data: np.ndarray) -> dict[str, float]:
        """
        Run all normality tests on the data.

        Args:
            data: Data array

        Returns:
            Dictionary with all test results
        """
        # Sample data for efficient testing
        sample_data = cls.sample_data(data)

        # Run all tests
        results = {}
        results.update(cls.shapiro_test(sample_data))
        results.update(cls.dagostino_test(sample_data))
        results.update(cls.anderson_test(sample_data))

        return results

    @staticmethod
    def interpret_normality(stats_dict: dict[str, float]) -> tuple[bool, list[str]]:
        """
        Interpret normality test results.

        Args:
            stats_dict: Dictionary with test statistics

        Returns:
            Tuple of (is_normal, reasons)
        """
        is_normal = True
        reasons = []

        # Interpret Shapiro-Wilk test (p < 0.05 means not normal)
        if stats_dict["shapiro_p_value"] < 0.05:
            is_normal = False
            reasons.append(
                f"Shapiro-Wilk test p-value: {stats_dict['shapiro_p_value']:.6f} < 0.05",
            )

        # Interpret D'Agostino's test
        if stats_dict["dagostino_p_value"] < 0.05:
            is_normal = False
            reasons.append(
                f"D'Agostino's test p-value: {stats_dict['dagostino_p_value']:.6f} < 0.05",
            )

        # Interpret Anderson-Darling test
        if stats_dict["anderson_statistic"] > stats_dict["anderson_critical_value"]:
            is_normal = False
            reasons.append(
                f"Anderson-Darling test: {stats_dict['anderson_statistic']:.4f} > "
                f"{stats_dict['anderson_critical_value']:.4f} (critical value)",
            )

        # Interpret skewness
        if "skewness" in stats_dict and abs(stats_dict["skewness"]) > 0.5:
            is_normal = False
            skew_dir = "right" if stats_dict["skewness"] > 0 else "left"
            reasons.append(
                f"Skewness: {stats_dict['skewness']:.4f}, indicating {skew_dir}-skewed distribution",
            )

        return is_normal, reasons


class GeospatialVisualizer:
    """Generate visualizations for geospatial data distribution analysis."""

    @staticmethod
    def create_distribution_plots(
        data: np.ndarray,
        file_name: str,
        stats_dict: dict[str, float],
    ) -> plt.Figure:
        """
        Create a set of distribution plots for the data.

        Args:
            data: Data array
            file_name: Name of the file for titles
            stats_dict: Dictionary with statistics

        Returns:
            Matplotlib figure with plots
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Histogram with KDE
        sns.histplot(data, kde=True, ax=axes[0, 0])
        axes[0, 0].set_title(f"{file_name} - Histogram with Density Curve")
        axes[0, 0].set_xlabel("Value")
        axes[0, 0].set_ylabel("Frequency")

        # Add vertical lines for mean and median
        axes[0, 0].axvline(
            stats_dict["mean"],
            color="red",
            linestyle="--",
            label=f"Mean: {stats_dict['mean']:.3f}",
        )
        axes[0, 0].axvline(
            stats_dict["median"],
            color="green",
            linestyle="--",
            label=f"Median: {stats_dict['median']:.3f}",
        )
        axes[0, 0].legend()

        # Q-Q Plot
        stats.probplot(data, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title(f"{file_name} - Q-Q Plot")

        # Box Plot
        sns.boxplot(y=data, ax=axes[1, 0])
        axes[1, 0].set_title(f"{file_name} - Box Plot")
        axes[1, 0].set_ylabel("Value")

        # Kernel Density Estimation
        sns.kdeplot(data, ax=axes[1, 1])
        axes[1, 1].set_title(f"{file_name} - Density Distribution")
        axes[1, 1].set_xlabel("Value")
        axes[1, 1].set_ylabel("Density")

        plt.tight_layout()
        return fig

    @staticmethod
    def create_comparison_plots(
        data_dict: dict[str, np.ndarray],
        stats_dict: dict[str, dict[str, float]],
    ) -> plt.Figure:
        """
        Create comparison plots for multiple indices.

        Args:
            data_dict: Dictionary mapping index names to data arrays
            stats_dict: Dictionary mapping index names to statistics

        Returns:
            Matplotlib figure with comparison plots
        """
        fig, axes = plt.subplots(len(data_dict), 2, figsize=(15, 5 * len(data_dict)))

        # Handle the case of a single index
        if len(data_dict) == 1:
            axes = np.array([axes])

        for i, (index_name, data) in enumerate(data_dict.items()):
            # Histogram with KDE
            sns.histplot(data, kde=True, ax=axes[i, 0])
            axes[i, 0].set_title(f"{index_name} - Distribution")
            axes[i, 0].set_xlabel("Value")
            axes[i, 0].set_ylabel("Frequency")

            # Add vertical lines for mean and median
            axes[i, 0].axvline(
                stats_dict[index_name]["mean"],
                color="red",
                linestyle="--",
                label=f"Mean: {stats_dict[index_name]['mean']:.3f}",
            )
            axes[i, 0].axvline(
                stats_dict[index_name]["median"],
                color="green",
                linestyle="--",
                label=f"Median: {stats_dict[index_name]['median']:.3f}",
            )
            axes[i, 0].legend()

            # Q-Q Plot
            stats.probplot(data, dist="norm", plot=axes[i, 1])
            axes[i, 1].set_title(f"{index_name} - Q-Q Plot")

        plt.tight_layout()
        return fig

    @staticmethod
    def save_plot(fig: plt.Figure, output_path: str) -> None:
        """
        Save a matplotlib figure to a file.

        Args:
            fig: Matplotlib figure
            output_path: Path to save the plot
        """
        fig.savefig(output_path, dpi=300)


class VegetationIndexAnalyzer:
    """Main class for analyzing vegetation indices."""

    def __init__(self, output_dir: str | None = None):
        """
        Initialize the analyzer.

        Args:
            output_dir: Directory to save analysis results
        """
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        self.stats_calculator = StatisticsCalculator()
        self.normality_tester = NormalityTester()
        self.visualizer = GeospatialVisualizer()

    def analyze_index(self, geotiff_path: str) -> dict[str, float]:
        """
        Analyze a single vegetation index.

        Args:
            geotiff_path: Path to the GeoTIFF file

        Returns:
            Dictionary with statistics
        """
        # Extract file name without extension
        file_name = Path(geotiff_path).stem
        print(f"Analyzing distribution for {file_name}...")

        # Load data
        valid_data, _, _ = StatisticsCalculator.load_raster_data(geotiff_path)

        # Calculate statistics
        stats_dict = StatisticsCalculator.calculate_basic_stats(valid_data)

        # Run normality tests
        normality_results = self.normality_tester.run_all_tests(valid_data)
        stats_dict.update(normality_results)

        # Create visualizations
        if self.output_dir:
            fig = self.visualizer.create_distribution_plots(
                valid_data,
                file_name,
                stats_dict,
            )
            self.visualizer.save_plot(
                fig,
                os.path.join(self.output_dir, f"{file_name}_distribution_analysis.png"),
            )

            # Save statistics to CSV
            pd.DataFrame([stats_dict]).to_csv(
                os.path.join(self.output_dir, f"{file_name}_statistics.csv"),
                index=False,
            )

        # Determine if distribution is normal
        is_normal, reasons = self.normality_tester.interpret_normality(stats_dict)

        # Print results
        self._print_analysis_results(file_name, stats_dict, is_normal, reasons)

        return stats_dict

    def compare_indices(self, geotiff_paths: dict[str, str]) -> pd.DataFrame:
        """
        Compare multiple vegetation indices.

        Args:
            geotiff_paths: Dictionary mapping index names to file paths

        Returns:
            DataFrame with statistics for all indices
        """
        # Store statistics and data for each index
        all_stats = {}
        all_data = {}

        # Analyze each index
        for index_name, path in geotiff_paths.items():
            print(f"\nAnalyzing {index_name}...")

            # Load data
            valid_data, _, _ = StatisticsCalculator.load_raster_data(path)
            all_data[index_name] = valid_data

            # Calculate statistics
            all_stats[index_name] = StatisticsCalculator.calculate_basic_stats(
                valid_data,
            )

        # Create comparison visualizations
        if self.output_dir:
            fig = self.visualizer.create_comparison_plots(all_data, all_stats)
            self.visualizer.save_plot(
                fig,
                os.path.join(self.output_dir, "index_comparison.png"),
            )

        # Create statistics DataFrame
        stats_df = pd.DataFrame.from_dict(all_stats, orient="index")

        # Save to CSV if output directory specified
        if self.output_dir:
            stats_df.to_csv(os.path.join(self.output_dir, "index_comparison_stats.csv"))

        # Print comparison info
        self._print_comparison_results(stats_df)

        return stats_df

    @staticmethod
    def _print_analysis_results(
        file_name: str,
        stats_dict: dict[str, float],
        is_normal: bool,
        reasons: list[str],
    ) -> None:
        """
        Print analysis results for a single index.

        Args:
            file_name: Name of the file
            stats_dict: Dictionary with statistics
            is_normal: Whether the distribution is normal
            reasons: Reasons if the distribution is not normal
        """
        print("\n=== Distribution Analysis Results ===")
        print(f"Mean: {stats_dict['mean']:.4f}")
        print(f"Median: {stats_dict['median']:.4f}")
        print(f"Standard Deviation: {stats_dict['std']:.4f}")
        print(f"Skewness: {stats_dict['skewness']:.4f}")
        print(f"Kurtosis: {stats_dict['kurtosis']:.4f}")

        print("\nNormality Assessment:")
        if is_normal:
            print("The distribution appears approximately normal.")
        else:
            print("The distribution is not normal. Reasons:")
            for reason in reasons:
                print(f"- {reason}")

        # Provide context specific to vegetation indices
        print("\nVegetation Index Context:")
        if file_name.upper().find("MSI") >= 0:
            print(
                "MSI (Moisture Stress Index) typically shows right-skewed distribution in most ecosystems,",
            )
            print(
                "with many values at the lower end (less stressed vegetation) and fewer high values (highly stressed vegetation).",
            )
        elif file_name.upper().find("LAI") >= 0:
            print(
                "LAI (Leaf Area Index) often follows non-normal distributions in natural landscapes,",
            )
            print("especially when the study area contains mixed vegetation types.")
        elif file_name.upper().find("EVI") >= 0:
            print(
                "EVI (Enhanced Vegetation Index) frequently exhibits bimodal or skewed distributions,",
            )
            print(
                "particularly in areas with both vegetated and non-vegetated regions.",
            )

    @staticmethod
    def _print_comparison_results(stats_df: pd.DataFrame) -> None:
        """
        Print comparison results for multiple indices.

        Args:
            stats_df: DataFrame with statistics for all indices
        """
        print("\n=== Vegetation Index Comparison ===")
        print(stats_df)

        # Print expected ranges for common indices
        print("\nTypical ranges for vegetation indices:")
        print("- LAI: 0-8 m²/m² (most natural vegetation: 0.5-5)")
        print("- EVI: -1 to +1 (healthy vegetation: 0.2-0.8)")
        print("- MSI: 0.4-2 (lower values indicate less water stress)")


# Example usage:
if __name__ == "__main__":
    # For single index analysis:
    # Replace with your GeoTIFF file path
    geotiff_path = "path/to/your/vegetation_index.tif"

    # Set output directory (optional)
    output_dir = "./distribution_analysis"

    # Initialize analyzer
    analyzer = VegetationIndexAnalyzer(output_dir)

    # Run the analysis
    stats = analyzer.analyze_index(geotiff_path)

    # For comparing multiple indices:
    geotiff_paths = {
        "LAI": "path/to/your/LAI.tif",
        "EVI": "path/to/your/EVI.tif",
        "MSI": "path/to/your/MSI.tif",
    }

    # Compare distributions
    comparison = analyzer.compare_indices(geotiff_paths)
