"""
Main entry point for the Pharma Sales Forecasting Project.
"""

from src.pipelines.etl_pipeline import ETLPipeline


def main():

    pipeline = ETLPipeline(
        input_path="data/raw/salesmonthly.csv",
        output_path="data/processed/pharma_sales_processed.csv"
    )

    pipeline.run()


if __name__ == "__main__":
    main()